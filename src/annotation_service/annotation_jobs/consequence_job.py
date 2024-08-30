
from ._job import Job
import common.paths as paths
import common.functions as functions
import os
import urllib


## this annotates various information from different vcf files
class consequence_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "annotate consequence"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []

    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ['do_consequence']):
            result = False
            self.status = "skipped"
        return result
    

    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        vcf_path = self.annotation_data.vcf_path
        annotated_path = vcf_path + ".ann.consequence"
        variant_id = self.annotation_data.variant.id

        self.generated_paths.append(annotated_path)
    
        # execute the annotation
        status_code, vcf_annotate_stderr, vcf_annotate_stdout = self.annotate_consequence(vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = "VcfAnnotateConsequence error: " + vcf_annotate_stderr
            return # abort execution
        
        # save to db
        info = self.get_info(annotated_path)
        self.save_to_db(info, variant_id, conn)
    
        # update state
        self.status = "success"


    def save_to_db(self, info, variant_id, conn):
        err_msg = ""
        status_code = 0

        info_field_prefix = "CSQ_"
        sources = ['ensembl', 'refseq']

        conn.delete_variant_consequences(variant_id)

        #FORMAT: Allele|Consequence|IMPACT|SYMBOL|HGNC_ID|Feature|Feature_type|EXON|INTRON|HGVSc|HGVSp
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
        

        reset_file = False
        with open(tmp_vcf, "r") as tmp_file:
            tmp_text = tmp_file.read()
            new_annotation = functions.find_between(tmp_text, "CSQ_ensembl=", '(;|$)')
            if new_annotation is not None and new_annotation == '': # this special case is needed because vcf check does not like if the info tag is there but there is not content
                reset_file = True
                functions.rm(tmp_vcf)
        if reset_file:
            with open(input_vcf, 'r') as input_file:
                with open(tmp_vcf, 'w') as tmp_file:
                    for line in input_file:
                        tmp_file.write(line)
        
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

