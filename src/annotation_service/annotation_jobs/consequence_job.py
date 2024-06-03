
from ._job import Job
import common.paths as paths
import common.functions as functions
import tempfile
import os
from os.path import exists
import urllib

from ..pubmed_parser import fetch

## this annotates various information from different vcf files
class consequence_job(Job):
    def __init__(self, job_config):
        self.job_name = "annotate consequence"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not any(self.job_config[x] for x in ['do_consequence']):
            return 0, '', ''

        self.print_executing()

        vcf_annotate_code, vcf_annotate_stderr, vcf_annotate_stdout = self.annotate_consequence(inpath, annotated_inpath)

        self.handle_result(inpath, annotated_inpath, vcf_annotate_code)

        return vcf_annotate_code, vcf_annotate_stderr, vcf_annotate_stdout



    def save_to_db(self, info, variant_id, conn):
        err_msg = ""
        status_code = 0

        info_field_prefix = "CSQ_"
        sources = ['ensembl', 'refseq']

        if self.job_config['do_consequence']:
            #print(info)
            conn.delete_variant_consequences(variant_id)

        #FORMAT: Allele|Consequence|IMPACT|SYMBOL|HGNC_ID|Feature|Feature_type|EXON|INTRON|HGVSc|HGVSp
        # CSQ=
        # T|synonymous_variant|LOW|CDH1|HGNC:1748|ENST00000261769.10|Transcript|12/16||c.1896C>T|p.His632%3D,
        # T|3_prime_UTR_variant&NMD_transcript_variant|MODIFIER|CDH1|HGNC:1748|ENST00000566612.5|Transcript|11/15||c.*136C>T|,
        # T|synonymous_variant|LOW|CDH1|HGNC:1748|ENST00000422392.6|Transcript|11/15||c.1713C>T|p.His571%3D,
        # T|3_prime_UTR_variant&NMD_transcript_variant|MODIFIER|CDH1|HGNC:1748|ENST00000566510.5|Transcript|11/15||c.*562C>T|,
        # T|non_coding_transcript_exon_variant|MODIFIER|CDH1|HGNC:1748|ENST00000562836.5|Transcript|11/15||n.1967C>T|,
        # T|upstream_gene_variant|MODIFIER|FTLP14|HGNC:37964|ENST00000562087.2|Transcript||||,
        # T|upstream_gene_variant|MODIFIER|CDH1|HGNC:1748|ENST00000562118.1|Transcript||||
        for source in sources:
            info_field = info_field_prefix + source + "="
            csq_info = functions.find_between(info, info_field, '(;|$)')
            if csq_info is None:
                continue
            csq_entries = csq_info.split(',')
            for csq_entry in csq_entries:
                if csq_entry.strip() == '':
                    continue
                parts = csq_entry.strip().split('|')
                feature_type = parts[6]
                if feature_type.lower() != "transcript":
                    continue
                consequence = parts[1].replace('_', ' ').replace('&', ' & ')
                impact = parts[2]
                gene_symbol = parts[3]
                hgnc_id = parts[4].strip('HGNC:')
                transcript_name = parts[5]
                if '.' in transcript_name:
                    transcript_name = transcript_name[:transcript_name.find('.')] # remove transcript version if it is present
                exon_nr = parts[7]
                if '/' in exon_nr:
                    exon_nr = exon_nr[:exon_nr.find('/')] # take only number from number/total
                intron_nr = parts[8][:parts[8].find('/')] 
                if '/' in intron_nr:
                    intron_nr = intron_nr[:intron_nr.find('/')] # take only number from number/total
                hgvs_c = urllib.parse.unquote(parts[9])
                hgvs_p = urllib.parse.unquote(parts[10])

                #variant_id, transcript_name, hgvs_c, hgvs_p, consequence, impact, exon_nr, intron_nr, hgnc_id, symbol, consequence_source, pfam_acc
                #print([variant_id, transcript_name, hgvs_c, hgvs_p, consequence, impact, exon_nr, intron_nr, hgnc_id, gene_symbol, source])
                conn.insert_variant_consequence(variant_id, transcript_name, hgvs_c, hgvs_p, consequence, impact, exon_nr, intron_nr, hgnc_id, gene_symbol, source)

        return status_code, err_msg


    def annotate_consequence(self, input_vcf, output_vcf):
        tmp_vcf = output_vcf + ".tmp"

        # annotate ensembl consequences
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateConsequence")]
        command.extend([ "-gff", paths.ensembl_transcript_path, "-ref", paths.ref_genome_path, "-all",  "-tag", "CSQ_ensembl", "-in", input_vcf, "-out", tmp_vcf])
        returncode, err_msg, vcf_errors = functions.execute_command(command, 'VcfAnnotateConsequenceEnsembl')

        if returncode != 0:
            functions.rm(tmp_vcf)
            return returncode, err_msg, vcf_errors
        

        with open(tmp_vcf, "r") as tmp_file:
            tmp_text = tmp_file.read()
            new_annotation = functions.find_between(tmp_text, "CSQ_ensembl=", '(;|$)')
            if new_annotation is not None and new_annotation == '':
                functions.rm(tmp_vcf)
                os.rename(input_vcf, tmp_vcf)
        
        # annotate refseq consequences
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateConsequence")]
        command.extend([ "-gff", paths.refseq_transcript_4_consequence_path, "-ref", paths.ref_genome_path, "-all",  "-tag", "CSQ_refseq", "-in", tmp_vcf, "-out", output_vcf])
        returncode, err_msg, vcf_errors = functions.execute_command(command, 'VcfAnnotateConsequenceRefSeq')

        with open(output_vcf, "r") as tmp_file:
            tmp_text = tmp_file.read()
            new_annotation = functions.find_between(tmp_text, "CSQ_refseq=", '(;|$)')
            if new_annotation is not None and new_annotation == '':
                functions.rm(output_vcf)
                os.rename(tmp_vcf, output_vcf)
        
        functions.rm(tmp_vcf)

        return returncode, err_msg, vcf_errors


    