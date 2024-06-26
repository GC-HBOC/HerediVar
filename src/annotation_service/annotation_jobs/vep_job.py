
from ._job import Job
import common.paths as paths
import common.functions as functions
import re
import os
import urllib.parse
from common.db_IO import Connection

from ..pubmed_parser import fetch


class vep_job(Job):
    def __init__(self, job_config):
        self.job_name = "vep ensembl"
        self.job_config = job_config
        self.err_subber = re.compile(r"Smartmatch is experimental at /.*/VEP/AnnotationSource/File.pm line 472.") 


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not self.job_config['do_vep']:
            return 0, '', ''

        self.print_executing()
        
        vep_code, vep_stderr, vep_stdout = self._annotate_vep(inpath, annotated_inpath)

        ## stupid workaround for this specific vep smartmatch warning:
        vep_stderr = re.sub(self.err_subber, "", vep_stderr)
        if vep_stderr.strip() == "VEP runtime WARNING:" or vep_stderr.strip() == "VEP runtime ERROR:":
            vep_stderr = ""

        self.handle_result(inpath, annotated_inpath, vep_code)
        return vep_code, vep_stderr, vep_stdout


    def save_to_db(self, info, variant_id, conn: Connection):
        status_code = 0
        err_msg = ""

        transcript_specific_annotation_type_ids = conn.get_recent_annotation_type_ids(only_transcript_specific = True)
        pfam_annotation_id = transcript_specific_annotation_type_ids["pfam_domains"]
        
        # !!!! format of annotations from vep need to be equal: 0Feature,1HGVSc,2HGVSp,3Consequence,4IMPACT,5EXON,6INTRON,7HGNC_ID,8SYMBOL,9DOMAIN,...additional info
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
                conn.insert_variant_transcript_annotation(variant_id, transcript = transcript_name, annotation_type_id = pfam_annotation_id, value = pfam_acc)

            num_vep_basic_entries = 10
            if not transcript_independent_saved and len(vep_entry) > num_vep_basic_entries:
                pmids = functions.collect_info(pmids, '', vep_entry[num_vep_basic_entries], sep = '&')

        # insert literature
        if pmids != '':
            literature_entries = fetch(pmids) # defined in pubmed_parser.py
            for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                #print(paper[0])
                conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4], "vep")

        return status_code, err_msg


    #"/mnt/storage2/GRCh38/share/data/genomes/GRCh38.fa"
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

        return return_code, err_msg, command_output