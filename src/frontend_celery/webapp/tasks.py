from urllib.error import HTTPError
from . import celery, mail
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import common.functions as functions
from common.db_IO import Connection
from annotation_service.main import process_one_request, get_default_job_config
from celery.exceptions import Ignore
from flask_mail import Message
from flask import render_template
import time
from annotation_service.heredicare_interface import heredicare_interface

"""
@celery.task(bind=True)
def long_task(self):
    #Background task that runs a long function with progress reports.
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 20)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        #time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task(bind=True)
def fetch_consequence_task(self, variant_id):
    #Background task for fetching the consequence from the database
    self.update_state(state='PROGRESS')
    
    conn = Connection()

    time.sleep(10)
    variant_consequences = conn.get_variant_consequences(variant_id) # 0transcript_name,1hgvs_c,2hgvs_p,3consequence,4impact,5exon_nr,6intron_nr,7symbol,8transcript.gene_id,9source,10pfam_accession,11pfam_description,12length,13is_gencode_basic,14is_mane_select,15is_mane_plus_clinical,16is_ensembl_canonical,17total_flag
    conn.close()
    return {'status': 'COMPLETED', 'result': variant_consequences}
"""









###################################################################################
############## IMPORT VARIANT LIST THAT GOT UPDATE SINCE LAST IMPORT ##############
###################################################################################

def start_variant_import(user_id, user_roles, conn: Connection): # starts the celery task
    import_request = conn.get_most_recent_import_request() # get the most recent import request
    min_date = None
    if import_request is not None:
        min_date = import_request.finished_at
    #print(import_request.finished_at)

    new_import_request = conn.insert_import_request(user_id)
    import_queue_id = new_import_request.id

    task = heredicare_variant_import.apply_async(args=[user_id, user_roles, min_date, import_queue_id]) # start task
    task_id = task.id

    conn.update_import_queue_celery_task_id(import_queue_id, celery_task_id = task_id) # save the task id for status updates

    return import_queue_id

@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def heredicare_variant_import(self, user_id, user_roles, min_date, import_queue_id):
    """Background task for fetching variants from HerediCare"""
    #from frontend_celery.webapp.utils.variant_importer import import_variants
    self.update_state(state='PROGRESS')

    conn = Connection(user_roles)

    conn.update_import_queue_status(import_queue_id, status = "progress", message = "")

    
    status, message = import_variants(conn, user_id, user_roles, functions.str2datetime(min_date, fmt = '%Y-%m-%dT%H:%M:%S'), import_queue_id)

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


def import_variants(conn: Connection, user_id, user_roles, min_date, import_queue_id): # the task worker
    status = "success"

    vids_heredicare, status, message = heredicare_interface.get_vid_list(min_date)

    if status == "success":

        vids_heredivar = conn.get_all_external_ids("heredicare")


        intersection, heredivar_exclusive_vids, heredicare_exclusive_vids = compare_v_id_lists(vids_heredicare, vids_heredivar)

        print("Intersection: " + str(len(intersection)))
        print("Deleted: " + str(len(heredivar_exclusive_vids)))
        print("New: " + str(len(heredicare_exclusive_vids)))

        # spawn one task for each variant import
        process_new_vids(heredicare_exclusive_vids + intersection, import_queue_id, user_id, user_roles, conn)
        process_deleted_vids(heredivar_exclusive_vids, import_queue_id, user_id, user_roles, conn)

    return status, message








def process_deleted_vids(vids, import_queue_id, user_id, user_roles, conn: Connection):
    vids = []
    for vid in vids:
        _ = start_delete_variant(vid, import_queue_id, user_id, user_roles, conn)



def process_new_vids(vids, import_queue_id, user_id, user_roles, conn: Connection):
    # simply insert them
    vids = vids[:1000]
    for vid in vids:
        _ = start_import_one_variant(vid, import_queue_id, user_id, user_roles, conn)




def compare_v_id_lists(vids_heredicare, vids_heredivar):
    vids_heredicare = set(vids_heredicare)
    vids_heredivar = set(vids_heredivar)

    intersection = list(vids_heredivar & vids_heredicare)
    heredivar_exclusive_variants = list(vids_heredivar - vids_heredicare) # this contains only variants which have a vid in heredivar!!!!
    heredicare_exclusive_variants = list(vids_heredicare - vids_heredivar)

    return intersection, heredivar_exclusive_variants, heredicare_exclusive_variants



################################################
############## DELETE THE VARIANT ##############
################################################

