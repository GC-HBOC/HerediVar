
from ._job import Job
import common.paths as paths
import common.functions as functions
import os


## annotate variant with phylop 100-way conservation scores
class phylop_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "phyloP"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []


    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ["do_phylop"]):
            result = False
            self.status = "skipped"
        return result


    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        vcf_path = self.annotation_data.vcf_path
        annotated_path = vcf_path + ".ann.phylop"
        variant_id = self.annotation_data.variant.id

        self.generated_paths.append(annotated_path)
    
        # execute the annotation
        status_code, phylop_stderr, phylop_stdout = self.annotate_phylop(vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = phylop_stderr
            return # abort execution
    
        # save to db
        info = self.get_info(annotated_path)
        self.save_to_db(info, variant_id, conn)
    
        # update state
        self.status = "success"


    def save_to_db(self, info, variant_id, conn):
        self.insert_annotation(variant_id, info, 'PHYLOP=', 4, conn)
        return 0, ""
        

    
    def annotate_phylop(self, input_vcf, output_vcf):
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateFromBigWig")]
        command.extend(["-in", input_vcf, "-bw", paths.phylop_file_path,
                   "-name", "PHYLOP", # "-desc", "PhyloP 100-way conservation scores (Annotation file used: " + paths.phylop_file_path + ", annotated using ngs-bits/VcfAnnotateFromBigWig - mode max)"
                   "-mode", "max", 
                   "-out", output_vcf])

        returncode, stderr, stdout = functions.execute_command(command, 'VcfAnnotateFromBigWig phylop')

        return returncode, stderr, stdout


