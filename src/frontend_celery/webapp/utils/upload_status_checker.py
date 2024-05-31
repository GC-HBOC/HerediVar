from flask import flash, current_app
import requests
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from common.heredicare_interface import Heredicare
from common.clinvar_interface import ClinVar




def check_update_clinvar_status(variant_id, publish_queue_ids_oi: list, conn: Connection, force_update = False):
    clinvar_queue_entries = conn.get_clinvar_queue_entries(publish_queue_ids_oi, variant_id) # id, publish_queue_id, requested_at, status, message, submission_id, accession_id, last_updated, celery_task_id, consensus_classification_id

    if clinvar_queue_entries is None:
        return None
    if len(clinvar_queue_entries) == 0:
        return None
    
    got_update = False
    for clinvar_queue_entry in clinvar_queue_entries:
        publish_clinvar_queue_id = clinvar_queue_entry[0]
        status = clinvar_queue_entry[3]
        submission_id = clinvar_queue_entry[5]

        # the request is still in process -> check for an update & synchronize heredivar database
        # pull new information from external
        if (status in ['processing', 'submitted', 'retry', 'process', 'pending'] and submission_id is not None) or force_update:
            clinvar_interface = ClinVar()
            new_submission_status = clinvar_interface.get_clinvar_submission_status(submission_id)
            status = new_submission_status['status']
            message = new_submission_status['message']
            conn.update_publish_clinvar_queue_status(publish_clinvar_queue_id, status, message, accession_id = new_submission_status['accession_id'], last_updated = new_submission_status['last_updated'])
            got_update = True
    
    if got_update:
        # pull updated information in proper format from database
        clinvar_queue_entries = conn.get_clinvar_queue_entries(publish_queue_ids_oi, variant_id)

        # update the respective needs_upload field if a submission chaged to success
        for clinvar_queue_entry in clinvar_queue_entries:
            if clinvar_queue_entry[3] in ["success", "processed"]:
                consensus_classification_id = clinvar_queue_entry[9]
                conn.update_consensus_classification_needs_clinvar_upload(consensus_classification_id)

    return clinvar_queue_entries



def check_heredicare_status(submission_id):
    heredicare_interface = Heredicare()
    finished_at, status, message = heredicare_interface.get_submission_status(submission_id)
    return finished_at, status, message
    

def check_update_heredicare_status(variant_id, publish_queue_ids_oi: list, conn: Connection):
    heredicare_queue_entries = conn.get_heredicare_queue_entries(publish_queue_ids_oi, variant_id)

    if heredicare_queue_entries is None:
        return None
    if len(heredicare_queue_entries) == 0:
        return None

    # pull new information from external
    got_update = False
    for heredicare_queue_entry in heredicare_queue_entries:
        publish_heredicare_queue_id = heredicare_queue_entry[0]
        status = heredicare_queue_entry[1]
        submission_id = heredicare_queue_entry[7]
        if status in ['pending', 'progress', 'submitted'] and submission_id is not None:
            finished_at, status, message = check_heredicare_status(submission_id)
            conn.update_publish_heredicare_queue_status(publish_heredicare_queue_id, status, message, finished_at = finished_at)
            got_update = True
    
    if got_update:
        # pull the updated information from the database (and return that later)
        heredicare_queue_entries = conn.get_heredicare_queue_entries(publish_queue_ids_oi, variant_id)

        # if an upload was successful update the respective needs_upload field
        for heredicare_queue_entry in heredicare_queue_entries:
            if heredicare_queue_entry[1] in ["success"]:
                consensus_classification_id = heredicare_queue_entry[8]
                conn.update_consensus_classification_needs_heredicare_upload(consensus_classification_id)

    return heredicare_queue_entries

#def check_update_all_progressing_heredicare(conn: Connection):
#    variant_ids = conn.get_variant_ids_by_publish_heredicare_status(stati = ['pending', 'progress', 'submitted'])
#    for variant_id in variant_ids:
#        heredicare_queue_entries = check_update_heredicare_status(variant_id, conn)

def check_update_all(variant_ids: list, publish_queue_ids_oi: list, conn: Connection):
    for variant_id in variant_ids:
        _ = check_update_heredicare_status(variant_id, publish_queue_ids_oi, conn)
        _ = check_update_clinvar_status(variant_id, publish_queue_ids_oi, conn)

def check_update_all_most_recent_heredicare(variant_ids: list, conn: Connection):
    for variant_id in variant_ids:
        publish_queue_ids_oi = conn.get_most_recent_publish_queue_ids_heredicare(variant_id)
        _ = check_update_heredicare_status(variant_id, publish_queue_ids_oi, conn)

def check_update_all_most_recent_clinvar(variant_ids: list, conn: Connection):
    for variant_id in variant_ids:
        publish_queue_ids_oi = conn.get_most_recent_publish_queue_ids_clinvar(variant_id)
        _ = check_update_clinvar_status(variant_id, publish_queue_ids_oi, conn)