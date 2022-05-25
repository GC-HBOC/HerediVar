
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import tempfile
import datetime
from pdf_generator import pdf_gen
from heredicare_interface import heredicare_interface


log_file_path = ''
log_file = None
conn = None
heredicare_api = None

def get_log_file_path():
    global log_file_path
    return log_file_path

def init(log_file_date):
    global log_file_path
    global log_file
    global conn
    global heredicare_api
    global family_count_dict
    global cases_count_dict

    os.environ['NO_PROXY'] = 'portal.img.med.uni-tuebingen.de'

    rootdir = os.path.dirname(__file__)
    log_file_path = rootdir + "/logs/heredicare_import:" + log_file_date + '.log' #datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '.log' #
    log_file = open(log_file_path, 'w')
    conn = Connection()

    heredicare_api = heredicare_interface()



def endit():
    global log_file
    global conn
    
    log_file.close()
    conn.close()

def compare_seq_id_lists():
    global log_file
    global conn
    global heredicare_api

    execution_code, seqids_heredicare = heredicare_api.get_heredicare_seqid_list()
    if execution_code != 0:
        log_file.write('Code: ~~' + get_log_code('xml of incorrect format') + '~~ ' +"FATAL ERROR: heredicare seq_id_list endpoint returned xml of wrong format! Import aborted.... \n")
        return [], [], []

    seqids_heredivar = conn.get_seqid_list()

    seqids_heredicare = set(seqids_heredicare)
    seqids_heredivar = set(seqids_heredivar)

    intersection = list(seqids_heredivar & seqids_heredicare)
    log_file.write('Code: ~~' + get_log_code('discovered common seqids') + '~~ ' +"INFO: a total of " + str(len(intersection)) + " seqids were found in both, HerediCare and HerediVar. \n")
    heredivar_exclusive_variants = list(seqids_heredivar - seqids_heredicare) # this contains only variants which have a seqid in heredivar!!!!
    log_file.write('Code: ~~' + get_log_code('discovered heredivar exclusive seqids') + '~~ ' +"INFO: a total of " + str(len(heredivar_exclusive_variants)) + " seqids were found only in HerediVar. \n")
    heredicare_exclusive_variants = list(seqids_heredicare - seqids_heredivar)
    log_file.write('Code: ~~' + get_log_code('discovered heredicare exclusive seqids') + '~~ ' +"INFO: a total of " + str(len(heredicare_exclusive_variants)) + " seqids were found only in HerediCare. \n")

    return intersection, heredivar_exclusive_variants, heredicare_exclusive_variants



