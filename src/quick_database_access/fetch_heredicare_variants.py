from lxml import etree, objectify
import requests
import os
from io import StringIO
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import tempfile
import datetime
from pdf_generator import pdf_gen
import subprocess


class xml_validator:

    def __init__(self, xsd_path: str):
        xmlschema_doc = etree.parse(xsd_path)
        self.xmlschema = etree.XMLSchema(xmlschema_doc)

    def validate(self, xml: str) -> bool:
        if xml.startswith('<'):
            xml = StringIO(xml)
        xml_doc = etree.parse(xml)
        result = self.xmlschema.validate(xml_doc)
        return result
    
    def object_from_string_validate(self, xml: str) -> bool:
        parser = objectify.makeparser(schema = self.xmlschema)
        result = objectify.fromstring(xml, parser)
        return result

    def object_from_string(self, xml: str) -> bool:
        return objectify.fromstring(xml)



rootdir = os.path.dirname(__file__)
log_file_path = rootdir + "/logs/heredicare_import_" + datetime.datetime.today().strftime('%Y-%m-%d') + '.log' #_%H:%M:%S
log_file = open(log_file_path, 'w')
conn = Connection()


def get_heredicare_seqid_list():
    list_validator = xml_validator('/mnt/users/ahdoebm1/HerediVar/doc/api/seq_id_list.xsd')
    seq_id_list_request = requests.get('https://portal.img.med.uni-tuebingen.de/ahdoebm1/HerediCareAPI/v1/seq_id_list.php')
    #res = validator.validate('/mnt/users/ahdoebm1/HerediVar/src/tools/mock-api/seq_id_list.xml')
    seq_id_list_xml = seq_id_list_request.text
    is_valid = list_validator.validate(seq_id_list_xml)

    if not is_valid:
        log_file.write('Code: ~~' + get_log_code('seqid list does not have the correct format') + '~~ ' +"FATAL ERROR: heredicare seq_id_list endpoint returned xml of wrong format: \n" + seq_id_list_xml)
        return []
    
    seqid_obj = list_validator.object_from_string(seq_id_list_xml)
    seqids_heredicare = []
    for seqid in seqid_obj.SeqId:
        seqids_heredicare.append(seqid.get('id'))
    
    return seqids_heredicare


def compare_seq_id_lists():
    seqids_heredicare = get_heredicare_seqid_list()
    seqids_heredivar = conn.get_seqid_list()

    seqids_heredicare = set(seqids_heredicare)
    seqids_heredivar = set(seqids_heredivar)

    intersection = list(seqids_heredivar & seqids_heredicare)
    heredivar_exclusive_variants = list(seqids_heredivar - seqids_heredicare)
    heredicare_exclusive_variants = list(seqids_heredicare - seqids_heredivar)

    return intersection, heredivar_exclusive_variants, heredicare_exclusive_variants



