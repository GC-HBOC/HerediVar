
from ._job import Job
import common.paths as paths
import common.functions as functions
import tempfile
import os
from os.path import exists

from ..pubmed_parser import fetch

## this annotates various information from different vcf files
class annotate_from_vcf_job(Job):
    def __init__(self, job_config):
        self.job_name = "vcf annotate from vcf"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not any(self.job_config[x] for x in ['do_dbsnp', 'do_revel', 
                                                'do_spliceai', 'do_cadd', 
                                                'do_clinvar', 'do_gnomad', 
                                                'do_brca_exchange', 
                                                'do_flossies', 
                                                'do_cancerhotspots', 
                                                'do_arup', 'do_tp53_database']):
            return 0, '', ''

        self.print_executing()


        config_file_path = self.write_vcf_annoate_config(one_variant = kwargs['one_variant'])
        vcf_annotate_code, vcf_annotate_stderr, vcf_annotate_stdout = self.annotate_from_vcf(config_file_path, inpath, annotated_inpath)




        self.handle_result(inpath, annotated_inpath, vcf_annotate_code)

        warnings_path = annotated_inpath + "_warnings.txt"
        #if exists(warnings_path):
        #    os.remove(warnings_path)

        return vcf_annotate_code, vcf_annotate_stderr, vcf_annotate_stdout



    def save_to_db(self, info, variant_id, conn):
        self.insert_annotation(variant_id, info, "dbSNP_RS=", 3, conn)

        self.insert_annotation(variant_id, info, "REVEL=", 6, conn)

        self.insert_annotation(variant_id, info, "CADD=", 5, conn)

        self.insert_annotation(variant_id, info, "GnomAD_AC=", 11, conn)
        self.insert_annotation(variant_id, info, "GnomAD_AF=", 12, conn)
        self.insert_annotation(variant_id, info, "GnomAD_hom=", 13, conn)
        self.insert_annotation(variant_id, info, "GnomAD_hemi=", 14, conn)
        self.insert_annotation(variant_id, info, "GnomAD_het=", 15, conn)
        self.insert_annotation(variant_id, info, "GnomAD_popmax=", 16, conn)
        self.insert_annotation(variant_id, info, "GnomAD_AF_popmax=", 51, conn)
        self.insert_annotation(variant_id, info, "GnomADm_AC_hom=", 17, conn)

        self.insert_annotation(variant_id, info, "BRCA_exchange_clin_sig_short=", 18, conn, value_modifier_function = lambda value : value.replace('_', ' ').replace(',', ';'))

        self.insert_annotation(variant_id, info, "FLOSSIES_num_afr=", 19, conn)
        self.insert_annotation(variant_id, info, "FLOSSIES_num_eur=", 20, conn)

        self.insert_annotation(variant_id, info, "cancerhotspots_cancertypes=", 22, conn)
        self.insert_annotation(variant_id, info, "cancerhotspots_AC=", 23, conn)
        self.insert_annotation(variant_id, info, "cancerhotspots_AF=", 24, conn)

        self.insert_annotation(variant_id, info, "ARUP_classification=", 21, conn)

        # spliceai is saved to the database in the dedicated spliceai job (which must be called after this job anyway)
        #self.insert_annotation(variant_id, info, 'SpliceAI=', 7, conn, value_modifier_function= lambda value : ','.join(['|'.join(x.split('|')[1:]) for x in value.split(',')]) )
        #self.insert_annotation(variant_id, info, 'SpliceAI=', 8, conn, value_modifier_function= lambda value : ','.join([str(max([float(x) for x in x.split('|')[2:6]])) for x in value.split(',')]) )

        self.insert_annotation(variant_id, info, "tp53db_class=", 27, conn)
        self.insert_annotation(variant_id, info, "tp53db_bayes_del=", 30, conn)
        self.insert_annotation(variant_id, info, "tp53db_DNE_LOF_class=", 29, conn)
        self.insert_annotation(variant_id, info, "tp53db_DNE_class=", 31, conn)
        self.insert_annotation(variant_id, info, "tp53db_domain_function=", 32, conn)
        self.insert_annotation(variant_id, info, "tp53db_transactivation_class=", 33, conn)
        pmids = functions.find_between(info, 'tp53db_pubmed=', '(;|$)')
        if pmids is not None and pmids != '':
            if self.job_config['insert_literature']:
                literature_entries = fetch(pmids) # defined in pubmed_parser.py
                for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                    conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4], "TP53_db")


        # CLINVAR
        clinvar_submissions = functions.find_between(info, 'ClinVar_submissions=', '(;|$)')
        if clinvar_submissions == '' or clinvar_submissions is None:
            clinvar_submissions = []
        else:
            clinvar_submissions = clinvar_submissions.split(',')
        clv_revstat = functions.find_between(info, 'ClinVar_revstat=', '(;|$)')
        clv_varid = functions.find_between(info, 'ClinVar_varid=', '(;|$)')
        clv_inpret = functions.find_between(info, 'ClinVar_inpret=', '(;|$)')

        if clv_revstat is not None and clv_inpret is not None and clv_varid is not None:
            clv_revstat.replace('\\', ',').replace('_', ' ')
            clv_inpret.replace('\\', ',').replace('_', ' ')

            conn.clean_clinvar(variant_id) # remove all clinvar information of this variant from database and insert it again -> only the most recent clinvar annotaion is saved in database!
            conn.insert_clinvar_variant_annotation(variant_id, clv_varid, clv_inpret, clv_revstat)
            clinvar_variant_annotation_id = conn.get_clinvar_variant_annotation_id_by_variant_id(variant_id)

            for submission in clinvar_submissions:
                #Format of one submission: 0VariationID|1ClinicalSignificance|2LastEvaluated|3ReviewStatus|5SubmittedPhenotypeInfo|7Submitter|8comment
                submissions = submission.replace('\\', ',').replace('_', ' ').replace(',', ', ').replace('  ', ' ').replace('&', ';').split('|')
                conn.insert_clinvar_submission(clinvar_variant_annotation_id, submissions[1], submissions[2], submissions[3], submissions[4], submissions[5], submissions[6])




    def annotate_from_vcf(self, config_file_path, input_vcf, output_vcf):
        #if os.environ.get('WEBAPP_ENV') == 'githubtest': # use docker container installation
        #    command = functions.get_docker_instructions(os.environ.get("NGSBITS_CONTAINER_ID"))
        #    command.append("VcfAnnotateFromVcf")
        #else: # use local installation
        command = [paths.ngs_bits_path + "VcfAnnotateFromVcf"]
        command.extend([ "-config_file", config_file_path, "-in", input_vcf, "-out", output_vcf])

        returncode, err_msg, vcf_errors = functions.execute_command(command, 'VcfAnnotateFromVcf')

        #if os.environ.get('WEBAPP_ENV') == 'githubtest':
        #    functions.execute_command(["chmod", "777", output_vcf], "chmod")
        return returncode, err_msg, vcf_errors


    
    def write_vcf_annoate_config(self, one_variant):
        config_file_path = tempfile.gettempdir() + "/.heredivar_vcf_annotate_config"
        config_file = open(config_file_path, 'w')

        ## add rs-num from dbsnp
        if self.job_config['do_dbsnp']:
            config_file.write(paths.dbsnp_path + "\tdbSNP\tRS\t\n")

        ## add revel score
        if self.job_config['do_revel']:
            config_file.write(paths.revel_path + "\t\tREVEL\t\n")

        ## add spliceai precomputed scores
        if self.job_config['do_spliceai']:
            config_file.write(paths.spliceai_path + "\t\tSpliceAI\t\n")

        ## add cadd precomputed scores
        if functions.is_snv(one_variant) and self.job_config['do_cadd']:
            config_file.write(paths.cadd_snvs_path + "\t\tCADD\t\n")
        elif self.job_config['do_cadd']:
            config_file.write(paths.cadd_indels_path + "\t\tCADD\t\n")

        ## add clinvar annotation
        if self.job_config['do_clinvar']:
            config_file.write(paths.clinvar_path + "\tClinVar\tinpret,revstat,varid,submissions\t\n")

        ## add gnomAD annotation
        if self.job_config['do_gnomad']:
            config_file.write(paths.gnomad_path + "\tGnomAD\tAF,AC,hom,hemi,het,popmax,AF_popmax\t\n")
            config_file.write(paths.gnomad_m_path + "\tGnomADm\tAC_hom\t\n")

        ## add BRCA_exchange clinical significance
        if self.job_config['do_brca_exchange']:
            config_file.write(paths.BRCA_exchange_path + "\tBRCA_exchange\tclin_sig_short\t\n")

        ## add FLOSSIES annotation
        if self.job_config['do_flossies']:
            config_file.write(paths.FLOSSIES_path + "\tFLOSSIES\tnum_eur,num_afr\t\n")

        ## add cancerhotspots annotations
        if self.job_config['do_cancerhotspots']:
            config_file.write(paths.cancerhotspots_path + "\tcancerhotspots\tcancertypes,AC,AF\t\n")

        ## add arup brca classification
        if self.job_config['do_arup']:
            config_file.write(paths.arup_brca_path + "\tARUP\tclassification\t\n")

        ## add TP53 database information
        if self.job_config['do_tp53_database']:
            config_file.write(paths.tp53_db + "\ttp53db\tclass,bayes_del,transactivation_class,DNE_LOF_class,DNE_class,domain_function,pubmed\t")

        config_file.close()
        return config_file_path




