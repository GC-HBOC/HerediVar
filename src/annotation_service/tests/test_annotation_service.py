

from ..main import process_one_request, get_empty_job_config, get_temp_vcf_path
from common.db_IO import Connection
from os import path

def test_vep_annotation_job():
    """
    This tests the vep annotation
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_vep'] = True
    job_config['insert_consequence'] = True
    job_config['insert_maxent'] = True
    job_config['insert_literature'] = True
    

    # test standard annotation
    variant_id = 139
    conn = Connection()
    conn.insert_annotation_request(variant_id, user_id)
    annotation_queue_id = conn.get_last_insert_id()
    conn.close()


    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    
    
    #assert filecmp.cmp(annotated_vcf_path, path.dirname(path.abspath(__file__)) + "/data/139_vep_annotated.vcf")

    #CSQ=ENST00000263934|ENST00000263934.10:c.1977+7031T>C||intron_variant|MODIFIER||20/46|HGNC:16636|KIF1B||||
	#ENST00000377081|ENST00000377081.5:c.2115+7031T>C||intron_variant|MODIFIER||21/47|HGNC:16636|KIF1B||||
	#ENST00000377083|ENST00000377083.5:c.3092T>C|ENSP00000366287.1:p.Ile1031Thr|missense_variant|MODERATE|21/21||HGNC:16636|KIF1B||||
	#ENST00000377086|ENST00000377086.5:c.2115+7031T>C||intron_variant|MODIFIER||22/48|HGNC:16636|KIF1B||||
	#ENST00000377093|ENST00000377093.9:c.3092T>C|ENSP00000366297.4:p.Ile1031Thr|missense_variant|MODERATE|21/21||HGNC:16636|KIF1B||||
	#ENST00000584329|||upstream_gene_variant|MODIFIER|||HGNC:46747|RN7SL731P||||
	#ENST00000620295|ENST00000620295.2:c.2073+7031T>C||intron_variant|MODIFIER||20/46|HGNC:16636|KIF1B||||
	#ENST00000622724|ENST00000622724.3:c.2037+7031T>C||intron_variant|MODIFIER||21/47|HGNC:16636|KIF1B||||
	#ENST00000676179|ENST00000676179.1:c.2115+7031T>C||intron_variant|MODIFIER||22/48|HGNC:16636|KIF1B||||
    #
    #CSQ_refseq=NM_001365951.3|NM_001365951.3:c.2115+7031T>C||intron_variant|MODIFIER||22/48||KIF1B|
	#NM_001365952.1|NM_001365952.1:c.2115+7031T>C||intron_variant|MODIFIER||22/48||KIF1B|
	#NM_001365953.1|NM_001365953.1:c.3092T>C|NP_001352882.1:p.Ile1031Thr|missense_variant|MODERATE|21/21|||KIF1B|
	#NM_015074.3|NM_015074.3:c.1977+7031T>C||intron_variant|MODIFIER||20/46||KIF1B|
	#NM_183416.4|NM_183416.4:c.3092T>C|NP_904325.2:p.Ile1031Thr|missense_variant|MODERATE|21/21|||KIF1B|

    conn = Connection()
    consequences = conn.get_variant_consequences(variant_id)
    all_gene_ids = list(set([consequence[8] for consequence in consequences]))
    conn.close()

    assert len(consequences) == 14
    assert 13764 in all_gene_ids
    assert 28804 in all_gene_ids

    # test pfam protein domains
    variant_id = 146
    conn = Connection()
    conn.insert_annotation_request(variant_id, user_id)
    annotation_queue_id = conn.get_last_insert_id()
    conn.close()

    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    
    conn = Connection()
    consequences = conn.get_variant_consequences(variant_id)
    conn.close()

    for consequence in consequences:
        if consequence[0] == 'ENST00000526567':
            assert consequence[10] == 'PF11640'
            assert consequence[11] == 'Telomere-length maintenance and DNA damage repair'
        if consequence[0] == 'ENST00000452508': # test outdated pfam accession id (this example was hand-crafted)
            assert consequence[10] == 'PF20150'
            assert consequence[11] == '2EXR family'


    # test that literature was inserted correctly
    conn = Connection()
    literature = conn.get_variant_literature(variant_id)
    conn.close()

    assert len(literature) == 1
    assert 24728327 in literature[0]
    assert "Germline variation in cancer-susceptibility genes in a healthy, ancestrally diverse cohort: implications for individual genome sequencing." in literature[0]
    assert "PloS one" in literature[0]
    assert 2014 in literature[0]
    assert "Dale L Bodian, Justine N McCutcheon" in literature[0][4]


    # test insert of maxentscan
    variant_id = 32
    conn = Connection()
    conn.insert_annotation_request(variant_id, user_id)
    annotation_queue_id = conn.get_last_insert_id()
    conn.close()

    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'

    conn = Connection()
    maxentscan_ref = conn.get_variant_annotation(variant_id, 9)
    maxentscan_alt = conn.get_variant_annotation(variant_id, 10)
    conn.close()

    assert len(maxentscan_alt) == 1 # it could potentially be longer because of legacy data / previous versions
    assert len(maxentscan_ref) == 1
    assert maxentscan_ref[0][3] == "8.333"
    assert maxentscan_alt[0][3] == "7.939"
    
    

def test_dbsnp_annotation():
    """
    This tests that the rs number from dbsnp is annotated
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_dbsnp'] = True
    conn = Connection()

    # insert annotation request
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=10001, ref='T', alt='A', orig_chr='chr1', orig_pos=10001, orig_ref='T', orig_alt='A', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    rs_num = conn.get_variant_annotation(variant_id, 3)
    assert len(rs_num) == 1
    assert rs_num[0][3] == "1570391677"


    # cleanup
    conn.close()


