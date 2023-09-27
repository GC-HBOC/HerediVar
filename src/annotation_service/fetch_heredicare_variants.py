
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
from common.pdf_generator import pdf_gen
import tempfile
from annotation_service.heredicare_interface import Heredicare


log_file_path = ''
log_file = None
conn = None
heredicare_api = None
user_id = ''

def get_log_file_path():
    global log_file_path
    return log_file_path

def init(f, u):
    global log_file_path
    global log_file
    global conn
    global heredicare_api
    global user_id

    os.environ['NO_PROXY'] = 'portal.img.med.uni-tuebingen.de'
    log_file_path = f #datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '.log' #
    log_file = open(log_file_path, 'w')
    conn = Connection()

    user_id = u

    heredicare_api = Heredicare()



def endit():
    global log_file
    global conn
    
    log_file.close()
    conn.close()

def compare_v_id_lists(vids_heredicare, vids_heredivar):
    global log_file
    #global conn
    #global heredicare_api

    #execution_code, vids_heredicare = heredicare_api.get_heredicare_vid_list()
    #if execution_code != 0:
    #    log_file.write('Code: ~~' + get_log_code('xml of incorrect format') + '~~ ' +"FATAL ERROR: heredicare v_id_list endpoint returned xml of wrong format! Import aborted.... \n")
    #    return [], [], []

    #vids_heredivar = conn.get_vid_list()

    vids_heredicare = set(vids_heredicare)
    vids_heredivar = set(vids_heredivar)

    intersection = list(vids_heredivar & vids_heredicare)
    log_file.write('Code: ~~' + get_log_code('discovered common vids') + '~~ ' +"INFO: a total of " + str(len(intersection)) + " vids were found in both, HerediCare and HerediVar. \n")
    heredivar_exclusive_variants = list(vids_heredivar - vids_heredicare) # this contains only variants which have a vid in heredivar!!!!
    log_file.write('Code: ~~' + get_log_code('discovered heredivar exclusive vids') + '~~ ' +"INFO: a total of " + str(len(heredivar_exclusive_variants)) + " vids were found only in HerediVar. \n")
    heredicare_exclusive_variants = list(vids_heredicare - vids_heredivar)
    log_file.write('Code: ~~' + get_log_code('discovered heredicare exclusive vids') + '~~ ' +"INFO: a total of " + str(len(heredicare_exclusive_variants)) + " vids were found only in HerediCare. \n")

    return intersection, heredivar_exclusive_variants, heredicare_exclusive_variants



def process_new_vids(vids):
    global log_file
    global conn
    global heredicare_api
    global user_id

    tmp_file_path = tempfile.gettempdir() + "/heredicare_variant_import.vcf"
    tmp_vcfcheck_out_path = tempfile.gettempdir() + "/heredicare_variant_import_vcf_errors.txt"

    for vid in vids:
        print('processing new vid: ' + vid)
        # get variant from heredicare api
        execution_code, orig_chr, orig_pos, orig_ref, orig_alt, reference_genome_build, meta_info = heredicare_api.get_variant(vid)
        if execution_code == 1:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' + "ERROR: heredicare variant endpoint returned xml of wrong format for vid:" + str(vid) + "\n")
            continue
        elif execution_code == 2:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: discovered wrong chr: " + str(orig_chr) + ' during parsing vid: ' + str(vid) + '\n')
            continue
        elif execution_code == 3:
            log_file.write('Code: ~~' + get_log_code('error import') + '~~ ' +"ERROR: missing information: " + 'chr: ' + str(orig_chr) + ', pos: ' + orig_pos + ', ref: ' + orig_ref + ', alt: ' + orig_alt + ', reference genome build: ' + reference_genome_build + ". During parsing of vid: " + str(vid) + '\n')
            continue
        

        # perform preprocessing
        functions.variant_to_vcf(orig_chr, orig_pos, orig_ref, orig_alt, tmp_file_path)
        command = ['/mnt/users/ahdoebm1/HerediVar/src/common/scripts/preprocess_variant.sh', '-i', tmp_file_path, '-o', tmp_vcfcheck_out_path]

        if reference_genome_build == 'GRCh37':
            command.append('-l') # enable liftover
            log_file.write('Code: ~~' + get_log_code('enabling liftover') + '~~ ' + "INFO: enabling liftover for variant: " + orig_chr + ' ' + str(orig_pos) + ' ' + orig_ref + ' ' + orig_alt + ' ' + reference_genome_build + " with vid " + str(vid) + '\n')
        
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
            unmapped_variant = functions.read_vcf_variant(tmp_file_path + '.lifted.unmap')
            if len(unmapped_variant) > 0:
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

        # insert variant & vid where apropriate
        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt)
        print('is duplicate: ' + str(is_duplicate))
        if not is_duplicate:

            conn.insert_variant(new_chr, new_pos, new_ref, new_alt, orig_chr, orig_pos, orig_ref, orig_alt, user_id)
            log_file.write('Code: ~~' + get_log_code('inserted new variant') + '~~ ' +"SUCCESS: imported variant: " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + ' \n')
        else:
            log_file.write('Code: ~~' + get_log_code('discovered duplicate') + '~~ ' +"INFO: discovered variant which is already in heredivar but vid is unknown (this is a duplicate): " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + ' ' + str(vid) + ' \n')
        variant_id = conn.get_variant_id(new_chr, new_pos, new_ref, new_alt)
        conn.insert_external_variant_id(variant_id, vid, 'heredicare') # we know that this is a new vid so we need to save it either way
        log_file.write('Code: ~~' + get_log_code('inserted new vid') + '~~ ' +"SUCCESS: imported vid: " + str(vid) + ' for variant: ' + new_chr + ' ' + new_pos + ' ' + new_ref + ' ' + new_alt + ' \n')


        # insert missing meta information
        insert_missing_meta_information(variant_id, meta_info, is_duplicate, vid, new_chr, new_pos, new_ref, new_alt, count_variant_updates=False)




