import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import subprocess
import paths
import tempfile

conn = Connection()

#"/mnt/storage2/GRCh38/share/data/genomes/GRCh38.fa"
def start_vep(input_vcf, output_vcf):
    fields_oi = "Allele,Consequence,IMPACT,SYMBOL,HGNC_ID,Feature,Feature_type,EXON,INTRON,HGVSc,HGVSp," \
        "DOMAINS,SIFT,PolyPhen,Existing_variation,AF,gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF," \
        "gnomAD_NFE_AF,gnomAD_SAS_AF,BIOTYPE,PUBMED"
    command = [paths.vep_path,
               "-i", input_vcf, "--format", "vcf",
               "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite",
               "--species", "homo_sapiens", "--assembly", "GRCh38",
               "--fork", "1",
               "--offline", "--cache", "--dir_cache", "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache",
               "--fasta", "data/genomes/GRCh38.fa",
               "--numbers", "--hgvs", "--domains", "--transcript_version",
               "--regulatory",
               "--sift", "b", "--polyphen", "b",
               "--af", "--af_gnomad", "--failed", "1",
               "--pubmed",
               "--fields", fields_oi]
    completed_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    std_err = completed_process.communicate()[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    if completed_process.returncode != 0:
        err_msg = "VEP ERROR: " + std_err + " Code: " + completed_process.returncode
    elif len(std_err):
        err_msg = "VEP WARNING: " + std_err
    return completed_process.returncode, err_msg


def collect_error_msgs(msg1, msg2):
    if len(msg2):
        res = msg1 + "\n~~\n" + msg2
    else:
        res = msg1
    return res


if __name__ == '__main__':
    pending_requests = conn.get_pending_requests()

    temp_file_path = tempfile.gettempdir()
    # print(temp_file_path)
    one_variant_path = temp_file_path + "/variant_temp.vcf"

    status = "success"

    for request_id, variant_id in pending_requests:
        err_msgs = ""
        one_variant = conn.get_one_variant(variant_id)
        functions.variant_to_vcf(one_variant, one_variant_path)

        ## VEP
        output_path = temp_file_path + "/variant_vep.vcf"
        execution_code_vep, err_msg_vep = start_vep(one_variant_path, output_path)

        if execution_code_vep != 0:
            status = "error"
            
        err_msgs = collect_error_msgs(err_msgs, err_msg_vep)
        
        ## Save Variant Consequence to database
        headers, vep_info = functions.read_vcf_info(output_path)

        vep_info = vep_info[0].split(',')
        headers = headers[0]
        headers = headers[headers.find('Format: ')+8:]
        headers = headers.split('|')

        num_fields = len(headers)
        
        transcript_name_pos = headers.index("Feature")
        HGVS_C_pos = headers.index("HGVSc")
        HGVS_P_pos = headers.index("HGVSp")
        consequence_pos = headers.index("Consequence")
        impact_pos = headers.index("IMPACT")
        exon_nr_pos = headers.index("EXON") 
        intron_nr_pos = headers.index("INTRON") 
        hgnc_id_pos = headers.index("HGNC_ID")

        for entry in vep_info:
            entry = entry.split('|')
            exon_nr = entry[exon_nr_pos]
            exon_nr = exon_nr[:exon_nr.find('/')] # take only number from number/total
            intron_nr = entry[intron_nr_pos]
            intron_nr = intron_nr[:intron_nr.find('/')] # take only number from number/total
            #conn.insert_variant_consequence(variant_id, entry[transcript_name_pos], entry[HGVS_C_pos], entry[HGVS_P_pos], entry[consequence_pos], entry[impact_pos], exon_nr, intron_nr, entry[hgnc_id_pos])
        

        ## extract rsid from VEP
        ids_pos = headers.index('Existing_variation')
        rsid = None
        rsid_error_msg = ""

        for entry in vep_info:
            entry = entry.split('|')
            ids = entry[ids_pos]
            
            if len(ids) > 0:
                ids = ids.split('&')
                if rsid is None:
                    rsid = ids[0]
                elif rsid != ids[0]:
                    rsid_error_msg = "RSID warning: multiple dbSNP rsids for one variant."
        
        conn.insert_variant_annotation(variant_id, 3, rsid)




        ## gnomAD

        # fetch one_variant from gnomAD database local copy
        # use vcfannotatefromvcf from ngs-bits: one_variant_path, path_to_gnomad.tbi + fields to annotate
        # read the annotated file back in
        # save INFO column to variant_annotation table

        





        

        #conn.update_annotation_queue(row_id=request_id, status=status, error_msg=err_msgs)


    conn.close()
