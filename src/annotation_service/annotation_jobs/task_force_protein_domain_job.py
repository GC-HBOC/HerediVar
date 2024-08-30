
from ._job import Job
import common.paths as paths
import common.functions as functions


## annotate vus task force protein domains
class task_force_protein_domain_job(Job):

    def __init__(self, annotation_data):
        self.job_name = "task force protein domains"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []


    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ["do_taskforce_domains"]):
            result = False
            self.status = "skipped"
        return result
    
    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        variant = self.annotation_data.variant
    
        # execute and save to db
        status_code, err_msg = self.save_to_db(variant, conn)
        if status_code != 0:
            self.status = "error"
            self.err_msg = err_msg
            return # abort
    
        # update state
        self.status = "success"


    def save_to_db(self, variant, conn):
        status_code = 0
        err_msg = ""

        task_force_protein_domains = conn.get_task_force_protein_domains(variant.chrom, variant.pos, variant.pos + max(len(variant.ref), len(variant.alt)))
        recent_annotation_ids = conn.get_recent_annotation_type_ids()
        for domain in task_force_protein_domains:
            conn.insert_variant_annotation(variant.id, recent_annotation_ids["task_force_protein_domain"], domain[5])
            conn.insert_variant_annotation(variant.id, recent_annotation_ids["task_force_protein_domain_source"], domain[6])
        
        return status_code, err_msg

