
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import common.functions as functions
from common.db_IO import Connection
from common.heredicare_interface import Heredicare
from annotation_service.main import process_one_request, get_default_job_config

from webapp.utils import search_utils
from webapp import celery, mail

from flask_mail import Message
from flask import render_template
import time

# errors:
from mysql.connector import Error, InternalError
from urllib.error import HTTPError
from celery.exceptions import Ignore
import traceback


###################################################################################
############## IMPORT VARIANT LIST THAT GOT UPDATE SINCE LAST IMPORT ##############
###################################################################################

def start_variant_import(vids, user_id, user_roles, conn: Connection): # starts the celery task
    source = "heredicare_specific"
    if vids == "update": # we are not processing specific vids
        source = "heredicare_update"
    elif vids == "all":
        source = "heredicare_complete"
    new_import_request = conn.insert_import_request(user_id, source)
    import_queue_id = new_import_request.id

    task = heredicare_variant_import.apply_async(args=[vids, user_id, user_roles, import_queue_id]) # start task
    task_id = task.id

    conn.update_import_queue_celery_task_id(import_queue_id, celery_task_id = task_id) # save the task id for status updates

    return import_queue_id

@celery.task(bind=True, retry_backoff=5, max_retries=3, soft_time_limit=6000)
def heredicare_variant_import(self, vids, user_id, user_roles, import_queue_id):
    """Background task for fetching variants from HerediCare"""
    self.update_state(state='PROGRESS')

    try:
        conn = Connection(user_roles)

        conn.update_import_queue_status(import_queue_id, status = "progress", message = "")

        status, message = import_variants(vids, conn, user_id, user_roles, import_queue_id)

    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        message = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()
    except Error as e:
        status = "error"
        message = "There was a database error: " + str(e)  + ' ' + traceback.format_exc()
    except HTTPError as e:
        status = "retry"
        message = "Attempting retry because of http error: " + str(e)  + ' ' + traceback.format_exc()
    except Exception as e:
        status = "error"
        message = "There was a runtime error: " + str(e) + ' ' + traceback.format_exc()


    if status != "retry":
        conn.close_import_request(import_queue_id, status = status, message = message)
    else:
        conn.update_import_queue_status(import_queue_id, status = status, message = message)

    conn.close()
    
    #status, message = fetch_heredicare(vid, heredicare_interface)
    if status == 'error':
        self.update_state(state="FAILURE", meta={ 
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'
                    })
        raise Ignore()
    elif status == "retry":
        self.update_state(state="RETRY", meta={
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'})
        heredicare_variant_import.retry()
    else:
        self.update_state(state="SUCCESS")


def import_variants(vids, conn: Connection, user_id, user_roles, import_queue_id): # the task worker
    status = "success"
    message = ""

    if vids in ['all', 'update']: # we do not have any specific vid(s) to to import -> search for updated / new vids in heredicare
        do_filter = True
        if vids == 'all':
            do_filter = False
        status, message, intersection, heredivar_exclusive_vids, heredicare_exclusive_vids = get_vid_sets(conn, do_filter)
        vids = []

        #intersection = []
        #heredicare_exclusive_vids = ['22081944', '22082395']
        #heredivar_exclusive_vids = [] #917, 12453169, 18794502

        vids.extend(intersection)
        vids.extend(heredivar_exclusive_vids)
        vids.extend(heredicare_exclusive_vids)


    if status == "success":
        # spawn one task for each variant import
        for vid in vids:
            _ = start_import_one_variant(vid, import_queue_id, user_id, user_roles, conn)

    return status, message


def get_vid_sets(conn: Connection, do_filter = True):
    intersection = []
    heredivar_exclusive_vids = []
    heredicare_exclusive_vids = []
    heredicare_interface = Heredicare()

    all_vids_heredicare_raw, status, message = heredicare_interface.get_vid_list()
    if status == "success":

        min_date = None
        if do_filter:
            min_date_1 = conn.get_min_date_heredicare_import(source = "heredicare_complete")
            min_date_2 = conn.get_min_date_heredicare_import(source = "heredicare_update") # returns None if there are no successful imports (or no import requests at all)
            if min_date_1 is None:
                min_date = min_date_2
            elif min_date_2 is None:
                min_date = min_date_1
            else:
                min_date = max(min_date_1, min_date_2)
            #min_date = functions.str2datetime(min_date, fmt = '%Y-%m-%dT%H:%M:%S')
        filtered_vids_heredicare, all_vids_heredicare, status, message = heredicare_interface.filter_vid_list(all_vids_heredicare_raw, min_date)

        if status == "success":
            annotation_type_id = conn.get_most_recent_annotation_type_id("heredicare_vid")
            all_vids_heredivar = conn.get_all_external_ids_from_annotation_type(annotation_type_id)

            #intersection, heredivar_exclusive_vids, heredicare_exclusive_vids = compare_v_id_lists(all_vids_heredicare, vids_heredivar, filtered_vids_heredicare)

            filtered_vids_heredicare = set(filtered_vids_heredicare)
            all_vids_heredivar = set(all_vids_heredivar)
            all_vids_heredicare = set(all_vids_heredicare)

            intersection = all_vids_heredicare & all_vids_heredivar # known vids
            heredivar_exclusive_vids = all_vids_heredivar - all_vids_heredicare # this contains variants which only have a vid in heredivar!!!!
            heredicare_exclusive_vids = all_vids_heredicare - all_vids_heredivar # new vids

            # filter for vids of interest
            # do not filter deleted vids because they are not returned by the heredicare api
            intersection = list(intersection & filtered_vids_heredicare)
            heredivar_exclusive_vids = list(heredivar_exclusive_vids)
            heredicare_exclusive_vids = list(heredicare_exclusive_vids & filtered_vids_heredicare)

            print("Total vids HerediCaRe: " + str(len(all_vids_heredicare)))
            print("Total vids HerediVar: " + str(len(all_vids_heredivar)))
            print("Total filtered vids HerediCaRe: " + str(len(filtered_vids_heredicare)))
            print("Intersection of filtered heredicare and heredivar vids: " + str(len(intersection)))
            print("Deleted vids (unknown to heredicare but known to heredivar): " + str(len(heredivar_exclusive_vids)))
            print("New vids (unknown to heredivar but known to heredicare): " + str(len(heredicare_exclusive_vids)))

    return status, message, intersection, heredivar_exclusive_vids, heredicare_exclusive_vids





################################################
############## IMPORT THE VARIANT ##############
################################################

def start_import_one_variant(vid, import_queue_id, user_id, user_roles, conn: Connection): # starts the celery task
    import_variant_queue_id = conn.insert_variant_import_request(vid, import_queue_id)

    task = import_one_variant_heredicare.apply_async(args=[vid, user_id, user_roles, import_variant_queue_id])
    task_id = task.id

    conn.update_import_variant_queue_celery_id(import_variant_queue_id, celery_task_id = task_id)

    return task_id

def retry_variant_import(import_variant_queue_id, user_id, user_roles, conn: Connection):
    conn.reset_import_variant_queue(import_variant_queue_id)
    vid = conn.get_vid_from_import_variant_queue(import_variant_queue_id)

    task = import_one_variant_heredicare.apply_async(args=[vid, user_id, user_roles, import_variant_queue_id])
    task_id = task.id

    conn.update_import_variant_queue_celery_id(import_variant_queue_id, celery_task_id = task_id)

    return task_id


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, soft_time_limit=600)
def import_one_variant_heredicare(self, vid, user_id, user_roles, import_variant_queue_id):
    """Background task for fetching variants from HerediCare"""
    self.update_state(state='PROGRESS')
    
    try:
        conn = Connection(user_roles)
        conn.update_import_variant_queue_status(import_variant_queue_id, status = "progress", message = "")
        status, message = fetch_heredicare(vid, user_id, conn, insert_variant = True, perform_annotation = True)
    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        message = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()
    except Error as e:
        status = "error"
        message = "There was a database error: " + str(e)  + ' ' + traceback.format_exc()
    except HTTPError as e:
        status = "retry"
        message = "Attempting retry because of http error: " + str(e)  + ' ' + traceback.format_exc()
    except Exception as e:
        status = "error"
        message = "There was a runtime error: " + str(e) + ' ' + traceback.format_exc()
    
    #print(status)

    if status != "retry":
        conn.close_import_variant_request(import_variant_queue_id, status = status, message = message[:10000])
    else:
        conn.update_import_variant_queue_status(import_variant_queue_id, status = status, message = message[:10000])
    
    conn.close()

    if status == 'error':
        self.update_state(state='FAILURE', meta={ 
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'
                    })
        raise Ignore()
    elif status == "retry":
        self.update_state(state="RETRY", meta={
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'})
        import_one_variant_heredicare.retry()
    else:
        self.update_state(state="SUCCESS")




def fetch_heredicare(vid, user_id, conn:Connection, insert_variant = True, perform_annotation = True):
    heredicare_interface = Heredicare()
    variant, status, message = heredicare_interface.get_variant(vid)

    if status != 'success': # error in variant retrieval from heredicare
        return status, message

    if (str(variant.get("VISIBLE", "0")) == "0" or len(variant) == 0) and insert_variant: # skip invisible vid or vid that is unknown by heredicare
        annotation_type_id = conn.get_most_recent_annotation_type_id("heredicare_vid")
        variant_id = conn.get_variant_id_from_external_id(vid, annotation_type_id) # check if heredivar knows the vid
        if variant_id is not None: # heredivar knows the vid, but heredicare doesnt OR vid is now invisible
            conn.delete_external_id(vid, annotation_type_id, variant_id)
            status = "deleted"
            all_vids_for_variant = conn.get_external_ids_from_variant_id(variant_id, annotation_type_id) # check if the variant still has heredicare vids
            if len(all_vids_for_variant) == 0: # hide variant in heredivar if not
                conn.hide_variant(variant_id, is_hidden = False)
                message = "Variant is already in database, but is hidden in HerediCare. It is now also hidden in HerediVar. If another VID points to this variant which is processed later this variant will get visible again."
            else:
                message = "Deleted VID because this vid is now hidden in HerediCare"
        else:
            status = "error"
            message = "HerediCaRe VID is invisible or unknown by HerediCaRe and HerediVar does not know this VID"
    else: # import variant
        status, message = map_hg38(variant, user_id, conn, insert_variant = insert_variant, perform_annotation = perform_annotation, external_ids = [vid])

    return status, message






###########################################################
############## START VARIANT VCF BULK IMPORT ##############
###########################################################

def start_variant_import_vcf(user_id, user_roles, conn: Connection, filename, filepath, genome_build):
    import_request = conn.insert_import_request(user_id, source = "vcf")
    import_queue_id = import_request.id

    task = variant_import_vcf.apply_async(args=[user_id, user_roles, import_queue_id, filepath, genome_build]) # start task
    task_id = task.id

    conn.update_import_queue_celery_task_id(import_queue_id, celery_task_id = task_id) # save the task id for status updates

    return import_queue_id


@celery.task(bind=True, retry_backoff=5, max_retries=3)
def variant_import_vcf(self, user_id, user_roles, import_queue_id, filepath, genome_build):
    """ Background task for importing a large number of variants from a tsv file """
    self.update_state("PROGRESS")

    try:
        conn = Connection(user_roles)

        conn.update_import_queue_status(import_queue_id, status = "progress", message = "")

        with open(filepath, "r") as vcf_file:
            vcf_file = list(vcf_file)
            status, message = insert_variants_vcf_file(vcf_file, genome_build, user_id, import_queue_id, conn)

    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        message = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()
    except Error as e:
        status = "error"
        message = "There was a database error: " + str(e)  + ' ' + traceback.format_exc()
    except HTTPError as e:
        status = "retry"
        message = "Attempting retry because of http error: " + str(e)  + ' ' + traceback.format_exc()
    except Exception as e:
        status = "error"
        message = "There was a runtime error: " + str(e) + ' ' + traceback.format_exc()

    if status != "retry":
        conn.close_import_request(import_queue_id, status, message)
        functions.rm(filepath)
    else:
        conn.update_import_queue_status(import_queue_id, status = status, message = message)

    conn.close()
    
    if status == 'error':
        self.update_state(state="FAILURE", meta={ 
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'
                    })
        raise Ignore()
    elif status == "retry":
        self.update_state(state="RETRY", meta={
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'})
        variant_import_vcf.retry()
    else:
        self.update_state(state="SUCCESS")



def insert_variants_vcf_file(vcf_file, genome_build, user_id, import_queue_id, conn:Connection):
    status = "success"
    message = ""
    skipped_lines = []
    for i, line in enumerate(vcf_file, 1):
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        parts = line.split('\t')
        if len(parts) < 8:
            skipped_lines.append(i)
            continue

        chrom = parts[0]
        pos = parts[1]
        ref = parts[3]
        alt = parts[4]

        was_successful, variant_message, variant_id = validate_and_insert_variant(chrom, pos, ref, alt, genome_build, user_id = user_id, conn = conn)
        variant_import_queue_id = conn.insert_variant_import_request(vid=variant_id, import_queue_id=import_queue_id)
        variant_status = "success"
        if (not was_successful and variant_id is not None) or "already in database!" in variant_message: # variant is already in database, start a reannotation
            variant_status = "update"
        elif not was_successful:
            variant_status = "error"
        conn.update_import_variant_queue_status(variant_import_queue_id, variant_status, variant_message)

    if len(skipped_lines) > 0:
        message += "Skipped lines " + str(skipped_lines) + " because they are malformed"
    return status, message





# this is the main add variant from heredicare function! -> sanitizes and inserts variant
def map_hg38(variant, user_id, conn:Connection, insert_variant = True, perform_annotation = True, external_ids = None): # the task worker
    message = ""
    status = "success"
    variant_id = None

    allowed_sequence_letters = "ACGT"

    # first check if the hg38 information is there
    chrom = variant.get('CHROM')
    pos = variant.get('POS_HG38')
    ref = variant.get('REF_HG38')
    alt = variant.get('ALT_HG38')
    genome_build = "GRCh38"

    was_successful = False
    if all([x is not None for x in [chrom, pos, ref, alt]]):
        was_successful, new_message, variant_id = validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn, user_id, allowed_sequence_letters = allowed_sequence_letters, insert_variant = insert_variant, perform_annotation=perform_annotation)
        if new_message not in message:
            message = functions.collect_info(message, "hg38_msg=", new_message, sep = " ~~ ")

    if not was_successful:
        # check hg19 information
        pos = variant.get('POS_HG19')
        ref = variant.get('REF_HG19')
        alt = variant.get('ALT_HG19')
        genome_build = "GRCh37"
        
        was_successful = False
        if all([x is not None for x in [chrom, pos, ref, alt]]):
            was_successful, new_message, variant_id = validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn, user_id, allowed_sequence_letters = allowed_sequence_letters, insert_variant = insert_variant, perform_annotation=perform_annotation)
            if new_message not in message:
                message = functions.collect_info(message, "hg37_msg=", new_message, sep = " ~~ ")
    
    if not was_successful:
        # if there is still missing data check if the variant has hgvs_c information
        transcript = variant.get('REFSEQ')
        hgvs_c = variant.get('CHGVS')
        gene_symbol = variant.get("GEN")
        genome_build = "GRCh38"

        transcript_valid = transcript is not None and transcript != "" and transcript != "unknown" and transcript != "unbekannt"
        hgvs_c_valid = hgvs_c is not None and hgvs_c != ""
        gene_valid = gene_symbol is not None and gene_symbol != ""

        #TODO: maybe check if you can get some transcripts from the gene??? gene = variant.get('GEN')
        if transcript_valid and hgvs_c_valid:
            chrom, pos, ref, alt, err_msg = functions.hgvsc_to_vcf([hgvs_c], [transcript]) # convert to vcf

            if err_msg != "": # catch runtime errors of hgvs to vcf
                new_message = "HGVS to VCF yieled an error: " + str(err_msg)
                if new_message not in message:
                    message = functions.collect_info(message, "hgvs_msg=", new_message, sep = " ~~ ")
            elif any([x is None for x in [chrom, pos, ref, alt]]): # the conversion was not successful
                new_message = "HGVS could not be converted to VCF: " + str(transcript) + ":" + str(hgvs_c)
                if new_message not in message:
                    message = functions.collect_info(message, "hgvs_msg=", new_message, sep = " ~~ ")
            else:
                was_successful = True
        
        if not was_successful and hgvs_c_valid and gene_valid:
            gene_id = conn.get_gene_id_by_symbol(gene_symbol)
            transcripts = conn.get_gencode_basic_transcripts(gene_id)
            #transcripts = conn.get_mane_select_for_gene(gene_id)

            if transcripts is not None:
                #print(transcripts)
                #print(variant["CHGVS"])

                chrom, pos, ref, alt, err_msg = functions.hgvsc_to_vcf([variant["CHGVS"]]*len(transcripts), transcripts) # convert to vcf

                #print(err_msg)

                if 'unequal' in err_msg:
                    if err_msg not in message:
                        message = functions.collect_info(message, "hgvs_msg=", err_msg, sep = " ~~ ")
                elif err_msg != '':
                    preferred_transcripts = conn.get_preferred_transcripts(gene_id, return_all = True)
                    err_msgs = err_msg.split('\n')
                    break_outer = False
                    for current_transcript in preferred_transcripts:
                        for e in err_msgs:
                            if current_transcript.name in e:
                                new_message = "HGVS to VCf yielded an error with transcript: " + e
                                if new_message not in message:
                                    message = functions.collect_info(message, "hgvs_msg=", new_message, sep = " ~~ ")
                                break_outer = True
                                break
                        if break_outer:
                            break
                elif any([x is None for x in [chrom, pos, ref, alt]]): # the conversion was not successful
                    new_message = "HGVS could not be converted to VCF: " + str(hgvs_c)
                    if new_message not in message:
                        message = functions.collect_info(message, "hgvs_msg=", new_message, sep = " ~~ ")
                else:
                    was_successful = True

                if not was_successful and all([x is not None for x in [chrom, pos, ref, alt]]):
                    message += " possible candidate variant: " + '-'.join([chrom, pos, ref, alt]) + " (from transcript(s): " + current_transcript.name + ")"

        if was_successful:
            was_successful, new_message, variant_id = validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn, user_id, allowed_sequence_letters = allowed_sequence_letters, insert_variant = insert_variant, perform_annotation=perform_annotation)
            if new_message not in message:
                message = functions.collect_info(message, "hgvs_msg=", new_message, sep = " ~~ ")

    if variant_id is not None and external_ids is not None: # insert new vid
        for external_id in external_ids:
            annotation_type_id = conn.get_most_recent_annotation_type_id("heredicare_vid")
            previous_variant_ids = conn.get_variant_ids_from_external_id(external_id, annotation_type_id)
            for previous_variant_id in previous_variant_ids:
                if previous_variant_id != variant_id:
                    conn.delete_external_id(external_id, annotation_type_id, previous_variant_id)
                    if perform_annotation:
                        start_annotation_service(previous_variant_id, user_id, conn)
            conn.insert_external_variant_id(variant_id, external_id, annotation_type_id)

    if not was_successful and message == '':
        new_message = "Not enough data to convert variant!"
        message = functions.collect_info(message, "", new_message, sep = " ~~ ")

    if (not was_successful and variant_id is not None) or "already in database!" in message: # variant is already in database, start a reannotation
        status = "update"
    elif not was_successful:
        status = "error"

    return status, message






def validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn: Connection, user_id, allowed_sequence_letters = "ACGT", insert_variant = True, perform_annotation = True):
    message = ""
    was_successful = True
    variant_id = None
    # validate request

    chrom, chrom_is_valid = functions.curate_chromosome(chrom)
    ref, ref_is_valid = functions.curate_sequence(ref, allowed_sequence_letters)
    alt, alt_is_valid = functions.curate_sequence(alt, allowed_sequence_letters)
    pos, pos_is_valid = functions.curate_position(pos)

    if not chrom_is_valid:
        message = "Chromosome is invalid: " + str(chrom)
    elif not ref_is_valid:
        message = "Invalid reference sequence! The sequence must contain only ACGT and must have 0 < length < 1000: "
        if ref is not None:
            if len(ref) > 1000:
                ref = ref[0:100] + "..."
        message = message + "\"" + str(ref) + "\""
    elif not alt_is_valid:
        message = "Invalid alternative sequence! The sequence must contain only ACGT and must have 0 < length < 1000: "
        if alt is not None:
            if len(alt) > 1000:
                alt = alt[0:100] + "..."
        message = message + "\"" + str(alt) + "\""
    elif not pos_is_valid:
        message = "Position is invalid: " + str(pos)
    if ref == alt:
        message = "Equal reference and alternative base are not allowed."
        alt_is_valid = False
    if not chrom_is_valid or not ref_is_valid or not alt_is_valid or not pos_is_valid:
        was_successful = False
        return was_successful, message, variant_id



    tmp_file_path = functions.get_random_temp_file("vcf")
    functions.variant_to_vcf(chrom, pos, ref, alt, tmp_file_path)

    do_liftover = genome_build == 'GRCh37'
    returncode, err_msg, command_output = functions.preprocess_variant(tmp_file_path, do_liftover = do_liftover)


    if returncode != 0:
        message = err_msg
        was_successful = False
        functions.rm(tmp_file_path)
        functions.rm(tmp_file_path + ".lifted.unmap")
        return was_successful, message, variant_id
    if 'ERROR:' in err_msg:
        message = err_msg.replace('\n', ' ')
        was_successful = False
        functions.rm(tmp_file_path)
        functions.rm(tmp_file_path + ".lifted.unmap")
        return was_successful, message, variant_id
    if genome_build == 'GRCh37':
        unmapped_variants_vcf = open(tmp_file_path + '.lifted.unmap', 'r')
        unmapped_variant = None
        for line in unmapped_variants_vcf:
            if line.startswith('#') or line.strip() == '':
                continue
            unmapped_variant = line
            break
        unmapped_variants_vcf.close()
        if unmapped_variant is not None:
            message = 'ERROR: could not lift variant ' + unmapped_variant
            was_successful = False
            functions.rm(tmp_file_path)
            functions.rm(tmp_file_path + ".lifted.unmap")
            return was_successful, message, variant_id


    if was_successful:
        tmp_file = open(tmp_file_path, 'r')
        for line in tmp_file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            parts = line.split('\t')
            new_chr = parts[0]
            new_pos = parts[1]
            new_ref = parts[3]
            new_alt = parts[4]
            break # there is only one variant in the file
        tmp_file.close()

        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt) # check if variant is already contained

        if not is_duplicate and insert_variant:
            # insert it & capture the annotation_queue_id of the newly inserted variant to start the annotation service in celery
            variant_id = conn.insert_variant(new_chr, new_pos, new_ref, new_alt, chrom, pos, ref, alt, user_id)
        elif is_duplicate and insert_variant:
            variant_id = conn.get_variant_id(new_chr, new_pos, new_ref, new_alt)
            message = "Variant not imported: already in database!!"
            conn.hide_variant(variant_id, True) # unhide variant
        if insert_variant and perform_annotation:
            celery_task_id = start_annotation_service(variant_id, user_id, conn = conn) # starts the celery background task

        if not insert_variant:
            message += "HG38 variant would be: " + '-'.join([str(new_chr), str(new_pos), str(new_ref), str(new_alt)])


    functions.rm(tmp_file_path)
    functions.rm(tmp_file_path + ".lifted.unmap")
    return was_successful, message, variant_id