def test_revel_annotation():
    """
    This tests that REVEL score is annotated correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_revel'] = True
    conn = Connection()

    # insert annotation request
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=35142, ref='G', alt='A', orig_chr='chr1', orig_pos=35142, orig_ref='G', orig_alt='A', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 6)
    assert len(res) == 1
    assert res[0][3] == "0.027"


    # cleanup
    conn.close()


def test_cadd_annotation():
    """
    This tests that CADD score is annotated correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_cadd'] = True
    conn = Connection()

    # insert annotation request
    #chr1    10009   .       A       T       .       .       CADD=8.518
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=10009, ref='A', alt='T', orig_chr='chr1', orig_pos=10009, orig_ref='A', orig_alt='T', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 5)
    assert len(res) == 1
    assert res[0][3] == "8.518"


    # cleanup
    conn.close()



def test_gnomad_annotation():
    """
    This tests that gnomad population counts are stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_gnomad'] = True
    conn = Connection()

    # insert annotation request
    #chr1	10037	.	T	C	.	AS_VQSR	AF=2.60139e-05;AC=2;hom=0;popmax=eas;AC_popmax=1;AN_popmax=2456;AF_popmax=0.000407166;het=2
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=10037, ref='T', alt='C', orig_chr='chr1', orig_pos=10037, orig_ref='T', orig_alt='A', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    #11	gnomad_ac
    #12	gnomad_af
    #13	gnomad_hom
    #14	gnomad_hemi
    #15	gnomad_het
    #16	gnomad_popmax
    #17	gnomadm_ac_hom
    #51	gnomad_popmax_AF
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 11)
    assert len(res) == 1
    assert res[0][3] == "2"

    res = conn.get_variant_annotation(variant_id, 12)
    assert len(res) == 1
    assert res[0][3] == "2.60139e-05"

    res = conn.get_variant_annotation(variant_id, 13)
    assert len(res) == 1
    assert res[0][3] == "0"
    
    res = conn.get_variant_annotation(variant_id, 14)
    assert len(res) == 0
    
    res = conn.get_variant_annotation(variant_id, 15)
    assert len(res) == 1
    assert res[0][3] == "2"
    
    res = conn.get_variant_annotation(variant_id, 16)
    assert len(res) == 1
    assert res[0][3] == "eas"
    
    res = conn.get_variant_annotation(variant_id, 17)
    assert len(res) == 0
    
    res = conn.get_variant_annotation(variant_id, 51)
    assert len(res) == 1
    assert res[0][3] == "0.000407166"


    # cleanup
    conn.close()
    

def test_brca_exchange_annotation():
    """
    This tests that BRCA exchange classification is stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_brca_exchange'] = True
    conn = Connection()

    # insert annotation request
    #chr13   32315226        .       G       A       .       .       clin_sig_detail=Benign(ENIGMA),_Benign_(ClinVar);clin_sig_short=Benign_/_Little_Clinical_Significance
    annotation_queue_id = conn.insert_variant(chr='chr13', pos=32315226, ref='G', alt='A', orig_chr='chr13', orig_pos=32315226, orig_ref='G', orig_alt='A', user_id=user_id)

    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 18)
    assert len(res) == 1
    assert res[0][3] == "Benign / Little Clinical Significance" # '_' are replaced with spaces


    # cleanup
    conn.close()
    

