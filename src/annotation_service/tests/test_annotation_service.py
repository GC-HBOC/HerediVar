

from ..main import process_one_request, get_empty_job_config, get_temp_vcf_path
from common.db_IO import Connection
import filecmp
from os import path

def test_vep_annotation_job():
    """
    This tests the vep annotation
    """

    conn = Connection()
    conn.insert_annotation_request(139, 3)
    annotation_queue_id = conn.get_last_insert_id()
    conn.close()

    job_config = get_empty_job_config()
    job_config['do_vep'] = True
    job_config['insert_consequence'] = True
    job_config['insert_maxent'] = True
    job_config['insert_literature'] = True
    status, runtime_error = process_one_request(annotation_queue_id, job_config)
    print(status)
    print(runtime_error)

    annotated_vcf_path = get_temp_vcf_path(annotation_queue_id)

    
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
    consequences = conn.get_variant_consequences(139)
    conn.close()

    print(consequences)

    assert len(consequences) == 14


