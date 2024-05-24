
from ._job import Job
import common.paths as paths
import common.functions as functions
import os
from common.heredicare_interface import Heredicare
import time
from datetime import datetime
from urllib.parse import unquote


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
        status_code = 0
        err_msg = ""

        if not self.job_config['do_heredicare']:
            return status_code, err_msg

        heredicare_interface = Heredicare()
        #conn.clear_heredicare_annotation(variant_id)
        
        heredicare_vid_annotation_type_id = conn.get_most_recent_annotation_type_id('heredicare_vid')
        vids = conn.get_external_ids_from_variant_id(variant_id, annotation_type_id=heredicare_vid_annotation_type_id) # the vids are imported from the import variants admin page
        conn.delete_unknown_heredicare_annotations(variant_id) # remove legacy annotations from vids that are deleted now

        #print(vids)
        
        for vid in vids:
            status = "retry"
            tries = 0
            max_tries = 5
            while status == "retry" and tries < max_tries:
                heredicare_variant, status, message = heredicare_interface.get_variant(vid)
                if tries > 0:
                    time.sleep(30 * tries)
                tries += 1
            if status in ["error"]:
                err_msg += "There was an error during variant retrieval from heredicare: " + str(message) + ". VID: " + str(vid)
                status_code = 1
            elif status == "deleted":
                err_msg += str(message)
                conn.delete_external_id(vid, heredicare_vid_annotation_type_id, variant_id)
                conn.delete_unknown_heredicare_annotations()
            else:
                #print(heredicare_variant)
                n_fam = heredicare_variant["N_FAM"]
                n_pat = heredicare_variant["N_PAT"]
                consensus_class = heredicare_variant["PATH_TF"] if heredicare_variant["PATH_TF"] != "-1" else None
                comment = heredicare_variant["VUSTF_21"] if heredicare_variant["VUSTF_21"] is not None else ''
                comment = comment.strip()
                comment = comment if comment != '' else None
                classification_date = heredicare_variant["VUSTF_DATUM"] if heredicare_variant["VUSTF_DATUM"] != '' else None
                lr_cooc = heredicare_variant["LR_COOC"]
                lr_coseg = heredicare_variant["LR_COSEG"]
                lr_family = heredicare_variant["LR_FAMILY"]
                if classification_date is not None:
                    try:
                        classification_date = datetime.strptime(classification_date, "%d.%m.%Y")
                    except:
                        err_msg += "The date could not be saved in the database. Format should be dd.mm.yyyy, but was: " + str(classification_date)
                        status_code = 1

                heredicare_annotation_id = None
                if status_code == 0:
                    heredicare_annotation_id = conn.insert_update_heredicare_annotation(variant_id, vid, n_fam, n_pat, consensus_class, classification_date, comment, lr_cooc, lr_coseg, lr_family)

                for key in heredicare_variant:
                    if key.startswith("PATH_Z"):
                        zid = int(key[6:])
                        heredicare_center_classification_raw = heredicare_variant[key]
                        if heredicare_center_classification_raw is not None and heredicare_variant[key] == "-1":
                            heredicare_center_classification_raw = None
                        classification, comment = self.preprocess_heredicare_center_classification(heredicare_center_classification_raw)
                        if classification is not None:
                            conn.insert_update_heredicare_center_classification(heredicare_annotation_id, zid, classification, comment)
                        else:
                            conn.delete_heredicare_center_classification(heredicare_annotation_id, zid)

        return status_code, err_msg



    def preprocess_heredicare_center_classification(self, info):
        if info is None:
            return None, None
        parts = info.split('|')
        classification = parts[0]
        comment = parts[1]
        comment = unquote(comment)
        comment = comment.strip()
        if comment == "" or comment == "<k.A. zur Begründung>":
            comment = None
        return classification, comment

        
