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



def start_heredicare_upload(user_id, user_roles, conn: Connection): # starts the celery task
    upload_queue_id = conn.insert_upload_request(user_id)

    task = heredicare_upload.apply_async(args=[user_id, user_roles, min_date, import_queue_id]) # start task
    task_id = task.id

    conn.update_import_queue_celery_task_id(import_queue_id, celery_task_id = task_id) # save the task id for status updates

    return import_queue_id


@celery.task(bind=True, retry_backoff=5, max_retries=3, time_limit=600)
def heredicare_upload(self, user_id, user_roles, min_date, import_queue_id):
    """Background task for fetching variants from HerediCare"""
    #from frontend_celery.webapp.utils.variant_importer import import_variants
    self.update_state(state='PROGRESS')

    try:
        conn = Connection(user_roles)

        conn.update_import_queue_status(import_queue_id, status = "progress", message = "")

        status, message = import_variants(conn, user_id, user_roles, functions.str2datetime(min_date, fmt = '%Y-%m-%dT%H:%M:%S'), import_queue_id)
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
        conn.close_import_request(import_queue_id, status = status, message = message)
    else:
        conn.update_import_queue_status(import_queue_id, status = status, message = message)

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
        heredicare_variant_import.retry()
    else:
        self.update_state(state="SUCCESS")