def test_flossies_annotation():
    """
    This tests that BRCA exchange classification is stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_flossies'] = True
    conn = Connection()

    # insert annotation request
    #chr2	17753961	.	G	C	.	.	num_eur=1;num_afr=0
    annotation_queue_id = conn.insert_variant(chr='chr2', pos=17753961, ref='G', alt='C', orig_chr='chr2', orig_pos=17753961, orig_ref='G', orig_alt='C', user_id=user_id)

    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 19)
    assert len(res) == 1
    assert res[0][3] == "0"

    res = conn.get_variant_annotation(variant_id, 20)
    assert len(res) == 1
    assert res[0][3] == "1"


    # cleanup
    conn.close()


def test_cancerhotspots_annotation():
    """
    This tests that cancerhotspots are stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_cancerhotspots'] = True
    conn = Connection()

    # insert annotation request
    #chr1	939434	.	A	AT	.	.	cancertypes=Colorectal_Adenocarcinoma:bowel|Invasive_Breast_Carcinoma:breast|Cutaneous_Melanoma:skin|Low-Grade_Glioma:cnsbrain;AC=4;AF=0.00016503692701241903
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=939434, ref='A', alt='AT', orig_chr='chr2', orig_pos=939434, orig_ref='A', orig_alt='AT', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 22)
    assert len(res) == 1
    assert res[0][3] == "Colorectal_Adenocarcinoma:bowel|Invasive_Breast_Carcinoma:breast|Cutaneous_Melanoma:skin|Low-Grade_Glioma:cnsbrain"

    res = conn.get_variant_annotation(variant_id, 23)
    assert len(res) == 1
    assert res[0][3] == "4"

    res = conn.get_variant_annotation(variant_id, 24)
    assert len(res) == 1
    assert res[0][3] == "0.00016503692701241903"


    # cleanup
    conn.close()




def test_arup_brca_annotation():
    """
    This tests that arup brca classifications are stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_arup'] = True
    conn = Connection()

    # insert annotation request
    #chr13	32316453	.	AGGTAAAAATGCCTATT	A	.	.	HGVSc=ENST00000380152:c.-5_11del;classification=5
    annotation_queue_id = conn.insert_variant(chr='chr13', pos=32316453, ref='AGGTAAAAATGCCTATT', alt='A', orig_chr='chr13', orig_pos=32316453, orig_ref='AGGTAAAAATGCCTATT', orig_alt='A', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 21)
    assert len(res) == 1
    assert res[0][3] == "5"


    # cleanup
    conn.close()
    


def test_tp53_db_annotation():
    """
    This tests that TP53 db annotations are stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_tp53_database'] = True
    job_config['insert_literature'] = True
    conn = Connection()

    # insert annotation request
    #chr17	7670613	.	A	C	.	.	class=FH;bayes_del=0.1186;transactivation_class=functional;DNE_LOF_class=notDNE_notLOF;DNE_class=No;domain_function=Regulation;pubmed=12672316&18511570
    annotation_queue_id = conn.insert_variant(chr='chr17', pos=7670613, ref='A', alt='C', orig_chr='chr17', orig_pos=7670613, orig_ref='A', orig_alt='C', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    #27	tp53db_class
    #29	tp53db_DNE_LOF_class
    #30	tp53db_bayes_del
    #31	tp53db_DNE_class
    #32	tp53db_domain_function
    #33	tp53db_transactivation_class
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 27)
    assert len(res) == 1
    assert res[0][3] == "FH"


    res = conn.get_variant_annotation(variant_id, 30)
    assert len(res) == 1
    assert res[0][3] == "0.1186"

    res = conn.get_variant_annotation(variant_id, 33)
    assert len(res) == 1
    assert res[0][3] == "functional"

    res = conn.get_variant_annotation(variant_id, 29)
    assert len(res) == 1
    assert res[0][3] == "notDNE_notLOF"

    res = conn.get_variant_annotation(variant_id, 31)
    assert len(res) == 1
    assert res[0][3] == "No"

    res = conn.get_variant_annotation(variant_id, 32)
    assert len(res) == 1
    assert res[0][3] == "Regulation"


    literature = conn.get_variant_literature(variant_id)
    assert len(literature) == 2
    assert any([12672316 in x or 18511570 in x for x in literature])


    # cleanup
    conn.close()
    

    