def validate_and_insert_cnv(chrom: str, start: int, end: int, sv_type: str, imprecise: int, hgvs_strings: list, genome_build: str, conn: Connection, insert_variant = True):
    message = ""
    was_successful = True
    variant_id = None

    chrom, chrom_is_valid = functions.curate_chromosome(chrom)
    start, start_is_valid = functions.curate_position(start)
    end, end_is_valid = functions.curate_position(end)

    sv_types = conn.get_enumtypes("sv_variant", "sv_type")
    sv_type_is_valid = True
    if sv_type not in sv_types:
        message = "Unknown cnv type: " + str(sv_type)
        sv_type_is_valid = False

    if not chrom_is_valid:
        message = "Chromosome is invalid: " + str(chrom)
    elif not start_is_valid:
        message = "Start position is invalid: " + str(start)
    elif not end_is_valid:
        message = "End position is invalid: " + str(end)
    elif start == end:
        message = "Equal start and end positions are not allowed."
        start_is_valid = False
    elif end < start:
        message = "End position is smaller than start position."
        start_is_valid = False
    
    if not chrom_is_valid or not start_is_valid or not end_is_valid or not sv_type_is_valid:
        was_successful = False
        return was_successful, message, variant_id


    do_liftover = genome_build == 'GRCh37'
    if do_liftover:
        tmp_file_path = functions.get_random_temp_file("bed")
        functions.cnv_to_bed(chrom, start, end, tmp_file_path)
        returncode, err_msg, command_output = functions.bgzip(tmp_file_path)
        if returncode != 0: 
            was_successful = False
            message = err_msg
            return was_successful, message, variant_id
        returncode, err_msg, command_output = functions.perform_liftover(infile = tmp_file_path, outfile = tmp_file_path + ".lifted", infile_format = "bed")
        if returncode != 0: # runtime error
            was_successful = False
            message = err_msg
            functions.rm(tmp_file_path)
            functions.rm(tmp_file_path + ".lifted")
            functions.rm(tmp_file_path + ".lifted.unmap")
            return was_successful, message, variant_id
        
        new_chrom = None
        new_start = None
        new_end = None
        l = 0
        with open(tmp_file_path + ".lifted") as lifted_file:
            for line in lifted_file:
                line = line.strip()
                if line.startswith('#') and line == '':
                    continue
                parts = line.split('\t')
                if l == 0:
                    new_chrom = parts[0]
                    new_start = parts[1]
                new_end = parts[2]
                l += 1
        if l == 0:
            was_successful = False
            message = "The region could not be lifted."
            functions.rm(tmp_file_path)
            functions.rm(tmp_file_path + ".lifted")
            functions.rm(tmp_file_path + ".lifted.unmap")
            return was_successful, message, variant_id
        if l >= 2:
            was_successful = False
            message = "The region was split into multiple parts during lifting. Please provide GRCh38 coordinates. Your region is in this area in GRCh38: " + new_chrom + "-" + new_start + "-" + new_end
            functions.rm(tmp_file_path)
            functions.rm(tmp_file_path + ".lifted")
            functions.rm(tmp_file_path + ".lifted.unmap")
            return was_successful, message, variant_id
        chrom = new_chrom
        start = new_start
        end = new_end


    is_duplicate = conn.check_sv_duplicate(chrom, start, end, sv_type)

    if not is_duplicate and insert_variant:
        variant_id, sv_variant_id = conn.insert_sv_variant(chrom, start, end, sv_type, imprecise)
    else:
        sv_variant_id = conn.get_sv_variant_id(chrom, start, end, sv_type)
        variant_id = conn.get_variant_id_by_sv_variant_id(sv_variant_id)
        if variant_id is None: # variant id is missing for some reason... add it afterwards -- failsave
            ref, alt, pos = functions.get_sv_variant_sequence(chrom, start, end, sv_type)
            variant_id = conn.insert_variant(chrom, pos, ref, alt, None,None,None,None,None, 'sv', sv_variant_id)
        message = "The variant is already in database."

    conn.add_hgvs_strings_sv_variant(sv_variant_id, hgvs_strings) # always update the hgvs strings independent of duplicate or not

    return was_successful, message, variant_id



