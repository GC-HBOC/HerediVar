
from ._job import Job
import common.paths as paths
import common.functions as functions
import os
from annotation_service.heredicare_interface import heredicare_interface
import time


## annotate variant with hexplorer splicing scores (Hexplorer score + HBond score)
class heredicare_job(Job):
    def __init__(self, job_config):
        self.job_name = "heredicare"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        execution_code = 0
        stderr = ""
        stdout = ""
        
        if not self.job_config['do_heredicare']:
            return execution_code, stderr, stdout

        self.print_executing()


        #hexplorer_code, hexplorer_stderr, hexplorer_stdout = self.annotate_hexplorer(inpath, annotated_inpath)


        #self.handle_result(inpath, annotated_inpath, hexplorer_code)
        return execution_code, stderr, stdout


    def save_to_db(self, info, variant_id, conn):

        conn.clear_heredicare_annotation(variant_id)
        
        vids = conn.get_external_ids_from_variant_id(variant_id, id_source="heredicare") # the vids are imported from the import variants admin page
        
        for vid in vids:
            status = "retry"
            tries = 0
            max_tries = 3
            while status == "retry" and tries < max_tries:
                heredicare_variant, status, message = heredicare_interface.get_variant(vid)
                if tries > 0:
                    time.sleep(30 * tries)
            if status == "error":
                raise Exception("There was an error during variant retrieval from heredicare: " + str(message))
            
            n_fam = heredicare_variant["N_FAM"]
            n_pat = heredicare_variant["N_PAT"]
            consensus_class = heredicare_variant["PATH_TF"] if heredicare_variant["PATH_TF"] != "-1" else None
            comment = heredicare_variant["BEMERK"] if heredicare_variant["BEMERK"] != '' else None
        
            conn.insert_heredicare_annotation(variant_id, vid, n_fam, n_pat, consensus_class, comment)



