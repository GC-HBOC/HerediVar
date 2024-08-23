from flask import flash, g, request, current_app, redirect, url_for, session, abort
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
import common.paths as paths

from urllib.parse import urlparse, urljoin

from webapp import tasks

# require-* functions
# they take some data, check the database and abort if conditions are not met
# these functions are ment to unify error responses
# do not use for user input data from form in eg POST requests, because we do not want to abort in these cases
# use only for data that is set by the programm (but could be modified by a user with malicious intentions...)

# data set
# 404: at least one of the items in data is not set
def require_set(*args):
    if not all(args):
        flash('Missing data. Required ' + str(len(args)) + " items", 'alert-danger')
        abort(404)

# validates that the db_id is known and valid by the database
# func should be a conn.xxx function returning a boolean
def require_valid(db_id, tablename, conn):
    if not conn.valid_db_id(db_id, tablename):
        flash('Unknown identifier in table ' + tablename, 'alert-danger')
        abort(404)

# list permission
# 404: unknown data
# 403: list permissions are not sufficient
def require_list_permission(list_id, required_permissions: list, conn: Connection):
    list_permissions = conn.check_list_permission(session['user']['user_id'], list_id)
    if list_permissions is None:
        abort(404)
    for required_permission in required_permissions:
        if not list_permissions[required_permission]:
            current_app.logger.error(session['user']['preferred_username'] + " attempted view list with id " + str(list_id) + ", but this list was neither created by him nor is it public.")
            abort(403)



# this prevents open redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    allowed_schemes = ('http')
    if current_app.config.get('TLS', True):
        allowed_schemes = ('https')
    is_same_scheme = test_url.scheme in allowed_schemes
    is_same_netloc = ref_url.netloc == test_url.netloc
    return is_same_scheme and is_same_netloc
           
def save_redirect(target):
    if not target or not is_safe_url(target):
        current_app.logger.error("Unsafe redirect url detected: " + str(target))
        return redirect(url_for('main.index')) # maybe use abort() here??
    return redirect(target) # url is save to redirect to!



# some user utils for frontend stuff
def is_user_logged_in():
    resp = session.get('tokenResponse', None)
    if resp is None:
        return False
    return True

def get_preferred_username():
    user_obj = session.get('user', None)
    if user_obj is not None:
        return user_obj['preferred_username']
    return "Anonymous user"


# some db connection utils
def request_has_connection():
    return hasattr(g, 'dbconn')

def get_connection():
    user = session.get('user')
    if user is None:
        roles = ['read_only']
    else:
        roles = user.get('roles', ['read_only'])
    if not request_has_connection():
        #print(roles)
        g.dbconn = Connection(roles)        
        current_app.logger.debug("established db connection")
    return g.dbconn




def strength_to_text(strength, scheme):
    if 'acmg' in scheme:
        if strength == 'pvs':
            return 'very strong pathogenic'
        if strength == 'ps':
            return 'strong pathogenic'
        if strength == 'pm':
            return 'moderate pathogenic'
        if strength == 'pp':
            return 'supporting pathogenic'
        if strength == 'bp':
            return 'supporting benign'
        if strength == 'bs':
            return 'strong benign'
        if strength == 'ba':
            return 'stand-alone benign'
    
    if 'task-force' in scheme:
        if strength == 'pvs':
            return 'pathogenic'
        if strength == 'ps':
            return 'likely pathogenic'
        if strength == 'pm':
            return 'likely benign'
        if strength == 'pp':
            return 'benign'
        if strength == 'bp':
            return 'uncertain'
        



def invalidate_download_queue(identifier, request_type, conn: Connection):
    download_queue_ids = conn.get_valid_download_queue_ids(identifier, request_type)

    for download_queue_id in download_queue_ids:
        download_queue = conn.get_download_queue(download_queue_id) # requested_at, status, finished_at, message, is_valid, filename, identifier, type
        filename = download_queue[5]
        celery_task_id = download_queue[8]
        status = download_queue[1]

        conn.invalidate_download_queue(download_queue_id)

        # abort task if it is still running
        if status in ['pending', 'progress', 'retry']:
            tasks.abort_task(celery_task_id)
            conn.update_download_queue_status(download_queue_id, "aborted", "")

        # delete file
        if functions.is_secure_filename(filename):
            filepath = paths.download_variant_list_dir + "/" + filename
            functions.rm(filepath)

