import re
from werkzeug.exceptions import abort
from flask import flash, Markup, g
import tempfile
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
from .decorators import *
from .search_utils import *
from .clinvar_utils import *
from urllib.parse import urlparse, urljoin
from ..tasks import annotate_variant
import pathlib
#import celery_module


def get_variant(conn, variant_id):
    if variant_id is None:
        abort(404)
    variant = conn.get_one_variant(variant_id)
    if variant is None:
        abort(404)
    return variant

def get_variant_id(conn, chr, pos, ref, alt):
    if chr is None or pos is None or ref is None or alt is None:
        abort(404)
    variant_id = conn.get_variant_id(chr, pos, ref, alt)
    return variant_id


def start_annotation_service(variant_id = None, annotation_queue_id = None):
    conn = get_connection()
    if variant_id is not None:
        annotation_queue_id = conn.insert_annotation_request(variant_id, session['user']['user_id']) # only inserts a new row if there is none with this variant_id & pending
        log_postfix = " for variant " + str(variant_id)
    else:
        log_postfix = " for annotation queue entry " + str(annotation_queue_id)
    task = annotate_variant.apply_async(args=[annotation_queue_id])
    print("Issued annotation for annotation queue id: " + str(annotation_queue_id) + "with celery task id: " + str(task.id))
    current_app.logger.info(session['user']['preferred_username'] + " started the annotation service for annotation queue id: " + str(annotation_queue_id) + " with celery task id: " + str(task.id))
    conn.insert_celery_task_id(annotation_queue_id, task.id)
    return task.id


def remove_oldest_file(folder, maxfiles=10):
    if os.path.exists(folder):
        list_of_files = os.listdir(folder)
        full_paths = [os.path.abspath(os.path.join(folder, x)) for x in list_of_files if not os.path.basename(x).startswith('.')]

        if len(list_of_files) >= maxfiles:
            oldest_file = min(full_paths, key=os.path.getctime)
            os.remove(oldest_file)


def mkdir_recursive(dirpath):
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)


def none_to_empty_list(obj):
    if obj is None:
        return []
    return obj


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



#def get_role_for_current_user():
#    if is_user_logged_in():
#        is_super_user, status_code = request_uma_ticket() # maybe overkill checking this everytime?
#        if is_super_user:
#            return "super_user_role"
#        return "user_role"
#    else:
#        return "readonly_role"


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