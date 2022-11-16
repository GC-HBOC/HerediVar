from flask import Blueprint, abort, current_app, send_from_directory, send_file, request, flash, redirect, url_for, session, jsonify, Markup, make_response
from os import path
import sys

from ..utils import require_login, get_connection
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import io
import tempfile
from shutil import copyfileobj
import re
import os
import uuid


download_blueprint = Blueprint(
    'download',
    __name__
)

# downloads
@download_blueprint.route('/download/evidence_document/<int:consensus_classification_id>')
@require_login
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
@require_login
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
@require_login
def log_file(log_file):
    logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
    return send_from_directory(directory=logs_folder, path='', filename=log_file)






# listens on get parameter: raw
@download_blueprint.route('/download/vcf/classified')
def classified_variants():
    return_raw = request.args.get('raw')
    force_url = url_for("download.classified_variants", raw=return_raw, force = True)
    redirect_url = url_for("main.index")

    classified_variants_folder = current_app.static_folder + "/files/classified_variants"
    last_dump_path = classified_variants_folder + "/.last_dump.txt"
    read_from_file = False
    last_dump_date = functions.get_today() # override with last dump date if there is one
    if os.path.isfile(last_dump_path):
        with open(last_dump_path, 'r') as last_dump_file:
            last_dump_date = last_dump_file.read()
            days_since_dump = functions.days_between(functions.get_today(), last_dump_date)
            if days_since_dump <= 7:
                read_from_file = True
            if days_since_dump > 7:
                last_dump_date = functions.get_today()

    path_to_download = classified_variants_folder + "/" + last_dump_date + ".vcf"

    # generate a new vcf file
    if not read_from_file:
        with open(last_dump_path, 'w') as last_dump_file:
            last_dump_file.write(functions.get_today())

        conn = get_connection()
        variants_oi = conn.get_variant_ids_with_consensus_classification()

        vcf_file_buffer, x, xx, xxx = get_vcf(variants_oi, conn)

        functions.buffer_to_file_system(vcf_file_buffer, path_to_download)

    returncode, err_msg, vcf_errors = functions.check_vcf(path_to_download)

    if returncode != 0:
        if request.args.get('force') is None:
            flash(Markup("Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + "<br> Click <a href=" + force_url + " class='alert-link'>here</a> to download it anyway."), "alert-danger")
            current_app.logger.error(session['user']['preferred_username'] + " tried to download a all classified variants as vcf, but it contains errors: " + vcf_errors)
            return redirect(redirect_url)


    current_app.logger.info(session['user']['preferred_username'] + " successfully downloaded vcf of all classified variants.")

    if return_raw is not None:
        with open(path_to_download, "r") as file_to_download:
            download_text = file_to_download.read()
            resp = make_response(download_text, 200)
            resp.mimetype = "text/plain"
            return resp
    else:
        return send_file(path_to_download, as_attachment=True, mimetype="text/vcf")





# listens on get parameter: list_id
@download_blueprint.route('/download/vcf/variant_list')
@require_login
def variant_list():
    conn = get_connection()

    list_id = request.args.get('list_id')
    if list_id is None:
        return abort(404)
    variants_oi = None
    # check that the logged in user is the owner of this list
    if list_id is not None:
        user_id = session['user']['user_id']
        is_list_owner = conn.check_user_list_ownership(user_id, list_id)
        if not is_list_owner:
            current_app.logger.error(session['user']['preferred_username'] + " attempted download of list with id " + str(list_id) + ", but this list was not created by him.")
            return abort(403)
        variants_oi = conn.get_variant_ids_from_list(list_id)    
    if variants_oi is None:
        abort(505, "No variants were found for download. Remember to put arguments list_id in url get parameters.")

    force_url = url_for("download.variant_list", list_id = list_id, force = True)
    redirect_url = url_for("user.my_lists", view = list_id)
    download_file_name = "list_" + str(list_id) + ".vcf"

    vcf_file_buffer, status, vcf_errors, err_msg = get_vcf(variants_oi, conn)

    if status == "redirect":
        flash(Markup("Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + "<br> Click <a href=" + force_url + " class='alert-link'>here</a> to download it anyway."), "alert-danger")
        current_app.logger.error(session['user']['preferred_username'] + " tried to download a vcf which contains errors: " + vcf_errors + ". For variant list " + str(list_id))
        return redirect(redirect_url)

    current_app.logger.info(session['user']['preferred_username'] + " downloaded vcf of variant list: " + str(list_id))
    
    return send_file(vcf_file_buffer, as_attachment=True, download_name=download_file_name, mimetype="text/vcf")



# listens on get parameter: variant_id
@download_blueprint.route('/download/vcf/one_variant')
def variant():
    conn = get_connection()

    variant_oi = request.args.get('variant_id')
    if variant_oi is None:
        return abort(404)

    force_url = url_for("download.variant", variant_id = variant_oi, force=True)
    redirect_url = url_for('variant.display', variant_id = variant_oi)
    download_file_name = "variant_" + str(variant_oi) + ".vcf"

    vcf_file_buffer, status, vcf_errors, err_msg = get_vcf([variant_oi], conn)

    if status == 'redirect':
        flash(Markup("Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + "<br> Click <a href=" + force_url + " class='alert-link'>here</a> to download it anyway."), "alert-danger")
        current_app.logger.error(session['user']['preferred_username'] + " tried to download a vcf which contains errors: " + vcf_errors + ". For variant ids: " + str(variant_oi))
        return redirect(redirect_url)

    current_app.logger.info(session['user']['preferred_username'] + " downloaded vcf of variant id: " + str(variant_oi))

    return send_file(vcf_file_buffer, as_attachment=True, download_name=download_file_name, mimetype="text/vcf")



def get_vcf(variants_oi, conn):
    status = 'success'

    final_info_headers = {}
    all_variant_vcf_lines = []
    for id in variants_oi:
        variant_vcf, info_headers = get_variant_vcf_line(id, conn)
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

    










def merge_info_headers(old_headers, new_headers):
    return {**old_headers, **new_headers}


def get_variant_vcf_line(variant_id, conn):
    variant_oi = conn.get_one_variant(variant_id)

    annotations = conn.get_all_variant_annotations(variant_id)
    external_variant_ids = conn.get_external_ids_from_variant_id(variant_id)
    
    #"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
    variant_vcf = '\t'.join((str(variant_oi[1]), str(variant_oi[2]), str(variant_oi[0]), str(variant_oi[3]), str(variant_oi[4]), '.', '.'))

    info = ''
    info_headers = {}
    # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
    for key in annotations:
        if key == 'clinvar_submissions':
            # no versioning
            info_headers['clinvar_submissions'] = '##INFO=<ID=clinvar_submissions,Number=.,Type=String,Description="An & separated list of clinvar submissions. Format:interpretation|last_evaluated|review_status|submission_condition|submitter|comment">\n'
            all_submission_strings = ''
            for submission in annotations[key]:
                submission_date = submission[3]
                if submission_date is not None:
                    submission_date = submission_date.strftime('%Y-%m-%d')
                else:
                    submission_date = str(submission_date)
                current_submission_string = '~7C'.join([submission[2], submission_date, submission[4], ';'.join([':'.join([submission_condition[0], submission_condition[1]]) for submission_condition in submission[5]]), submission[6], str(submission[7])])
                current_submission_string = functions.encode_vcf(current_submission_string)
                all_submission_strings = functions.collect_info(all_submission_strings, '', current_submission_string, sep = '&')
            info = functions.collect_info(info, 'clinvar_submissions=', all_submission_strings)
        
        elif key == 'clinvar_variant_annotation':
            content = annotations[key]
            # no versioning
            info_headers['clinvar_variant_annotation'] = '##INFO=<ID=clinvar_summary,Number=.,Type=String,Description="summary of the clinvar submissions">\n'
            value = content[4] + ':' + content[3]
            value = functions.encode_vcf(value)
            info = functions.collect_info(info, 'clinvar_summary=', value)

        elif key == 'variant_consequences':
            # no versioning
            info_headers['variant_consequences'] = '##INFO=<ID=consequences,Number=.,Type=String,Description="An & separated list of variant consequences from vep. Format:Transcript|hgvsc|hgvsp,consequence|impact|exonnr|intronnr|genesymbol|proteindomain|isgencodebasic|ismaneselect|ismaneplusclinical|isensemblcanonical">\n'
            all_consequence_strings = ''
            for consequence in annotations['variant_consequences']:
                consequence = [str(x) for x in consequence]
                current_consequence_string = '~7C'.join(consequence[0:8] + consequence[13:17])
                current_consequence_string = functions.encode_vcf(current_consequence_string)
                all_consequence_strings = functions.collect_info(all_consequence_strings, '', current_consequence_string, sep = '&')
            info = functions.collect_info(info, 'consequences=', all_consequence_strings)

        elif key == 'literature':
            # no versioning
            info_headers['literature'] = '##INFO=<ID=pubmed,Number=.,Type=String,Description="An & separated list of pubmed ids relevant for this variant.">\n'
            all_pubmed_ids = ''
            for entry in annotations['literature']:
                all_pubmed_ids = functions.collect_info(all_pubmed_ids, '', entry[2], sep='&')
            info = functions.collect_info(info, 'pubmed=', all_pubmed_ids)
    
        elif key == 'consensus_classification':
            # this has the same format as the individual user_classifications
            info_headers[key] = '##INFO=<ID=' + key + ',Number=1,Type=String,Description="The recent consensus classification by the VUS-task-force. Format: consensus_class|consensus_comment|submission_date|consensus_scheme|consensus_scheme_class|consensus_criteria_string. The consensus criteria string itself is a $ separated list with the Format: criterium_name+criterium_strength+criterium_evidence ">\n'
            consensus_classification = annotations[key][0] # [0], because this contains only the most recent consensus classification
            # no versioning - handled by consensus_date info column
            consensus_class = consensus_classification[3]
            consensus_comment = consensus_classification[4]
            submission_date = consensus_classification[5].strftime('%Y-%m-%d %H:%M:%S')
            consensus_scheme = consensus_classification[12]
            consensus_criteria = consensus_classification[14]
            all_criteria = ""
            consensus_criteria_string = ""
            for criterium in consensus_criteria:
                criterium_name = criterium[5]
                criterium_strength = criterium[7]
                criterium_evidence = criterium[4]
                all_criteria = "+".join([all_criteria, criterium_name])
                new_consensus_criteria_string = "~2B".join([criterium_name, criterium_strength, criterium_evidence]) # sep: +
                consensus_criteria_string = functions.collect_info(consensus_criteria_string, "", new_consensus_criteria_string, sep = "~24") # sep: $
            resp = calculate_class(consensus_classification[13], all_criteria)
            consensus_scheme_class = str(resp.get_json()['final_class'])
            consensus_classification_vcf = "~7C".join([consensus_class, consensus_comment, submission_date, consensus_scheme, consensus_scheme_class, consensus_criteria_string]) # sep: |
            #print("consensus classification: " + functions.encode_vcf(consensus_classification_vcf))
            info = functions.collect_info(info, key + '=', functions.encode_vcf(consensus_classification_vcf))
    
        elif key == 'user_classifications':
            # no versioning - handled by date field
            info_headers[key] = '##INFO=<ID=' + key + ',Number=.,Type=String,Description="Classifications by individual users of HerediVar. Single classifications are separated by & symbols. Format: user_class|user_comment|submission_date|user_scheme|user_scheme_class|user_criteria_string. The user criteria string itself is a $ separated list with the Format: criterium_name+criterium_strength+criterium_evidence ">\n'
            user_classifications_vcf = ''
            user_classifications = annotations[key]
            for user_classification in user_classifications:
                user_class = user_classification[1]
                user_comment = user_classification[4]
                submission_date = user_classification[5].strftime('%Y-%m-%d %H:%M:%S')
                user_scheme = user_classification[11]
                user_criteria = user_classification[13]
                all_criteria = ""
                user_criteria_string = ""
                for criterium in user_criteria:
                    criterium_name = criterium[5]
                    criterium_strength = criterium[7]
                    criterium_evidence = criterium[4]
                    all_criteria = "+".join([all_criteria, criterium_name])
                    new_user_criteria_string = "~2B".join([criterium_name, criterium_strength, criterium_evidence]) # sep: +
                    user_criteria_string = functions.collect_info(user_criteria_string, "", new_user_criteria_string, sep = "~24") # sep: $
                resp = calculate_class(user_classification[12], all_criteria)
                user_scheme_class = str(resp.get_json()['final_class'])
                current_user_classification_vcf = "~7C".join([user_class, user_comment, submission_date, user_scheme, user_scheme_class, user_criteria_string]) # sep: |
                user_classifications_vcf = functions.collect_info(user_classifications_vcf, "", current_user_classification_vcf, sep = "~26") # sep: &
            #print("User classification: " + functions.encode_vcf(user_classifications_vcf))
            info = functions.collect_info(info, key + "=", functions.encode_vcf(user_classifications_vcf))

        elif key == 'heredicare_center_classifications':
            # no versioning - handled by date field
            info_headers['heredicare_center_classifications'] = '##INFO=<ID=heredicare_center_classifications,Number=.,Type=String,Description="An & separated list of the variant classifications from centers imported from HerediCare. Format:class|center|comment|date">\n'
            all_center_classifications = ''
            for classification in annotations['heredicare_center_classifications']:
                current_center_classification = '~7C'.join([classification[1], classification[3], classification[4], classification[5].strftime('%Y-%m-%d')])
                current_center_classification = functions.encode_vcf(current_center_classification)
                all_center_classifications = functions.collect_info(all_center_classifications, '', current_center_classification, sep = '&')
            info = functions.collect_info(info, 'heredicare_center_classifications=', all_center_classifications)
       
        elif key == 'assays':
            content = annotations[key]
            info_key = 'assays'
            info_headers[key] = '##INFO=<ID=' + info_key + ',Number=.,Type=String,Description="All types of assays (e. g. functional or splicing) which were submitted to HerediVar. Assays are separated by "&" symbols. Format:date|assay_type|score.">\n'
            all_assay_strings = ""
            for assay in content:
                assay_type = assay[1]
                score = str(assay[2])
                date = assay[3].strftime('%Y-%m-%d')
                assay_string = '~7C'.join([date, assay_type, score])
                assay_string = functions.encode_vcf(assay_string)
                all_assay_strings = functions.collect_info(all_assay_strings, "", assay_string, sep = '&')
            info = functions.collect_info(info, info_key + "=", all_assay_strings)

        
        else: # scores and other non-special values
            content = annotations[key]
            key_and_date = key + '_' + content[2].strftime('%Y%m%d')
            version_num = content[1]
            if version_num == '' or version_num is None:
                version_num = '-'
            info_headers[key_and_date] = '##INFO=<ID=' + key_and_date + ',Number=.,Type=String,Description="' + content[0] + ' version: ' + version_num + ', version date: ' + content[2].strftime('%Y-%m-%d') + '">\n'
            value = content[4]
            value = functions.encode_vcf(value)
            info = functions.collect_info(info, key_and_date + '=', value)

    all_external_variant_ids_string = ""
    key = "external_ids"
    info_headers[key] = '##INFO=<ID=' + key + ',Number=.,Type=String,Description="All external variant ids recorded in HerediVar. Entries are separated by & symbols. Format:source|id.">\n'
    for entry in external_variant_ids:
        external_variant_id = str(entry[0])
        source = entry[1]
        external_variant_id_string = '~7C'.join([source, external_variant_id])
        external_variant_id_string = functions.encode_vcf(external_variant_id_string)
        all_external_variant_ids_string = functions.collect_info(all_external_variant_ids_string, "", external_variant_id_string, sep = "&")
    info = functions.collect_info(info, key + "=", all_external_variant_ids_string)


    if info == '':
        info = '.'


    return variant_vcf + '\t' + info, info_headers



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