def process_new_seqids(seqids):
    variant_validator = xml_validator('/mnt/users/ahdoebm1/HerediVar/doc/api/variant.xsd')
    tmp_file_path = tempfile.gettempdir() + "/heredicare_variant_import.vcf"

    for seqid in seqids:
        print(seqid)
        variant_request = requests.get('https://portal.img.med.uni-tuebingen.de/ahdoebm1/HerediCareAPI/v1/variant.php?seqid=' + str(seqid) + '\n')
        variant_xml = variant_request.text
        is_valid_variant = variant_validator.validate(variant_xml)
        
        if not is_valid_variant:
            log_file.write('Code: ~~' + get_log_code('variant xml of incorrect format') + '~~ ' + "ERROR: heredicare variant endpoint returned xml of wrong format: \n" + variant_xml + '\n')
            continue
        
        heredicare_variant = variant_validator.object_from_string(variant_xml)
        chr = heredicare_variant.get('chr')
        chr_num = functions.validate_chr(chr)
        if not functions.validate_chr(chr):
            log_file.write('Code: ~~' + get_log_code('wrong chr number during import') + '~~ ' +"ERROR: discovered wrong chr: " + chr + ' during parsing seqid: ' + seqid + '\n')
            continue
        chr = 'chr' + chr_num
        pos = heredicare_variant.get('pos')
        if int(pos) <= 0:
            log_file.write('Code: ~~' + get_log_code('wrong position number during import') + '~~ ' +"ERROR: discovered wrong position number: " + str(pos) + " during parsing of seqid: " + seqid + '\n')
        ref = heredicare_variant.get('ref')
        alt = heredicare_variant.get('alt')
        reference_genome_build = heredicare_variant.get('genome_build')

        
        functions.variant_to_vcf(chr, pos, ref, alt, tmp_file_path)
        command = ['/mnt/users/ahdoebm1/HerediVar/src/quick_database_access/scripts/preprocess_variant.sh', '-i', tmp_file_path]

        if reference_genome_build == 'GRCh37':
            command.append('-l') # enable liftover
            log_file.write('Code: ~~' + get_log_code('enabling liftover') + '~~ ' + "INFO: enabling liftover for variant: " + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ' ' + reference_genome_build + " with seqid " + str(seqid) + '\n')
        
        returncode, err_msg, command_output = functions.execute_command(command, 'preprocess_variant')
        print(err_msg)
        print(command_output)

        if returncode != 0:
            log_file.write('Code: ~~' + get_log_code('execution error during variant preprocessing') + '~~ ' +"ERROR: could not transform variant: " + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' : \n' + err_msg + '\n')
            continue
        
        if reference_genome_build == 'GRCh37':
            if '[INFO]  Failed to map: 0' not in err_msg:
                log_file.write('Code: ~~' + get_log_code('variant could not be lifted') + '~~ ' +"ERROR: could not lift variant: " + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' \n')
                continue

        variant = functions.read_vcf_variant(tmp_file_path)[0] # accessing only the first element of the returned list is save because we process only one variant at a time
        chr = variant.CHROM
        pos = variant.POS
        ref = variant.REF
        alt = variant.ALT

        is_duplicate = conn.check_variant_duplicate(chr, pos, ref, alt)
        print(is_duplicate)
        if not is_duplicate:
            conn.insert_variant(chr, pos, ref, alt)
            log_file.write('Code: ~~' + get_log_code('inserted new variant') + '~~ ' +"SUCCESS: imported variant: " + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' \n')
        else:
            log_file.write('Code: ~~' + get_log_code('discovered duplicate') + '~~ ' +"INFO: discovered variant which is already in heredivar but seqid is unknown (this is a duplicate): " + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' ' + seqid + ' \n')
        variant_id = conn.get_variant_id(chr, pos, ref, alt)
        conn.insert_external_variant_id_from_variant_id(variant_id, seqid, 'heredicare') # we know that this is a new seqid so we need to save it either way
        log_file.write('Code: ~~' + get_log_code('inserted new seqid') + '~~ ' +"SUCCESS: imported seqid: " + seqid + ' for variant: ' + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' \n')
            
        # insert missing meta information
        for center in heredicare_variant.findall('ClassificationCenter'):
            classification = center.get('class')
            date = center.get('date')
            center_name = center.get('center_name')
            comment = center.get('comment')
            # if it is not a duplicate do it. If it IS a duplicate chekc if the classification is already contained in there and do it if it is not there
            if not is_duplicate or (not conn.check_heredicare_center_classification(variant_id, classification, center_name, comment, date)):
                conn.insert_heredicare_center_classification(variant_id, classification, center_name, comment, date)
                log_file.write('Code: ~~' + get_log_code('inserted new heredicare center classification') + '~~ ' +"SUCCESS: imported new heredicare variant classification: " + classification + ' ' + date + ' ' + center_name + ' ' + comment + ". For variant: " + variant_id + ' ' + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' \n')

        task_force = heredicare_variant.find('ClassificationTaskForce')
        if task_force is not None:
            consensus_classification = task_force.get('class')
            date = task_force.get('date')
            comment = task_force.get('comment')
            if not is_duplicate or (not conn.check_consensus_classification(variant_id, consensus_classification, comment, date)):
                path_to_report = 'default_heredicare_report.pdf'
                gen = pdf_gen(path_to_report)
                gen.generate_default_report(reason="it was imported from HerediCare")
                evidence_document_base64 = gen.get_base64_encoding()
                conn.insert_consensus_classification_from_variant_id(variant_id, consensus_classification, comment, date, evidence_document_base64)
                log_file.write('Code: ~~' + get_log_code('inserted new consensus classification') + '~~ ' +"SUCCESS: imported new consensus classification from heredicare: " + consensus_classification + ' ' + date + ' ' + comment + ". For variant: " + variant_id + ' ' + chr + ' ' + pos + ' ' + ref + ' ' + alt + ' \n')