##########################################################
############## START THE ANNOTATION SERVICE ##############
##########################################################

# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, soft_time_limit=600)
def annotate_all_variants(self, variant_ids, selected_job_config, user_id, roles):
    """Background task for running the annotation service"""
    conn = Connection(roles)
    for variant_id in variant_ids:
        _ = start_annotation_service(variant_id, user_id, conn = conn, job_config = selected_job_config) # inserts a new annotation queue entry before submitting the task to celery
        #conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])
    conn.close()
    self.update_state(state="SUCCESS", meta={})


def start_annotation_service(variant_id, user_id, conn: Connection, job_config = get_default_job_config()): # start the celery task
    annotation_queue_id = conn.insert_annotation_request(variant_id, user_id) # only inserts a new row if there is none with this variant_id & pending

    task = annotate_variant.apply_async(args=[annotation_queue_id, job_config])
    task_id = task.id
    print("Issued annotation for annotation queue id: " + str(annotation_queue_id) + " with celery task id: " + str(task_id) + " for variant_id: " + str(variant_id))

    conn.update_annotation_queue_celery_task_id(annotation_queue_id, task_id)
    
    return task_id


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, soft_time_limit=6000)
def annotate_variant(self, annotation_queue_id, job_config):
    """Background task for running the annotation service"""
    self.update_state(state='PROGRESS')
    status, runtime_error = process_one_request(annotation_queue_id, job_config=job_config)
    celery_status = 'success'
    if status == 'error':
        celery_status = 'FAILURE'
        self.update_state(state=celery_status, meta={ 
                        'exc_type': "Runtime error",
                        'exc_message': "The annotation service yielded a runtime error: " + runtime_error, 
                        'custom': '...'
                    })
        raise Ignore()
    if status == "retry":
        celery_status = "RETRY"
        self.update_state(state=celery_status, meta={
                        'exc_type': "Runtime error",
                        'exc_message': "The annotation service yielded " + runtime_error + "! Will attempt retry.", 
                        'custom': '...'})
        annotate_variant.retry()
    self.update_state(state=celery_status)











