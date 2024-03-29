
from ._job import Job
import common.paths as paths
import common.functions as functions


## annotate vus task force protein domains
class task_force_protein_domain_job(Job):
    def __init__(self, job_config):
        self.job_name = "task_force_protein_domain"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
            return 0, '', ''


    def save_to_db(self, info, variant_id, conn):
        status_code = 0
        err_msg = ""
        if self.job_config['do_taskforce_domains']:
            one_variant = conn.get_one_variant(variant_id) # 0id,1chr,2pos,3ref,4alt
            task_force_protein_domains = conn.get_task_force_protein_domains(one_variant[1], one_variant[2], int(one_variant[2]) + len(one_variant[4]))
            recent_annotation_ids = conn.get_recent_annotation_type_ids()
            for domain in task_force_protein_domains:
                conn.insert_variant_annotation(variant_id, recent_annotation_ids["task_force_protein_domain"], domain[5])
                conn.insert_variant_annotation(variant_id, recent_annotation_ids["task_force_protein_domain_source"], domain[6])
        
        return status_code, err_msg