def process_deleted_seqids(seqids):
    for seqid in seqids:
        variant_id = conn.get_variant_id_from_external_id(seqid, 'heredicare')

        if conn.get_consensus_classification(variant_id, most_recent = True) is not None:
            log_file.write('Code: ~~' + get_log_code('did not delete variant because there is a consensus classification') + '~~ ' +"INFO: did not delete variant with id: " + variant_id + ' because there is an existing consensus classification' + ' \n')
            continue
        user_classifications = conn.get_user_classifications(variant_id)
        if len(user_classifications) > 0:
            log_file.write('Code: ~~' + get_log_code('did not delete variant because there are user classifications') + '~~ ' +"INFO: did not delete variant with id: " + variant_id + ' because there are user classifications from users with ids: ' + str([x[3] for x in user_classifications]) + ' \n')
            continue
        
        conn.delete_variant(variant_id)
        log_file.write('Code: ~~' + get_log_code('deleted variant') + '~~ ' +"SUCCESS: deleted variant with id: " + variant_id + ' \n')



def get_log_code(log_type):
    if log_type == 'seqid list does not have the correct format':
        return 'e0'
    elif log_type == 'variant xml of incorrect format':
        return 'e1'
    elif log_type == 'wrong chr number during import':
        return 'e2'
    elif log_type == 'execution error during variant preprocessing':
        return 'e3'
    elif log_type == 'wrong position number during import':
        return 'e4'
    elif log_type == 'variant could not be lifted':
        return 'e5'
    

    elif log_type == 'enabling liftover':
        return 'i0'
    elif log_type == 'discovered duplicate':
        return 'i1'
    elif log_type == 'did not delete variant because there is a consensus classification':
        return 'i2'
    elif log_type == 'did not delete variant because there are user classifications':
        return 'i3'

    elif log_type == 'inserted new variant':
        return 's0'
    elif log_type == 'deleted variant':
        return 's1'
    elif log_type == 'inserted new heredicare center classification':
        return 's2'
    elif log_type == 'inserted new consensus classification':
        return 's3'



if __name__ == '__main__':
    os.environ['NO_PROXY'] = 'portal.img.med.uni-tuebingen.de'

    intersection, heredivar_exclusive_variants, heredicare_exclusive_variants = compare_seq_id_lists()
    print(heredivar_exclusive_variants)
    print(heredicare_exclusive_variants)
    print(intersection)

    process_new_seqids(heredicare_exclusive_variants)
    #process_deleted_seqids(heredivar_exclusive_variants)
    
    conn.close()




# variantenimport:

# variante noch nicht da: import variant + seqid + metainformation
# variante ist ein duplikat: import seqid wenn die noch nicht da ist + zusätzliche metainformationen?
# seqid gelöscht: lösche variante sofern keine klassifizierung durch die task force vorhanden ist
# variante hat neue klassifizierungen durch zentren: checken welche schon da sind und neue importieren

# variante hat eine taskforce klassifikation DAZUBEKOMMEN??
# variante wurde geändert???


# get list of seqids from heredicare
# get list of seqids from heredivar
# compare the two sets 
#  - get the seqids which are only contained in heredicare (-> new ones)
#  - get the seqids which are only contained in heredivar (-> deleted ones)
#  - get the seqids which are contained in both (-> old ones which might need an update?)

# iterate over new seqids and receive information from heredicare api
# check if variant is a duplicate
# NOT a DUPLICATE: 
# -> import the variant and all its metainformation and seqid into heredivar
# DUPLICATE: (this means that the seqid is new but it refers to the same variant)
# -> import new seqid
# check if there is additional metainformation and import it for the variant in heredivar and skip the rest

# iterate over the deleted ones
# check if there is a vus task force classification for the variant
# -> delete variant & all its metainformation form the database (needs to be done in the right order)

# iterate over the maybe update ones


# generate log file & show stats on frontend page