def send_mail(subject, sender, recipient, text_body):
    msg = Message(subject, sender=sender, recipients=[recipient])
    msg.body = ""
    msg.html = text_body
    mail.send(msg)



@celery.task(bind=True, retry_backoff=5, max_retries=3)
def notify_new_user(self, full_name, email, username, password):
    """Background task for sending two consecutive mails"""
    # first mail: username
    sender = "noreply@heredivar.uni-koeln.de"
    body = render_template("mail_templates/mail_username.html", full_name = full_name, username = username)
    send_mail(
        subject = "[VICC-CP] User account",
        sender = sender,
        recipient = email, 
        text_body = body  
    )

    # wait a couple of seconds before sending another message
    time.sleep(10)
    
    #second mail: password
    body = render_template("mail_templates/mail_password.html", full_name = full_name, password = password)
    send_mail(
        subject = "[VICC-CP] User account",
        sender = sender,
        recipient = email, 
        text_body = body  
    )


# It is not possible to put this into a task itself because if the queue is full it would need to wait for all
# tasks first to finish before aborting them -> this defeats the purpose of aborting tasks
def abort_annotation_tasks(annotation_requests, conn:Connection):
    for annotation_request in annotation_requests:
        #id, status, celery_task_id
        annotation_queue_id = annotation_request[0]
        status = annotation_request[1]
        celery_task_id = annotation_request[2]
        if status not in ["success", "error", "aborted"]: # just for safety
            abort_annotation_task(annotation_queue_id, celery_task_id, conn)

