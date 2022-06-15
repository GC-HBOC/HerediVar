from hmac import trans_36
import sys
import os
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.functions as functions
import subprocess
import common.paths as paths
import tempfile
import re
import pubmed_parser
import fetch_heredicare_variants as heredicare
import datetime

## switches
# external programs
do_phylop = True
do_spliceai = True
do_hexplorer = True

# vep dependent
do_vep = True
insert_consequence = True
insert_maxent = True
insert_literature = True

#vcf annotate from vcf
do_dbsnp = True
do_revel = True
do_cadd = True
do_clinvar = True
do_gnomad = True
do_brca_exchange = True
do_flossies = True
do_cancerhotspots = True
do_arup = True
do_tp53_database = True



conn = Connection()

#"/mnt/storage2/GRCh38/share/data/genomes/GRCh38.fa"
def annotate_vep(input_vcf, output_vcf, refseq = False):
    fields_oi_base = "Feature,HGVSc,HGVSp,Consequence,IMPACT,EXON,INTRON,HGNC_ID,SYMBOL,DOMAINS"
    command = [paths.vep_path + "/vep",
               "-i", input_vcf, "--format", "vcf",
               "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite",
               "--species", "homo_sapiens", "--assembly", paths.ref_genome_name,
               "--fork", "1",
               "--offline", "--cache", "--dir_cache", "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache", "--fasta", paths.ref_genome_path,
               "--numbers", "--hgvs", "--symbol", "--domains", #"--transcript_version",
               "--failed", "1",
               #"--sift", "b", "--polyphen", "b", "--af","--pubmed"
               ]

    if not refseq:
        #use ensembl
        #gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF,gnomAD_NFE_AF,gnomAD_SAS_AF, "--af_gnomad",
        #DOMAINS,SIFT,PolyPhen,PUBMED,AF
        
        fields_oi = fields_oi_base + ",MaxEntScan_ref,MaxEntScan_alt,PUBMED"
        command = command + ["--plugin", "MaxEntScan," + paths.vep_path + "/MaxEntScan/",
                             "--regulatory",
                             "--pubmed",
                             "--fields", fields_oi]
        
    if refseq:
        fields_oi = fields_oi_base
        command = command + ["--refseq",
                             "--vcf_info_field", "CSQ_refseq",
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


def annotate_hexplorer(input_vcf_path, output_vcf_path):
    command = [paths.ngs_bits_path + "Hexplorer", "-vcf", "-in", input_vcf_path, "-out", output_vcf_path]
    returncode, err_msg, command_output = functions.execute_command(command, process_name = "hexplorer")
    return returncode, err_msg




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
        one_variant = conn.get_one_variant(variant_id) # 0id,1chr,2pos,3ref,4alt
        print("processing request " + str(one_variant[0]) + " annotating variant: " + " ".join([str(x) for x in one_variant[1:5]]))

        vids = conn.get_external_ids_from_variant_id(variant_id, id_source='heredicare')
        #log_file_date = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        log_file_path = path.join(path.dirname(path.abspath(__file__)),  'logs/heredicare_update.log')
        heredicare.update_specific_vids(log_file_path, vids)
        #look for error code: s1 (deleted variant)
        log_file = open(log_file_path, 'r')
        deleted_variant = False
        for line in log_file:
            if '~~s1~~' in line:
                deleted_variant = True
        log_file.close()
        if deleted_variant:
            continue # stop annotation if it was deleted!


        functions.variant_to_vcf(one_variant[1], one_variant[2], one_variant[3], one_variant[4], one_variant_path)
        variant_annotated_path = temp_file_path + "/variant_annotated.vcf"
        
        ## VEP
        if do_vep:
            print("executing vep...")
            execution_code_vep, err_msg_vep = annotate_vep(one_variant_path, variant_annotated_path, refseq=False)
            update_output(one_variant_path, variant_annotated_path, execution_code_vep)
            if execution_code_vep != 0:
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, err_msg_vep)

            execution_code_vep_refseq, err_msg_vep_refseq = annotate_vep(one_variant_path, variant_annotated_path, refseq=True)
            update_output(one_variant_path, variant_annotated_path, execution_code_vep_refseq)
            if execution_code_vep_refseq != 0:
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, err_msg_vep_refseq)

        ## annotate variant with phylop 100-way conservation scores
        if do_phylop:
            print("annotating phyloP...")
            execution_code_phylop, err_msg_phylop = annotate_phylop(one_variant_path, variant_annotated_path)
            update_output(one_variant_path, variant_annotated_path, execution_code_phylop)
            if execution_code_phylop != 0:
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, err_msg_phylop)
        
        ## annotate variant with hexplorer splicing scores (Hexplorer score + HBond score)
        if do_hexplorer:
            print("annotation hexplorer scores...")
            execution_code_hexplorer, err_msg_hexplorer = annotate_hexplorer(one_variant_path, variant_annotated_path)
            update_output(one_variant_path, variant_annotated_path, execution_code_hexplorer)
            if execution_code_hexplorer != 0:
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, err_msg_hexplorer)

        # create config file for vcfannotatefromvcf
        print("annotating from vcf resources...")
        config_file_path = temp_file_path + "/.config"
        config_file = open(config_file_path, 'w')

        ## add rs-num from dbsnp
        if do_dbsnp:
            config_file.write(paths.dbsnp_path + "\tdbSNP\tRS\t\n")

        ## add revel score
        if do_revel:
            config_file.write(paths.revel_path + "\t\tREVEL\t\n")

        ## add spliceai precomputed scores
        if do_spliceai:
            config_file.write(paths.spliceai_path + "\t\tSpliceAI\t\n")

        ## add cadd precomputed scores
        if is_snv(one_variant) and do_cadd:
            config_file.write(paths.cadd_snvs_path + "\t\tCADD\t\n")
        elif do_cadd:
            config_file.write(paths.cadd_indels_path + "\t\tCADD\t\n")

        ## add clinvar annotation
        if do_clinvar:
            config_file.write(paths.clinvar_path + "\tClinVar\tinpret,revstat,varid,submissions\t\n")

        ## add gnomAD annotation
        if do_gnomad:
            config_file.write(paths.gnomad_path + "\tGnomAD\tAF,AC,hom,hemi,het,popmax\t\n")
            config_file.write(paths.gnomad_m_path + "\tGnomADm\tAC_hom\t\n")

        ## add BRCA_exchange clinical significance
        if do_brca_exchange:
            config_file.write(paths.BRCA_exchange_path + "\tBRCA_exchange\tclin_sig_short\t\n")

        ## add FLOSSIES annotation
        if do_flossies:
            config_file.write(paths.FLOSSIES_path + "\tFLOSSIES\tnum_eur,num_afr\t\n")

        ## add cancerhotspots annotations
        if do_cancerhotspots:
            config_file.write(paths.cancerhotspots_path + "\tcancerhotspots\tcancertypes,AC,AF\t\n")

        ## add arup brca classification
        if do_arup:
            config_file.write(paths.arup_brca_path + "\tARUP\tclassification\t\n")

        ## add TP53 database information
        if do_tp53_database:
            config_file.write(paths.tp53_db + "\ttp53db\tclass,bayes_del,transactivation_class,DNE_LOF_class,DNE_class,domain_function,pubmed\t")

        config_file.close()

        ## execute vcfannotatefromvcf
        if do_dbsnp or do_revel or do_spliceai or do_cadd or do_clinvar or do_gnomad or do_brca_exchange or do_flossies or do_cancerhotspots or do_arup or do_tp53_database:
            execution_code_vcf_anno, err_msg_vcf_anno = annotate_from_vcf(config_file_path, one_variant_path, variant_annotated_path)
            update_output(one_variant_path, variant_annotated_path, execution_code_vcf_anno)
            if execution_code_vcf_anno != 0:
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, err_msg_vcf_anno)

        print("checking validity of annotated vcf file...")
        execution_code_vcfcheck, err_msg_vcfcheck, vcf_errors = functions.check_vcf(one_variant_path)
        print(vcf_errors)
        if execution_code_vcfcheck != 0:
            status = "error"
        err_msgs = collect_error_msgs(err_msgs, err_msg_vcfcheck)

        ## run SpliecAI on the variants which are not contained in the precomputed file
        if do_spliceai:
            execution_code_spliceai, err_msg_spliceai = annotate_missing_spliceai(one_variant_path, variant_annotated_path)
            update_output(one_variant_path, variant_annotated_path, execution_code_spliceai)
            if execution_code_spliceai > 0: # execution resulted in an error (we didn't execute spliceai algorithm at -1)
                status = "error"
            err_msgs = collect_error_msgs(err_msgs, err_msg_spliceai)


        ## Save to database
        print("saving to database...")
        #one_variant_path = "/tmp/variant_old_pfam.vcf"
        headers, info = functions.read_vcf_info(one_variant_path)

        clv_revstat = ''
        clv_inpret = ''
        clv_varid = ''
        clinvar_submissions = []
        pmids = ''
        for vcf_variant_idx in range(len(info)):
            current_info = info[vcf_variant_idx].split(';')

            for entry in current_info:
                entry = entry.strip()
                # save variant consequences from ensembl and refseq
                # !!!! format of refseq and ensembl annotations from vep need to be equal: 0Feature,1HGVSc,2HGVSp,3Consequence,4IMPACT,5EXON,6INTRON,7HGNC_ID,8SYMBOL,9DOMAIN,...additional info
                if entry.startswith("CSQ=") or entry.startswith("CSQ_refseq="):
                    consequence_source = ''
                    if entry.startswith("CSQ="):
                        consequence_source = "ensembl"
                    elif entry.startswith("CSQ_refseq="):
                        consequence_source = "refseq"
                    vep_entries = entry.lstrip('CSQ').lstrip('_refseq').lstrip('=').split(',')
                    transcript_independent_saved = False
                    for vep_entry in vep_entries:
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
                            pfam_acc = re.search('Pfam:(PF\d+)[&|]', domains).group(1) # grab only pfam accession id from all protein domains which were returned
                            if domains.count("Pfam:") > 1:
                                print("WARNING: there were multiple PFAM domain ids in: " + str(domains) + ". defaulting to the first one.")
                        if insert_consequence:
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
                            if maxentscan_ref != '' and insert_maxent:
                                conn.insert_variant_annotation(variant_id, 9, maxentscan_ref)
                            maxentscan_alt = vep_entry[num_vep_basic_entries+1]
                            if maxentscan_alt != '' and insert_maxent:
                                conn.insert_variant_annotation(variant_id, 10, maxentscan_alt)
                            pmids = functions.collect_info(pmids, '', vep_entry[num_vep_basic_entries+2].replace('&', ','), sep = ',')
                elif entry.startswith("ClinVar_submissions="):
                    clinvar_submissions = entry[20:].split(',')
                elif entry.startswith("ClinVar_revstat="):
                    clv_revstat = entry[16:].replace('\\', ',').replace('_', ' ')
                elif entry.startswith("ClinVar_varid="):
                    clv_varid = entry[14:]
                elif entry.startswith("ClinVar_inpret="):
                    clv_inpret = entry[15:].replace('\\', ',').replace('_', ' ')
                elif entry.startswith("PHYLOP="):
                    value = entry[7:]
                    conn.insert_variant_annotation(variant_id, 4, value)
                elif entry.startswith("dbSNP_RS="):
                    value = entry[9:]
                    conn.insert_variant_annotation(variant_id, 3, value)
                elif entry.startswith("REVEL="):
                    value = entry[6:]
                    conn.insert_variant_annotation(variant_id, 6, value)
                elif entry.startswith("SpliceAI="):
                    values = entry[9:]
                    values = values.split('|')
                    conn.insert_variant_annotation(variant_id, 7, '|'.join(values[2:]))
                    max_delta_score = max(values[2:6])
                    conn.insert_variant_annotation(variant_id, 8, max_delta_score)
                elif entry.startswith("CADD="):
                    value = entry[5:]
                    conn.insert_variant_annotation(variant_id, 5, value)
                elif entry.startswith("GnomAD_AC="):
                    value = entry[10:]
                    conn.insert_variant_annotation(variant_id, 11, value)
                elif entry.startswith("GnomAD_AF="):
                    value = entry[10:]
                    conn.insert_variant_annotation(variant_id, 12, value)
                elif entry.startswith("GnomAD_hom="):
                    value = entry[11:]
                    conn.insert_variant_annotation(variant_id, 13, value)
                elif entry.startswith("GnomAD_hemi="):
                    value = entry[12:]
                    conn.insert_variant_annotation(variant_id, 14, value)
                elif entry.startswith("GnomAD_het="):
                    value = entry[11:]
                    conn.insert_variant_annotation(variant_id, 15, value)
                elif entry.startswith("GnomAD_popmax="):
                    value = entry[14:]
                    conn.insert_variant_annotation(variant_id, 16, value)
                elif entry.startswith("GnomADm_AC_hom="):
                    value = entry[15:]
                    conn.insert_variant_annotation(variant_id, 17, value)
                elif entry.startswith("BRCA_exchange_clin_sig_short="):
                    value = entry[29:].replace('_', ' ').replace(',', ';')
                    conn.insert_variant_annotation(variant_id, 18, value)
                elif entry.startswith("FLOSSIES_num_afr="):
                    value = entry[17:]
                    conn.insert_variant_annotation(variant_id, 19, value)
                elif entry.startswith("FLOSSIES_num_eur="):
                    value = entry[17:]
                    conn.insert_variant_annotation(variant_id, 20, value)
                elif entry.startswith("cancerhotspots_cancertypes="):
                    value = entry[27:]
                    conn.insert_variant_annotation(variant_id, 22, value)
                elif entry.startswith("cancerhotspots_AC="):
                    value = entry[18:]
                    conn.insert_variant_annotation(variant_id, 23, value)
                elif entry.startswith("cancerhotspots_AF="):
                    value = entry[18:]
                    conn.insert_variant_annotation(variant_id, 24, value)
                elif entry.startswith("ARUP_classification="):
                    value = entry[20:]
                    conn.insert_variant_annotation(variant_id, 21, value)
                elif entry.startswith("tp53db_class="):
                    value = entry[13:]
                    conn.insert_variant_annotation(variant_id, 27, value)
                elif entry.startswith("tp53db_bayes_del="):
                    value = entry[17:]
                    conn.insert_variant_annotation(variant_id, 30, value)
                elif entry.startswith("tp53db_DNE_LOF_class="):
                    value = entry[21:]
                    conn.insert_variant_annotation(variant_id, 29, value)
                elif entry.startswith("tp53db_DNE_class="):
                    value = entry[17:]
                    conn.insert_variant_annotation(variant_id, 31, value)
                elif entry.startswith("tp53db_domain_function="):
                    value = entry[23:]
                    conn.insert_variant_annotation(variant_id, 32, value)
                elif entry.startswith("tp53db_transactivation_class="):
                    value = entry[29:]
                    conn.insert_variant_annotation(variant_id, 33, value)
                elif entry.startswith("tp53db_pubmed="):
                    pmids = functions.collect_info(pmids, '', entry[14:].replace('&', ','), sep = ',')


            # submit collected clinvar data to db if it exists
            if clv_varid != '' and clv_inpret != '' and clv_revstat != '':
                conn.clean_clinvar(variant_id) # remove all clinvar information of this variant from database and insert it again -> only the most recent clinvar annotaion is saved in database!
                conn.insert_clinvar_variant_annotation(variant_id, clv_varid, clv_inpret, clv_revstat)
                clinvar_variant_annotation_id = conn.get_clinvar_variant_annotation_id_by_variant_id(variant_id)
                if clinvar_variant_annotation_id is None:
                    err_msgs = collect_error_msgs(err_msgs, "CLINVAR_VARIANT_ANNOTATION ERROR: no variant annotation ids for variant " + str(variant_id))
                else:
                    for submission in clinvar_submissions:
                        #Format of one submission: 0VariationID|1ClinicalSignificance|2LastEvaluated|3ReviewStatus|5SubmittedPhenotypeInfo|7Submitter|8comment
                        submissions = submission.replace('\\', ',').replace('_', ' ').replace(',', ', ').replace('  ', ' ').split('|')
                        conn.insert_clinvar_submission(clinvar_variant_annotation_id, submissions[1], submissions[2], submissions[3], submissions[4], submissions[5], submissions[6])
            
            if pmids != '' and insert_literature:
                literature_entries = pubmed_parser.fetch(pmids)
                for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                    conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4])
        

        print(err_msgs)

        

        #conn.update_annotation_queue(row_id=request_id, status=status, error_msg=err_msgs)
        


    conn.close()
