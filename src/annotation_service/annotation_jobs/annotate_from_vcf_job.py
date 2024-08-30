
from ._job import Job
import common.paths as paths
import common.functions as functions
import os

from ..pubmed_parser import fetch

## this annotates various information from different vcf files
class annotate_from_vcf_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "vcf annotate from vcf"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []

    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ['do_dbsnp', 'do_revel', 
                                            'do_cadd', 
                                            'do_clinvar', 'do_gnomad', 
                                            'do_brca_exchange', 
                                            'do_flossies',
                                            'do_tp53_database', 'do_priors', 
                                            'do_bayesdel', 'do_cosmic',
                                            'do_cspec_brca_assays'
                                        ]):
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
        variant = self.annotation_data.variant
        variant_id = variant.id

        self.generated_paths.append(annotated_path)
        self.generated_paths.append(annotated_path + "_warnings.txt")

        # annotate the vcf
        config_file_path = self.write_vcf_annoate_config()
        self.generated_paths.append(config_file_path)
        status_code, vcf_annotate_stderr, vcf_annotate_stdout = self.annotate_from_vcf(config_file_path, vcf_path, annotated_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = vcf_annotate_stderr
            return # abort execution

        # check that the annotated vcf is valid
        status_code, err_msg_vcfcheck, vcf_errors = functions.check_vcf(vcf_path)
        if status_code != 0:
            self.status = "error"
            self.err_msg = vcf_errors
            return

        # save to db
        info = self.get_info(annotated_path)
        self.save_to_db(info, variant_id, conn)

        # update state
        self.status = "success"


    def save_to_db(self, info, variant_id, conn):
        recent_annotation_ids = conn.get_recent_annotation_type_ids()

        # dbsnp rs number
        self.insert_external_id(variant_id, info, "dbSNP_RS=", recent_annotation_ids['rsid'], conn)

        # CADD scaled
        self.insert_annotation(variant_id, info, "CADD=", recent_annotation_ids['cadd_scaled'], conn)

        # gnomad
        self.insert_annotation(variant_id, info, "GnomAD_AC=", recent_annotation_ids['gnomad_ac'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_AF=", recent_annotation_ids['gnomad_af'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_hom=", recent_annotation_ids['gnomad_hom'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_hemi=", recent_annotation_ids['gnomad_hemi'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_het=", recent_annotation_ids['gnomad_het'], conn)

        self.insert_annotation(variant_id, info, "GnomAD_AC_NC=", recent_annotation_ids['gnomad_ac_nc'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_AF_NC=", recent_annotation_ids['gnomad_af_nc'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_hom_NC=", recent_annotation_ids['gnomad_hom_nc'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_hemi_NC=", recent_annotation_ids['gnomad_hemi_nc'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_het_NC=", recent_annotation_ids['gnomad_het_nc'], conn)

        self.insert_annotation(variant_id, info, "GnomAD_popmax=", recent_annotation_ids['gnomad_popmax'], conn, value_modifier_function = lambda value : value.upper())
        self.insert_annotation(variant_id, info, "GnomAD_AF_popmax=", recent_annotation_ids['gnomad_popmax_AF'], conn)
        self.insert_annotation(variant_id, info, "GnomADm_AC_hom=", recent_annotation_ids['gnomadm_ac_hom'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_AC_popmax=", recent_annotation_ids['gnomad_popmax_AC'], conn)
        self.insert_annotation(variant_id, info, "faf95_popmax=", recent_annotation_ids['faf95_popmax'], conn)

        # brca exchange
        self.insert_annotation(variant_id, info, "BRCA_exchange_clin_sig_short=", recent_annotation_ids['brca_exchange_clinical_significance'], conn, value_modifier_function = lambda value : value.replace('_', ' ').replace(',', ';'))

        # flossies
        self.insert_annotation(variant_id, info, "FLOSSIES_num_afr=", recent_annotation_ids['flossies_num_afr'], conn)
        self.insert_annotation(variant_id, info, "FLOSSIES_num_eur=", recent_annotation_ids['flossies_num_eur'], conn)

        # priors
        self.insert_annotation(variant_id, info, "HCI_prior=", recent_annotation_ids['hci_prior'], conn)

        # bayesdel
        self.insert_annotation(variant_id, info, "BayesDEL_noAF=", recent_annotation_ids['bayesdel'], conn)

        # cosmic id
        self.insert_multiple_ids(variant_id, info, "COSMIC_COSV=", recent_annotation_ids['cosmic'], conn, sep = '&')

        # REVEL
        revel_scores = functions.find_between(info, "REVEL=", '(;|$)')
        if revel_scores is not None and revel_scores != '':
            revel_scores = revel_scores.split('|')
            for revel_score in revel_scores:
                revel_parts = revel_score.split('&')
                transcripts = revel_parts[1].split('+')
                revel_score = revel_parts[0]
                for transcript in transcripts:
                    conn.insert_variant_transcript_annotation(variant_id, transcript, recent_annotation_ids['revel'], revel_score)

        # TP53 DB
        self.insert_annotation(variant_id, info, "tp53db_class=", recent_annotation_ids['tp53db_class'], conn)
        self.insert_annotation(variant_id, info, "tp53db_DNE_LOF_class=", recent_annotation_ids['tp53db_DNE_LOF_class'], conn)
        self.insert_annotation(variant_id, info, "tp53db_DNE_class=", recent_annotation_ids['tp53db_DNE_class'], conn)
        self.insert_annotation(variant_id, info, "tp53db_domain_function=", recent_annotation_ids['tp53db_domain_function'], conn)
        self.insert_annotation(variant_id, info, "tp53db_transactivation_class=", recent_annotation_ids['tp53db_transactivation_class'], conn)
        pmids = functions.find_between(info, 'tp53db_pubmed=', '(;|$)')
        if pmids is not None and pmids != '':
            literature_entries = fetch(pmids) # defined in pubmed_parser.py
            for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4], "TP53_db")

        # CLINVAR
        clinvar_submissions = functions.find_between(info, 'ClinVar_submissions=', '(;|$)')
        if clinvar_submissions == '' or clinvar_submissions is None:
            clinvar_submissions = []
        else:
            clinvar_submissions = clinvar_submissions.split('&')
        clv_revstat = functions.find_between(info, 'ClinVar_revstat=', '(;|$)')
        clv_varid = functions.find_between(info, 'ClinVar_varid=', '(;|$)')
        self.insert_external_id(variant_id, info, "ClinVar_varid=", recent_annotation_ids['clinvar'], conn)
        clv_inpret = functions.find_between(info, 'ClinVar_inpret=', '(;|$)')

        if clv_revstat is not None and clv_inpret is not None and clv_varid is not None:
            clv_revstat = functions.decode_vcf(clv_revstat)
            clv_inpret = functions.decode_vcf(clv_inpret)

            conn.clean_clinvar(variant_id) # remove all clinvar information of this variant from database and insert it again -> only the most recent clinvar annotaion is saved in database!
            conn.insert_clinvar_variant_annotation(variant_id, clv_varid, clv_inpret, clv_revstat)
            clinvar_variant_annotation_id = conn.get_clinvar_variant_annotation_id_by_variant_id(variant_id)

            for submission in clinvar_submissions:
                #Format of one submission: 0VariationID|1ClinicalSignificance|2LastEvaluated|3ReviewStatus|5SubmittedPhenotypeInfo|7Submitter|8comment
                submissions = submission.split('|')
                submissions = [functions.decode_vcf(s) for s in submissions]
                #submissions = functions.decode_vcf(submission)#.replace('\\', ',').replace('_', ' ').replace(',', ', ').replace('  ', ' ').replace('&', ';').split('|')
                conn.insert_clinvar_submission(clinvar_variant_annotation_id, submissions[1], submissions[2], submissions[3], submissions[4], submissions[5], submissions[6])

        # CSpec assays
        conn.delete_assays(variant_id = variant_id, user_id = None) # delete only automatically annotated assays
        # splicing
        cspec_splicing_assays = functions.find_between(info, "cspec_splicing_assay=", '(;|$)')
        if cspec_splicing_assays == '' or cspec_splicing_assays is None:
            cspec_splicing_assays = []
        else:
            cspec_splicing_assays = cspec_splicing_assays.split('&')
        
        assay_type_id = conn.get_assay_id("splicing")
        assay_metadata_types = conn.get_assay_metadata_types(assay_type_id, format = "dict")
        for assay in cspec_splicing_assays:
            assay_parts = assay.split('|')
            link = assay_parts[5]
            assay_id = conn.insert_assay(variant_id, assay_type_id, report = None, filename = None, link = link, date = functions.get_today(), user_id = None)

            is_patient_rna = self.convert_assay_dat(assay_parts[0]) 
            is_minigene = self.convert_assay_dat(assay_parts[1])
            minimal_percentage = self.convert_assay_dat(assay_parts[2])
            allele_specific = self.convert_assay_dat(assay_parts[3])
            comment = self.convert_assay_dat(assay_parts[4])
            conn.insert_assay_metadata(assay_id, assay_metadata_types["patient_rna"].id, is_patient_rna)
            conn.insert_assay_metadata(assay_id, assay_metadata_types["minigene"].id, is_minigene)
            conn.insert_assay_metadata(assay_id, assay_metadata_types["minimal_percentage"].id, minimal_percentage)
            conn.insert_assay_metadata(assay_id, assay_metadata_types["allele_specific"].id, allele_specific)
            conn.insert_assay_metadata(assay_id, assay_metadata_types["comment"].id, comment)

        # functional
        cspec_functional_assays = functions.find_between(info, "cspec_functional_assay=", "(;|$)")
        if cspec_functional_assays == '' or cspec_functional_assays is None:
            cspec_functional_assays = []
        else:
            cspec_functional_assays = cspec_functional_assays.split('&')
        
        assay_type_id = conn.get_assay_id("functional")
        assay_metadata_types = conn.get_assay_metadata_types(assay_type_id, format = "dict")
        for assay in cspec_functional_assays:
            assay_parts = assay.split('|')
            link = assay_parts[1]
            assay_id = conn.insert_assay(variant_id, assay_type_id, report = None, filename = None, link = link, date = functions.get_today(), user_id = None)

            functional_category = self.convert_assay_dat(assay_parts[0])
            conn.insert_assay_metadata(assay_id, assay_metadata_types["functional_category"].id, functional_category)


    def convert_assay_dat(self, value):
        value = value.strip()
        assay_bool_converter = {"Y": "True", "N": "False", "": None}
        return assay_bool_converter.get(value, value)


    def annotate_from_vcf(self, config_file_path, input_vcf, output_vcf):
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateFromVcf")]
        command.extend([ "-config_file", config_file_path, "-in", input_vcf, "-out", output_vcf])

        returncode, err_msg, vcf_errors = functions.execute_command(command, 'VcfAnnotateFromVcf')

        return returncode, err_msg, vcf_errors


    
    def write_vcf_annoate_config(self):
        variant = self.annotation_data.variant
        job_config = self.annotation_data.job_config

        config_file_path = functions.get_random_temp_file(".conf", filename_ext = "vcf_annoate")
        config_file = open(config_file_path, 'w')

        ## add rs-num from dbsnp
        if job_config['do_dbsnp']:
            config_file.write(paths.dbsnp_path + "\tdbSNP\tRS\t\n")

        ## add revel score
        if job_config['do_revel']:
            config_file.write(paths.revel_path + "\t\tREVEL\t\n")

        ## add cadd precomputed scores
        if variant.is_snv() and job_config['do_cadd']:
            config_file.write(paths.cadd_snvs_path + "\t\tCADD\t\n")
        elif job_config['do_cadd']:
            config_file.write(paths.cadd_indels_path + "\t\tCADD\t\n")

        ## add clinvar annotation
        if job_config['do_clinvar']:
            config_file.write(paths.clinvar_path + "\tClinVar\tinpret,revstat,varid,submissions\t\n")

        ## add gnomAD annotation
        if job_config['do_gnomad']:
            config_file.write(paths.gnomad_path + "\tGnomAD\tAF,AC,hom,hemi,het,AF_NC,AC_NC,hom_NC,hemi_NC,het_NC,popmax,AF_popmax,AC_popmax,faf95_popmax\t\n")
            config_file.write(paths.gnomad_m_path + "\tGnomADm\tAC_hom\t\n")

        ## add BRCA_exchange clinical significance
        if job_config['do_brca_exchange']:
            config_file.write(paths.BRCA_exchange_path + "\tBRCA_exchange\tclin_sig_short\t\n")

        ## add FLOSSIES annotation
        if job_config['do_flossies']:
            config_file.write(paths.FLOSSIES_path + "\tFLOSSIES\tnum_eur,num_afr\t\n")

        ## add TP53 database information
        if job_config['do_tp53_database']:
            config_file.write(paths.tp53_db + "\ttp53db\tclass,transactivation_class,DNE_LOF_class,DNE_class,domain_function,pubmed\t\n")

        ## add priors
        if job_config['do_priors']:
            config_file.write(paths.hci_priors + "\t\tHCI_prior\t\n")

        ## add bayesdel
        if job_config['do_bayesdel']:
            config_file.write(paths.bayesdel + "\t\tBayesDEL_noAF\t\n")

        ## add COSMIC database CMC significance tier
        if job_config['do_cosmic']:
            config_file.write(paths.cosmic + "\t\tCOSMIC_COSV\t\n") # COSMIC_CMC

        ## add cspec brca assays
        if job_config['do_cspec_brca_assays']:
            config_file.write(paths.cspec_brca_assays_functional + "\tcspec\tfunctional_assay\t\n")
            config_file.write(paths.cspec_brca_assays_splicing + "\tcspec\tsplicing_assay\t\n")

        config_file.close()
        return config_file_path