def process_new_seqids(seqids):
    global log_file
    global conn
    global heredicare_api

    tmp_file_path = tempfile.gettempdir() + "/heredicare_variant_import.vcf"
    tmp_vcfcheck_out_path = tempfile.gettempdir() + "/heredicare_variant_import_vcf_errors.txt"

    for seqid in seqids:
        print('processing new seqid: ' + seqid)
        # get variant from heredicare api
        execution_code, orig_chr, orig_pos, orig_ref, orig_alt, reference_genome_build, meta_info = heredicare_api.get_variant(seqid)
        if execution_code == 1:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' + "ERROR: heredicare variant endpoint returned xml of wrong format for seqid:" + str(seqid) + "\n")
            continue
        elif execution_code == 2:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: discovered wrong chr: " + str(orig_chr) + ' during parsing seqid: ' + str(seqid) + '\n')
            continue
        elif execution_code == 3:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: missing information: " + 'chr: ' + str(orig_chr) + ', pos: ' + orig_pos + ', ref: ' + orig_ref + ', alt: ' + orig_alt + ', reference genome build: ' + reference_genome_build + ". During parsing of seqid: " + str(seqid) + '\n')
            continue
        

        # perform preprocessing
        functions.variant_to_vcf(orig_chr, orig_pos, orig_ref, orig_alt, tmp_file_path)
        command = ['/mnt/users/ahdoebm1/HerediVar/src/quick_database_access/scripts/preprocess_variant.sh', '-i', tmp_file_path, '-o', tmp_vcfcheck_out_path]

        if reference_genome_build == 'GRCh37':
            command.append('-l') # enable liftover
            log_file.write('Code: ~~' + get_log_code('enabling liftover') + '~~ ' + "INFO: enabling liftover for variant: " + orig_chr + ' ' + str(orig_pos) + ' ' + orig_ref + ' ' + orig_alt + ' ' + reference_genome_build + " with seqid " + str(seqid) + '\n')
        
        returncode, err_msg, command_output = functions.execute_command(command, 'preprocess_variant')
        #print(err_msg)
        #print(command_output)

        if returncode != 0:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: could not transform variant: " + orig_chr + ' ' + str(orig_pos) + ' ' + orig_ref + ' ' + orig_alt + ' : \n' + err_msg + '\n')
            continue
        vcfcheck_errors = open(tmp_vcfcheck_out_path + '.pre', 'r').read()
        if 'ERROR:' in vcfcheck_errors:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: input vcf contains errors: " + vcfcheck_errors.replace('\n', ' ') + ' \n')
            continue
        if reference_genome_build == 'GRCh37':
            if '[INFO]  Failed to map: 0' not in err_msg:
                log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: could not lift variant: " + orig_chr + ' ' + str(orig_pos) + ' ' + orig_ref + ' ' + orig_alt + ' \n')
                continue
        vcfcheck_errors = open(tmp_vcfcheck_out_path + '.post', 'r').read()
        if 'ERROR:' in vcfcheck_errors:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: the vcf contains errors after preprocessing: " + vcfcheck_errors.replace('\n', ' ') + ' \n')
            continue

        variant = functions.read_vcf_variant(tmp_file_path)[0] # accessing only the first element of the returned list is save because we process only one variant at a time
        new_chr = variant.CHROM
        new_pos = variant.POS
        new_ref = variant.REF
        new_alt = variant.ALT

        # insert variant & seqid where apropriate
        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt)
        print('is duplicate: ' + str(is_duplicate))
        if not is_duplicate:
            conn.insert_variant(new_chr, new_pos, new_ref, new_alt, orig_chr, orig_pos, orig_ref, orig_alt)
            log_file.write('Code: ~~' + get_log_code('inserted new variant') + '~~ ' +"SUCCESS: imported variant: " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + ' \n')
        else:
            log_file.write('Code: ~~' + get_log_code('discovered duplicate') + '~~ ' +"INFO: discovered variant which is already in heredivar but seqid is unknown (this is a duplicate): " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + ' ' + str(seqid) + ' \n')
        variant_id = conn.get_variant_id(new_chr, new_pos, new_ref, new_alt)
        conn.insert_external_variant_id_from_variant_id(variant_id, seqid, 'heredicare') # we know that this is a new seqid so we need to save it either way
        log_file.write('Code: ~~' + get_log_code('inserted new seqid') + '~~ ' +"SUCCESS: imported seqid: " + str(seqid) + ' for variant: ' + new_chr + ' ' + new_pos + ' ' + new_ref + ' ' + new_alt + ' \n')


        # insert missing meta information
        insert_missing_meta_information(variant_id, meta_info, is_duplicate, seqid, new_chr, new_pos, new_ref, new_alt, count_variant_updates=False)




def process_deleted_seqids(seqids):
    global log_file
    global conn
    global heredicare_api

    for seqid in seqids:
        print('processing deleted seqid: ' + seqid)
        variant_id = conn.get_variant_id_from_external_id(seqid, 'heredicare')
        all_seqids_for_variant = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
        if len(all_seqids_for_variant) > 1:
            conn.delete_seqid(seqid)
            log_file.write('Code: ~~' + get_log_code('deleted seqid') + '~~ ' +"SUCCESS: deleted seqid: " + str(seqid) + ' for variant id: ' + str(variant_id) + ' \n')
        else:
            if conn.get_consensus_classification(variant_id, most_recent = True) is not None:
                log_file.write('Code: ~~' + get_log_code('rejected delete') + '~~ ' +"INFO: did not delete variant with id: " + str(variant_id) + ' because there is an existing consensus classification' + ' \n')
                continue
            user_classifications = conn.get_user_classifications(variant_id)
            if len(user_classifications) > 0:
                log_file.write('Code: ~~' + get_log_code('rejected delete') + '~~ ' +"INFO: did not delete variant with id: " + str(variant_id) + ' because there are user classifications from users with ids: ' + str([x[3] for x in user_classifications]) + ' \n')
                continue
        
            conn.delete_variant(variant_id)
            log_file.write('Code: ~~' + get_log_code('deleted variant') + '~~ ' +"SUCCESS: deleted variant with id: " + str(variant_id) + ' \n')


