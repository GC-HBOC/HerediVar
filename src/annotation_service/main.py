import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import tempfile
import traceback
from urllib.error import HTTPError
from os.path import exists
from .annotation_queue import Annotation_Queue
from .annotation_data import Annotation_Data
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

        # consequences
        'do_consequence': True,
        'do_vep': True,

        #vcf annotate from vcf
        'do_dbsnp': True,
        'do_revel': True,
        'do_cadd': True,
        'do_clinvar': True,
        'do_gnomad': True,
        'do_brca_exchange': True,
        'do_flossies': True,
        
        'do_tp53_database': True,
        'do_priors': True,
        'do_bayesdel': True,
        'do_cosmic': True,

        # assays
        'do_cspec_brca_assays': True,

        # additional annotations
        'do_cancerhotspots': True,
        'do_taskforce_domains': True,
        'do_coldspots': True,
        'do_litvar': True,
        'do_auto_class': True

        # outdated
        #'do_arup': True,
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


def get_temp_vcf_path(annotation_queue_id):
    vcf_path = functions.get_random_temp_file(fileending = '', filename_ext = str(annotation_queue_id))
    #vcf_path_annotated = vcf_path + "_annotated"
    return vcf_path + '.vcf'




def process_one_request(annotation_queue_id, job_config = get_default_job_config()):
    """ this is the main worker of the annotation job - A 4 step process -"""

    print(job_config)

    runtime_error = ""
    vcf_path = ""

    try:
        #if random.randint(1,10) > 5:
        #    raise HTTPError(url = "srv18", code=429, msg="Too many requests", hdrs = {}, fp = None)


        # initialize the connection
        conn = Connection(roles=["annotation"])


        # get the variant_id from the annotation queue id & check that the annotation_queue_id is valid
        annotation_queue_entry = conn.get_annotation_queue_entry(annotation_queue_id)
        if annotation_queue_entry is None:
            status = "error"
            return status, "Annotation queue entry not found"
        variant_id = annotation_queue_entry[1]


        # check the variant type
        variant = conn.get_variant(variant_id, include_annotations = False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_automatic_classification = False, include_clinvar = False, include_assays = False, include_literature = False, include_external_ids = False) # 0id,1chr,2pos,3ref,4alt
        if variant.variant_type in ['sv']:
            status = "error"
            return "Variant type " + str(variant.variant_type) + " is not supported by the annotation algorithm."
        
        # update the annotation queue status
        conn.set_annotation_queue_status(annotation_queue_id, status="progress")
        print("processing request " + str(annotation_queue_id)  + " annotating variant: " + "-".join([variant.chrom, str(variant.pos), variant.ref, variant.alt]) + " with id: " + str(variant.id) )

        # invalidate variant list download vcf files
        list_ids = conn.get_list_ids_with_variant(variant_id)
        for list_id in list_ids:
            download_queue_ids = conn.get_valid_download_queue_ids(list_id, "list_download")
            for download_queue_id in download_queue_ids:
                conn.invalidate_download_queue(download_queue_id)

        # write a vcf with the current variant to disc
        vcf_path = get_temp_vcf_path(annotation_queue_id)
        functions.variant_to_vcf(variant.chrom, variant.pos, variant.ref, variant.alt, vcf_path)

        # execute the annotation jobs sequentially
        annotation_data = Annotation_Data(job_config = job_config, variant = variant, vcf_path = vcf_path)
        annotation_queue = Annotation_Queue(annotation_data)
        status, err_msgs = annotation_queue.execute(conn)

        print("~~~")
        print("Annotation done!")
        print("Status: " + status)
        print(err_msgs)

        # update the annotation queue status and error messages if any
        conn.update_annotation_queue(annotation_queue_id, status=status, error_msg=err_msgs)


    except HTTPError as e: # we want to catch http errors to be able to retry later again (eg. 429)
        # cleanup after http error before retry
        print("An HTTP exception occured: " + str(e))
        print(traceback.format_exc())

        status = "retry"
        conn.update_annotation_queue(annotation_queue_id, status=status, error_msg=str(e))
        
        runtime_error = str(e)

        #raise e #HTTPError(url = e.url, code = e.code, msg = "A HTTP error occured", hdrs = e.hdrs, fp = e.fp)
    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        conn.update_annotation_queue(annotation_queue_id, status=status, error_msg=str(e))
        runtime_error = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()

    except Exception as e:
        print("An exception occured: " + str(e))
        print(traceback.format_exc())
        conn.update_annotation_queue(annotation_queue_id, status="error", error_msg = "Annotation service runtime error: " + str(e) + ' ' + traceback.format_exc())
        status = "error"
        runtime_error = str(e)


    functions.rm(vcf_path)


    conn.close()


    return status, runtime_error



# sequentially processes all pending requests
#pending_requests = conn.get_pending_requests() <- call this to get the pending requests!
# not used atm!!!
def process_all_pending_requests(pending_requests):
    """ fetches all pending requests from the annotatino queue and annotates all of them sequentially"""
    for pending_request in pending_requests:
        process_one_request(pending_request[0])




