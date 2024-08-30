
from ._job import Job
import common.paths as paths
import common.functions as functions
import os


## annotate variant with hexplorer splicing scores (Hexplorer score + HBond score)
class maxentscan_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "maxentscan"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []

    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ["do_maxentscan"]):
            result = False
            self.status = "skipped"
        return result
    

    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        vcf_path = self.annotation_data.vcf_path
        annotated_path = vcf_path + ".ann.maxentscan"
        variant_id = self.annotation_data.variant.id

        self.generated_paths.append(annotated_path)
    
        # execute the annotation
        status_code, hexplorer_stderr, hexplorer_stdout = self.annotate_maxentscan(vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = hexplorer_stderr
            return # abort execution
    
        # save to db
        info = self.get_info(annotated_path)
        self.save_to_db(info, variant_id, conn)
    
        # update state
        self.status = "success"


    def save_to_db(self, info, variant_id, conn):
        status_code = 0
        err_msg = ""

        recent_annotation_ids = conn.get_recent_annotation_type_ids()
        mes_annotation_id = recent_annotation_ids["maxentscan"]
        mes_swa_annotation_id = recent_annotation_ids["maxentscan_swa"]

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
        
        # MES SWA
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

        return status_code, err_msg


    
    def annotate_maxentscan(self, input_vcf_path, output_vcf_path):
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateMaxEntScan")]
        command = command + ["-swa", "-in", input_vcf_path, "-out", output_vcf_path, "-ref", paths.ref_genome_path, "-gff", paths.ensembl_transcript_path]
        returncode, stderr, stdout = functions.execute_command(command, 'VcfAnnotateMaxEntScan')

        return returncode, stderr, stdout



