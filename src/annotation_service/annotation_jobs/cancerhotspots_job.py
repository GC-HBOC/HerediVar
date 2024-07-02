
from ._job import Job
from .consequence_job import consequence_job
import common.paths as paths
import common.functions as functions
from common.db_IO import Connection
import tempfile
import os
import re

## this annotates various information from different vcf files
class cancerhotspots_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "cancerhotspots"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []


    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ["do_cancerhotspots"]):
            result = False
            self.status = "skipped"

        queue = kwargs['queue']
        self.require_job(consequence_job(None), queue)
        return result


    def execute(self, conn: Connection):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        variant_id = self.annotation_data.variant.id
        # pull variant again from database to get its consequences -> THEY HAVE TO BE ANNOTATED FIRST!
        variant = conn.get_variant(variant_id, include_consequences=True, include_annotations = False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications=False, include_automatic_classification=False, include_clinvar=False, include_assays = False, include_literature = False, include_external_ids = False)
    
        # execute the annotation
        status_code, err_msg, result = self.annotate_cancerhotspots(variant)
        if status_code > 1: # 0: match, 1: no match, 2: trouble
            self.status = "error"
            self.err_msg = err_msg
            return # abort execution

        # save to db
        if status_code == 0:
            self.save_to_db(result, variant_id, conn)
    
        # update state
        self.status = "success"




    def annotate_cancerhotspots(self, variant):
        status_code = 0
        err_msg = ""
        result = ""

        consequences = variant.get_sorted_consequences()

        if consequences is None:
            err_msg = "Skipping cancerhotspots annotation because there are no consequences"
            return status_code, err_msg, result# abort if no consequences
        
        # get cancerhotspots barcodes: transcript_name-amino_acid_position-reference_amino_acid-alternative_amino_acid
        # amino acids are in one letter code
        all_barcodes = []
        for consequence in consequences:
            gene_name = consequence.transcript.gene.symbol
            hgvs_p = consequence.hgvs_p

            if not self.hgvs_p_useful(hgvs_p):
                continue

            cancerhotspots_barcode = self.get_cancerhotspots_barcode(gene_name, hgvs_p)
            all_barcodes.append(cancerhotspots_barcode)
        
        for barcode in all_barcodes:
            status_code, err_msg, result = functions.grep(barcode, paths.cancerhotspots_path)
            result = result.strip()
            if status_code == 0: # greedily take the first one
                break

        return status_code, err_msg, result
            

    def get_cancerhotspots_barcode(self, gene_name, hgvs_p):
        # remove p. prefix
        hgvs_p = hgvs_p[2:]
        # split between numbers and letters
        parts = re.split(r'(\d+)',hgvs_p)
        ref_aa = functions.three_to_one_letter(parts[0])
        aa_pos = parts[1]
        alt_aa = functions.three_to_one_letter(parts[2])
        return '-'.join([gene_name, aa_pos, ref_aa, alt_aa])




    def hgvs_p_useful(self, hgvs_p):
        if hgvs_p is None:
            return False
        
        #example: p.Lys7Met
        pattern = re.compile(r"p\.[a-zA-Z]+\d+[a-zA-Z]+")
        result = pattern.match(hgvs_p)
        if result is None:
            return False
        
        return True







    def save_to_db(self, result, variant_id, conn):
        if result is None or len(result) == 0:
            return

        recent_annotation_ids = conn.get_recent_annotation_type_ids()

        parts = result.split('\t')
        cancerhotspots = parts[1].strip()
        ac = parts[2].strip()
        af = parts[3].strip()

        if cancerhotspots is not None and cancerhotspots != '':
            cancerhotspots = cancerhotspots.split('|')
            for cancerhotspot in cancerhotspots:
                cancerhotspot_parts = cancerhotspot.split(':')
                oncotree_symbol = functions.decode_vcf(cancerhotspot_parts[0])
                cancertype = functions.decode_vcf(cancerhotspot_parts[1])
                tissue = functions.decode_vcf(cancerhotspot_parts[2])
                occurances = functions.decode_vcf(cancerhotspot_parts[3])
                conn.insert_cancerhotspots_annotation(variant_id, recent_annotation_ids['cancerhotspots'], oncotree_symbol, cancertype, tissue, occurances)

        conn.insert_variant_annotation(variant_id, recent_annotation_ids['cancerhotspots_ac'], ac)
        conn.insert_variant_annotation(variant_id, recent_annotation_ids['cancerhotspots_af'], af)