def process_deleted_vids(vids):
    global log_file
    global conn
    global heredicare_api

    for vid in vids:
        print('processing deleted vid: ' + vid)
        variant_id = conn.get_variant_id_from_external_id(vid, 'heredicare')
        all_vids_for_variant = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
        if len(all_vids_for_variant) > 1:
            conn.delete_external_id(vid, 'heredicare')
            log_file.write('Code: ~~' + get_log_code('deleted vid') + '~~ ' +"SUCCESS: deleted vid: " + str(vid) + ' for variant id: ' + str(variant_id) + ' \n')
        else:
            consensus_classification = conn.get_consensus_classification(variant_id, most_recent = True)
            if len(consensus_classification) > 0:
                log_file.write('Code: ~~' + get_log_code('rejected delete') + '~~ ' +"INFO: did not delete variant with id: " + str(variant_id) + ' because there is an existing consensus classification' + ' \n')
                continue
            user_classifications = conn.get_user_classifications(variant_id)
            if len(user_classifications) > 0:
                log_file.write('Code: ~~' + get_log_code('rejected delete') + '~~ ' +"INFO: did not delete variant with id: " + str(variant_id) + ' because there are user classifications from users with ids: ' + str([x[3] for x in user_classifications]) + ' \n')
                continue
        
            conn.delete_variant(variant_id)
            log_file.write('Code: ~~' + get_log_code('deleted variant') + '~~ ' +"SUCCESS: deleted variant with id: " + str(variant_id) + ' \n')


def process_existing_v_ids(vids):
    global log_file
    global conn
    global heredicare_api

    for vid in vids:
        print('processing existing vid: ' + vid)
        # get variant id from heredivar
        variant_id = conn.get_variant_id_from_external_id(vid, 'heredicare')
        orig_variant = conn.get_orig_variant(variant_id)
        orig_chr = orig_variant[0]
        orig_pos = orig_variant[1]
        orig_ref = orig_variant[2].upper()
        orig_alt = orig_variant[3].upper()
        
        # get variant from heredicare api
        execution_code, heredicare_chr, heredicare_pos, heredicare_ref, heredicare_alt, reference_genome_build, meta_info = heredicare_api.get_variant(vid)
        if execution_code == 1:
            log_file.write('Code: ~~' + get_log_code('xml of incorrect format') + '~~ ' + "ERROR: heredicare variant endpoint returned xml of wrong format. \n")
            continue
        # no need to check the remaining execution code because the variant was imported previously and errors were checked there so it should be correct if nothing changed!
        if (orig_chr, str(orig_pos), orig_ref, orig_alt) != (heredicare_chr, heredicare_pos, heredicare_ref, heredicare_alt):
            log_file.write('Code: ~~' + get_log_code('unequal heredicare and heredivar variant') + '~~ ' +"ERROR: vcf style information for vid: " + str(vid) + '  are unequal heredivar (' + orig_chr + ' ' + str(orig_pos) + ' ' + orig_ref + ' ' + orig_alt + ') and heredicare ('  + heredicare_chr + ' ' + str(heredicare_pos) + ' ' + heredicare_ref + ' ' + heredicare_alt +  ') \n')
            continue

        # insert missing meta information
        known_vids = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
        capture_counts = True
        if len(known_vids) > 1:
            capture_counts = False # skip count stuff if this is a REAL duplicate else update counts as well ONLY 'problem': if there is an update in duplicate variants it is not tracked here. But counts are useless nonetheless for duplicated variants!
        insert_missing_meta_information(variant_id, meta_info, True, vid, orig_chr, orig_pos, orig_ref, orig_alt, count_variant_updates = True, capture_counts = capture_counts)




