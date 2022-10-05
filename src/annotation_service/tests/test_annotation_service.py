

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
    print(conn.get_variant_annotation(156, 3))
    rs_num = conn.get_variant_annotation(variant_id, 3)
    assert len(rs_num) == 1
    assert rs_num[0][3] == "1570391677"


    # cleanup
    conn.close()