def start_delete_variant(vid, import_queue_id, user_id, user_roles, conn: Connection): # starts the celery task
    import_variant_queue_id = conn.insert_variant_import_request(vid, import_queue_id)

    task = delete_variant_heredicare.apply_async(args=[vid, user_id, user_roles, import_variant_queue_id])
    task_id = task.id

    conn.update_import_variant_queue_celery_id(import_variant_queue_id, celery_task_id = task_id)

    return task_id


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def delete_variant_heredicare(self, vid, user_id, user_roles, import_variant_queue_id):
    """Background task for fetching variants from HerediCare"""
    #from frontend_celery.webapp.utils.variant_importer import fetch_heredicare
    self.update_state(state='PROGRESS')
    
    conn = Connection(user_roles)
    
    conn.update_import_variant_queue_status(import_variant_queue_id, status = "progress", message = "")
    
    message = "Removed heredicare vid"
    status = "update"
    variant_id = conn.get_variant_id_from_external_id(vid, 'heredicare')
    all_vids_for_variant = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
    conn.delete_external_id(vid, 'heredicare', variant_id = variant_id)
    if len(all_vids_for_variant) <= 1:
        status, message = conn.delete_variant(variant_id) # this only deletes if there are no classifications
        
    print(status)

    if status != "retry":
        conn.close_import_variant_request(import_variant_queue_id, status = status, message = message)
    else:
        conn.update_import_variant_queue_status(import_variant_queue_id, status = status, message = message)
    
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



################################################
############## IMPORT THE VARIANT ##############
################################################

def start_import_one_variant(vid, import_queue_id, user_id, user_roles, conn: Connection): # starts the celery task
    import_variant_queue_id = conn.insert_variant_import_request(vid, import_queue_id)

    task = import_one_variant_heredicare.apply_async(args=[vid, user_id, user_roles, import_variant_queue_id])
    task_id = task.id

    conn.update_import_variant_queue_celery_id(import_variant_queue_id, celery_task_id = task_id)

    return task_id


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def import_one_variant_heredicare(self, vid, user_id, user_roles, import_variant_queue_id):
    """Background task for fetching variants from HerediCare"""
    #from frontend_celery.webapp.utils.variant_importer import fetch_heredicare
    self.update_state(state='PROGRESS')
    
    conn = Connection(user_roles)
    
    conn.update_import_variant_queue_status(import_variant_queue_id, status = "progress", message = "")
    status, message = fetch_heredicare(vid, heredicare_interface, user_id, conn)
    print(status)

    if status != "retry":
        conn.close_import_variant_request(import_variant_queue_id, status = status, message = message)
    else:
        conn.update_import_variant_queue_status(import_variant_queue_id, status = status, message = message)
    
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



def fetch_heredicare(vid, heredicare_interface, user_id, conn:Connection): # the task worker
    
    variant, status, message = heredicare_interface.get_variant(vid)

    if status != 'success':
        return status, message


    genome_build = "GRCh38"

    
    # first check if the hg38 information is there
    chrom = variant.get('CHROM')
    pos = variant.get('POS_HG38')
    ref = variant.get('REF_HG38')
    alt = variant.get('ALT_HG38')

    # if there is missing information check if there is hg19 information
    if any([x is None for x in [chrom, pos, ref, alt]]):
        pos = variant.get('POS_HG19')
        ref = variant.get('REF_HG19')
        alt = variant.get('ALT_HG19')
        genome_build = "GRCh37"
    
    # if there is still missing data check if the variant has hgvs_c information
    if any([x is None for x in [chrom, pos, ref, alt]]):
        transcript = variant.get('REFSEQ')
        hgvs_c = variant.get('CHGVS')

        #TODO: maybe check if you can get some transcripts from the gene??? gene = variant.get('GEN')
        if any([x is None for x in [transcript, hgvs_c]]):
            status = "error"
            message = "Not enough data to convert variant!"
            return status, message

        chrom, pos, ref, alt, err_msg = functions.hgvsc_to_vcf(hgvs_c, transcript) # convert to vcf

        if err_msg != "": # catch runtime errors of hgvs to vcf
            status = "error"
            message = "HGVS to VCF yieled an error: " + str(err_msg)
            return status, message
        
        # the conversion was not successful
        if any([x is None for x in [chrom, pos, ref, alt]]): 
            status = "error"
            message = "HGVS could not be converted to VCF: " + str(transcript) + ":" + str(hgvs_c)
            return status, message
    


    was_successful, message, variant_id = validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn, user_id, allowed_sequence_letters = "ACGT")

    ## vid was moved from one variant to another -> delete it from the existing variant
    #if was_successful:
    #    # check that vid and variant refer to the same thing in heredicare and heredivar
    #    existing_variant_id = conn.get_variant_id_from_external_id(vid, "heredicare")
    #    if existing_variant_id is not None:
    #        if existing_variant_id != variant_id: # sanity check maybe not neccessary
    #            start_delete_variant(vid, import_queue_id, user_id, user_roles, conn) # deletes the vid and the variant if 


    if variant_id is not None: # insert new vid
        conn.insert_external_variant_id(variant_id, vid, "heredicare")

    if not was_successful and variant_id is not None: # variant is already in database, start a reannotation
        status = "update"
        start_annotation_service(conn, user_id, variant_id)
    elif not was_successful:
        status = "error"

    return status, message






def validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn: Connection, user_id, allowed_sequence_letters = "ACGT", perform_annotation = True):
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
        message = "Reference base is invalid: " + str(ref)
    elif not alt_is_valid:
        message = "Alternative base is invalid: " + str(alt)
    elif not pos_is_valid:
        message = "Position is invalid: " + str(pos)
    if not chrom_is_valid or not ref_is_valid or not alt_is_valid or not pos_is_valid:
        was_successful = False
        return was_successful, message, variant_id



    tmp_file_path = functions.get_random_temp_file("vcf")
    functions.variant_to_vcf(chrom, pos, ref, alt, tmp_file_path)

    do_liftover = genome_build == 'GRCh37'
    returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post = functions.preprocess_variant(tmp_file_path, do_liftover = do_liftover)

    
    if returncode != 0:
        message = err_msg
        was_successful = False
        functions.rm(tmp_file_path)
        return was_successful, message, variant_id
    if 'ERROR:' in vcf_errors_pre:
        message = vcf_errors_pre.replace('\n', ' ')
        was_successful = False
        functions.rm(tmp_file_path)
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
    if 'ERROR:' in vcf_errors_post:
        message = vcf_errors_post.replace('\n', ' ')
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
        
        if not is_duplicate:
            # insert it & capture the annotation_queue_id of the newly inserted variant to start the annotation service in celery
            variant_id = conn.insert_variant(new_chr, new_pos, new_ref, new_alt, chrom, pos, ref, alt, user_id)
        else:
            variant_id = conn.get_variant_id(new_chr, new_pos, new_ref, new_alt)
            message = "Variant not imported: already in database!!"
            was_successful = False
        if perform_annotation:
            celery_task_id = start_annotation_service(conn, user_id, variant_id) # starts the celery background task

    functions.rm(tmp_file_path)
    functions.rm(tmp_file_path + ".lifted.unmap")
    return was_successful, message, variant_id






##########################################################
############## START THE ANNOTATION SERVICE ##############
##########################################################

def start_annotation_service(conn: Connection, user_id, variant_id = None, annotation_queue_id = None, job_config = get_default_job_config()): # start the celery task
    if variant_id is not None:
        annotation_queue_id = conn.insert_annotation_request(variant_id, user_id) # only inserts a new row if there is none with this variant_id & pending
        log_postfix = " for variant " + str(variant_id)
    else:
        log_postfix = " for annotation queue entry " + str(annotation_queue_id)
    task = annotate_variant.apply_async(args=[annotation_queue_id, job_config])
    print("Issued annotation for annotation queue id: " + str(annotation_queue_id) + " with celery task id: " + str(task.id) + log_postfix)
    #current_app.logger.info(session['user']['preferred_username'] + " started the annotation service for annotation queue id: " + str(annotation_queue_id) + " with celery task id: " + str(task.id) + log_postfix)
    conn.insert_celery_task_id(annotation_queue_id, task.id)
    return task.id

# the worker is the annotation service itself!


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def annotate_variant(self, annotation_queue_id, job_config):
    """Background task for running the annotation service"""
    self.update_state(state='PROGRESS', meta={'annotation_queue_id':annotation_queue_id})
    status, runtime_error = process_one_request(annotation_queue_id, job_config=job_config)
    celery_status = 'success'
    if status == 'error':
        celery_status = 'FAILURE'
        self.update_state(state=celery_status, meta={'annotation_queue_id':annotation_queue_id, 
                        'exc_type': "Runtime error",
                        'exc_message': "The annotation service yielded a runtime error: " + runtime_error, 
                        'custom': '...'
                    })
        raise Ignore()
    if status == "retry":
        celery_status = "RETRY"
        self.update_state(state=celery_status, meta={'annotation_queue_id':annotation_queue_id,
                        'exc_type': "Runtime error",
                        'exc_message': "The annotation service yielded " + runtime_error + "! Will attempt retry.", 
                        'custom': '...'})
        annotate_variant.retry()
    self.update_state(state=celery_status, meta={'annotation_queue_id':annotation_queue_id})









# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=60)
def generate_consensus_only_vcf_task(self):
    """Background task for generating consensus only vcf"""
    from webapp.io.download_routes import generate_consensus_only_vcf
    generate_consensus_only_vcf()


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
    body = render_template("auth/mail_username.html", full_name = full_name, username = username)
    send_mail(
        subject = "[VICC-CP] User account",
        sender = sender,
        recipient = email, 
        text_body = body  
    )

    # wait a couple of seconds before sending another message
    time.sleep(10)
    
    #second mail: password
    body = render_template("auth/mail_password.html", full_name = full_name, password = password)
    send_mail(
        subject = "[VICC-CP] User account",
        sender = sender,
        recipient = email, 
        text_body = body  
    )
    