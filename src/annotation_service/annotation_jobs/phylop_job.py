
from ._job import Job
import common.paths as paths
import common.functions as functions


## annotate variant with phylop 100-way conservation scores
class phylop_job(Job):
    def __init__(self, job_config):
        self.job_name = "phyloP annotation"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not self.job_config['do_phylop']:
            return 0, '', ''

        self.print_executing()

        
        phylop_code, phylop_stderr, phylop_stdout = self.annotate_phylop(inpath, annotated_inpath)


        self.handle_result(inpath, annotated_inpath, phylop_code)
        return phylop_code, phylop_stderr, phylop_stdout


    def save_to_db(self, info, variant_id, conn):
        self.insert_annotation(variant_id, info, 'PHYLOP=', 4, conn)
        

    
    def annotate_phylop(self, input_vcf, output_vcf):
        command = [paths.ngs_bits_path + "VcfAnnotateFromBigWig",
                   "-in", input_vcf, "-bw", paths.phylop_file_path,
                   "-name", "PHYLOP", "-desc", "PhyloP 100-way conservation scores (Annotation file used: " + paths.phylop_file_path + ", annotated using ngs-bits/VcfAnnotateFromBigWig - mode max)",
                   "-mode", "max", 
                   "-out", output_vcf]

        return_code, err_msg, command_output = functions.execute_command(command, process_name="PhyloP")
        return return_code, err_msg, command_output


