
from ._job import Job
import common.paths as paths
import common.functions as functions
import os


## run SpliecAI on the variants which are not contained in the precomputed file
# this should be called after the annotate_from_vcf_job!
class spliceai_job(Job):

    def __init__(self, annotation_data):
        self.job_name = "spliceAI"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []


    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ['do_spliceai']):
            result = False
            self.status = "skipped"
        return result


    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        vcf_path = self.annotation_data.vcf_path
        annotated_path = vcf_path + ".ann.spliceai"
        annotated_path_2 = annotated_path + ".2"
        variant_id = self.annotation_data.variant.id

        self.generated_paths.append(annotated_path)
        self.generated_paths.append(annotated_path + "_warnings.txt")
        self.generated_paths.append(annotated_path_2)
    
        # execute the annotation
        config_file_path = self.write_vcf_annoate_config()
        self.generated_paths.append(config_file_path)
        status_code, vcf_annotate_stderr, vcf_annotate_stdout = self.annotate_from_vcf(config_file_path, vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = vcf_annotate_stderr
            return

        status_code, spliceai_stderr, splicai_stdout = self.annotate_missing_spliceai(annotated_path, annotated_path_2)
        if status_code != 0:
            self.status = "error"
            self.err_msg = spliceai_stderr
            return

        status_code, err_msg_vcfcheck, vcf_errors = functions.check_vcf(vcf_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = vcf_errors
            return
    
        # save to db
        info = self.get_info(annotated_path_2)
        self.save_to_db(info, variant_id, conn)

        # update state
        self.status = "success"


    def annotate_from_vcf(self, config_file_path, input_vcf, output_vcf):
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateFromVcf")]
        command.extend([ "-config_file", config_file_path, "-in", input_vcf, "-out", output_vcf])

        returncode, err_msg, vcf_errors = functions.execute_command(command, 'VcfAnnotateFromVcf_SpliceAI')

        return returncode, err_msg, vcf_errors
    

    def save_to_db(self, info, variant_id, conn):
        recent_annotation_ids = conn.get_recent_annotation_type_ids()

        for prefix in ['snv_', 'indel_', '']:
            self.insert_annotation(variant_id, info, prefix + 'SpliceAI=', recent_annotation_ids["spliceai_details"], conn, value_modifier_function= lambda value : ','.join(['|'.join(x.split('|')[1:]) for x in value.replace(',', '&').split('&')]) )
            self.insert_annotation(variant_id, info, prefix + 'SpliceAI=', recent_annotation_ids["spliceai_max_delta"], conn, value_modifier_function= self.get_spliceai_max_delta )
        
        return 0, ""


    def write_vcf_annoate_config(self):
        config_file_path = functions.get_random_temp_file(".conf", filename_ext = "vcf_annoate")
        config_file = open(config_file_path, 'w')

        ## add spliceai precomputed scores
        config_file.write(paths.spliceai_snv_path + "\tsnv\tSpliceAI\t\n")
        config_file.write(paths.spliceai_indel_path + "\tindel\tSpliceAI\t\n")

        config_file.close()
        return config_file_path


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
            errors = '; '.join(errors)
        else:
            spliceai_code, errors, spliceai_stdout = functions.execute_command(["mv", input_vcf_path, output_vcf_path], "mv")

        return spliceai_code, errors, spliceai_stdout



    def annotate_spliceai_algorithm(self, input_vcf_path, output_vcf_path):
        # prepare input data
        input_vcf_zipped_path = input_vcf_path + ".gz"

        # bgzip and index the input file as this is required for spliceai...
        returncode, stderr, stdout = functions.execute_command([os.path.join(paths.htslib_path, 'bgzip'), '-f', '-k', input_vcf_path], 'bgzip')
        if returncode != 0:
            return returncode, "SpliceAI bgzip error:" + stderr, stdout
        returncode, stderr, stdout = functions.execute_command([os.path.join(paths.htslib_path, 'tabix'), "-f", "-p", "vcf", input_vcf_zipped_path], 'tabix')
        if returncode != 0:
            functions.rm(input_vcf_zipped_path)
            return returncode, "SpliceAI tabix error: " + stderr, stdout

        # execute spliceai
        # -M: masked scores!
        command = ['spliceai', '-I', input_vcf_zipped_path, '-O', output_vcf_path, '-R', paths.ref_genome_path, '-A', paths.ref_genome_name.lower(), '-M', '1']
        returncode, stderr, stdout = functions.execute_command(command, 'SpliceAI')

        functions.rm(input_vcf_zipped_path)
        functions.rm(input_vcf_zipped_path + ".tbi")

        return returncode, stderr, stdout



