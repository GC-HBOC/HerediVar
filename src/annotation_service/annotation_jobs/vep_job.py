
from ._job import Job
import common.paths as paths
import common.functions as functions
import re
import os
from common.db_IO import Connection

from ..pubmed_parser import fetch


class vep_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "VEP: protein domains"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []
        self.err_subber = re.compile(r"Smartmatch is experimental at /.*/VEP/AnnotationSource/File.pm line 472.") 


    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ['do_vep']):
            result = False
            self.status = "skipped"
        return result


    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        vcf_path = self.annotation_data.vcf_path
        annotated_path = vcf_path + ".ann.vcffromvcf"
        variant_id = self.annotation_data.variant.id
    
        self.generated_paths.append(annotated_path)
    
        # execute the annotation
        status_code, vep_stderr, vep_stdout = self._annotate_vep(vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = vep_stderr
            return # abort execution
    
        # save to db
        info = self.get_info(annotated_path)
        self.save_to_db(info, variant_id, conn)
    
        # update state
        self.status = "success"


    def save_to_db(self, info, variant_id, conn: Connection):
        status_code = 0
        err_msg = ""

        transcript_specific_annotation_type_ids = conn.get_recent_annotation_type_ids(only_transcript_specific = True)
        pfam_annotation_id = transcript_specific_annotation_type_ids["pfam_domains"]
        
        csq_info = functions.find_between(info, "CSQ=", '(;|$)')
        
        if csq_info == '' or csq_info is None:
            return status_code, err_msg

        vep_entries = csq_info.split(',')
        transcript_independent_saved = False
        pmids = ''
        for vep_entry in vep_entries:
            vep_entry = vep_entry.split('|')
            transcript_name = vep_entry[0]
            if '.' in transcript_name:
                transcript_name = transcript_name[:transcript_name.find('.')] # remove transcript version if it is present
            domains = vep_entry[9]
            if domains.find('Pfam:') >= 0:
                pfam_acc = ','.join(re.findall(r'Pfam:(PF\d+)(?:\s+|$|\&|\|)', domains)) # grab only pfam accession id from all protein domains which were returned
                pfam_acc, domain_description = conn.get_pfam_description_by_pfam_acc(pfam_acc)
                if domain_description is not None and pfam_acc is not None and domain_description != 'removed':
                    conn.insert_variant_transcript_annotation(variant_id, transcript = transcript_name, annotation_type_id = pfam_annotation_id, value = pfam_acc)

            num_vep_basic_entries = 10
            if not transcript_independent_saved and len(vep_entry) > num_vep_basic_entries:
                pmids = functions.collect_info(pmids, '', vep_entry[num_vep_basic_entries], sep = '&')

        # insert literature
        if pmids != '':
            literature_entries = fetch(pmids) # defined in pubmed_parser.py
            for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4], "vep")

        return status_code, err_msg


    def _annotate_vep(self, input_vcf, output_vcf):
        fields_oi_base = "Feature,HGVSc,HGVSp,Consequence,IMPACT,EXON,INTRON,HGNC_ID,SYMBOL,DOMAINS"
        command = [os.path.join(paths.vep_path, "vep"),
                   "-i", input_vcf, "--format", "vcf",
                   "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite",
                   "--species", "homo_sapiens", "--assembly", paths.ref_genome_name,
                   "--fork", "1",
                   "--offline", "--cache", "--dir_cache", paths.vep_cache_dir, "--fasta", paths.ref_genome_path,
                   "--numbers", "--hgvs", "--symbol", "--domains", #"--transcript_version",
                   "--failed", "1",
                   "--quiet"
                   #"--sift", "b", "--polyphen", "b", "--af","--pubmed"
                   ]

        #gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF,gnomAD_NFE_AF,gnomAD_SAS_AF, "--af_gnomad",
        #DOMAINS,SIFT,PolyPhen,PUBMED,AF
        fields_oi = fields_oi_base + ",PUBMED" # ,MaxEntScan_ref,MaxEntScan_alt
        command = command + [#"--plugin", "MaxEntScan," + os.path.join(paths.vep_path, "MaxEntScan"),
                             "--regulatory",
                             "--pubmed",
                             "--fields", fields_oi]
        


        return_code, err_msg, command_output = functions.execute_command(command, process_name="VEP")

        ## stupid workaround for this specific vep smartmatch warning:
        err_msg = re.sub(self.err_subber, "", err_msg)
        if err_msg.strip() == "VEP runtime WARNING:" or err_msg.strip() == "VEP runtime ERROR:":
            err_msg = ""

        return return_code, err_msg, command_output