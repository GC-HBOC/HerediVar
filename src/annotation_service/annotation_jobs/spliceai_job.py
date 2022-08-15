
from ._job import Job
import common.paths as paths
import common.functions as functions
import tempfile

## run SpliecAI on the variants which are not contained in the precomputed file
class spliceai_job(Job):
    def __init__(self, job_config):
        self.job_name = "spliceAI on missing variants"
        self.job_config = job_config


    def execute(self, inpath, **kwargs):
        if not self.job_config['do_spliceai']:
            return 0, '', ''

        self.print_executing()


        spliceai_code, spliceai_stderr, splicai_stdout = self.annotate_missing_spliceai(inpath, self.get_annotation_tempfile())


        self.handle_result(inpath, spliceai_code)
        return spliceai_code, spliceai_stderr, splicai_stdout


    def save_to_db(self, info, variant_id, conn):
        self.insert_annotation(variant_id, info, 'SpliceAI=', 7, conn, value_modifier_function= lambda value : '|'.join(value.split('|')[2:]))
        self.insert_annotation(variant_id, info, 'SpliceAI=', 8, conn, value_modifier_function= lambda value : max(value.split('|')[2:6]))




    def annotate_missing_spliceai(self, input_vcf_path, output_vcf_path):
        input_file = open(input_vcf_path, 'r')
        temp_path = tempfile.gettempdir() + "/spliceai_temp.vcf"
        temp_file = open(temp_path, 'w')

        found_spliceai_header = False
        need_annotation = False
        errors = ''
        spliceai_code = -1
        splicai_stdout = ''
        errors = []
        for line in input_file:
            if line.startswith('#'):
                temp_file.write(line)
                if line.startswith('##INFO=<ID=SpliceAI'):
                    found_spliceai_header = True
                continue
            else:
                entries = line.split('\t')
                if len(entries) != 8: 
                    errors.append("SpliceAI ERROR: not the correct number of entries in input vcf line: " + line)
                    continue
                
                if "SpliceAI=" in line:
                    continue
                
                need_annotation = True
                temp_file.write(line)
        temp_file.close()
        if not found_spliceai_header:
            errors.append("SpliceAI WARNING: did not find a SpliceAI INFO entry in input vcf, did you annotate the file using a precomputed file before?")
        if need_annotation:
            functions.execute_command(['sed', '-i', '/SpliceAI/d', temp_path], "sed")
            spliceai_code, spliceai_stderr, splicai_stdout = self.annotate_spliceai_algorithm(temp_path, output_vcf_path)
            errors.append(spliceai_stderr)

        # need to insert some code here to merge the newly annotated variants and previously 
        # annotated ones from the db if there are files which contain more than one variant! 
        input_file.close()

        return spliceai_code, '; '.join(errors), splicai_stdout



    def annotate_spliceai_algorithm(self, input_vcf_path, output_vcf_path):
        # prepare input data
        input_vcf_zipped_path = input_vcf_path + ".gz"
        functions.execute_command([paths.ngs_bits_path + "VcfSort", "-in", input_vcf_path, "-out", input_vcf_path], 'vcfsort')
        functions.execute_command(['bgzip', '-f', input_vcf_path], 'bgzip')
        functions.execute_command(['tabix', "-f", "-p", "vcf", input_vcf_zipped_path], 'tabix')

        # execute spliceai
        command = ['spliceai', '-I', input_vcf_zipped_path, '-O', output_vcf_path, '-R', paths.ref_genome_path, '-A', paths.ref_genome_name.lower()]
        returncode, stderr, stdout = functions.execute_command(command, 'SpliceAI')

        return returncode, stderr, stdout





