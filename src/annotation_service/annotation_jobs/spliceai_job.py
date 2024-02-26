
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
        recent_annotation_ids = conn.get_recent_annotation_type_ids()

        for prefix in ['snv_', 'indel_', '']:
            self.insert_annotation(variant_id, info, prefix + 'SpliceAI=', recent_annotation_ids["spliceai_details"], conn, value_modifier_function= lambda value : ','.join(['|'.join(x.split('|')[1:]) for x in value.replace(',', '&').split('&')]) )
            self.insert_annotation(variant_id, info, prefix + 'SpliceAI=', recent_annotation_ids["spliceai_max_delta"], conn, value_modifier_function= self.get_spliceai_max_delta )
        
        return 0, ""


    #','.join([str(max([float(x) for x in x.split('|')[2:6] if x != '.'])) for x in value.replace(',', '&').split('&')])
    def get_spliceai_max_delta(self, spliceai_raw):
        spliceai_parts = spliceai_raw.replace(',', '&').split('&')
        all_max_values = []
        for splice_ai in spliceai_parts:
            all_values = []
            for value in splice_ai.split('|')[2:6]:
                if value != '.':
                    all_values.append(float(value))
            if len(all_values) > 0:
                all_max_values.append(str(max(all_values)))
            else:
                all_max_values.append('.')
        return ','.join(all_max_values)


    def annotate_missing_spliceai(self, input_vcf_path, output_vcf_path):

        found_spliceai_header = False
        need_annotation = False
        errors = ''
        spliceai_code = -1
        spliceai_stdout = ''
        errors = []
        with open(input_vcf_path, 'r') as input_file:
            for line in input_file:
                if line.startswith('#'):
                    if line.startswith('##INFO=<ID=snv_SpliceAI') or line.startswith('##INFO=<ID=indel_SpliceAI') :
                        found_spliceai_header = True
                    continue
                else:
                    if "SpliceAI=" in line:
                        continue
                    
                    need_annotation = True

        if not found_spliceai_header:
            errors.append("SpliceAI WARNING: did not find a SpliceAI INFO entry in input vcf, did you annotate the file using a precomputed file before?")
        if need_annotation:
            spliceai_code, spliceai_stderr, spliceai_stdout = self.annotate_spliceai_algorithm(input_vcf_path, output_vcf_path)
            if 'SpliceAI runtime ERROR:' in spliceai_stderr:
                errors.append(spliceai_stderr)
            elif 'Skipping record' in spliceai_stderr:
                errors.append("SpliceAI WARNING skipping: " + functions.find_between(spliceai_stderr, 'WARNING:', ': chr'))

        # need to insert some code here to merge the newly annotated variants and previously 
        # annotated ones from the db if there are files which contain more than one variant! 



        return spliceai_code, '; '.join(errors), spliceai_stdout



    def annotate_spliceai_algorithm(self, input_vcf_path, output_vcf_path):
        # prepare input data
        input_vcf_zipped_path = input_vcf_path + ".gz"

        # gbzip and index the input file as this is required for spliceai...
        returncode, stderr, stdout = functions.execute_command([os.path.join(paths.htslib_path, 'bgzip'), '-f', '-k', input_vcf_path], 'bgzip')
        if returncode != 0:
            return returncode, stderr, stdout
        returncode, stderr, stdout = functions.execute_command([os.path.join(paths.htslib_path, 'tabix'), "-f", "-p", "vcf", input_vcf_zipped_path], 'tabix')
        if returncode != 0:
            functions.rm(input_vcf_zipped_path)
            return returncode, stderr, stdout

        # execute spliceai
        command = ['spliceai', '-I', input_vcf_zipped_path, '-O', output_vcf_path, '-R', paths.ref_genome_path, '-A', paths.ref_genome_name.lower(), '-M', '1']
        returncode, stderr, stdout = functions.execute_command(command, 'SpliceAI')

        functions.rm(input_vcf_zipped_path)
        functions.rm(input_vcf_zipped_path + ".tbi")

        return returncode, stderr, stdout



