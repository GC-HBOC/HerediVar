import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
from .annotation_jobs import *


class Annotation_Queue:

    def __init__(self, annotation_data):
        self.annotation_data = annotation_data
        self.queue = [
            # general information & scores
            annotate_from_vcf_job(annotation_data),
            consequence_job(annotation_data),
            
            # splicing predictions
            hexplorer_job(annotation_data),
            spliceai_job(annotation_data),
            maxentscan_job(annotation_data),
            
            # other scores
            heredicare_job(annotation_data),
            phylop_job(annotation_data),
            cancerhotspots_job(annotation_data),
            
            # protein domains
            vep_job(annotation_data),
            task_force_protein_domain_job(annotation_data),
            coldspots_job(annotation_data),
            
            # literature
            litvar2_job(annotation_data), # must be called after consequence & annotate from vcf job

            # automatic classification
            automatic_classification_job(annotation_data) # must be called last
        ]


    def execute(self, conn):
        err_msg = ""
        status = "success"
        for job in self.queue:
            if job.do_execution(job_config = self.annotation_data.job_config, queue = self.queue):
                job.execute(conn)
                job.cleanup()
                if job.status != "success":
                    status = "error"
                    err_msg = self.collect_error_msgs(err_msg, "Job " + job.job_name + " finished with status " + job.status + ". Message: " + job.err_msg)
        return status, err_msg


    def collect_error_msgs(self, msg1, msg2):
        res = msg1
        if msg2 not in msg1:
            if len(msg1) > 0 and len(msg2) > 0:
                res = msg1 + "\n~~\n" + msg2.strip()
            elif len(msg2) > 0:
                res = msg2.strip()
            else:
                res = msg1
        return res