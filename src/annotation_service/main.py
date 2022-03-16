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
def annotate_vep(input_vcf, output_vcf):
    # Existing_variation
    fields_oi = "Allele,Consequence,IMPACT,SYMBOL,HGNC_ID,Feature,Feature_type,EXON,INTRON,HGVSc,HGVSp," \
        "DOMAINS,SIFT,PolyPhen,AF,gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF," \
        "gnomAD_NFE_AF,gnomAD_SAS_AF,BIOTYPE,PUBMED"
    command = [paths.vep_path,
               "-i", input_vcf, "--format", "vcf",
               "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite",
               "--species", "homo_sapiens", "--assembly", "GRCh38",
               "--fork", "1",
               "--offline", "--cache", "--dir_cache", "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache",
               "--fasta", paths.ref_genome_path,
               "--numbers", "--hgvs", "--domains", "--transcript_version",
               "--regulatory",
               "--sift", "b", "--polyphen", "b",
               "--af", "--af_gnomad", "--failed", "1",
               "--pubmed",
               "--fields", fields_oi]
    completed_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    std_err = completed_process.communicate()[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    err_msg = ""
    if completed_process.returncode != 0:
        err_msg = "VEP ERROR: " + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        err_msg = "VEP WARNING: " + std_err
    return completed_process.returncode, err_msg


def annotate_phylop(input_vcf, output_vcf):
    command = [paths.ngs_bits_path + "VcfAnnotateFromBigWig",
               "-in", input_vcf, "-bw", paths.phylop_file_path,
               "-name", "PHYLOP", "-desc", "PhyloP 100-way conservation scores (Annotation file used: " + paths.phylop_file_path + ", annotated using ngs-bits/VcfAnnotateFromBigWig - mode max)",
               "-mode", "max", 
               "-out", output_vcf]
    completed_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    std_err = completed_process.communicate()[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    err_msg = ""
    if completed_process.returncode != 0:
        err_msg = "PhyloP ERROR: " + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        err_msg = "PhyloP WARNING: " + std_err
    return completed_process.returncode, err_msg


def annotate_from_vcf(config_file, input_vcf, output_vcf):
    command = [paths.ngs_bits_path + "VcfAnnotateFromVcf",
               "-config_file", config_file, "-in", input_vcf, "-out", output_vcf]
    completed_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    std_err = completed_process.communicate()[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    err_msg = ""
    if completed_process.returncode != 0:
        err_msg = "VCFAnnotation ERROR: " + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        err_msg = "VCFAnnotation WARNING: " + std_err
    return completed_process.returncode, err_msg


def check_vcf(path):
    command = [paths.ngs_bits_path + "VcfCheck",
               "-in", path, "-lines", "0", "-ref", paths.ref_genome_path]
    completed_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = completed_process.communicate()#[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    #vcf_errors = completed_process.communicate()[0].strip().decode("utf-8") # catch errors and warnings and convert to str
    std_err = std_err.strip().decode("utf-8")
    vcf_errors = std_out.strip().decode("utf-8")
    err_msg = ""
    if completed_process.returncode != 0:
        err_msg = "CheckVCF runtime ERROR: " + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        err_msg = "CheckVCF runtime WARNING: " + std_err
    return completed_process.returncode, err_msg, vcf_errors



def collect_error_msgs(msg1, msg2):
    if len(msg1) > 0 and len(msg2) > 0:
        res = msg1 + "\n~~\n" + msg2.strip()
    elif len(msg2) > 0:
        res = msg2.strip()
    else:
        res = msg1
    return res


if __name__ == '__main__':
    pending_requests = conn.get_pending_requests()

    temp_file_path = tempfile.gettempdir()
    # print(temp_file_path)
    one_variant_path = temp_file_path + "/variant.vcf"

    status = "success"

    for request_id, variant_id in pending_requests:
        err_msgs = ""
        one_variant = conn.get_one_variant(variant_id)
        print("processing request " + str(one_variant[0]) + " annotating variant: " + " ".join([str(x) for x in one_variant[1:5]]))

        functions.variant_to_vcf(one_variant, one_variant_path)

        ## VEP
        variant_annotated_path = temp_file_path + "/variant_annotated.vcf"
        execution_code_vep, err_msg_vep = annotate_vep(one_variant_path, variant_annotated_path)

        if execution_code_vep != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vep)
                

        ## annotate variant with phylop 100-way conservation scores
        #execution_code_phylop, err_msg_phylop = annotate_phylop(one_variant_path, output_path)
        #if execution_code_phylop != 0:
        #    status = "error"
        #err_msgs = collect_error_msgs(err_msgs, err_msg_phylop)


        # create config file for vcfannotatefromvcf
        config_file_path = temp_file_path + "/.config"
        config_file = open(config_file_path, 'w')

        ## add rs-num from dbsnp
        config_file.write(paths.dbsnp_path + "\tdbSNP\tRS\t\n")

        ## add gnomAD
        # fetch one_variant from gnomAD database local copy
        # use vcfannotatefromvcf from ngs-bits: one_variant_path, path_to_gnomad.tbi + fields to annotate
        # read the annotated file back in
        # save INFO column to variant_annotation table

        config_file.close()

        ## execute vcfannotatefromvcf
        variant_annotated_path_2 = temp_file_path + "/variant_annotated_2.vcf"
        execution_code_vcf_anno, err_msg_vcf_anno = annotate_from_vcf(config_file_path, variant_annotated_path, variant_annotated_path_2)
        if execution_code_vcf_anno != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vcf_anno)

        
        execution_code_vcfcheck, err_msg_vcfcheck, vcf_erros = check_vcf(variant_annotated_path_2)
        if execution_code_vcfcheck != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vcfcheck)

        print(vcf_erros)


        ## Save Variant Consequence to database
        headers, info = functions.read_vcf_info(variant_annotated_path_2)
        vep_header_pos = [i for i, s in enumerate(headers) if 'ID=CSQ' in s]
        if len(vep_header_pos) > 1:
            err_msgs = collect_error_msgs(err_msgs, "VEP DB save WARNING: There were multiple CSQ INFO columns for this variant. Taking the first one.")
        if len(vep_header_pos) == 0:
            err_msgs = collect_error_msgs(err_msgs, "VEP DB save ERROR: There was no CSQ INFO column for this variant. Skipping variant consequences.")
        else:
            vep_header_pos = vep_header_pos[0]
            vep_headers = headers[vep_header_pos]
            vep_headers = vep_headers[vep_headers.find('Format: ')+8:]
            vep_headers = vep_headers.split('|')
            num_fields = len(vep_headers)

            transcript_name_pos = vep_headers.index("Feature")
            HGVS_C_pos = vep_headers.index("HGVSc")
            HGVS_P_pos = vep_headers.index("HGVSp")
            consequence_pos = vep_headers.index("Consequence")
            impact_pos = vep_headers.index("IMPACT")
            exon_nr_pos = vep_headers.index("EXON") 
            intron_nr_pos = vep_headers.index("INTRON") 
            hgnc_id_pos = vep_headers.index("HGNC_ID")

            for vcf_variant_idx in range(len(info)):
                current_info = info[vcf_variant_idx].split(';')

                for entry in current_info:
                    if entry.startswith("CSQ="):
                        vep_entries = entry.split(',')
                        for vep_entry in vep_entries:
                            vep_entry = vep_entry.split('|')
                            exon_nr = vep_entry[exon_nr_pos]
                            exon_nr = exon_nr[:exon_nr.find('/')] # take only number from number/total
                            intron_nr = vep_entry[intron_nr_pos]
                            intron_nr = intron_nr[:intron_nr.find('/')] # take only number from number/total
                            conn.insert_variant_consequence(variant_id, 
                                                            vep_entry[transcript_name_pos], 
                                                            vep_entry[HGVS_C_pos], 
                                                            vep_entry[HGVS_P_pos], 
                                                            vep_entry[consequence_pos], 
                                                            vep_entry[impact_pos], 
                                                            exon_nr, 
                                                            intron_nr, 
                                                            vep_entry[hgnc_id_pos])
        ## save dbsnp rsid to database




            print(err_msgs)

        

    #conn.update_annotation_queue(row_id=request_id, status=status, error_msg=err_msgs)
        


    conn.close()
