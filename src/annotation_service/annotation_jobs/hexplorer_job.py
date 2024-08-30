
from ._job import Job
import common.paths as paths
import common.functions as functions
import os


## annotate variant with hexplorer splicing scores (Hexplorer score + HBond score)
class hexplorer_job(Job):

    def __init__(self, annotation_data):
        self.job_name = "hexplorer"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []
        

    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ['do_hexplorer']):
            result = False
            self.status = "skipped"
        return result

    
    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        vcf_path = self.annotation_data.vcf_path
        annotated_path = vcf_path + ".ann.hexplorer"
        variant_id = self.annotation_data.variant.id

        self.generated_paths.append(annotated_path)
    
        # execute the annotation
        status_code, hexplorer_stderr, hexplorer_stdout = self.annotate_hexplorer(vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = "Hexplorer error: " + hexplorer_stderr
            return # abort execution
    
        # save to db
        info = self.get_info(annotated_path)
        self.save_to_db(info, variant_id, conn)
    
        # update state
        self.status = "success"


    def save_to_db(self, info, variant_id, conn):
        status_code = 0
        err_msg = ""
        self.insert_annotation(variant_id, info, "hexplorer_delta=", 39, conn)
        self.insert_annotation(variant_id, info, "hexplorer_wt=", 41, conn)
        self.insert_annotation(variant_id, info, "hexplorer_mut=", 40, conn)
        self.insert_annotation(variant_id, info, "hexplorer_delta_rev=", 42, conn)
        self.insert_annotation(variant_id, info, "hexplorer_wt_rev=", 44, conn)
        self.insert_annotation(variant_id, info, "hexplorer_mut_rev=", 43, conn)

        self.insert_annotation(variant_id, info, "max_hbond_delta=", 45, conn)
        self.insert_annotation(variant_id, info, "max_hbond_wt=", 47, conn)
        self.insert_annotation(variant_id, info, "max_hbond_mut=", 46, conn)
        self.insert_annotation(variant_id, info, "max_hbond_delta_rev=", 48, conn)
        self.insert_annotation(variant_id, info, "max_hbond_wt_rev=", 50, conn)
        self.insert_annotation(variant_id, info, "max_hbond_mut_rev=", 49, conn)

        return status_code, err_msg


    
    def annotate_hexplorer(self, input_vcf_path, output_vcf_path):
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateHexplorer")]
        command = command + ["-in", input_vcf_path, "-out", output_vcf_path, "-ref", paths.ref_genome_path]
        returncode, stderr, stdout = functions.execute_command(command, 'VcfAnnotateHexplorer')

        return returncode, stderr, stdout



