
from ._job import Job
import common.paths as paths
import common.functions as functions
import os


## annotate variant with hexplorer splicing scores (Hexplorer score + HBond score)
class maxentscan_job(Job):
    def __init__(self, job_config):
        self.job_name = "maxentscan"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not self.job_config['do_maxentscan']:
            return 0, '', ''

        self.print_executing()


        hexplorer_code, hexplorer_stderr, hexplorer_stdout = self.annotate_maxentscan(inpath, annotated_inpath)


        self.handle_result(inpath, annotated_inpath, hexplorer_code)
        return hexplorer_code, hexplorer_stderr, hexplorer_stdout


    def save_to_db(self, info, variant_id, conn):

        mes_annotation_id = 53
        mes_swa_annotation_id = 54

        #print(info)

        # STANDARD MES
        mes_annotation = functions.find_between(info, "MES=", '(;|$)')

        if mes_annotation != '' and mes_annotation is not None:

            parts = mes_annotation.split('|')

            for mes_raw in parts:
                mes_parts = mes_raw.split('&')

                transcript = mes_parts[2]
                mes_ref = mes_parts[0]
                mes_alt = mes_parts[1]

                conn.insert_variant_transcript_annotation(variant_id, transcript, mes_annotation_id, '|'.join([mes_ref.strip(), mes_alt.strip()]))
        
        mes_swa_annotation = functions.find_between(info, "MES_SWA=", '(;|$)')
        if mes_swa_annotation != '' and mes_swa_annotation is not None:

            parts = mes_swa_annotation.split('|')

            for mes_raw in parts:
                mes_parts = mes_raw.split('&')

                maxentscan_ref_donor = mes_parts[0]
                maxentscan_alt_donor = mes_parts[1]
                maxentscan_donor_comp = mes_parts[2]
                maxentscan_ref_acceptor = mes_parts[3]
                maxentscan_alt_acceptor = mes_parts[4]
                maxentscan_acceptor_comp = mes_parts[5]
                transcript = mes_parts[6]

                data = [maxentscan_ref_donor, maxentscan_alt_donor, maxentscan_donor_comp, maxentscan_ref_acceptor, maxentscan_alt_acceptor, maxentscan_acceptor_comp]
                data = [x.strip() for x in data]

                conn.insert_variant_transcript_annotation(variant_id, transcript, mes_swa_annotation_id, '|'.join(data))



    
    def annotate_maxentscan(self, input_vcf_path, output_vcf_path):

        #if os.environ.get('WEBAPP_ENV') == 'githubtest': # use docker container installation
        #    command = functions.get_docker_instructions(os.environ.get("NGSBITS_CONTAINER_ID"))
        #    command.append("VcfAnnotateHexplorer")
        #else: # use local installation
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateMaxEntScan")]
        command = command + ["-swa", "-in", input_vcf_path, "-out", output_vcf_path, "-ref", paths.ref_genome_path, "-gff", paths.ensembl_transcript_path]
        returncode, stderr, stdout = functions.execute_command(command, 'VcfAnnotateMaxEntScan')

        return returncode, stderr, stdout



        #command = [paths.ngs_bits_path + "VcfAnnotateHexplorer", "-in", input_vcf_path, "-out", output_vcf_path, "-ref", paths.ref_genome_path]
        #returncode, stderr, stdout = functions.execute_command(command, process_name = "hexplorer")
        #return returncode, stderr, stdout



