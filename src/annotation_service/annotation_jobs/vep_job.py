
from ._job import Job
import common.paths as paths
import common.functions as functions
import re
import os

from ..pubmed_parser import fetch


class vep_job(Job):
    def __init__(self, job_config, refseq=False):
        if refseq:
            self.job_name = "vep refseq"
        else:
            self.job_name = "vep ensembl"
        self.refseq=refseq
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not self.job_config['do_vep']:
            return 0, '', ''

        self.print_executing()
        
        if os.environ.get("WEBAPP_ENV") == "githubtest":
            one_variant = kwargs['one_variant']
            vep_code, vep_stderr, vep_stdout = self._fake_vep(one_variant[0], annotated_inpath)
        else:
            vep_code, vep_stderr, vep_stdout = self._annotate_vep(inpath, annotated_inpath)

        self.handle_result(inpath, annotated_inpath, vep_code)
        return vep_code, vep_stderr, vep_stdout


    def save_to_db(self, info, variant_id, conn):
        
        # save variant consequences from ensembl and refseq
        # !!!! format of refseq and ensembl annotations from vep need to be equal: 0Feature,1HGVSc,2HGVSp,3Consequence,4IMPACT,5EXON,6INTRON,7HGNC_ID,8SYMBOL,9DOMAIN,...additional info
        if self.refseq:
            csq_info = functions.find_between(info, "CSQ_refseq=", ';')
            consequence_source = "refseq"
        else:
            csq_info = functions.find_between(info, "CSQ=", ';')
            consequence_source = "ensembl"
        
        print(csq_info)
        if csq_info == '' or csq_info is None:
            return

        vep_entries = csq_info.split(',')
        transcript_independent_saved = False
        pmids = ''
        for vep_entry in vep_entries:
            print(vep_entry)
            #10MaxEntScan_ref,11MaxEntScan_alt
            vep_entry = vep_entry.split('|')
            exon_nr = vep_entry[5]
            exon_nr = exon_nr[:exon_nr.find('/')] # take only number from number/total
            intron_nr = vep_entry[6]
            intron_nr = intron_nr[:intron_nr.find('/')] # take only number from number/total
            hgvs_c = vep_entry[1]
            hgvs_c = hgvs_c[hgvs_c.find(':')+1:] # remove transcript name
            hgvs_p = vep_entry[2]
            hgvs_p = hgvs_p[hgvs_p.find(':')+1:] # remove transcript name
            transcript_name = vep_entry[0]
            if '.' in transcript_name:
                transcript_name = transcript_name[:transcript_name.find('.')] # remove transcript version if it is present
            domains = vep_entry[9]
            pfam_acc = ''
            if domains.count("Pfam:") >= 1:
                pfam_acc = re.search(r'Pfam:(PF\d+)(?:\s+|$|\&|\|)', domains).group(1) # grab only pfam accession id from all protein domains which were returned
                if domains.count("Pfam:") > 1:
                    print("WARNING: there were multiple PFAM domain ids in: " + str(domains) + ". defaulting to the first one.")
            if self.job_config['insert_consequence']:
                conn.insert_variant_consequence(variant_id, 
                                                transcript_name, 
                                                hgvs_c, 
                                                hgvs_p, 
                                                vep_entry[3].replace('_', ' ').replace('&', ' & '), 
                                                vep_entry[4], 
                                                exon_nr, 
                                                intron_nr, 
                                                vep_entry[7],
                                                vep_entry[8],
                                                consequence_source,
                                                pfam_acc)
            num_vep_basic_entries = 10
            if not transcript_independent_saved and len(vep_entry) > num_vep_basic_entries:
                transcript_independent_saved = True
                maxentscan_ref = vep_entry[num_vep_basic_entries]
                if maxentscan_ref != '' and self.job_config['insert_maxent']:
                    conn.insert_variant_annotation(variant_id, 9, maxentscan_ref)
                maxentscan_alt = vep_entry[num_vep_basic_entries+1]
                if maxentscan_alt != '' and self.job_config['insert_maxent']:
                    conn.insert_variant_annotation(variant_id, 10, maxentscan_alt)
                pmids = functions.collect_info(pmids, '', vep_entry[num_vep_basic_entries+2], sep = '&')
                #self.update_saved_data('pmids', vep_entry[num_vep_basic_entries+2], operation = lambda x, y : functions.collect_info(x, '', y, sep = '&'))

        # insert literature
        if self.job_config['insert_literature'] and pmids != '':
            literature_entries = fetch(pmids) # defined in pubmed_parser.py
            for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4])


    def _fake_vep(self, variant_id, output_vcf):
        """This function is only for testing purposes"""
        import shutil
        shutil.copy2(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/tests/data/" + str(variant_id) + "_vep_annotated.vcf", output_vcf)
        return 0, "", ""


    #"/mnt/storage2/GRCh38/share/data/genomes/GRCh38.fa"
    def _annotate_vep(self, input_vcf, output_vcf):
        fields_oi_base = "Feature,HGVSc,HGVSp,Consequence,IMPACT,EXON,INTRON,HGNC_ID,SYMBOL,DOMAINS"
        command = [paths.vep_path + "/vep",
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

        if not self.refseq: #use ensembl
            #gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF,gnomAD_NFE_AF,gnomAD_SAS_AF, "--af_gnomad",
            #DOMAINS,SIFT,PolyPhen,PUBMED,AF
            fields_oi = fields_oi_base + ",MaxEntScan_ref,MaxEntScan_alt,PUBMED"
            command = command + ["--plugin", "MaxEntScan," + paths.vep_path + "/MaxEntScan/",
                                 "--regulatory",
                                 "--pubmed",
                                 "--fields", fields_oi]

        if self.refseq:
            fields_oi = fields_oi_base
            command = command + ["--refseq",
                                 "--vcf_info_field", "CSQ_refseq",
                                 "--fields", fields_oi]
        


        return_code, err_msg, command_output = functions.execute_command(command, process_name="VEP")
        return return_code, err_msg, command_output