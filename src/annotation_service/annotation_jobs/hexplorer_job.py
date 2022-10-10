
from ._job import Job
import common.paths as paths
import common.functions as functions
import os


## annotate variant with hexplorer splicing scores (Hexplorer score + HBond score)
class hexplorer_job(Job):
    def __init__(self, job_config):
        self.job_name = "hexplorer"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not self.job_config['do_hexplorer']:
            return 0, '', ''

        self.print_executing()


        hexplorer_code, hexplorer_stderr, hexplorer_stdout = self.annotate_hexplorer(inpath, annotated_inpath)


        self.handle_result(inpath, annotated_inpath, hexplorer_code)
        return hexplorer_code, hexplorer_stderr, hexplorer_stdout


    def save_to_db(self, info, variant_id, conn):
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


    
    def annotate_hexplorer(self, input_vcf_path, output_vcf_path):

        if os.environ.get('WEBAPP_ENV') == 'githubtest': # use docker container installation
            command = functions.get_docker_instructions(os.environ.get("NGSBITS_CONTAINER_ID"))
            command.append("VcfAnnotateHexplorer")
        else: # use local installation
            command = [paths.ngs_bits_path + "VcfAnnotateHexplorer"]
        command = command + ["-in", input_vcf_path, "-out", output_vcf_path, "-ref", paths.ref_genome_path]
        returncode, stderr, stdout = functions.execute_command(command, 'VcfAnnotateHexplorer')

        return returncode, stderr, stdout



        #command = [paths.ngs_bits_path + "VcfAnnotateHexplorer", "-in", input_vcf_path, "-out", output_vcf_path, "-ref", paths.ref_genome_path]
        #returncode, stderr, stdout = functions.execute_command(command, process_name = "hexplorer")
        #return returncode, stderr, stdout