def test_clinvar_annotation():
    """
    This tests that clinvar annotations are stored correctly
    """

    # setup
    user_id = 3
    job_config = get_empty_job_config()
    job_config['do_clinvar'] = True
    conn = Connection()

    # insert annotation request
    #chr1	925952	1019397	G	A	.	.	
    #inpret=Uncertain_significance
    #revstat=criteria_provided,_single_submitter
    #varid=1019397
    #submissions=1019397|Uncertain_significance|2020-07-03|criteria_provided\_single_submitter|CN517202:not_provided|Invitae|description:_This_sequence_change_replaces_glycine_with_glutamic_acid_at_codon_4_of_the_SAMD11_protein_(p.Gly4Glu)._The_glycine_residue_is_weakly_conserved_and_there_is_a_moderate_physicochemical_difference_between_glycine_and_glutamic_acid._This_variant_is_not_present_in_population_databases_(ExAC_no_frequency)._This_variant_has_not_been_reported_in_the_literature_in_individuals_with_SAMD11-related_conditions._Algorithms_developed_to_predict_the_effect_of_missense_changes_on_protein_structure_and_function_are_either_unavailable_or_do_not_agree_on_the_potential_impact_of_this_missense_change_(SIFT:_Deleterious&_PolyPhen-2:_Probably_Damaging&_Align-GVGD:_Class_C0)._In_summary\_the_available_evidence_is_currently_insufficient_to_determine_the_role_of_this_variant_in_disease._Therefore\_it_has_been_classified_as_a_Variant_of_Uncertain_Significance.
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=925952, ref='G', alt='A', orig_chr='chr1', orig_pos=925952, orig_ref='G', orig_alt='A', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    #27	tp53db_class
    #29	tp53db_DNE_LOF_class
    #30	tp53db_bayes_del
    #31	tp53db_DNE_class
    #32	tp53db_domain_function
    #33	tp53db_transactivation_class
    conn = Connection()
    clinvar_variant_annotation = conn.get_clinvar_variant_annotation(variant_id)
    clinvar_variation_id = clinvar_variant_annotation[2]
    print("Clinvar variant annotation: " + str(clinvar_variant_annotation))

    assert clinvar_variant_annotation is not None
    assert clinvar_variant_annotation[1] == variant_id
    assert str(clinvar_variant_annotation[2]) == str(clinvar_variation_id) == str(1019397)
    assert clinvar_variant_annotation[3] == 'Uncertain_significance'
    assert clinvar_variant_annotation[4] == 'criteria_provided,_single_submitter'


    clinvar_submissions = conn.get_clinvar_submissions(clinvar_variant_annotation[0])

    print("Clinvar submissions: " + str(clinvar_submissions))

    assert len(clinvar_submissions) == 1



    # cleanup
    conn.close()



def test_task_force_protein_domain_annotation():
    """
    This tests that the task force protein domains stored correctly
    """

    # setup
    user_id = 3
    variant_id = 32
    job_config = get_empty_job_config()
    job_config['do_task_force_protein_domains'] = True
    conn = Connection()

    # insert annotation request
    conn.insert_annotation_request(variant_id, user_id)
    annotation_queue_id = conn.get_last_insert_id()


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    protein_domains = conn.get_variant_annotation(variant_id, 36)
    assert len(protein_domains) == 1
    assert protein_domains[0][3].strip() == "C-terminal RAD51 binding domain (inkl. NLS1 und BRC-)"

    protein_domains_sources = conn.get_variant_annotation(variant_id, 37)
    assert len(protein_domains_sources) == 1
    assert protein_domains_sources[0][3] == "BWRL/ENIGMA"



    # cleanup
    conn.close()


