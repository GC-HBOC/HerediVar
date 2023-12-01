import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import tempfile
import traceback
from urllib.error import HTTPError
from os.path import exists
from .annotation_jobs import *
from .annotation_jobs import litvar2_job
import random
from mysql.connector import Error, InternalError

import os


## configuration
def get_default_job_config():
    job_config = {
        # heredicare annotations
        'do_heredicare': True,

        # external programs
        'do_phylop': True,
        'do_spliceai': True,
        'do_hexplorer': True,
        'do_maxentscan': True,

        # vep dependent
        'do_vep': True,
        'insert_consequence': True,
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
        'do_priors': True,
        'do_bayesdel': True,
        'do_cosmic': True,

        # additional annotations
        'do_taskforce_domains': True,
        'do_litvar': True,
        'do_auto_class': True
    }
    return job_config

def get_job_config(items_to_select):
    job_config = get_default_job_config()
    for key in job_config:
        if key in items_to_select:
            job_config[key] = True
        else:
            job_config[key] = False
    return job_config


# annotation job definitions
def get_jobs(job_config):
    all_jobs = [
        vep_job.vep_job(job_config, refseq=False),
        vep_job.vep_job(job_config, refseq=True),
        phylop_job.phylop_job(job_config),
        hexplorer_job.hexplorer_job(job_config),
        annotate_from_vcf_job.annotate_from_vcf_job(job_config),
        spliceai_job.spliceai_job(job_config),
        task_force_protein_domain_job.task_force_protein_domain_job(job_config),
        litvar2_job.litvar2_job(job_config), # must be called after vep_jobs & annotate from vcf job
        heredicare_job.heredicare_job(job_config),
        maxentscan_job.maxentscan_job(job_config)
    ]
    return all_jobs





def collect_error_msgs(msg1, msg2):
    res = msg1
    if msg2 not in msg1:
        if len(msg1) > 0 and len(msg2) > 0:
            res = msg1 + "\n~~\n" + msg2.strip()
        elif len(msg2) > 0:
            res = msg2.strip()
        else:
            res = msg1
    return res


def get_temp_vcf_path(annotation_queue_id):
    vcf_path = functions.get_random_temp_file(fileending = '', filename_ext = str(annotation_queue_id))
    vcf_path_annotated = vcf_path + "_annotated"
    #vcf_path = temp_file_path + "/" + str(annotation_queue_id) + ".vcf"
    return vcf_path + '.vcf', vcf_path_annotated + '.vcf'


def process_one_request(annotation_queue_id, job_config = get_default_job_config()):
    """ this is the main worker of the annotation job - A 4 step process -"""

    print(job_config)

    all_jobs = get_jobs(job_config)

    conn = Connection(roles=["annotation"])
    vcf_path, vcf_path_annotated = get_temp_vcf_path(annotation_queue_id)
    runtime_error = ""

    try:

        #if random.randint(1,10) > 5:
        #    raise HTTPError(url = "srv18", code=429, msg="Too many requests", hdrs = {}, fp = None)

        status = "success"

        annotation_queue_entry = conn.get_annotation_queue_entry(annotation_queue_id)
        if annotation_queue_entry is None:
            return "error: annotation queue entry not found"
        variant_id = annotation_queue_entry[1]
        user_id = annotation_queue_entry[2]

        err_msgs = ""
        one_variant = conn.get_one_variant(variant_id) # 0id,1chr,2pos,3ref,4alt
        print("processing request " + str(annotation_queue_id)  + " annotating variant: " + " ".join([str(x) for x in one_variant[1:5]]) + " with id: " + str(one_variant[0]) )

        functions.variant_to_vcf(one_variant[1], one_variant[2], one_variant[3], one_variant[4], vcf_path)

        ############################################################
        ############ 1: execute jobs (ie. annotate vcf) ############
        ############################################################
        for job in all_jobs:
            current_code, current_stderr, current_stdout = job.execute(vcf_path, vcf_path_annotated, one_variant=one_variant) # this one_variant thing is kinda ugly as it is only used in annotate_from_vcf_job..
            if current_code > 0:
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, current_stderr)


        ############################################################
        ############ 2: check validity of annotated vcf ############
        ############################################################
        #print("checking validity of annotated vcf file...")
        execution_code_vcfcheck, err_msg_vcfcheck, vcf_errors = functions.check_vcf(vcf_path)
        if execution_code_vcfcheck != 0:
            status = "error"
            err_msgs = collect_error_msgs(err_msgs, "VCFCheck errors: " + vcf_errors)
        else:
            print("VCF OK")
        


        ############################################################
        ########### 3: save the collected data to the db ###########
        ############################################################
        print("saving to database...")

        file = open(vcf_path, "r")
        for line in file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            
            info = line.split('\t')[7]
            for job in all_jobs:
                status_code, err_msg = job.save_to_db(info, variant_id, conn=conn)
                if status_code > 0:
                    status = "error"
                err_msgs = collect_error_msgs(err_msgs, err_msg)
        file.close()


        print("~~~")
        print("Annotation done!")
        print("Status: " + status)
        print(err_msgs)

        ############################################################
        ############## 4: run automatic classification #############
        ############################################################
        #if any(job_config[x] for x in ['do_auto_class']):
        #    print("Executing automatic classification...")
        #    autoclass_job = automatic_classification_job.automatic_classification_job(job_config)
        #    status_code, err_msg = autoclass_job.save_to_db("", variant_id, conn=conn)
        #    if status_code > 0:
        #        status = "error"
        #    err_msgs = collect_error_msgs(err_msgs, err_msg)




        ############################################################
        ############## 5: update the annotation queue ##############
        ############################################################
        conn.update_annotation_queue(row_id=annotation_queue_id, status=status, error_msg=err_msgs)


    except HTTPError as e: # we want to catch http errors to be able to retry later again (eg. 429)
        # cleanup after http error before retry
        print("An HTTP exception occured: " + str(e))
        print(traceback.format_exc())

        status = "retry"
        conn.update_annotation_queue(row_id=annotation_queue_id, status=status, error_msg=str(e))
        
        runtime_error = str(e)

        #raise e #HTTPError(url = e.url, code = e.code, msg = "A HTTP error occured", hdrs = e.hdrs, fp = e.fp)
    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        conn.update_annotation_queue(row_id=annotation_queue_id, status=status, error_msg=str(e))
        runtime_error = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()

    except Exception as e:
        print("An exception occured: " + str(e))
        print(traceback.format_exc())
        conn.update_annotation_queue(row_id = annotation_queue_id, status="error", error_msg = "Annotation service runtime error: " + str(e) + ' ' + traceback.format_exc())
        status = "error"
        runtime_error = str(e)


    if exists(vcf_path): 
        os.remove(vcf_path)
    if exists(vcf_path_annotated):
        os.remove(vcf_path_annotated)


    conn.close()


    return status, runtime_error



# sequentially processes all pending requests
#pending_requests = conn.get_pending_requests() <- call this to get the pending requests!
# not used atm!!!
def process_all_pending_requests(pending_requests):
    """ fetches all pending requests from the annotatino queue and annotates all of them sequentially"""
    for pending_request in pending_requests:
        process_one_request(pending_request[0])