def process_existing_seq_ids(seqids):
    global log_file
    global conn
    global heredicare_api

    for seqid in seqids:
        print('processing existing seqid: ' + seqid)
        # get variant id from heredivar
        variant_id = conn.get_variant_id_from_external_id(seqid, 'heredicare')
        orig_variant = conn.get_orig_variant(variant_id)
        orig_chr = orig_variant[0]
        orig_pos = orig_variant[1]
        orig_ref = orig_variant[2].upper()
        orig_alt = orig_variant[3].upper()
        
        # get variant from heredicare api
        execution_code, heredicare_chr, heredicare_pos, heredicare_ref, heredicare_alt, reference_genome_build, meta_info = heredicare_api.get_variant(seqid)
        if execution_code == 1:
            log_file.write('Code: ~~' + get_log_code('xml of incorrect format') + '~~ ' + "ERROR: heredicare variant endpoint returned xml of wrong format. \n")
            continue
        # no need to check the remaining execution code because the variant was imported previously and errors were checked there so it should be correct if nothing changed!
        if (orig_chr, str(orig_pos), orig_ref, orig_alt) != (heredicare_chr, heredicare_pos, heredicare_ref, heredicare_alt):
            log_file.write('Code: ~~' + get_log_code('unequal heredicare and heredivar variant') + '~~ ' +"ERROR: vcf style information for seqid: " + str(seqid) + '  are unequal heredivar (' + orig_chr + ' ' + str(orig_pos) + ' ' + orig_ref + ' ' + orig_alt + ') and heredicare ('  + heredicare_chr + ' ' + str(heredicare_pos) + ' ' + heredicare_ref + ' ' + heredicare_alt +  ') \n')
            continue

        # insert missing meta information
        known_seqids = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
        capture_counts = True
        if len(known_seqids) > 1:
            capture_counts = False # skip count stuff if this is a REAL duplicate else update counts as well ONLY 'problem': if there is an update in duplicate variants it is not tracked here. But counts are useless nonetheless for duplicated variants!
        insert_missing_meta_information(variant_id, meta_info, True, seqid, orig_chr, orig_pos, orig_ref, orig_alt, count_variant_updates = True, capture_counts = capture_counts)




