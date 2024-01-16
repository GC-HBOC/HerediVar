
from ._job import Job
import common.paths as paths
import common.functions as functions


## annotate vus task force protein domains
class coldspots_job(Job):
    def __init__(self, job_config):
        self.job_name = "coldspots"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
            return 0, '', ''


    def save_to_db(self, info, variant_id, conn):
        status_code = 0
        err_msg = ""
        if self.job_config['do_coldspots']:
            variant = conn.get_variant(variant_id, 
                                    include_annotations = False, 
                                    include_consensus = False, 
                                    include_user_classifications = False, 
                                    include_heredicare_classifications = False, 
                                    include_automatic_classification = False,
                                    include_clinvar = False, 
                                    include_consequences = False, 
                                    include_assays = False, 
                                    include_literature = False,
                                    include_external_ids = False
                                )
            recent_annotation_ids = conn.get_recent_annotation_type_ids()
            coldspots = conn.get_coldspots(variant.chrom, variant.pos, variant.pos + max(len(variant.ref), len(variant.alt)))

            if len(coldspots) > 0:
                conn.insert_variant_annotation(variant_id, recent_annotation_ids["coldspot"], "True")
        
        return status_code, err_msg



