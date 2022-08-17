import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import tempfile

from .annotation_jobs import *

import os


## configuration
job_config = {
    # heredicare annotations
    'do_heredicare': False,

    # external programs
    'do_phylop': True,
    'do_spliceai': True,
    'do_hexplorer': True,

    # vep dependent
    'do_vep': True,
    'insert_consequence': True,
    'insert_maxent': True,
    'insert_literature': True,

    #vcf annotate from vcf
    'do_dbsnp': True,
    'do_revel': True,
    'do_cadd': True,
    'do_clinvar': True,
    'do_gnomad': True,
    'do_brca_exchange': True,
    'do_flossies': True,
    'do_cancerhotspots': True,
    'do_arup': True,
    'do_tp53_database': True,

    # additional annotations
    'do_task_force_protein_domains': True
}


# annotation job definitions
all_jobs = [
    vep_job.vep_job(job_config, refseq=False),
    vep_job.vep_job(job_config, refseq=True),
    phylop_job.phylop_job(job_config),
    hexplorer_job.hexplorer_job(job_config),
    annotate_from_vcf_job.annotate_from_vcf_job(job_config),
    spliceai_job.spliceai_job(job_config),
    task_force_protein_domain_job.task_force_protein_domain_job(job_config)
]


conn = Connection()


def collect_error_msgs(msg1, msg2):
    if len(msg1) > 0 and len(msg2) > 0:
        res = msg1 + "\n~~\n" + msg2.strip()
    elif len(msg2) > 0:
        res = msg2.strip()
    else:
        res = msg1
    return res


def get_temp_vcf_path(annotation_queue_id):
    temp_file_path = tempfile.gettempdir()
    vcf_path = temp_file_path + "/" + str(annotation_queue_id) + ".vcf"
    return vcf_path

def get_annotation_tempfile(annotation_queue_id):
    res = tempfile.gettempdir() + "/" + str(annotation_queue_id) + "_annotated.vcf"
    return res


def process_one_request(annotation_queue_id):
    """ this is the main worker of the annotation job - A 5 step process -"""

    status = "success"

    annotation_queue_entry = conn.get_annotation_queue_entry(annotation_queue_id)
    if annotation_queue_entry is None:
        return "error: annotation queue entry not found"
    variant_id = annotation_queue_entry[1]
    user_id = annotation_queue_entry[2]

    err_msgs = ""
    one_variant = conn.get_one_variant(variant_id) # 0id,1chr,2pos,3ref,4alt
    print("processing request " + str(one_variant[0]) + " annotating variant: " + " ".join([str(x) for x in one_variant[1:5]]))

    '''
    if do_heredicare:
        vids = conn.get_external_ids_from_variant_id(variant_id, id_source='heredicare')
        #log_file_date = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        log_file_path = path.join(path.dirname(path.abspath(__file__)),  'logs/heredicare_update.log')
        heredicare.update_specific_vids(log_file_path, vids, conn.get_user(user_id)[1])
        #look for error code: s1 (deleted variant)
        log_file = open(log_file_path, 'r')
        deleted_variant = False
        for line in log_file:
            if '~~s1~~' in line:
                deleted_variant = True
        log_file.close()
        if deleted_variant:
            continue # stop annotation if it was deleted!
    '''

    vcf_path = get_temp_vcf_path(annotation_queue_id)
    functions.variant_to_vcf(one_variant[1], one_variant[2], one_variant[3], one_variant[4], vcf_path)
    vcf_annotated_tmp_path = get_annotation_tempfile(annotation_queue_id)

    ############################################################
    ############ 1: execute jobs (ie. annotate vcf) ############
    ############################################################
    for job in all_jobs:
        current_code, current_stderr, current_stdout = job.execute(vcf_path, vcf_annotated_tmp_path, one_variant=one_variant) # this one_variant thing is kinda ugly as it is only used in annotate_from_vcf_job..
        if current_code > 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, current_stderr)


    ############################################################
    ############ 2: check validity of annotated vcf ############
    ############################################################
    print("checking validity of annotated vcf file...")
    execution_code_vcfcheck, err_msg_vcfcheck, vcf_errors = functions.check_vcf(vcf_path)
    if execution_code_vcfcheck != 0:
        status = "error"
    else:
        print("VCF OK")
    err_msgs = collect_error_msgs(err_msgs, vcf_errors)


    ############################################################
    ########### 3: save the collected data to the db ###########
    ############################################################
    print("saving to database...")
    headers, info = functions.read_vcf_info(vcf_path)

    for vcf_variant_idx in range(len(info)):
        current_info = info[vcf_variant_idx]

        for job in all_jobs:
            job.save_to_db(current_info, variant_id, conn=conn)



    print("~~~")
    print("Annotation done!")
    print("Status: " + status)
    print(err_msgs)


    ############################################################
    ############## 5: update the annotation queue ##############
    ############################################################
    conn.update_annotation_queue(row_id=annotation_queue_id, status=status, error_msg=err_msgs)


    # revert
    #os.remove(vcf_path)

    return status




def process_all_pending_requests():
    """ fetches all pending requests from the annotatino queue and annotates all of them sequentially"""
    pending_requests = conn.get_pending_requests()

    for pending_request in pending_requests:
        process_one_request(pending_request[0])
        
    conn.close()