def abort_annotation_task(annotation_queue_id, celery_task_id, conn:Connection):
    if annotation_queue_id is not None:
        celery.control.revoke(celery_task_id, terminate = True)

        #row_id, status, error_msg
        conn.update_annotation_queue(annotation_queue_id, "aborted", "")


def purge_celery():
    celery.control.purge()





##################################################
############## ADD VARIANTS TO LIST ##############
##################################################

def start_variant_list_import(user_id, list_id, request_args, conn: Connection):
    list_variant_import_queue_id = conn.insert_list_variant_import_request(list_id, user_id)

    task = variant_list_import.apply_async(args=[user_id, list_id, list_variant_import_queue_id, request_args]) # start task
    task_id = task.id

    conn.update_list_variant_queue_celery_task_id(list_variant_import_queue_id, celery_task_id = task_id) # save the task id for status updates

    return list_variant_import_queue_id



@celery.task(bind=True, retry_backoff=5, max_retries=3)
def variant_list_import(self, user_id, list_id, list_variant_import_queue_id, request_args):
    """ Background task for importing a large number of variants from a tsv file """
    self.update_state("PROGRESS")

    message = ""
    status = "success"

    try:
        conn = Connection()
        conn.update_list_variant_import_status(list_variant_import_queue_id, status = "progress", message = "")
        selected_variants = request_args.get('selected_variants', "").split(',')
        select_all_variants = request_args.get('select_all_variants', "false") == "true"
        if select_all_variants:
            static_information = search_utils.get_static_search_information(user_id, conn)
            variants, total, page, selected_page_size = search_utils.get_merged_variant_page(request_args, user_id, static_information, conn, flash_messages = False, select_all = True)
            variant_ids = [variant.id for variant in variants]
            for variant_id in variant_ids:
                if str(variant_id) not in selected_variants:
                    num_new_variants = conn.add_variant_to_list(list_id, variant_id)
        else:
            for variant_id in selected_variants:
                variant = conn.get_variant(variant_id)
                if variant is not None:
                    num_new_variants = conn.add_variant_to_list(list_id, variant_id)
    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        message = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()
    except Error as e:
        status = "error"
        message = "There was a database error: " + str(e)  + ' ' + traceback.format_exc()
    except HTTPError as e:
        status = "retry"
        message = "Attempting retry because of http error: " + str(e)  + ' ' + traceback.format_exc()
    except Exception as e:
        status = "error"
        message = "There was a runtime error: " + str(e) + ' ' + traceback.format_exc()
    
    if status != "retry":
        conn.close_list_variant_import_request(status, list_variant_import_queue_id, message)
    else:
        conn.update_list_variant_import_status(list_variant_import_queue_id, status = status, message = message)

    conn.close()
    
    if status == 'error':
        self.update_state(state="FAILURE", meta={ 
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'
                    })
        raise Ignore()
    elif status == "retry":
        self.update_state(state="RETRY", meta={
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'})
        variant_list_import.retry()
    else:
        self.update_state(state="SUCCESS")








