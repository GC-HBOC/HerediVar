from flask import Blueprint, abort, current_app, send_from_directory, send_file, request, flash, redirect, url_for, session, jsonify, Markup, make_response
from os import path
import sys

from ..utils import require_permission, get_connection, get_preferred_username, remove_oldest_file, mkdir_recursive
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import common.paths as paths
import io
import tempfile
from shutil import copyfileobj
import re
import os
import uuid
import pathlib


download_blueprint = Blueprint(
    'download',
    __name__
)

# downloads
@download_blueprint.route('/download/evidence_document/<int:consensus_classification_id>')
@require_permission(['read_resources'])
def evidence_document(consensus_classification_id):
    conn = get_connection()
    consensus_classification = conn.get_evidence_document(consensus_classification_id)
    if consensus_classification is None:
        abort(404)
    b_64_report = consensus_classification[0]

    #report_folder = path.join(path.dirname(current_app.root_path), current_app.config['CONSENSUS_CLASSIFICATION_REPORT_FOLDER'])
    report_filename = 'consensus_classification_report_' + str(consensus_classification_id) + '.pdf'
    #report_path = path.join(report_folder, report_filename)
    #functions.base64_to_file(base64_string = b_64_report, path = report_path)

    buffer = io.BytesIO()
    buffer.write(functions.decode_base64(b_64_report))
    buffer.seek(0)

    current_app.logger.info(session['user']['preferred_username'] + " downloaded consensus classification evidence document for consensus classification " + str(consensus_classification_id))
    
    return send_file(buffer, as_attachment=True, download_name=report_filename, mimetype='application/pdf')



@download_blueprint.route('/download/assay_report/<int:assay_id>')
@require_permission(['read_resources'])
def assay_report(assay_id):
    conn = get_connection()
    assay = conn.get_assay_report(assay_id)
    if assay is None:
        abort(404)

    b_64_assay = assay[0]
    print(b_64_assay)
    filename = assay[1]

    buffer = io.BytesIO()
    buffer.write(functions.decode_base64(b_64_assay))
    buffer.seek(0)

    current_app.logger.info(session['user']['preferred_username'] + " downloaded assay " + str(assay_id))
    
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application')



@download_blueprint.route('/import-variants/summary/download?file=<string:log_file>')
@require_permission(['read_resources'])
def log_file(log_file):
    logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
    return send_from_directory(directory=logs_folder, path='', filename=log_file)



