from flask import flash, current_app
import requests
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from common.heredicare_interface import Heredicare

def get_clinvar_submission_status(clinvar_submission_id, headers): # SUB11770209
    #"https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions/%s/actions/"
    base_url = (current_app.config['CLINVAR_API_ENDPOINT'] + "/%s/actions/") % (clinvar_submission_id, )
    #print(base_url)
    resp = requests.get(base_url, headers = headers)
    print(resp.json())
    return resp

# returns None if there was an ERROR
def check_clinvar_status(submission_id):
    # collect relevant information
    api_key = current_app.config['CLINVAR_API_KEY']
    headers = {'SP-API-KEY': api_key, 'Content-type': 'application/json'}
    submission_status = {'status': None, 'last_updated': None, 'message': '', 'accession_id': None}

    # query clinvar for the current status of the submission
    resp = get_clinvar_submission_status(submission_id, headers = headers)
    if resp.status_code not in [200]:
        flash("Could not check the status of ClinVar submission with submission id " + str(submission_id) + " Reason: " + resp.content.decode("UTF-8"), "alert-danger")
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
            flash("Could not check ClinVar status: " + "\n" + clinvar_submission_file_url + "\n" + submission_file_response.content.decode("UTF-8"), "alert-danger")
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


def check_update_clinvar_status(variant_id, conn: Connection, force_update = False):
    previous_clinvar_submission = conn.get_heredivar_clinvar_submission(variant_id)

    if previous_clinvar_submission is None:
        return None
    
    submission_id = previous_clinvar_submission[2]
    previous_clinvar_submission_status = previous_clinvar_submission[4]
    previous_clinar_accession = previous_clinvar_submission[3]

    # the request is still in process -> check for an update & synchronize heredivar database
    if previous_clinvar_submission_status in ['processing', 'submitted'] or force_update:
        new_submission_status = check_clinvar_status(submission_id)
        conn.insert_update_heredivar_clinvar_submission(variant_id, submission_id, new_submission_status['accession_id'], new_submission_status['status'], new_submission_status['message'], new_submission_status['last_updated'], previous_clinvar_accession = previous_clinar_accession)
        return conn.get_heredivar_clinvar_submission(variant_id)
    else:
        return previous_clinvar_submission



def check_heredicare_status(submission_id):
    heredicare_interface = Heredicare()
    finished_at, status, message = heredicare_interface.get_submission_status(submission_id)
    return finished_at, status, message
    

def check_update_heredicare_status(variant_id, conn: Connection):
    heredicare_queue_entries = conn.get_most_recent_publish_heredicare_queue_entries(variant_id)
    summary_status = "unknown"

    if heredicare_queue_entries is not None:
        for heredicare_queue_entry in heredicare_queue_entries:
            publish_heredicare_queue_id = heredicare_queue_entry[0]
            status = heredicare_queue_entry[1]
            submission_id = heredicare_queue_entry[7]
            if status in ['submitted', 'api_error']and submission_id is not None:
                finished_at, status, message = check_heredicare_status(submission_id)
                conn.update_publish_heredicare_queue_status(publish_heredicare_queue_id, status, message, finished_at, submission_id)
                # take the updated information and return this
        heredicare_queue_entries = conn.get_most_recent_publish_heredicare_queue_entries(variant_id)
        for heredicare_queue_entry in heredicare_queue_entries:
            current_status = heredicare_queue_entry[1]
            if summary_status == "unknown":
                summary_status = current_status
            elif summary_status != current_status:
                summary_status = "multiple stati"
                break

    return heredicare_queue_entries, summary_status