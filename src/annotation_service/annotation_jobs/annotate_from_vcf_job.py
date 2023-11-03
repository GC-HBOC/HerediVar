
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
                                                'do_arup', 'do_tp53_database', 'do_priors', 'do_bayesdel']):
            return 0, '', ''

        self.print_executing()


        config_file_path = self.write_vcf_annoate_config(one_variant = kwargs['one_variant'])
        vcf_annotate_code, vcf_annotate_stderr, vcf_annotate_stdout = self.annotate_from_vcf(config_file_path, inpath, annotated_inpath)




        self.handle_result(inpath, annotated_inpath, vcf_annotate_code)

        warnings_path = annotated_inpath + "_warnings.txt"
        if exists(warnings_path):
            os.remove(warnings_path)

        return vcf_annotate_code, vcf_annotate_stderr, vcf_annotate_stdout



    def save_to_db(self, info, variant_id, conn):
        recent_annotation_ids = conn.get_recent_annotation_type_ids()
        self.insert_external_id(variant_id, info, "dbSNP_RS=", recent_annotation_ids['rsid'], conn)

        self.insert_annotation(variant_id, info, "REVEL=", recent_annotation_ids['revel'], conn)

        self.insert_annotation(variant_id, info, "CADD=", recent_annotation_ids['cadd_scaled'], conn)

        self.insert_annotation(variant_id, info, "GnomAD_AC=", recent_annotation_ids['gnomad_ac'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_AF=", recent_annotation_ids['gnomad_af'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_hom=", recent_annotation_ids['gnomad_hom'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_hemi=", recent_annotation_ids['gnomad_hemi'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_het=", recent_annotation_ids['gnomad_het'], conn)
        self.insert_annotation(variant_id, info, "GnomAD_popmax=", recent_annotation_ids['gnomad_popmax'], conn, value_modifier_function = lambda value : value.upper())
        self.insert_annotation(variant_id, info, "GnomAD_AF_popmax=", recent_annotation_ids['gnomad_popmax_AF'], conn)
        self.insert_annotation(variant_id, info, "GnomADm_AC_hom=", recent_annotation_ids['gnomadm_ac_hom'], conn)

        self.insert_annotation(variant_id, info, "BRCA_exchange_clin_sig_short=", recent_annotation_ids['brca_exchange_clinical_significance'], conn, value_modifier_function = lambda value : value.replace('_', ' ').replace(',', ';'))

        self.insert_annotation(variant_id, info, "FLOSSIES_num_afr=", recent_annotation_ids['flossies_num_afr'], conn)
        self.insert_annotation(variant_id, info, "FLOSSIES_num_eur=", recent_annotation_ids['flossies_num_eur'], conn)

        self.insert_annotation(variant_id, info, "cancerhotspots_cancertypes=", recent_annotation_ids['cancerhotspots_cancertypes'], conn)
        self.insert_annotation(variant_id, info, "cancerhotspots_AC=", recent_annotation_ids['cancerhotspots_ac'], conn)
        self.insert_annotation(variant_id, info, "cancerhotspots_AF=", recent_annotation_ids['cancerhotspots_af'], conn)

        self.insert_annotation(variant_id, info, "ARUP_classification=", recent_annotation_ids['arup_classification'], conn)

        self.insert_annotation(variant_id, info, "HCI_prior=", recent_annotation_ids['hci_prior'], conn)

        self.insert_annotation(variant_id, info, "BayesDEL_noAF=", recent_annotation_ids['bayesdel'], conn)

        # spliceai is saved to the database in the dedicated spliceai job (which must be called after this job anyway)
        #self.insert_annotation(variant_id, info, 'SpliceAI=', 7, conn, value_modifier_function= lambda value : ','.join(['|'.join(x.split('|')[1:]) for x in value.split(',')]) )
        #self.insert_annotation(variant_id, info, 'SpliceAI=', 8, conn, value_modifier_function= lambda value : ','.join([str(max([float(x) for x in x.split('|')[2:6]])) for x in value.split(',')]) )

        self.insert_annotation(variant_id, info, "tp53db_class=", recent_annotation_ids['tp53db_class'], conn)
        self.insert_annotation(variant_id, info, "tp53db_bayes_del=", recent_annotation_ids['tp53db_bayes_del'], conn)
        self.insert_annotation(variant_id, info, "tp53db_DNE_LOF_class=", recent_annotation_ids['tp53db_DNE_LOF_class'], conn)
        self.insert_annotation(variant_id, info, "tp53db_DNE_class=", recent_annotation_ids['tp53db_DNE_class'], conn)
        self.insert_annotation(variant_id, info, "tp53db_domain_function=", recent_annotation_ids['tp53db_domain_function'], conn)
        self.insert_annotation(variant_id, info, "tp53db_transactivation_class=", recent_annotation_ids['tp53db_transactivation_class'], conn)
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
            clinvar_submissions = clinvar_submissions.split('&')
        clv_revstat = functions.find_between(info, 'ClinVar_revstat=', '(;|$)')
        clv_varid = functions.find_between(info, 'ClinVar_varid=', '(;|$)')
        self.insert_external_id(variant_id, info, "ClinVar_varid=", recent_annotation_ids['clinvar'], conn)
        clv_inpret = functions.find_between(info, 'ClinVar_inpret=', '(;|$)')

        if clv_revstat is not None and clv_inpret is not None and clv_varid is not None:
            clv_revstat = functions.decode_vcf(clv_revstat)#.replace('\\', ',').replace('_', ' ')
            clv_inpret = functions.decode_vcf(clv_inpret)#.replace('\\', ',').replace('_', ' ')

            conn.clean_clinvar(variant_id) # remove all clinvar information of this variant from database and insert it again -> only the most recent clinvar annotaion is saved in database!
            conn.insert_clinvar_variant_annotation(variant_id, clv_varid, clv_inpret, clv_revstat)
            clinvar_variant_annotation_id = conn.get_clinvar_variant_annotation_id_by_variant_id(variant_id)

            for submission in clinvar_submissions:
                #Format of one submission: 0VariationID|1ClinicalSignificance|2LastEvaluated|3ReviewStatus|5SubmittedPhenotypeInfo|7Submitter|8comment
                submissions = submission.split('|')
                submissions = [functions.decode_vcf(s) for s in submissions]
                #submissions = functions.decode_vcf(submission)#.replace('\\', ',').replace('_', ' ').replace(',', ', ').replace('  ', ' ').replace('&', ';').split('|')
                conn.insert_clinvar_submission(clinvar_variant_annotation_id, submissions[1], submissions[2], submissions[3], submissions[4], submissions[5], submissions[6])




    def annotate_from_vcf(self, config_file_path, input_vcf, output_vcf):
        command = [os.path.join(paths.ngs_bits_path, "VcfAnnotateFromVcf")]
        command.extend([ "-config_file", config_file_path, "-in", input_vcf, "-out", output_vcf])

        returncode, err_msg, vcf_errors = functions.execute_command(command, 'VcfAnnotateFromVcf')

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
            config_file.write(paths.spliceai_snv_path + "\tsnv\tSpliceAI\t\n")
            config_file.write(paths.spliceai_indel_path + "\tindel\tSpliceAI\t\n")

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
            config_file.write(paths.tp53_db + "\ttp53db\tclass,bayes_del,transactivation_class,DNE_LOF_class,DNE_class,domain_function,pubmed\t\n")

        ## add priors
        if self.job_config['do_priors']:
            config_file.write(paths.hci_priors + "\t\tHCI_prior\t\n")

        ## add bayesdel
        if self.job_config['do_bayesdel']:
            config_file.write(paths.bayesdel + "\t\tBayesDEL_noAF\t\n")

        config_file.close()
        return config_file_path





"""

CSQ=ENST00000240651|||downstream_gene_variant|MODIFIER|||HGNC:26162|PYROXD1||||,ENST00000375266|||downstream_gene_variant|MODIFIER|||HGNC:26162|PYROXD1||||,ENST00000421138|ENST00000421138.6:c.1643_1644del|ENSP00000395449.2:p.His548LeufsTer8|frameshift_variant|HIGH|14/16||HGNC:9948|RECQL|Gene3D:1.10.10.10&PDB-ENSP_mappings:2v1x.A&PDB-ENSP_mappings:2v1x.B&PDB-ENSP_mappings:2wwy.A&PDB-ENSP_mappings:2wwy.B&PDB-ENSP_mappings:4u7d.A&PDB-ENSP_mappings:4u7d.B&PDB-ENSP_mappings:4u7d.C&PDB-ENSP_mappings:4u7d.D&PDB-ENSP_mappings:6jtz.A&PDB-ENSP_mappings:6jtz.B&AFDB-ENSP_mappings:AF-P46063-F1.A&Pfam:PF09382&PANTHER:PTHR13710&PANTHER:PTHR13710:SF72|||,ENST00000444129|ENST00000444129.7:c.1643_1644del|ENSP00000416739.2:p.His548LeufsTer8|frameshift_variant|HIGH|13/15||HGNC:9948|RECQL|Gene3D:1.10.10.10&PDB-ENSP_mappings:2v1x.A&PDB-ENSP_mappings:2v1x.B&PDB-ENSP_mappings:2wwy.A&PDB-ENSP_mappings:2wwy.B&PDB-ENSP_mappings:4u7d.A&PDB-ENSP_mappings:4u7d.B&PDB-ENSP_mappings:4u7d.C&PDB-ENSP_mappings:4u7d.D&PDB-ENSP_mappings:6jtz.A&PDB-ENSP_mappings:6jtz.B&AFDB-ENSP_mappings:AF-P46063-F1.A&Pfam:PF09382&PANTHER:PTHR13710&PANTHER:PTHR13710:SF72|||,ENST00000536851|||downstream_gene_variant|MODIFIER|||HGNC:26162|PYROXD1||||,ENST00000538582|||downstream_gene_variant|MODIFIER|||HGNC:26162|PYROXD1||||,ENST00000538615|||downstream_gene_variant|MODIFIER|||HGNC:26162|PYROXD1||||,ENST00000544970|||downstream_gene_variant|MODIFIER|||HGNC:26162|PYROXD1||||,ENSR00000452487|||regulatory_region_variant|MODIFIER||||||||
CSQ_refseq=NM_001350912.2|||downstream_gene_variant|MODIFIER||||PYROXD1|,NM_001350913.2|||downstream_gene_variant|MODIFIER||||PYROXD1|,NM_002907.4|NM_002907.4:c.1643_1644del|NP_002898.2:p.His548LeufsTer8|frameshift_variant|HIGH|13/15|||RECQL|,NM_024854.5|||downstream_gene_variant|MODIFIER||||PYROXD1|,NM_032941.3|NM_032941.3:c.1643_1644del|NP_116559.1:p.His548LeufsTer8|frameshift_variant|HIGH|14/16|||RECQL|,XM_005253461.3|XM_005253461.3:c.1643_1644del|XP_005253518.1:p.His548LeufsTer8|frameshift_variant|HIGH|14/16|||RECQL|,XM_005253462.5|XM_005253462.5:c.1643_1644del|XP_005253519.1:p.His548LeufsTer8|frameshift_variant|HIGH|14/16|||RECQL|,XM_005253463.4|XM_005253463.4:c.1643_1644del|XP_005253520.1:p.His548LeufsTer8|frameshift_variant|HIGH|13/15|||RECQL|,XM_005253464.4|XM_005253464.4:c.1643_1644del|XP_005253521.1:p.His548LeufsTer8|frameshift_variant|HIGH|13/15|||RECQL|,XM_017019976.2|||downstream_gene_variant|MODIFIER||||PYROXD1|,XR_242902.4|||downstream_gene_variant|MODIFIER||||PYROXD1|
PHYLOP=4.112
hexplorer_delta=-0.20
hexplorer_mut=-2.18
hexplorer_wt=-1.99
hexplorer_delta_rev=-0.83
hexplorer_mut_rev=-7.99
hexplorer_wt_rev=-7.16
max_hbond_delta=0.00
max_hbond_mut=5.40
max_hbond_wt=5.40
dbSNP_RS=1942960300
indel_SpliceAI=A|RECQL|0.00|0.00|0.00|0.00|23|-24|-22|-26
ClinVar_inpret=Uncertain_significance
ClinVar_revstat=criteria_provided,_single_submitter
ClinVar_varid=2450947
ClinVar_submissions=index,VariationID,ClinicalSignificance,DateLastEvaluated,Description,SubmittedPhenotypeInfo,ReportedPhenotypeInfo,ReviewStatus,CollectionMethod,OriginCounts,Submitter,SCV,SubmittedGeneSymbol,ExplanationOfInterpretation

"""


