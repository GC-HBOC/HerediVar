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
from urllib.parse import urlparse, urljoin
from ..tasks import annotate_variant
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






def preprocess_search_query(query):
    res = re.search("(.*)(%.*%)", query)
    ext = ''
    if res is not None:
        query = res.group(1)
        ext = res.group(2)
    query = query.strip()
    if query.startswith(("HGNC:", "hgnc:")):
        return "gene", query[5:]
    if "%gene%" in ext:
        return "gene", query
    if "c." in query or "p." in query or "%hgvs%" in ext:
        return "hgvs", query
    if "-" in query or "%range%" in ext:
        return "range", query
    return "standard", query


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


def preprocess_query(query, pattern = '.*'):
    query = query.strip()
    query = ''.join(re.split('[ \r\f\v]', query)) # remove whitespace except for newline and tab
    pattern = re.compile("^(%s[;,\t\n]*)*$" % (pattern, ))
    result = pattern.match(query)
    #print(result.group(0))
    if result is None:
        return None # means that there is an error!
    # split into list
    query = re.split('[;,\n\t]', query)
    query = [x for x in query if x != '']
    return query


def get_clinvar_submission_status(clinvar_submission_id, headers): # SUB11770209
    base_url = "https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions/%s/actions/" % (clinvar_submission_id, )
    print(base_url)
    resp = requests.get(base_url, headers = headers)
    #print(resp)
    print(resp.json())
    return resp


def get_role_for_current_user():
    is_super_user, status_code = request_uma_ticket() # maybe overkill checking this everytime?
    if is_super_user:
        return "super_user_role"
    return "user_role"


def request_has_connection():
    return hasattr(g, 'dbconn')


def get_connection():
    role = get_role_for_current_user()
    if not request_has_connection():
        g.dbconn = Connection(role)        
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