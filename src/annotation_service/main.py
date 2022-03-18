import sys
import os
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
    #gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF,gnomAD_NFE_AF,gnomAD_SAS_AF, "--af_gnomad",
    fields_oi = "Allele,Consequence,IMPACT,SYMBOL,HGNC_ID,Feature,Feature_type,EXON,INTRON,HGVSc,HGVSp," \
        "DOMAINS,SIFT,PolyPhen,AF,BIOTYPE,PUBMED,MaxEntScan_ref,MaxEntScan_alt"
    #fields_oi = "Allele,MaxEntScan_ref,MaxEntScan_alt"
    command = [paths.vep_path + "/vep",
               "-i", input_vcf, "--format", "vcf",
               "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite",
               "--species", "homo_sapiens", "--assembly", paths.ref_genome_name,
               "--fork", "1",
               "--offline", "--cache", "--dir_cache", "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache",
               "--fasta", paths.ref_genome_path,
               "--numbers", "--hgvs", "--domains", "--transcript_version",
               "--regulatory",
               "--sift", "b", "--polyphen", "b",
               "--af", "--failed", "1",
               "--pubmed",
               "--plugin", "MaxEntScan," + paths.vep_path + "/MaxEntScan/",
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


def annotate_missing_spliceai(input_vcf_path, output_vcf_path):
    input_file = open(input_vcf_path, 'r')
    temp_path = tempfile.gettempdir() + "/spliceai_temp.vcf"
    temp_file = open(temp_path, 'w')

    found_spliceai_header = False
    need_annotation = False
    errors = ''
    execution_code_spliceai = -1
    for line in input_file:
        if line.startswith('#'):
            temp_file.write(line)
            if line.startswith('##INFO=<ID=SpliceAI'):
                found_spliceai_header = True
            continue
        else:
            entries = line.split('\t')
            if len(entries) != 8: 
                errors = collect_error_msgs(errors, "SpliceAI ERROR: not the correct number of entries in input vcf line: " + line)
                continue
            
            if "SpliceAI=" in line:
                continue
            
            need_annotation = True
            temp_file.write(line)
    temp_file.close()
    if not found_spliceai_header:
        errors = collect_error_msgs(errors, "SpliceAI WARNING: did not find a SpliceAI INFO entry in input vcf, did you annotate the file using a precomputed file before?")
    if need_annotation:
        print('executing SpliceAI to annotate new variant...')
        subprocess.run(['sed', '-i', '/SpliceAI/d', temp_path])
        execution_code_spliceai, err_msg_spliceai = annotate_spliceai_algorithm(temp_path, output_vcf_path)
        errors = collect_error_msgs(errors, err_msg_spliceai)

    # need to insert some code here to merge the newly annotated variants and previously 
    # annotated ones from the db if there are files which contain more than one variant! 
    input_file.close()

    return execution_code_spliceai, errors



def annotate_spliceai_algorithm(input_vcf_path, output_vcf_path):
    input_vcf_zipped_path = input_vcf_path + ".gz"
    subprocess.run([paths.ngs_bits_path + "VcfSort", "-in", input_vcf_path, "-out", input_vcf_path])
    subprocess.run(['bgzip', '-f', input_vcf_path])
    subprocess.run(['tabix', "-f", "-p", "vcf", input_vcf_zipped_path])

    command = ['spliceai', '-I', input_vcf_zipped_path, '-O', output_vcf_path, '-R', paths.ref_genome_path, '-A', paths.ref_genome_name.lower()]
    completed_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    std_err = completed_process.communicate()[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    err_msg = ""
    if completed_process.returncode != 0:
        err_msg = "SpliceAI ERROR: " + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        err_msg = "SpliceAI WARNING: " + std_err
    return completed_process.returncode, err_msg




def collect_error_msgs(msg1, msg2):
    if len(msg1) > 0 and len(msg2) > 0:
        res = msg1 + "\n~~\n" + msg2.strip()
    elif len(msg2) > 0:
        res = msg2.strip()
    else:
        res = msg1
    return res


def update_output(not_annotated_file_path, annotated_file_path, error_code):
    if error_code == 0: # execution worked and we want to keep the info
        os.replace(annotated_file_path, not_annotated_file_path)


def is_snv(one_var):
    ref = one_var[3]
    alt = one_var[4]
    if len(ref) > 1 or len(alt) > 1:
        return False
    else:
        return True


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
        variant_annotated_path = temp_file_path + "/variant_annotated.vcf"
        
        ## VEP
        print("executing vep...")
        execution_code_vep, err_msg_vep = annotate_vep(one_variant_path, variant_annotated_path)
        update_output(one_variant_path, variant_annotated_path, execution_code_vep)
        if execution_code_vep != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vep)
                

        ## annotate variant with phylop 100-way conservation scores
        print("annotating phyloP...")
        execution_code_phylop, err_msg_phylop = annotate_phylop(one_variant_path, variant_annotated_path)
        update_output(one_variant_path, variant_annotated_path, execution_code_phylop)
        if execution_code_phylop != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_phylop)


        # create config file for vcfannotatefromvcf
        print("annotating from vcf resources...")
        config_file_path = temp_file_path + "/.config"
        config_file = open(config_file_path, 'w')

        ## add rs-num from dbsnp
        config_file.write(paths.dbsnp_path + "\tdbSNP\tRS\t\n")

        ## add revel score
        config_file.write(paths.revel_path + "\t\tREVEL\t\n")

        ## add spliceai precomputed scores
        config_file.write(paths.spliceai_path + "\t\tSpliceAI\t\n")

        ## add cadd precomputed scores
        if is_snv(one_variant):
            config_file.write(paths.cadd_snvs_path + "\t\tCADD\t\n")
        else:
            config_file.write(paths.cadd_indels_path + "\t\tCADD\t\n")


        ## add gnomAD
        # fetch one_variant from gnomAD database local copy
        # use vcfannotatefromvcf from ngs-bits: one_variant_path, path_to_gnomad.tbi + fields to annotate
        # read the annotated file back in
        # save INFO column to variant_annotation table

        config_file.close()

        ## execute vcfannotatefromvcf
        execution_code_vcf_anno, err_msg_vcf_anno = annotate_from_vcf(config_file_path, one_variant_path, variant_annotated_path)
        update_output(one_variant_path, variant_annotated_path, execution_code_vcf_anno)
        if execution_code_vcf_anno != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vcf_anno)

        print("checking validity of annotated vcf file...")
        execution_code_vcfcheck, err_msg_vcfcheck, vcf_erros = check_vcf(one_variant_path)
        if execution_code_vcfcheck != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vcfcheck)

        print(vcf_erros)


        ## run SpliecAI on the variants which are not contained in the precomputed file
        execution_code_spliceai, err_msg_spliceai = annotate_missing_spliceai(one_variant_path, variant_annotated_path)
        update_output(one_variant_path, variant_annotated_path, execution_code_spliceai)
        if execution_code_spliceai > 0: # execution resulted in an error (we didn't execute spliceai algorithm at -1)
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_spliceai)


        ## Save to database
        print("saving to database...")
        headers, info = functions.read_vcf_info(one_variant_path)
        vep_header_pos = [i for i, s in enumerate(headers) if 'ID=CSQ' in s]

        vep_header_present = False
        if len(vep_header_pos) > 1:
            err_msgs = collect_error_msgs(err_msgs, "VEP DB save WARNING: There were multiple CSQ INFO columns for this variant. Taking the first one.")
        if len(vep_header_pos) == 0:
            err_msgs = collect_error_msgs(err_msgs, "VEP DB save ERROR: There was no CSQ INFO column for this variant. Skipping variant consequences.")
        else:
            vep_header_pos = vep_header_pos[0]
            vep_headers = headers[vep_header_pos]
            vep_headers = vep_headers[vep_headers.find('Format: ')+8:len(vep_headers)-2]
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

            maxentscan_ref_pos = vep_headers.index("MaxEntScan_ref")
            maxentscan_alt_pos = vep_headers.index("MaxEntScan_alt")

            vep_header_present = True

        for vcf_variant_idx in range(len(info)):
            current_info = info[vcf_variant_idx].split(';')

            for entry in current_info:
                # save variant consequence
                if entry.startswith("CSQ=") and vep_header_present: 
                    vep_entries = entry.split(',')
                    transcript_independent_saved = False
                    for vep_entry in vep_entries:
                        vep_entry = vep_entry.split('|')
                        exon_nr = vep_entry[exon_nr_pos]
                        exon_nr = exon_nr[:exon_nr.find('/')] # take only number from number/total
                        intron_nr = vep_entry[intron_nr_pos]
                        intron_nr = intron_nr[:intron_nr.find('/')] # take only number from number/total
                        #conn.insert_variant_consequence(variant_id, 
                        #                                vep_entry[transcript_name_pos], 
                        #                                vep_entry[HGVS_C_pos], 
                        #                                vep_entry[HGVS_P_pos], 
                        #                                vep_entry[consequence_pos], 
                        #                                vep_entry[impact_pos], 
                        #                                exon_nr, 
                        #                                intron_nr, 
                        #                                vep_entry[hgnc_id_pos])
                        if not transcript_independent_saved:
                            transcript_independent_saved = True
                            maxentscan_ref = vep_entry[maxentscan_ref_pos]
                            if maxentscan_ref != '':
                                conn.insert_variant_annotation(variant_id, 9, maxentscan_ref)
                            maxentscan_alt = vep_entry[maxentscan_alt_pos]
                            if maxentscan_alt != '':
                                conn.insert_variant_annotation(variant_id, 10, maxentscan_alt)
                if entry.startswith("PHYLOP="):
                    value = entry[7:]
                    #conn.insert_variant_annotation(variant_id, 4, value)
                if entry.startswith("dbSNP_RS="):
                    value = entry[9:]
                    #conn.insert_variant_annotation(variant_id, 3, value)
                if entry.startswith("REVEL="):
                    value = entry[6:]
                    #conn.insert_variant_annotation(variant_id, 6, value)
                if entry.startswith("SpliceAI="):
                    values = entry[9:]
                    values = values.split('|')
                    #conn.insert_variant_annotation(variant_id, 7, '|'.join(values[2:]))
                    max_delta_score = max(values[2:6])
                    #conn.insert_variant_annotation(variant_id, 8, max_delta_score)
                if entry.startswith("CADD="):
                    value = entry[5:]
                    #conn.insert_variant_annotation(variant_id, 5, value)

        



        print(err_msgs)

        

        #conn.update_annotation_queue(row_id=request_id, status=status, error_msg=err_msgs)
        


    conn.close()