def insert_missing_meta_information(variant_id, meta_info, is_duplicate, vid, chr, pos, ref, alt, count_variant_updates = True, capture_counts = True): # vcf info & vid are only for logging!
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
                    log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: imported new valid cases count (" + str(cases_count) + ") for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
                else: # valid number but duplicate variant -> overwrite existing counts (-> result: if there are multiple vids for the same variant only the counts from the last one are saved. --> Works well if there is an update to HerediCare: Consider a duplicate variant with two different count values. The last one is saved in HerediVar. If HerediCare decides to delete one of the vids and update the counts for the other one the deprecated values will be overwritten)
                    value = conn.get_variant_annotation(variant_id, 34)[0][3]
                    if value != cases_count:
                        updated_meta_info = True
                        conn.update_variant_annotation(variant_id, 34, cases_count)
                        log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: updated cases count (from " + str(value) + ' to ' + str(cases_count) + ") for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
            else: # not a valid number
                error_occured = True
        except:
            error_occured = True
        finally:
            if error_occured:
                log_file.write('Code: ~~' + get_log_code('skipped variant annotation') + '~~ ' +"ERROR: did not import cases count for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + '), because it is not a valid number: ' + str(cases_count) + '\n')

        family_count = occurances.get('family_count')
        error_occured = False
        try:
            if int(family_count) >= 0:
                if not is_duplicate:
                    conn.insert_variant_annotation(variant_id, 35, family_count)
                    updated_meta_info = True
                    log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: imported new valid family count (" + str(family_count) + ") for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
                else: # valid number but duplicate variant
                    value = conn.get_variant_annotation(variant_id, 35)[0][3]
                    if value != family_count:
                        updated_meta_info = True
                        conn.update_variant_annotation(variant_id, 35, family_count)
                        log_file.write('Code: ~~' + get_log_code('imported variant annotation') + '~~ ' +"SUCCESS: updated family count (from " + str(value) + ' to ' + str(family_count) + ") for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')
            else:
                error_occured = True
        except:
            error_occured = True
        finally:
            if error_occured:
                log_file.write('Code: ~~' + get_log_code('skipped variant annotation') + '~~ ' +"ERROR: did not import family count for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + '), because it is not a valid number: ' + str(family_count) + '\n')


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
            root = os.path.dirname(os.path.abspath(__file__))
            path_to_report = os.path.join(root, 'imported_consensus_classification_reports', 'default_heredicare_report.pdf')
            gen = pdf_gen(path_to_report)
            gen.generate_default_report(reason="it was imported from HerediCare")
            evidence_document_base64 = functions.get_base64_encoding(path_to_report)
            conn.insert_consensus_classification_from_variant_id(variant_id, consensus_classification, comment, date, evidence_document_base64)
            updated_meta_info = True
            log_file.write('Code: ~~' + get_log_code('imported variant classification') + '~~ ' +"SUCCESS: imported new consensus classification from heredicare: " + str(consensus_classification) + ' ' + str(date) + ' ' + str(comment) + ". For variant: " + str(variant_id) + ' ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ' \n')


    if updated_meta_info and count_variant_updates:
        log_file.write('Code: ~~' + get_log_code('updated meta information') + '~~ ' +"INFO: imported new meta information for vid: " + str(vid) + ' (variant: ' + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + ') \n')


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
    elif log_type == 'discovered heredivar exclusive vids':
        return 'i5'
    elif log_type == 'discovered heredicare exclusive vids':
        return 'i6'
    elif log_type == 'discovered common vids':
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
    elif log_type == 'inserted new vid':
        return 's5'
    elif log_type == 'deleted vid':
        return 's6'



def process_all(log_file_path, user_id):
    global heredicare_api
    global conn

    init(log_file_path, user_id)

    execution_code, vids_heredicare = heredicare_api.get_heredicare_vid_list()
    if execution_code != 0:
        log_file.write('Code: ~~' + get_log_code('xml of incorrect format') + '~~ ' +"FATAL ERROR: heredicare vid_list endpoint returned xml of wrong format! Import aborted.... \n")
    else:
        vids_heredivar = conn.get_vid_list()

        intersection, heredivar_exclusive_variants, heredicare_exclusive_variants = compare_v_id_lists(vids_heredicare, vids_heredivar)
        #print(heredivar_exclusive_variants)
        #print(heredicare_exclusive_variants)
        #print(intersection)

        process_new_vids(heredicare_exclusive_variants)
        process_deleted_vids(heredivar_exclusive_variants)
        process_existing_v_ids(intersection)
        
    endit()


def update_specific_vids(log_file_path, vids, user_id):
    global heredicare_api

    init(log_file_path, user_id)

    execution_code, vids_heredicare = heredicare_api.get_heredicare_vid_list()
    if execution_code != 0:
        log_file.write('Code: ~~' + get_log_code('xml of incorrect format') + '~~ ' +"FATAL ERROR: heredicare v_id_list endpoint returned xml of wrong format! Import aborted.... \n")
    else:
        intersection, heredivar_exclusive_variants, heredicare_exclusive_variants = compare_v_id_lists(vids_heredicare, vids)

        process_deleted_vids(heredivar_exclusive_variants)
        process_existing_v_ids(intersection)
    

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