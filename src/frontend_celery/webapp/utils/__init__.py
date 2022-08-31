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

def validate_and_insert_variant(chr, pos, ref, alt, genome_build):
    was_successful = True
    # validate request
    tmp_file_path = tempfile.gettempdir() + "/new_variant.vcf"
    tmp_vcfcheck_out_path = tempfile.gettempdir() + "/frontend_variant_import_vcf_errors.txt"
    functions.variant_to_vcf(chr, pos, ref, alt, tmp_file_path)
    

    command = ['/mnt/users/ahdoebm1/HerediVar/src/common/scripts/preprocess_variant.sh', '-i', tmp_file_path, '-o', tmp_vcfcheck_out_path]

    if genome_build == 'GRCh37':
        command.append('-l') # enable liftover
        
    returncode, err_msg, command_output = functions.execute_command(command, 'preprocess_variant')
    #print(err_msg)
    #print(command_output)
    
    if returncode != 0:
        flash(err_msg, 'alert-danger')
        was_successful = False
        return was_successful
    vcfcheck_errors = open(tmp_vcfcheck_out_path + '.pre', 'r').read()
    if 'ERROR:' in vcfcheck_errors:
        flash(vcfcheck_errors.replace('\n', ' '), 'alert-danger')
        was_successful = False
        return was_successful
    if genome_build == 'GRCh37':
        unmapped_variants_vcf = open(tmp_file_path + '.lifted.unmap', 'r')
        unmapped_variant = None
        for line in unmapped_variants_vcf:
            if line.startswith('#') or line.strip() == '':
                continue
            unmapped_variant = line
            break
        unmapped_variants_vcf.close()
        if unmapped_variant is not None:
            flash('ERROR: could not lift variant ' + unmapped_variant, ' alert-danger')
            was_successful = False
            return was_successful
    vcfcheck_errors = open(tmp_vcfcheck_out_path + '.post', 'r').read()
    if 'ERROR:' in vcfcheck_errors:
        flash(vcfcheck_errors.replace('\n', ' '), 'alert-danger')
        was_successful = False
        return was_successful

    if was_successful:
        variant = functions.read_vcf_variant(tmp_file_path)[0] # accessing only the first element of the returned list is save because we process only one variant at a time
        new_chr = variant.CHROM
        new_pos = variant.POS
        new_ref = variant.REF
        new_alt = variant.ALT

        conn = get_connection()
        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt) # check if variant is already contained
        if not is_duplicate:
            # insert it & capture the annotation_queue_id of the newly inserted variant to start the annotation service in celery
            annotation_queue_id = conn.insert_variant(new_chr, new_pos, new_ref, new_alt, chr, pos, ref, alt, user_id = session['user']['user_id'])
            celery_task_id = start_annotation_service(annotation_queue_id = annotation_queue_id) # starts the celery background task
            flash(Markup("Successfully inserted variant: " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + 
                        ' (view your variant <a href="display/chr=' + str(new_chr) + '&pos=' + str(new_pos) + '&ref=' + str(new_ref) + '&alt=' + str(new_alt) + '" class="alert-link">here</a>)'), "alert-success")
        else:
            flash("Variant not imported: already in database!!", "alert-danger")
            was_successful = False

    return was_successful


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
    if current_app.config['TLS']:
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


def request_has_connection():
    return hasattr(g, 'dbconn')

def get_connection():
    if not request_has_connection():
        g.dbconn = Connection()        
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