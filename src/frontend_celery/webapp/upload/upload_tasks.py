from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from common import functions
from common.heredicare_interface import Heredicare
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from webapp import celery, utils

# errors:
from mysql.connector import Error, InternalError
from urllib.error import HTTPError
from celery.exceptions import Ignore
from werkzeug.exceptions import abort
import traceback




def start_upload_one_variant_heredicare(variant_id, upload_queue_id, user_id, user_roles, conn: Connection): # starts the celery task # upload queue id can be None if it is not linked to a complete upload
    variant = conn.get_variant(variant_id, include_consequences=False, include_assays=False, include_literature=False, include_clinvar=False, include_annotations=False, include_user_classifications=False)
    vids = variant.get_external_ids("heredicare_vid")
    for vid_annotation in vids:
        vid = vid_annotation.value
        upload_variant_queue_id = conn.insert_variant_upload_request(vid, variant_id, upload_queue_id, user_id)

        task = heredicare_upload_one_variant.apply_async(args=[variant_id, vid, user_roles, upload_variant_queue_id])
        task_id = task.id

        conn.update_upload_variant_queue_celery_id(upload_variant_queue_id, celery_task_id = task_id)
    return task_id


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def heredicare_upload_one_variant(self, variant_id, vid, user_roles, upload_variant_queue_id):
    """Background task for uploading one variant and its consensus classification to HerediCare. It also updates the consensus classification in case the variant is already known to HerediCare"""
    #from frontend_celery.webapp.utils.variant_importer import fetch_heredicare
    self.update_state(state='PROGRESS')
    
    try:
        conn = Connection(user_roles)
        heredicare_interface = Heredicare()
        conn.update_upload_variant_queue_status(upload_variant_queue_id, status = "progress", message = "")
        variant = conn.get_variant(variant_id)
        submission_id, status, message = heredicare_interface.upload_consensus_classification(variant, vid)
        finished_at = None
        if status == "success":
            finished_at, status, message = heredicare_interface.get_submission_status(submission_id)
    except InternalError as e:
        # deadlock: code 1213
        status = "retry"
        message = "Attempting retry because of database error: " + str(e)  + ' ' + traceback.format_exc()
    except Error as e:
        status = "error"
        message = "There was a database error: " + str(e)  + ' ' + traceback.format_exc()
    except HTTPError as e:
        status = "retry"
        message = "Attempting retry because of http error: " + str(e)  + ' ' + traceback.format_exc()
    except Exception as e:
        status = "error"
        message = "There was a runtime error: " + str(e) + ' ' + traceback.format_exc()
    
    #print(status)

    conn.update_upload_variant_queue_status(upload_variant_queue_id, status = status, message = message[:10000], finished_at = finished_at, submission_id = submission_id)
    
    conn.close()

    if status == 'error':
        self.update_state(state='FAILURE', meta={ 
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'
                    })
        raise Ignore()
    elif status == "retry":
        self.update_state(state="RETRY", meta={
                        'exc_type': "Runtime error",
                        'exc_message': message, 
                        'custom': '...'})
        heredicare_upload_one_variant.retry()
    else:
        self.update_state(state="SUCCESS")





