
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common.functions as functions
from common.xml_validator import xml_validator
from common.singleton import Singleton
from . import paths

from datetime import datetime, timedelta
import re
import json
import urllib
import jsonschema



class ClinVar(metaclass=Singleton):

    def __init__(self):
        self.base_url = "/".join(["https://submit.ncbi.nlm.nih.gov", os.environ.get('CLINVAR_API_PROJECT').strip('/'), os.environ.get('CLINVAR_API_VERSION').strip('/')])
        self.endpoints = {
            # upload endpoints
            "submit": "submissions",
            "check_status": "submissions/%s/actions/"
        }
        #print("NEW INSTANCE")

        #os.environ.get('CLINVAR_API_KEY')

    def get_url(self, endpoint):
        return "/".join([self.base_url, self.endpoints[endpoint]])
    
    def get_header(self):
        return {'SP-API-KEY': os.environ.get('CLINVAR_API_KEY'), 'Content-type': 'application/json'}
    

    def get_clinvar_submission_json(self, variant, selected_gene, clinvar_accession = None):
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

        assertion_criteria = self.get_assertion_criteria(mrcc.scheme.reference)
        data['assertionCriteria'] = assertion_criteria
    
        germline_classification = {}
        germline_classification['germlineClassificationDescription'] = mrcc.class_to_text()
        germline_classification['comment'] = mrcc.get_extended_comment()
        germline_classification['dateLastEvaluated'] = functions.reformat_date(mrcc.date, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d") # 2024-05-06 11:49:11
        clinvar_submission_properties['germlineClassification'] =  germline_classification

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
        variant_properties['chromosomeCoordinates'] = {
            'assembly': 'GRCh38', 
            'chromosome': variant.chrom.strip('chr'), 
            'referenceAllele': variant.ref, 
            'alternateAllele': variant.alt, 
            'start': variant.pos,
            'stop': int(variant.pos) + len(variant.ref)-1
        }

        if selected_gene is not None:
            gene = []
            gene_properties = {'symbol': selected_gene}
            gene.append(gene_properties)
            variant_properties['gene'] = gene
    
        variant_json.append(variant_properties)
        variant_set['variant'] = variant_json
        clinvar_submission_properties['variantSet'] =  variant_set

        clinvar_submission.append(clinvar_submission_properties)

        data['germlineSubmission'] = clinvar_submission
        #print(data)
        return data


    def get_assertion_criteria(self, assertion_criteria_source):
        assertion_criteria = {}
        if assertion_criteria_source.startswith("https://pubmed.ncbi.nlm.nih.gov/"):
            assertion_criteria_source = assertion_criteria_source.replace('https://pubmed.ncbi.nlm.nih.gov/', '').strip('/')
            assertion_criteria['db'] = "PubMed"
            assertion_criteria['id'] = assertion_criteria_source
        else:
            assertion_criteria['url'] = assertion_criteria_source
        return assertion_criteria

    def get_postable_consensus_classification(self, variant, selected_gene, clinvar_accession):
        schema = json.loads(open(paths.clinvar_submission_schema).read())
        data = self.get_clinvar_submission_json(variant, selected_gene, clinvar_accession)
        jsonschema.validate(instance = data, schema = schema) # this throws jsonschema.exceptions.ValidationError on fail

        postable_data = {
            "actions": [{
                "type": "AddData",
                "targetDb": "clinvar",
                "data": {"content": data}
            }]
        }
        return postable_data

    def post_consensus_classification(self, variant, selected_gene, clinvar_accession):
        status = "success"
        message = ""
        submission_id = None

        mrcc = variant.get_recent_consensus_classification()
        if mrcc is None:
            status = "skipped"
            message = "This variant does not have a consensus classification to submit."
            return submission_id, status, message
        elif not mrcc.needs_clinvar_upload:
            status = "skipped"
            message = "The consensus classification is already submitted to ClinVar"
            return submission_id, status, message
        elif mrcc.scheme.type in ['none', 'task-force']:
            status = "skipped"
            message = "The consensus classification does not follow a scheme. This type of classification can not be submitted to ClinVar. Please use a proper scheme."
            return submission_id, status, message
        
        postable_data = self.get_postable_consensus_classification(variant, selected_gene, clinvar_accession)
        url = self.get_url(endpoint = "submit")
        print(url)
        headers = self.get_header()

        resp = requests.post(url, headers = headers, data=json.dumps(postable_data))

        if resp.status_code not in [200, 201]:
            status = "api_error"
            message = 'Status code of ClinVar submission API endpoint was: ' + str(resp.status_code) + ': ' + str(resp.json())
        else:
            submission_id = resp.json()['id']
        
        return submission_id, status, message
    


    # returns None if there was an ERROR
    def get_clinvar_submission_status(self, submission_id):
        submission_status = {'status': None, 'last_updated': None, 'message': '', 'accession_id': None}

        # query clinvar for the current status of the submission
        #https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions/%s/actions/
        url = self.get_url("check_status") % (submission_id, )
        headers = self.get_header()
        resp = requests.get(url, headers = headers)
        if resp.status_code not in [200]:
            print("Could not check the status of ClinVar submission with submission id " + str(submission_id) + " Reason: " + resp.content.decode("UTF-8") + " Code: " + str(resp.status_code))
            return None

        # extract relevant information from the clinvar response if successful
        response_content = resp.json()['actions'][0]
        clinvar_submission_status = response_content['status']
        submission_status['status'] = clinvar_submission_status
        if clinvar_submission_status in ['submitted', 'processing']:
            clinvar_submission_date = response_content['updated']
            submission_status['last_updated'] = clinvar_submission_date.replace('T', '\n').replace('Z', '')
        else:
            # fetch the submission file which contains more information about errors if there were any
            clinvar_submission_file_url = response_content['responses'][0]['files'][0]['url']
            submission_file_response = requests.get(clinvar_submission_file_url, headers = headers)
            if submission_file_response.status_code != 200:
                print("Could not check ClinVar status: " + "\n" + clinvar_submission_file_url + "\n" + submission_file_response.content.decode("UTF-8"))
                return None

            # extract relevant information from the clinvar response if it was successful
            submission_file_response = submission_file_response.json()
            submission_status['last_updated'] = submission_file_response['submissionDate']
            if clinvar_submission_status == 'processed':
                submission_status['accession_id'] = submission_file_response['submissions'][0]['identifiers']['clinvarAccession']
            if clinvar_submission_status == 'error':
                clinvar_submission_messages = submission_file_response['submissions'][0]['errors'][0]['output']['errors']
                clinvar_submission_messages = [x['userMessage'] for x in clinvar_submission_messages]
                clinvar_submission_message = ';'.join(clinvar_submission_messages)
                submission_status['message'] = clinvar_submission_message

        return submission_status