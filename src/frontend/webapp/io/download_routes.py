from turtle import down
from flask import Blueprint, abort, current_app, send_from_directory, send_file, request, flash, redirect, url_for, session, jsonify
from os import path
import sys
from ..utils import require_login
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import io
import datetime
import tempfile
from shutil import copyfileobj
import re


download_blueprint = Blueprint(
    'download',
    __name__
)

# downloads
@download_blueprint.route('/download_evidence_document/<int:consensus_classification_id>')
@require_login
def evidence_document(consensus_classification_id):
    conn = Connection()
    consensus_classification = conn.get_evidence_document(consensus_classification_id)
    conn.close()
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
    
    return send_file(buffer, as_attachment=True, attachment_filename=report_filename, mimetype='application/pdf')


@download_blueprint.route('/import-variants/summary/download?file=<string:log_file>')
@require_login
def log_file(log_file):
    logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
    return send_from_directory(directory=logs_folder, path='', filename=log_file)


@download_blueprint.route('/download/vcf?variant_id=<int:variant_id>')
@download_blueprint.route('/download/vcf?list_id=<int:list_id>')
@require_login
def variant(variant_id = None, list_id = None):
    conn = Connection()
    
    # check if the logged in user is the owner of this list
    if list_id is not None:
        user_id = session['user']['user_id']
        is_list_owner = conn.check_user_list_ownership(user_id, list_id)
        if not is_list_owner:
            return redirect(url_for('doc.error', code='403', text='No permission to view this variant list!'))

        variants_oi = conn.get_variant_ids_from_list(list_id)

    if variant_id is not None:
        variants_oi = [variant_id]
    


    final_info_headers = {}
    all_variant_vcf_lines = []
    for variant_id in variants_oi:
        variant_vcf, info_headers = get_variant_vcf_line(variant_id, conn)
        all_variant_vcf_lines.append(variant_vcf)
        final_info_headers = merge_info_headers(final_info_headers, info_headers)
        
    conn.close()
    


    helper = io.StringIO()
    printable_info_headers = list(final_info_headers.values())
    printable_info_headers.sort()
    functions.write_vcf_header(printable_info_headers, helper.write, tail='\n')
    for line in all_variant_vcf_lines:
        helper.write(line + '\n')


    buffer = io.BytesIO()
    buffer.write(helper.getvalue().encode())
    buffer.seek(0)


    temp_file_path = tempfile.gettempdir() + "/variant_download.vcf"
    with open(temp_file_path, 'w') as tf:
        helper.seek(0)
        copyfileobj(helper, tf)
    helper.close()

    returncode, err_msg, vcf_errors = functions.check_vcf(temp_file_path)

    if returncode != 0:
        flash("ERROR: VCF could not be checked! Reason: " + err_msg, "alert-danger")
        return redirect(url_for('variant.display', variant_id=variant_id))
    if vcf_errors != '':
        for line in vcf_errors.split('\n'):
            if line.startswith('WARNING') or line.startswith('ERROR'):
                flash("The generated VCF contains errors: " + line, "alert-warning")
                flash("Ask an admin to fix this issue!", "alert-danger")
                return redirect(url_for('variant.display', variant_id=variant_id))

    return send_file(buffer, as_attachment=True, attachment_filename="variant_" + str(variant_id) + ".vcf", mimetype="text/vcf")


def merge_info_headers(old_headers, new_headers):
    return {**old_headers, **new_headers}