def test_hexplorer_annotation():
    """
    This tests that the hexplorer tool is run correctly and that annotations are stored
    """

    # setup
    user_id = 3
    variant_id = 164
    job_config = get_empty_job_config()
    job_config['do_hexplorer'] = True
    conn = Connection()

    # insert annotation request
    #chr1-45332791-C-T
    conn.insert_annotation_request(variant_id, user_id)
    annotation_queue_id = conn.get_last_insert_id()


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 39)
    assert len(res) == 1
    assert res[0][3] == "1.51"

    res = conn.get_variant_annotation(variant_id, 41)
    assert len(res) == 1
    assert res[0][3] == "-10.82"

    res = conn.get_variant_annotation(variant_id, 40)
    assert len(res) == 1
    assert res[0][3] == "-9.31"

    res = conn.get_variant_annotation(variant_id, 42)
    assert len(res) == 1
    assert res[0][3] == "4.88"
    
    res = conn.get_variant_annotation(variant_id, 44)
    assert len(res) == 1
    assert res[0][3] == "-7.76"

    res = conn.get_variant_annotation(variant_id, 43)
    assert len(res) == 1
    assert res[0][3] == "-2.88"

    res = conn.get_variant_annotation(variant_id, 45)
    assert len(res) == 1
    assert res[0][3] == "9.80"

    res = conn.get_variant_annotation(variant_id, 47)
    assert len(res) == 0

    res = conn.get_variant_annotation(variant_id, 46)
    assert len(res) == 1
    assert res[0][3] == "9.80"

    res = conn.get_variant_annotation(variant_id, 48)
    assert len(res) == 1
    assert res[0][3] == "0.00"

    res = conn.get_variant_annotation(variant_id, 50)
    assert len(res) == 1
    assert res[0][3] == "10.30"

    res = conn.get_variant_annotation(variant_id, 49)
    assert len(res) == 1
    assert res[0][3] == "10.30"


    # cleanup
    conn.close()

def test_spliceai_annotation():
    """
    This tests that the hexplorer tool is run correctly and that annotations are stored
    """

    # setup
    user_id = 3
    variant_id = 32
    job_config = get_empty_job_config()
    job_config['do_spliceai'] = True
    conn = Connection()

    # test variant where the annotation was read from the preannotated file
    # insert annotation request
    #chr1	69092	.	T	C	.	.	SpliceAI=C|OR4F5|0.01|0.00|0.09|0.01|41|42|1|23
    annotation_queue_id = conn.insert_variant(chr='chr1', pos=69092, ref='T', alt='C', orig_chr='chr1', orig_pos=69092, orig_ref='T', orig_alt='C', user_id=user_id)
    variant_id = conn.get_annotation_queue_entry(annotation_queue_id)[1]


    # start annotation service
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == 'success'
    conn.close()

    # check that annotation was inserted correctly
    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 7)
    assert len(res) == 1
    assert res[0][3] == "OR4F5|0.01|0.00|0.09|0.01|41|42|1|23"

    res = conn.get_variant_annotation(variant_id, 8)
    assert len(res) == 1
    assert res[0][3] == "0.09"

    # cleanup
    conn.close()

    # test running spliceai
    conn = Connection()
    #164	chr14	39335204	A	G	0		chr14	39335204	A	G
    variant_id = 164
    conn.insert_annotation_request(variant_id, user_id)
    annotation_queue_id = conn.get_last_insert_id()

    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(runtime_error)
    assert status == "success"
    conn.close()

    conn = Connection()
    res = conn.get_variant_annotation(variant_id, 7)
    assert len(res) == 1
    assert res[0][3] == "RP11-407N17.3|0.00|0.00|0.00|0.00|-38|14|-1|-44,CTAGE5|0.00|0.00|0.00|0.00|-38|14|-1|-44"

    res = conn.get_variant_annotation(variant_id, 8)
    assert len(res) == 1
    assert res[0][3] == "0.0,0.0"

    conn.close()