# listens on get parameter: raw
@download_blueprint.route('/download/vcf/classified')
def classified_variants():
    return_raw = request.args.get('raw')
    classified_variants_folder = current_app.static_folder + "/files/classified_variants"
    last_dump_path = classified_variants_folder + "/.last_dump.txt"
    force_url = url_for("download.classified_variants", raw=return_raw, force = True)
    redirect_url = url_for("main.index")

    if os.path.isfile(last_dump_path):
        with open(last_dump_path, 'r') as last_dump_file:
            last_dump_date = last_dump_file.read()
    else: # generate a new file if it is missing...
        generate_consensus_only_vcf()
        with open(last_dump_path, 'r') as last_dump_file:
            last_dump_date = last_dump_file.read()
    
    path_to_download = classified_variants_folder + "/" + last_dump_date + ".vcf"
    returncode, err_msg, vcf_errors = functions.check_vcf(path_to_download)

    if returncode != 0:
        if request.args.get('force') is None:
            flash(Markup("Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + "<br> Click <a href=" + force_url + " class='alert-link'>here</a> to download it anyway."), "alert-danger")
            current_app.logger.error(get_preferred_username() + " tried to download a all classified variants as vcf, but it contains errors: " + vcf_errors)
            return redirect(redirect_url)

    if return_raw is not None:
        with open(path_to_download, "r") as file_to_download:
            download_text = file_to_download.read()
            resp = make_response(download_text, 200)
            resp.mimetype = "text/plain"
            return resp
    else:
        return send_file(path_to_download, download_name="HerediVar-classified-" + functions.get_today(), as_attachment=True, mimetype="text/vcf")  

def generate_consensus_only_vcf():
    classified_variants_folder = current_app.static_folder + "/files/classified_variants"
    mkdir_recursive(classified_variants_folder)
    last_dump_path = classified_variants_folder + "/.last_dump.txt"
    last_dump_date = functions.get_today()
    path_to_download = classified_variants_folder + "/" + last_dump_date + ".vcf"

    remove_oldest_file(classified_variants_folder, maxfiles=10)

    conn = Connection(['read_only'])
    variant_ids_oi = conn.get_variant_ids_with_consensus_classification()
    vcf_file_buffer, x, xx, xxx = get_vcf(variant_ids_oi, conn, get_variant_vcf_line_only_consensus)
    functions.buffer_to_file_system(vcf_file_buffer, path_to_download)
    conn.close()

    with open(last_dump_path, 'w') as last_dump_file:
        last_dump_file.write(functions.get_today())


def get_variant_vcf_line_only_consensus(variant_id, conn: Connection):
    variant = conn.get_variant(variant_id)
    headers, info = variant.to_vcf(simple = True)

    return headers, info



# listens on get parameter: list_id
@download_blueprint.route('/download/vcf/variant_list')
@require_permission(['read_resources'])
def variant_list():
    conn = get_connection()

    list_id = request.args.get('list_id')
    if list_id is None:
        return abort(404)
    variant_ids_oi = None
    # check that the logged in user is the owner of this list
    if list_id is not None:
        user_id = session['user']['user_id']
        list_permissions = conn.check_list_permission(user_id, list_id)
        if not list_permissions['read']:
            current_app.logger.error(session['user']['preferred_username'] + " attempted download of list with id " + str(list_id) + ", but the user had no permission to do so.")
            return abort(403)
        variant_ids_oi = conn.get_variant_ids_from_list(list_id)    
    if variant_ids_oi is None:
        abort(505, "No variants were found for download. Remember to put arguments list_id in url get parameters.")

    force_url = url_for("download.variant_list", list_id = list_id, force = True)
    redirect_url = url_for("user.my_lists", view = list_id)
    download_file_name = "list_" + str(list_id) + ".vcf"

    vcf_file_buffer, status, vcf_errors, err_msg = get_vcf(variant_ids_oi, conn)

    if status == "redirect":
        flash(Markup("Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + "<br> Click <a href=" + force_url + " class='alert-link'>here</a> to download it anyway."), "alert-danger")
        current_app.logger.error(session['user']['preferred_username'] + " tried to download a vcf which contains errors: " + vcf_errors + ". For variant list " + str(list_id))
        return redirect(redirect_url)

    current_app.logger.info(session['user']['preferred_username'] + " downloaded vcf of variant list: " + str(list_id))
    
    return send_file(vcf_file_buffer, as_attachment=True, download_name=download_file_name, mimetype="text/vcf")



# listens on get parameter: variant_id
@download_blueprint.route('/download/vcf/one_variant')
@require_permission(['read_resources'])
def variant():
    conn = get_connection()

    variant_id = request.args.get('variant_id')
    if variant_id is None:
        return abort(404)

    force_url = url_for("download.variant", variant_id = variant_id, force=True)
    redirect_url = url_for('variant.display', variant_id = variant_id)
    download_file_name = "variant_" + str(variant_id) + ".vcf"

    vcf_file_buffer, status, vcf_errors, err_msg = get_vcf([variant_id], conn)

    if status == 'redirect':
        flash(Markup("Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + "<br> Click <a href=" + force_url + " class='alert-link'>here</a> to download it anyway."), "alert-danger")
        current_app.logger.error(get_preferred_username() + " tried to download a vcf which contains errors: " + vcf_errors + ". For variant ids: " + str(variant_id))
        return redirect(redirect_url)

    current_app.logger.info(get_preferred_username() + " downloaded vcf of variant id: " + str(variant_id))

    return send_file(vcf_file_buffer, as_attachment=True, download_name=download_file_name, mimetype="text/vcf")



def merge_info_headers(old_headers, new_headers):
    return {**old_headers, **new_headers}


def get_variant_vcf_line(variant_id, conn: Connection):
    variant = conn.get_variant(variant_id)
    # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
    headers, info = variant.to_vcf()
    return headers, info



def get_vcf(variants_oi, conn, worker=get_variant_vcf_line):
    status = 'success'

    final_info_headers = {}
    all_variant_vcf_lines = []
    for id in variants_oi:
        info_headers, variant_vcf = worker(id, conn)
        all_variant_vcf_lines.append(variant_vcf)
        final_info_headers = merge_info_headers(final_info_headers, info_headers)
    
    helper = io.StringIO()
    printable_info_headers = list(final_info_headers.values())
    printable_info_headers.sort()
    functions.write_vcf_header(printable_info_headers, helper.write, tail='\n')
    for line in all_variant_vcf_lines:
        helper.write(line + '\n')

    buffer = io.BytesIO()
    buffer.write(helper.getvalue().encode())
    buffer.seek(0)

    temp_file_path = tempfile.gettempdir() + "/variant_download_" + str(uuid.uuid4()) + ".vcf"
    with open(temp_file_path, 'w') as tf:
        helper.seek(0)
        copyfileobj(helper, tf)
    helper.close()

    returncode, err_msg, vcf_errors = functions.check_vcf(temp_file_path)

    os.remove(temp_file_path)

    if returncode != 0:
        if request.args.get('force') is None:
            status = "redirect"
            return None, status, vcf_errors, err_msg

    return buffer, status, "", ""




# example
@download_blueprint.route('/calculate_class/<string:scheme_type>/<string:selected_classes>')
@download_blueprint.route('/calculate_class/<string:scheme_type>/')
@download_blueprint.route('/calculate_class/<string:scheme_type>')
def calculate_class(scheme_type, selected_classes = ''):
    scheme_type = scheme_type.lower()

    if scheme_type == "none":
        return jsonify({'final_class': '-'})

    selected_classes = selected_classes.split('+')
    #scheme = request.args.get('scheme')

    print(selected_classes)

    final_class = None
    if scheme_type == 'acmg':
        selected_classes = [re.sub(r'[0-9]+', '', x) for x in selected_classes] # remove numbers from critera if there are any
        class_counts = get_class_counts(selected_classes) # count how often we have each strength
        #print(class_counts)
        possible_classes = get_possible_classes_acmg(class_counts) # get a set of possible classes depending on selected criteria following PMC4544753
        final_class = decide_for_class_acmg(possible_classes) # decide for class follwing the original publicatoin of ACMG (PMC4544753)
    
    if scheme_type == 'task-force':
        final_class = decide_for_class_task_force(selected_classes)

    if final_class is None:
        raise RuntimeError('The class could not be calculated with given parameters. Did you specify a supported scheme? (either "acmg" or VUS "task-force" based)')

    result = {'final_class': final_class}
    return jsonify(result)


def decide_for_class_task_force(selected_classes):
    if '1.1' in selected_classes:
        return 1
    if '2.1' in selected_classes:
        return 2
    if any(x in ['5.1', '5.2', '5.3', '5.4', '5.5', '5.6'] for x in selected_classes):
        return 5
    if any(x in ['1.2', '1.3'] for x in selected_classes):
        return 1
    if any(x in ['2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8', '2.9', '2.10'] for x in selected_classes):
        return 2
    if any(x in ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7', '4.8', '4.9'] for x in selected_classes):
        return 4
    #if any(x in ['3.1', '3.2', '3.3', '3.4', '3.5'] for x in selected_classes):
    #    return 3
    return 3



def get_class_counts(data):
    result = {'pvs':0, 'ps':0, 'pm':0, 'pp':0, 'bp':0, 'bs':0, 'ba':0}
    for key in result:
        result[key] = sum(key in x for x in data)
    return result


def get_possible_classes_acmg(class_counts):
    
    possible_classes = set()

    # numbering comments are nubmers from the official ACMG paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4544753/ (TABLE 5)
    # pathogenic
    if class_counts['pvs'] == 1: # 1
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2: # 2 
        possible_classes.add(5)
    if class_counts['ps'] == 1: # 3
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pm'] == 1: # 1
        possible_classes.add(4)
    if class_counts['ps'] == 1 and (1 <= class_counts['pm'] <= 2): # 2
        possible_classes.add(4)
    if class_counts['ps'] == 1 and class_counts['pp'] >= 2: # 3
        possible_classes.add(4)
    if class_counts['pm'] >= 3: # 4
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2: # 5
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4: # 6
        possible_classes.add(4)

    # benign
    if class_counts['ba'] == 1: # 1
        possible_classes.add(1)
    if class_counts['bs'] >=2: # 2
        possible_classes.add(1)
    
    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1: # 1
        possible_classes.add(2)
    if class_counts['bp'] >= 2: # 2
        possible_classes.add(2)
    
    #print(selected_classes)
    #print(class_counts)
    #print(possible_classes)

    return possible_classes



def decide_for_class_acmg(possible_classes):
    # uncertain significance if criteria for benign and pathogenic are contradictory
    if (1 in possible_classes or 2 in possible_classes) and (4 in possible_classes or 5 in possible_classes):
        final_class = 3

    # choose the one with higher significance if there are different pathogenic possibilities
    elif 4 in possible_classes and 5 in possible_classes:
        final_class = 5

    # choose the one with higher significance if there are different benign possibilities
    elif 1 in possible_classes and 2 in possible_classes:
        final_class = 1

    # if there is only one possibility choose it
    elif len(possible_classes) == 1:
        final_class = list(possible_classes)[0]

    # uncertain significance if no other criteria match
    elif len(possible_classes) == 0:
        final_class = 3
    
    return final_class


@download_blueprint.route('/download/refgene_ngsd.gff3')
def refgene_ngsd():
    filename = "refgene_ngsd.gff3"
    return send_from_directory(directory=paths.igv_data_path, path=filename, download_name="refgene_ngsd.gff3", as_attachment=True, mimetype="text")

@download_blueprint.route('/download/hg38.fa')
def ref_genome():
    filename = "GRCh38.fa"
    return send_from_directory(directory=paths.ref_genome_dir, path=filename, download_name="GRCh38.fa", as_attachment=True, mimetype="text")

@download_blueprint.route('/download/hg38.fa.fai')
def ref_genome_index():
    filename = "GRCh38.fa.fai"
    return send_from_directory(directory=paths.ref_genome_dir, path=filename, download_name="GRCh38.fa.fai", as_attachment=True, mimetype="text")

