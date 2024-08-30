from urllib.error import HTTPError
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from webapp import celery, utils
from common import functions
from common import paths
from common.db_IO import Connection
from celery.exceptions import Ignore

from . import download_functions
# errors
from urllib.error import HTTPError
from mysql.connector import Error, InternalError
import traceback



###########################################################
############## START VARIANT TSV BULK IMPORT ##############
###########################################################

def start_generate_list_vcf(list_id, user_roles, conn: Connection):
    functions.mkdir_recursive(paths.download_variant_list_dir)
    filename = functions.get_random_temp_file(fileending = ".vcf", filename_ext = "_".join(["list", str(list_id), functions.get_today()]), folder = "")
    
    request_type = "list_download"

    utils.invalidate_download_queue(list_id, request_type, conn)
    download_queue_id = conn.insert_download_request(list_id, request_type, filename)

    task = generate_list_vcf.apply_async(args=[list_id, user_roles, download_queue_id, filename]) # start task
    task_id = task.id

    conn.update_download_queue_celery_task_id(download_queue_id, celery_task_id = task_id) # save the task id for status updates

    return download_queue_id


@celery.task(bind=True, retry_backoff=5, max_retries=3)
def generate_list_vcf(self, list_id, user_roles, download_queue_id, filename):
    """ Background task for importing generating vcf file of variant list """
    self.update_state("PROGRESS")

    try:
        conn = Connection(user_roles)
        message = ""
        status = "success"

        conn.update_download_queue_status(download_queue_id, status = "progress", message = "")

        if not functions.is_secure_filename(filename): # just for safety - might not be required
            status = "error"
            message = "Invalid filename provided!"
        else:
            variant_ids_oi = conn.get_variant_ids_from_list(list_id)
            filepath = paths.download_variant_list_dir + "/" + filename
            status, message = download_functions.write_vcf_file(variant_ids_oi, filepath, conn)

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
    #print(message)

    if status != "retry":
        conn.close_download_queue(status, download_queue_id, message = message[0:1000])
    else:
        conn.update_download_queue_status(download_queue_id, status = status, message = message[0:1000])

    conn.close()
    
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
        generate_list_vcf.retry()
    else:
        self.update_state(state="SUCCESS")

