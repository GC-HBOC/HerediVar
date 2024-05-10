from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common import functions
from common.heredicare_interface import Heredicare



def extract_variant_ids(request_args):
    variant_ids_strs = request_args.getlist('variant_ids')
    result = []
    for variant_ids_str in variant_ids_strs:
        result.extend(variant_ids_str.split(','))
    return result

def extract_clinvar_selected_genes(variant_ids, request_form):
    result = {}
    for variant_id in variant_ids:
        selected_gene_id = request_form.get("clinvar_gene_" + str(variant_id))
        if selected_gene_id is not None:
            result[variant_id] = selected_gene_id
    return result


def get_clinvar_submission_json(variant, selected_gene, clinvar_accession = None):
    # required fields: 
    # clinvarSubmission > clinicalSignificance > clinicalSignificanceDescription (one of: "Pathogenic", "Likely pathogenic", "Uncertain significance", "Likely benign", "Benign", "Pathogenic, low penetrance", "Uncertain risk allele", "Likely pathogenic, low penetrance", "Established risk allele", "Likely risk allele", "affects", "association", "drug response", "confers sensitivity", "protective", "other", "not provided")
    # clinvarSubmission > clinicalSignificance > comment
    # clinvarSubmission > clinicalSignificance > customAssertionScore (ACMG) !!! requires assertion method as well
    # clinvarSubmission > clinicalSignificance > dateLastEvaluated

    # clinvarSubmission > conditionSet > condition > id (hereditary breast cancer)
    # clinvarSubmission > conditionSet > condition > db (OMIM)

    # clinvarSubmission > localID (HerediVar variant_id)

    # clinvarSubmission > observedIn > affectedStatus (not provided??)
    # clinvarSubmission > observedIn > alleleOrigin (germline)
    # clinvarSubmission > observedIn > collectionMethod (curation: For variants that were not directly observed by the submitter, but were interpreted by curation of multiple sources, including clinical testing laboratory reports, publications, private case data, and public databases.)
    
    # clinvarSubmission > variantSet > variant > chromosomeCoordinates > alternateAllele (vcf alt field if up to 50nt long variant!)
    # clinvarSubmission > variantSet > variant > assembly (GRCh38)
    # clinvarSubmission > variantSet > variant > chromosome (Values are 1-22, X, Y, and MT)
    # clinvarSubmission > variantSet > variant > referenceAllele (vcf ref field)
    # clinvarSubmission > variantSet > variant > start (vcf pos field: 1-based coordinates)
    # clinvarSubmission > variantSet > variant > stop (vcf pos field + length of variant)
    mrcc = variant.get_recent_consensus_classification()

    data = {}
    clinvar_submission = []
    clinvar_submission_properties = {}

    assertion_criteria = get_assertion_criteria(mrcc.scheme.type, mrcc.scheme.reference)
    data['assertionCriteria'] = assertion_criteria
    
    clinical_significance = {}
    clinical_significance['clinicalSignificanceDescription'] = mrcc.class_to_text()
    clinical_significance['comment'] = mrcc.get_extended_comment()
    clinical_significance['dateLastEvaluated'] = mrcc.date.split(' ')[0] # only grab the date and trim the time
    clinvar_submission_properties['clinicalSignificance'] =  clinical_significance

    if clinvar_accession is not None:
        clinvar_submission_properties['clinvarAccession'] = str(clinvar_accession)


    condition_set = {}
    condition = []
    condition.append({'id': "145", 'db': 'Orphanet'}) #(https://www.omim.org/entry/114480)
    condition_set['condition'] = condition
    clinvar_submission_properties['conditionSet'] =  condition_set

    clinvar_submission_properties['localID'] =  str(variant.id)

    observed_in = []

    observed_in_properties = {}
    observed_in_properties['affectedStatus'] = 'not provided'
    observed_in_properties['alleleOrigin'] = 'germline'
    observed_in_properties['collectionMethod'] = 'curation'
    observed_in.append(observed_in_properties)
    clinvar_submission_properties['observedIn'] =  observed_in

    if clinvar_accession is None:
        clinvar_submission_properties['recordStatus'] = 'novel'
    else:
        clinvar_submission_properties['recordStatus'] = 'update'
    data['clinvarSubmissionReleaseStatus'] = 'public'

    variant_set = {}
    variant_json = []
    variant_properties = {}

    # id,chr,pos,ref,alt
    variant_properties['chromosomeCoordinates'] = {'alternateAllele': variant.alt, 
                                                   'assembly': 'GRCh38', 
                                                   'chromosome': variant.chrom.strip('chr'), 
                                                   'referenceAllele': variant.ref, 
                                                   'start': variant.pos,
                                                   'stop': int(variant.pos) + len(variant.ref)-1}

    if selected_gene is not None:
        gene = []
        gene_properties = {'symbol': selected_gene}
        gene.append(gene_properties)
        variant_properties['gene'] = gene
    
    variant_json.append(variant_properties)
    variant_set['variant'] = variant_json
    clinvar_submission_properties['variantSet'] =  variant_set

    clinvar_submission.append(clinvar_submission_properties)

    data['clinvarSubmission'] = clinvar_submission
    #print(data)
    return data


def get_assertion_criteria(scheme_type, assertion_criteria_source):
    assertion_criteria = {}
    if scheme_type in ['acmg', 'enigma-brca1', 'enigma-brca2']:
        assertion_criteria_source = assertion_criteria_source.replace('https://pubmed.ncbi.nlm.nih.gov/', '').strip('/')
        assertion_criteria['db'] = "PubMed"
        assertion_criteria['id'] = assertion_criteria_source
    elif scheme_type in ['enigma-brca1', 'enigma-brca2']:
        assertion_criteria['url'] = assertion_criteria_source
    else:
        assertion_criteria['url'] = assertion_criteria_source
    return assertion_criteria

