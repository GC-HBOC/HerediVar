
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
    def __init__(self, annotation_data):
        self.job_name = "heredicare"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []

    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ["do_heredicare"]):
            result = False
            self.status = "skipped"
        return result


    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        variant_id = self.annotation_data.variant.id
    
        # execute and save to db
        status_code, err_msg = self.annotate_heredicare(variant_id, conn)
        if status_code != 0:
            self.status = "error"
            self.err_msg = err_msg
            return # abort execution
    
        # update state
        self.status = "success"


    def annotate_heredicare(self, variant_id, conn):
        status_code = 0
        err_msg = ""

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
            # we need to check the length of the heredicare variant
            # if it is 0 the variant is unknown to heredicare
            # this might happen when a variant was just submitted to heredicare and it is not processed yet. Then, the vid is already known by heredivar but heredicare doesnt have information about this variant
            # In this case we simply skip the heredicare annotation
            # It is however good have the vid in heredivar right after insert because then we do not need a reimport after every heredicare insert
            elif len(heredicare_variant) > 0: 
                #print(heredicare_variant)
                n_fam = heredicare_variant["N_FAM"]
                n_pat = heredicare_variant["N_PAT"]
                consensus_class = heredicare_variant["PATH_TF"] if heredicare_variant["PATH_TF"] != "-1" else None
                comment = heredicare_variant.get("VUSTF_21", heredicare_variant["VUSTF_15"]) # use vustf21, but if it is missing fallback to vustf15 - fallback can be removed later once the production heredicare api has the vustf21 field
                comment = comment.strip() if comment is not None else None
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

        
