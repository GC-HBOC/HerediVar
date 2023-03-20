
from ._job import Job
import common.paths as paths
import common.functions as functions
import tempfile
import uuid
import os
from os.path import exists


## run SpliecAI on the variants which are not contained in the precomputed file
# this should be called after the annotate_from_vcf_job!
class spliceai_job(Job):
    def __init__(self, job_config):
        self.job_name = "spliceAI on missing variants"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not self.job_config['do_spliceai']:
            return 0, '', ''

        self.print_executing()


        spliceai_code, spliceai_stderr, splicai_stdout = self.annotate_missing_spliceai(inpath, annotated_inpath)


        self.handle_result(inpath, annotated_inpath, spliceai_code)
        return spliceai_code, spliceai_stderr, splicai_stdout


    def save_to_db(self, info, variant_id, conn):
        self.insert_annotation(variant_id, info, 'SpliceAI=', 7, conn, value_modifier_function= lambda value : ','.join(['|'.join(x.split('|')[1:]) for x in value.split(',')]) )
        self.insert_annotation(variant_id, info, 'SpliceAI=', 8, conn, value_modifier_function= lambda value : ','.join([str(max([float(x) for x in x.split('|')[2:6]])) for x in value.split(',')]) )




    def annotate_missing_spliceai(self, input_vcf_path, output_vcf_path):
        #input_file = open(input_vcf_path, 'r')
        #temp_path = tempfile.gettempdir() + '/' + str(uuid.uuid4()) + '.vcf'
        #temp_file = open(temp_path, 'w')

        found_spliceai_header = False
        need_annotation = False
        errors = ''
        spliceai_code = -1
        spliceai_stdout = ''
        errors = []
        with open(input_vcf_path, 'r') as input_file:
            for line in input_file:
                if line.startswith('#'):
                    #temp_file.write(line)
                    if line.startswith('##INFO=<ID=SpliceAI'):
                        found_spliceai_header = True
                    continue
                else:
                    if "SpliceAI=" in line:
                        continue
                    
                    need_annotation = True
                    #temp_file.write(line)
        #temp_file.close()
        if not found_spliceai_header:
            errors.append("SpliceAI WARNING: did not find a SpliceAI INFO entry in input vcf, did you annotate the file using a precomputed file before?")
        if need_annotation:
            #returncode, stderr, stdout = functions.execute_command(['sed', '-i', '/SpliceAI/d', input_vcf_path], "sed")
            #if returncode != 0:
            #    errors.append(stderr)
            #returncode, stderr, stdout = functions.execute_command(['chmod', '777', input_vcf_path], 'chmod')
            #if returncode != 0:
            #    errors.append(stderr)
            #returncode, stderr, stdout = functions.execute_command(["ls", "-l", "/tmp"], "ls")
            #print(stdout)
            spliceai_code, spliceai_stderr, spliceai_stdout = self.annotate_spliceai_algorithm(input_vcf_path, output_vcf_path)
            errors.append(spliceai_stderr)

        # need to insert some code here to merge the newly annotated variants and previously 
        # annotated ones from the db if there are files which contain more than one variant! 
        #input_file.close()



        return spliceai_code, '; '.join(errors), spliceai_stdout



    def annotate_spliceai_algorithm(self, input_vcf_path, output_vcf_path):
        # prepare input data
        input_vcf_zipped_path = input_vcf_path + ".gz"

        # gbzip and index the input file as this is required for spliceai...
        returncode, stderr, stdout = functions.execute_command([os.path.join(paths.htslib_path, 'bgzip'), '-f', input_vcf_path], 'bgzip')
        if returncode != 0:
            return returncode, stderr, stdout
        returncode, stderr, stdout = functions.execute_command([os.path.join(paths.htslib_path, 'tabix'), "-f", "-p", "vcf", input_vcf_zipped_path], 'tabix')
        if returncode != 0:
            return returncode, stderr, stdout

        # execute spliceai
        command = ['spliceai', '-I', input_vcf_zipped_path, '-O', output_vcf_path, '-R', paths.ref_genome_path, '-A', paths.ref_genome_name.lower()]
        returncode, stderr, stdout = functions.execute_command(command, 'SpliceAI')

        if exists(input_vcf_zipped_path):
            os.remove(input_vcf_zipped_path)
        if exists(input_vcf_zipped_path + ".tbi"):
            os.remove(input_vcf_zipped_path + ".tbi")

        return returncode, stderr, stdout