def insert_missing_meta_information(variant_id, meta_info, is_duplicate, seqid, chr, pos, ref, alt, count_variant_updates = True, capture_counts = True): # vcf info & seqid are only for logging!
    global log_file
    global conn
    global heredicare_api

    updated_meta_info = False

    if capture_counts:
        occurances = meta_info.find('Occurances')
        cases_count = occurances.get('cases_count')
        error_occured = False
        try:
            if int(cases_count) >= 0:
                if not is_duplicate:
                    conn.insert_variant_annotation(variant_id, 34, cases_count)
                    updated_meta_info = True
                    log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: imported new valid cases count (" + str(cases_count) + ") for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
                else: # valid number but duplicate variant -> overwrite existing counts (-> result: if there are multiple seqids for the same variant only the counts from the last one are saved. --> Works well if there is an update to HerediCare: Consider a duplicate variant with two different count values. The last one is saved in HerediVar. If HerediCare decides to delete one of the seqids and update the counts for the other one the deprecated values will be overwritten)
                    value = conn.get_variant_annotation(variant_id, 34)[0][3]
                    if value != cases_count:
                        updated_meta_info = True
                        conn.update_variant_annotation(variant_id, 34, cases_count)
                        log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: updated cases count (from " + str(value) + ' to ' + str(cases_count) + ") for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
            else: # not a valid number
                error_occured = True
        except:
            error_occured = True
        finally:
            if error_occured:
                log_file.write('Code: ~~' + get_log_code('skipped variant annotation') + '~~ ' +"ERROR: did not import cases count for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + '), because it is not a valid number: ' + str(cases_count) + '\n')

        family_count = occurances.get('family_count')
        error_occured = False
        try:
            if int(family_count) >= 0:
                if not is_duplicate:
                    conn.insert_variant_annotation(variant_id, 35, family_count)
                    updated_meta_info = True
                    log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: imported new valid family count (" + str(family_count) + ") for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
                else: # valid number but duplicate variant
                    value = conn.get_variant_annotation(variant_id, 35)[0][3]
                    if value != family_count:
                        updated_meta_info = True
                        conn.update_variant_annotation(variant_id, 35, family_count)
                        log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: updated family count (from " + str(value) + ' to ' + str(family_count) + ") for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
            else:
                error_occured = True
        except:
            error_occured = True
        finally:
            if error_occured:
                log_file.write('Code: ~~' + get_log_code('skipped variant annotation') + '~~ ' +"ERROR: did not import family count for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + '), because it is not a valid number: ' + str(family_count) + '\n')


    for center in meta_info.findall('ClassificationCenter'):
        classification = center.get('class')
        date = center.get('date')
        center_name = center.get('center_name')
        comment = center.get('comment')
        # if it is not a duplicate do it. If it IS a duplicate chekc if the classification is already contained in there and do it if it is not there
        if not is_duplicate or (not conn.check_heredicare_center_classification(variant_id, classification, center_name, comment, date)):
            conn.insert_heredicare_center_classification(variant_id, classification, center_name, comment, date)
            updated_meta_info = True
            log_file.write('Code: ~~' + get_log_code('imported variant classification') + '~~ ' +"SUCCESS: imported new heredicare variant classification: " + str(classification) + ' ' + str(date) + ' ' + center_name + ' ' + str(comment) + ". For variant: " + str(variant_id) + ' ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ' \n')

    task_force = meta_info.find('ClassificationTaskForce')
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
            updated_meta_info = True
            log_file.write('Code: ~~' + get_log_code('imported variant classification') + '~~ ' +"SUCCESS: imported new consensus classification from heredicare: " + str(consensus_classification) + ' ' + str(date) + ' ' + str(comment) + ". For variant: " + str(variant_id) + ' ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ' \n')


    if updated_meta_info and count_variant_updates:
        log_file.write('Code: ~~' + get_log_code('updated meta information') + '~~ ' +"INFO: imported new meta information for seqid: " + str(seqid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')


def get_log_code(log_type):
    if log_type == 'xml of incorrect format':
        return 'e1'
    elif log_type == 'error import':
        return 'e2'
    elif log_type =='skipped variant annotation':
        return 'e6'
    elif log_type == 'unequal heredicare and heredivar variant':
        return 'e7'
    

    elif log_type == 'enabling liftover':
        return 'i0'
    elif log_type == 'discovered duplicate':
        return 'i1'
    elif log_type == 'rejected delete':
        return 'i2'
    elif log_type == 'discovered heredivar exclusive seqids':
        return 'i5'
    elif log_type == 'discovered heredicare exclusive seqids':
        return 'i6'
    elif log_type == 'discovered common seqids':
        return 'i7'
    elif log_type == 'updated meta information':
        return 'i8'


    elif log_type == 'inserted new variant':
        return 's0'
    elif log_type == 'deleted variant':
        return 's1'
    elif log_type == 'imported variant classification':
        return 's2'
    elif log_type == 'imported variant annotation':
        return 's4'
    elif log_type == 'inserted new seqid':
        return 's5'
    elif log_type == 'deleted seqid':
        return 's6'


def process_all(log_file_date):

    init(log_file_date)

    intersection, heredivar_exclusive_variants, heredicare_exclusive_variants = compare_seq_id_lists()
    #print(heredivar_exclusive_variants)
    #print(heredicare_exclusive_variants)
    #print(intersection)

    process_new_seqids(heredicare_exclusive_variants)
    process_deleted_seqids(heredivar_exclusive_variants)
    process_existing_seq_ids(intersection)



    endit()



if __name__ == '__main__':
    process_all()




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
# check if there is a user-classification or vus taskforce classification for the variant if it doesnt:
# -> delete variant & all its metainformation form the database

# iterate over the maybe update ones
# get variant from heredicare & check all annotations if they are already in there or if they added something new


# generate log file & show stats on frontend page




# if there are duplicated variants with different seqids:
# ignore count values
# ALSO display an ! on the variant page which states that there are multiple seqids for this variant and that the counts are probably wrong