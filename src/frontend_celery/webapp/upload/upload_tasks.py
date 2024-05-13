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




def start_publish(variant_ids, options, user_id, user_roles, conn: Connection):
    publish_queue_id = conn.insert_publish_request(user_id)

    task = publish.apply_async(args = [publish_queue_id, variant_ids, options, user_roles])
    task_id = task.id

    conn.update_publish_queue_celery_task_id(publish_queue_id, celery_task_id = task_id)

    return publish_queue_id



@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def publish(self, publish_queue_id, variant_ids, options, user_roles):
    """Background task for adding all tasks for publishing variants"""
    #from frontend_celery.webapp.utils.variant_importer import import_variants
    self.update_state(state='PROGRESS')

    print("Started variant upload of variant ids: " + str(variant_ids))
    print("... with these options: " + str(options))

    try:
        status = "success"
        message = ""
        conn = Connection(user_roles)

        conn.update_publish_queue_status(publish_queue_id, status = "progress", message = "")

        for variant_id in variant_ids:
            # start the task to upload the consensus classification to clinvar
            if options['do_clinvar']:
                # TODO: start upload to clinvar TASK
                pass
            
            # start the task to upload the variant/consensus_classification/whatever to HerediCaRe
            if options['do_heredicare']:
                celery_task_id = start_upload_one_variant_heredicare(variant_id, publish_queue_id, options, user_roles, conn)

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

    if status != "retry":
        conn.close_publish_request(publish_queue_id, status = status, message = message)
    else:
        conn.update_publish_queue_status(publish_queue_id, status = status, message = message)

    conn.close()
    
    #status, message = fetch_heredicare(vid, heredicare_interface)
    if status == 'error':
        self.update_state(state="FAILURE", meta={ 
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
        publish.retry()
    else:
        self.update_state(state="SUCCESS")









def start_upload_one_variant_heredicare(variant_id, publish_queue_id, options, user_roles, conn: Connection): # starts the celery task # upload queue id can be None if it is not linked to a complete upload
    heredicare_vid_annotation_id = conn.get_most_recent_annotation_type_id("heredicare_vid")
    vids = conn.get_external_ids_from_variant_id(variant_id, heredicare_vid_annotation_id)
    if len(vids) == 0:
        vids = [None]
    for vid in vids:
        publish_heredicare_queue_id = conn.insert_publish_heredicare_request(vid, variant_id, publish_queue_id)

        task = heredicare_upload_one_variant.apply_async(args=[variant_id, vid, user_roles, options, publish_heredicare_queue_id])
        task_id = task.id

        conn.update_publish_heredicare_queue_celery_task_id(publish_heredicare_queue_id, celery_task_id = task_id)
    return task_id


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def heredicare_upload_one_variant(self, variant_id, vid, user_roles, options, publish_heredicare_queue_id):
    """Background task for uploading one variant and its consensus classification to HerediCare. It also updates the consensus classification in case the variant is already known to HerediCare"""
    #from frontend_celery.webapp.utils.variant_importer import fetch_heredicare
    self.update_state(state='PROGRESS')
    
    try:
        submission_id = None
        finished_at = None
        message = ""
        status = "success"

        heredicare_interface = Heredicare()
        conn = Connection(user_roles)
        conn.update_publish_heredicare_queue_status(publish_heredicare_queue_id, status = "progress", message = "")

        variant = conn.get_variant(variant_id, include_annotations = False, include_assays=False, include_automatic_classification=False, include_clinvar=False, include_literature=False, include_user_classifications=False)
        vid, submission_id, status, message = heredicare_interface.post(variant, vid, options)
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
    
    #print("MRCC: " + str(mrcc))
    print("variant_id: " + str(variant_id))
    print("status: " + status)
    print("message: " + message)

    conn.update_publish_heredicare_queue_status(publish_heredicare_queue_id, status = status, message = message[:10000], finished_at = finished_at, submission_id = submission_id)
    
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