def get_variant_vcf_line(variant_id, conn):
    variant_oi = conn.get_one_variant(variant_id)

    annotations = conn.get_all_variant_annotations(variant_id)
    
    #"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
    variant_vcf = '\t'.join((str(variant_oi[1]), str(variant_oi[2]), str(variant_oi[0]), str(variant_oi[3]), str(variant_oi[4]), '.', '.'))

    info = ''
    info_headers = {}
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
                current_submission_string = '|'.join([submission[2], submission_date, submission[4], submission[5][0] + ':' + submission[5][1], submission[6], str(submission[7])])
                current_submission_string = functions.make_vcf_safe(current_submission_string)
                all_submission_strings = functions.collect_info(all_submission_strings, '', current_submission_string, sep = '&')
            info = functions.collect_info(info, 'clinvar_submissions=', all_submission_strings)
        
        elif key == 'clinvar_variant_annotation':
            content = annotations[key]
            # no versioning
            info_headers['clinvar_variant_annotation'] = '##INFO=<ID=clinvar_summary,Number=.,Type=String,Description="summary of the clinvar submissions">\n'
            value = content[4] + ':' + content[3]
            value = functions.make_vcf_safe(value)
            info = functions.collect_info(info, 'clinvar_summary=', value)

        elif key == 'variant_consequences':
            # no versioning
            info_headers['variant_consequences'] = '##INFO=<ID=consequences,Number=.,Type=String,Description="An & separated list of variant consequences from vep. Format:Transcript|hgvsc|hgvsp,consequence|impact|exonnr|intronnr|genesymbol|proteindomain|isgencodebasic|ismaneselect|ismaneplusclinical|isensemblcanonical">\n'
            all_consequence_strings = ''
            for consequence in annotations['variant_consequences']:
                consequence = [str(x) for x in consequence]
                current_consequence_string = '|'.join(consequence[0:8] + consequence[13:17])
                current_consequence_string = functions.make_vcf_safe(current_consequence_string)
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
            consensus_classification = annotations['consensus_classification']
            submission_date = consensus_classification[5].strftime('%Y-%m-%d')
            # no versioning - handled by consensus_date info column
            info_headers['consensus_class'] = '##INFO=<ID=consensus_class,Number=1,Type=Integer,Description="The recent consensus classification by the VUS-task-force.">\n'
            info = functions.collect_info(info, 'consensus_class=', consensus_classification[3])
            info_headers['consensus_comment'] = '##INFO=<ID=consensus_comment,Number=1,Type=String,Description="The comment for the consensus classification by the VUS-task-force.">\n'
            info = functions.collect_info(info, 'consensus_comment=', functions.make_vcf_safe(consensus_classification[3]))
            info_headers['consensus_date'] = '##INFO=<ID=consensus_date,Number=1,Type=String,Description="The submission date of the most recent consensus classification.">\n'
            info = functions.collect_info(info, 'consensus_date=', functions.make_vcf_safe(submission_date))
    
        elif key == 'user_classifications':
            # no versioning - handled by date field
            info_headers['user_classifications'] = '##INFO=<ID=user_classifications,Number=.,Type=String,Description="Classifications by individual users of HerediVar. Format:class|user|comment|date">\n'
            all_user_classifications = ''
            for classification in annotations['user_classifications']:
                current_user_classification = '|'.join([classification[1], classification[8] + '_' + classification[9], classification[4], classification[5].strftime('%Y-%m-%d')])
                current_user_classification = functions.make_vcf_safe(current_user_classification)
                all_user_classifications = functions.collect_info(all_user_classifications, '', current_user_classification, sep = '&')
            info = functions.collect_info(info, 'user_classifications=', all_user_classifications)

        elif key == 'heredicare_center_classifications':
            # no versioning - handled by date field
            info_headers['heredicare_center_classifications'] = '##INFO=<ID=heredicare_center_classifications,Number=.,Type=String,Description="An & separated list of the variant classifications from centers imported from HerediCare. Format:class|center|comment|date">\n'
            all_center_classifications = ''
            for classification in annotations['heredicare_center_classifications']:
                current_center_classification = '|'.join([classification[1], classification[3], classification[4], classification[5].strftime('%Y-%m-%d')])
                current_center_classification = functions.make_vcf_safe(current_center_classification)
                all_center_classifications = functions.collect_info(all_center_classifications, '', current_center_classification, sep = '&')
            info = functions.collect_info(info, 'heredicare_center_classifications=', all_center_classifications)
        
        else: # scores and other non-special values
            content = annotations[key]
            key_and_date = key + '_' + content[2].strftime('%Y%m%d')
            version_num = content[1]
            if version_num == '':
                version_num = '-'
            info_headers[key_and_date] = '##INFO=<ID=' + key_and_date + ',Number=.,Type=String,Description="' + content[0] + ' version: ' + version_num + ', version date: ' + content[2].strftime('%Y-%m-%d') + '">\n'
            value = content[4]
            value = functions.make_vcf_safe(value)
            info = functions.collect_info(info, key_and_date + '=', value)

    if info == '':
        info = '.'


    return variant_vcf + '\t' + info, info_headers



# example
@download_blueprint.route('/calculate_class/<string:scheme>/<string:selected_classes>')
@download_blueprint.route('/calculate_class/<string:scheme>/')
@download_blueprint.route('/calculate_class/<string:scheme>')
def calculate_class(scheme, selected_classes = ''):
    selected_classes = selected_classes.split('+')
    #scheme = request.args.get('scheme')

    final_class = None
    if 'acmg' in scheme:
        selected_classes = [re.sub(r'[0-9]+', '', x) for x in selected_classes] # remove numbers from critera if there are any
        class_counts = get_class_counts(selected_classes) # count how often we have each strength
        #print(class_counts)
        possible_classes = get_possible_classes_acmg(class_counts) # get a set of possible classes depending on selected criteria following PMC4544753
        final_class = decide_for_class_acmg(possible_classes) # decide for class follwing the original publicatoin of ACMG (PMC4544753)
    
    if 'task-force' in scheme:
        final_class = decide_for_class_task_force(selected_classes)

    if final_class is None:
        raise RuntimeError('The class could not be calculated with given parameters. Did you specify a supported scheme? (either acmg or VUS task-force based)')

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
        final_class = 2

    # if there is only one possibility choose it
    elif len(possible_classes) == 1:
        final_class = list(possible_classes)[0]

    # uncertain significance if no other criteria match
    elif len(possible_classes) == 0:
        final_class = 3
    
    return final_class