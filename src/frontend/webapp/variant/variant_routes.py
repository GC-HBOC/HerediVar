from calendar import c
from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort
from flask_paginate import Pagination

from ..utils import *

import datetime
import sys
from os import path

#sys.path.append(path.dirname(path.abspath(__file__)))
from .variant_functions import *

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection






variant_blueprint = Blueprint(
    'variant',
    __name__
)



#http://srv018.img.med.uni-tuebingen.de:5000/search?ranges=chr1%3A0-9999999999999%3Bchr2%3A0-99999999999999999999%3BchrMT%3A0-9999999999999999
@variant_blueprint.route('/search')  # CDH1  chr1:10295758-17027834; chr11:108229378-108229378
@require_login
def search():

    genes = request.args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")

    ranges = request.args.get('ranges', '')
    ranges = preprocess_query(ranges, pattern= "chr.+:\d+-\d+")
    if ranges is None:
        flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    
    consensus = request.args.getlist('consensus')
    consensus = ';'.join(consensus)
    consensus = preprocess_query(consensus, '[12345]?')
    if consensus is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")

    hgvs = request.args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = ".+:c\.\d+[ACGTNacgtn]+>\d+[ACGTNacgtn]+")
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! Results are not filtered by hgvs.", "alert-danger")

    variant_ids_oi = request.args.get('variant_ids_oi', '')
    variant_ids_oi = preprocess_query(variant_ids_oi, '\d*')
    if variant_ids_oi is None:
        flash("You have an error in your variant id query(s). It must contain only numbers. Results are not filtered by variants.", "alert-danger")

    page = int(request.args.get('page', 1))
    per_page = 20
    conn = Connection()
    variants, total = conn.get_variants_page_merged(page, per_page, user_id=session['user']['user_id'], ranges=ranges, genes = genes, consensus=consensus, hgvs=hgvs, variant_ids_oi=variant_ids_oi)
    conn.close()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('variant/search.html', variants=variants, page=page, per_page=per_page, pagination=pagination)



@variant_blueprint.route('/create', methods=('GET', 'POST'))
@require_login
def create():
    chrs = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13',
            'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT']

    if request.method == 'POST':
        create_variant_from = request.args.get("type")
        if create_variant_from == 'vcf':
            chr = request.form['chr']
            pos = ''.join(request.form['pos'].split())
            ref = request.form['ref'].upper().strip()
            alt = request.form['alt'].upper().strip()

            if not chr or not pos or not ref or not alt or 'genome' not in request.form:
                flash('All fields are required!', 'alert-danger')
            else:
                try:
                    if int(pos) < 0:
                        flash('ERROR: Negative genomic position given, but must be positive.', 'alert-danger')
                    else:
                        genome_build = request.form['genome']
                        was_successful = validate_and_insert_variant(chr, pos, ref, alt, genome_build)
                        if was_successful:
                            return redirect(url_for('variant.create'))
                except:
                    flash('ERROR: Genomic position is not a valid integer.', 'alert-danger')


        if create_variant_from == 'hgvsc':
            reference_transcript = request.form['transcript']
            hgvsc = request.form['hgvsc']
            if not hgvsc or not reference_transcript:
                flash('All fields are required!', 'alert-danger')
            else:
                chr, pos, ref, alt, possible_errors = functions.hgvsc_to_vcf(reference_transcript + ':' + hgvsc)
                if possible_errors != '':
                    flash(possible_errors, "alert-danger")
                else:
                    was_successful = validate_and_insert_variant(chr, pos, ref, alt, 'GRCh38')
                    if was_successful:
                        return redirect(url_for('variant.create'))

    return render_template('variant/create.html', chrs=chrs)


@variant_blueprint.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http://srv023.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http://srv023.img.med.uni-tuebingen.de:5000/display/17
@require_login
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = Connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    current_annotation_status = conn.get_current_annotation_status(variant_id)
    if request.method == 'POST':
        user_action = request.args.get('action')
        if user_action == 'add_to_list':
            list_id = request.form['add-to-list']
            conn.add_variant_to_list(list_id, variant_id) # MAYBE add a check that this list belongs to you!
            return redirect(url_for('variant.display', variant_id=variant_id))
        if user_action == 'reannotate' and (current_annotation_status is None or current_annotation_status[4] != 'pending'):
            conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])
            conn.close()
            return redirect(url_for('variant.display', variant_id=variant_id, from_reannotate='True'))

    if request.args.get('from_reannotate', 'False') == 'True':
        variant_oi = conn.get_one_variant(variant_id)
        if variant_oi is None:
            return redirect(url_for('doc.deleted_variant'))
    else:
        variant_oi = get_variant(conn, variant_id) # this redirects to 404 page if the variant was not found
    
    vids = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
    if len(vids) > 1:
        has_multiple_vids = True
    else:
        has_multiple_vids = False
    
    annotations = conn.get_all_variant_annotations(variant_id, group_output=True)
    if annotations.get('consensus_scheme_classifications', None) is not None:
        annotations['consensus_scheme_classifications'] = add_scheme_classes(annotations['consensus_scheme_classifications'], 10)
        annotations['consensus_scheme_classifications'] = prepare_scheme_criteria(annotations['consensus_scheme_classifications'], 10)

    if annotations.get('user_scheme_classifications', None) is not None:
        annotations['user_scheme_classifications'] = add_scheme_classes(annotations['user_scheme_classifications'], 9)
        annotations['user_scheme_classifications'] = prepare_scheme_criteria(annotations['user_scheme_classifications'], 9)

    lists = conn.get_lists_for_user(user_id = session['user']['user_id'], variant_id=variant_id)


    clinvar_submission_id = conn.get_external_ids_from_variant_id(variant_id, id_source="clinvar_submission")
    clinvar_submission = {'status': None, 'date': None, 'message': None}
    if len(clinvar_submission_id) > 1: # this should not happen!
        clinvar_submission_id = clinvar_submission_id[len(clinvar_submission_id) - 1]
        flash("WARNING: There are multiple clinvar submission ids for this variant. There is probably an old clinvar submission somewhere in the system which should be deleted. Using " + str(clinvar_submission_id) + " now.", "alert-warning")
    if len(clinvar_submission_id) == 1: # variant was already submitted to clinvar
        clinvar_submission_id = clinvar_submission_id[0]
    if len(clinvar_submission_id) > 0:
        api_key = os.environ.get('CLINVAR_API_KEY')
        headers = {'SP-API-KEY': api_key, 'Content-type': 'application/json'}
        resp = get_clinvar_submission_status(clinvar_submission_id, headers = headers)
        if resp.status_code not in [200]:
            conn.close()
            raise RuntimeError("Status check failed:\n" + resp.content.decode("UTF-8"))
        response_content = resp.json()['actions'][0]
        clinvar_submission_status = response_content['status']
        clinvar_submission['status'] = clinvar_submission_status
        if clinvar_submission_status in ['submitted', 'processing']:
            clinvar_submission_date = response_content['updated']
            clinvar_submission['date'] = clinvar_submission_date.replace('T', '\n').replace('Z', '')
        else:
            clinvar_submission_file_url = response_content['responses'][0]['files'][0]['url']
            submission_file_response = requests.get(clinvar_submission_file_url, headers = headers)
            if submission_file_response.status_code != 200:
                raise RuntimeError("Status check failed:" + "\n" + clinvar_submission_file_url + "\n" + submission_file_response.content.decode("UTF-8"))
            submission_file_response = submission_file_response.json()
            clinvar_submission_date = submission_file_response['submissionDate']
            clinvar_submission['date'] = clinvar_submission_date
            if clinvar_submission_status == 'error':
                clinvar_submission_messages = submission_file_response['submissions'][0]['errors'][0]['output']['errors']
                clinvar_submission_messages = [x['userMessage'] for x in clinvar_submission_messages]
                clinvar_submission_message = ';'.join(clinvar_submission_messages)
                clinvar_submission['message'] = clinvar_submission_message

    conn.close()
    return render_template('variant/variant.html', 
                            variant=variant_oi, 
                            annotations = annotations,
                            current_annotation_status=current_annotation_status,
                            clinvar_submission = clinvar_submission,
                            has_multiple_vids=has_multiple_vids,
                            lists = lists)





@variant_blueprint.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
@require_login
def classify(variant_id):
    conn = Connection()

    user_id = session['user']['user_id']
    schemes_with_info = {user_id: get_schemes_with_info(variant_id, user_id, conn)}
    previous_classification = get_previous_user_classification(variant_id, user_id, conn)

    variant_oi = conn.get_variant_more_info(variant_id)

    #print(schemes_with_info)

    do_redirect = False

    is_admin, status_code = request_uma_ticket() # checks if the user has rights to access the consensus classification

    if request.method == 'POST':
        
        ####### classification based on classification scheme submit 
        scheme = request.form['scheme']

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        possible_classifications = ["1","2","3","4","5"]

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form)
        scheme_classification_is_valid, message = is_valid_acmg(criteria, scheme)
        user_classification_is_valid = (str(classification) in possible_classifications) and comment
        
        # actually submit the data to the database
        if (not scheme_classification_is_valid) and (scheme != 'none'): # error in scheme
            flash(message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a user classification!", "alert-danger")
        if scheme_classification_is_valid and (scheme != 'none') and user_classification_is_valid: # only if both are valid submit the scheme classification
            # test if the current user already has an acmg classification for this scheme
            if scheme not in schemes_with_info[user_id]:
                conn.insert_user_acmg_classification(variant_id, user_id, scheme)
                acmg_classification_id = conn.get_user_acmg_classification(variant_id, user_id, scheme=scheme)[0][0]
            else:
                acmg_classification_id = schemes_with_info[user_id][scheme]['classification_id']
            handle_acmg_classification(acmg_classification_id, criteria, conn)
        if user_classification_is_valid and ((scheme_classification_is_valid and scheme != 'none') or (scheme == 'none')): # we want to submit the user classification if scheme is none
            handle_user_classification(variant_id, user_id, previous_classification, classification, comment, conn)
            do_redirect = True

    # either redirect or show the webpage depending on success of submission / page reload
    conn.close()
    if do_redirect: # do redirect if one of the submissions was successful
        return redirect(url_for('variant.classify', variant_id = variant_id))
    else:
        return render_template('variant/classify.html',
                                classification_type='user',
                                variant_oi=variant_oi, 
                                schemes_with_info=schemes_with_info, 
                                previous_classification=previous_classification,
                                is_admin=is_admin)


@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission
def consensus_classify(variant_id):
    conn = Connection()

    variant_oi = conn.get_variant_more_info(variant_id)
    previous_classification = get_default_previous_classification() # keep empty because we always submit a new consensus classification 
    schemes_with_info = {} # keep empty because this is used to preselect from previous classify submission

    # get dict of all previous user classifications
    user_acmg_classification = conn.get_user_acmg_classification(variant_id, user_id='all', scheme='all')
    if user_acmg_classification is not None:
        for classification in user_acmg_classification:
            current_user_id = classification[2]
            current_schemes_with_info = get_schemes_with_info(variant_id, current_user_id, conn)
            current_schemes_with_info['user'] = conn.get_user(current_user_id)
            schemes_with_info[current_user_id] = current_schemes_with_info

    print(schemes_with_info)

    do_redirect=False
    if request.method == 'POST':
        print(request.form)

        ####### classification based on classification scheme submit 
        scheme = request.form['scheme']

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        possible_classifications = ["1","2","3","4","5"]

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form)
        scheme_classification_is_valid, message = is_valid_acmg(criteria, scheme)
        user_classification_is_valid = (str(classification) in possible_classifications) and comment
        
        # actually submit the data to the database
        if (not scheme_classification_is_valid) and (scheme != 'none'): # error in scheme
            flash(message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a consensus classification", "alert-danger")
        if scheme_classification_is_valid and (scheme != 'none') and user_classification_is_valid: # only if both are valid submit the scheme classification
            acmg_classification_id = conn.insert_consensus_acmg_classification(session['user']['user_id'], variant_id, scheme)
            #acmg_classification_id = conn.get_consensus_acmg_classification(variant_id, scheme=scheme, most_recent=True)[0][0]
            handle_acmg_classification(acmg_classification_id, criteria, conn)
        if user_classification_is_valid and ((scheme_classification_is_valid and scheme != 'none') or (scheme == 'none')):
            handle_consensus_classification(variant_id, classification, comment, conn)
            flash(Markup("Successfully inserted new consensus classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
            do_redirect = True


    conn.close()
    if do_redirect: # do redirect if one of the submissions was successful
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))
    else:
        return render_template('variant/classify.html', 
                                classification_type='consensus',
                                variant_oi=variant_oi,
                                schemes_with_info=schemes_with_info,
                                previous_classification=previous_classification,
                                is_admin=True)





@variant_blueprint.route('/display/<int:variant_id>/classification_history')
@require_login
def classification_history(variant_id):
    conn = Connection()
    variant_oi = conn.get_variant_more_info(variant_id)
    if variant_oi is None:
        abort(404)
    consensus_classifications = conn.get_consensus_classification(variant_id, sql_modifier=conn.add_userinfo)
    user_classifications = conn.get_user_classifications(variant_id)
    user_scheme_classifications = conn.get_user_acmg_classification(variant_id, sql_modifier=conn.add_userinfo)
    consensus_scheme_classifications = conn.get_consensus_acmg_classification(variant_id, scheme = 'all', most_recent = False, sql_modifier=conn.add_userinfo)
    
    recorded_classifications = []
    most_recent_consensus_classification = None
    # each entry in recorded_classifications is of this form: (type, id, user_id, variant_id, class, comment/evidence, date, is_recent)
    if consensus_classifications is not None:
        most_recent_consensus_classification = [x for x in consensus_classifications if x[6] == 1][0]
        recorded_classifications.extend([{'type':'consensus classification', 
                                     'submitter': x[8] + ' ' + x[9],
                                     'affiliation':x[10],
                                     'class':x[3], 
                                     'date':x[5], 
                                     # additional information
                                     'comment':x[4], 
                                     'evidence_document_url':url_for('download.evidence_document', consensus_classification_id=x[0]) 
                                    } for x in consensus_classifications])
    if user_classifications is not None:
        recorded_classifications.extend([{'type':'user classification',
                                          'submitter':x[8] + ' ' + x[9],
                                          'affiliation':x[10],
                                          'class':x[1],
                                          'date':x[5], 
                                          # additional information
                                          'comment':x[4]
                                        } for x in user_classifications])
    if user_scheme_classifications is not None:
        for entry in user_scheme_classifications:
            current_criteria = conn.get_acmg_criteria(entry[0])
            current_criteria_dict = convert_acmg_criteria_to_dict(current_criteria)
            acmg_class = get_acmg_classification(current_criteria)
            new_classification = {'type':'user scheme classification',
                                  'submitter':entry[6] + ' ' + entry[7],
                                  'affiliation':entry[8],
                                  'class':acmg_class,
                                  'date':entry[4], 
                                  # additional information
                                  'scheme':entry[3].replace('_', ' '),
                                  'selected_criteria':current_criteria_dict
                                }
            recorded_classifications.append(new_classification)
    
    #most_recent_consensus_scheme_classifications = [x for x in consensus_scheme_classifications if x[2] == 1][0]
    #old_consensus_scheme_classifications = [x for x in consensus_scheme_classifications if x[2] == 0]
    if consensus_scheme_classifications is not None:
        for entry in consensus_scheme_classifications:
            current_criteria = conn.get_acmg_criteria(entry[0])
            current_criteria_dict = convert_acmg_criteria_to_dict(current_criteria)
            acmg_class = get_acmg_classification(current_criteria)
            new_classification = {'type':'consensus scheme classification',
                                  'submitter':entry[7] + ' ' + entry[8],
                                  'affiliation':entry[9],
                                  'class':acmg_class,
                                  'date':entry[4], 
                                  # additional information
                                  'scheme':entry[3].replace('_', ' '),
                                  'selected_criteria':current_criteria_dict
                                }
            recorded_classifications.append(new_classification)

    conn.close()
    return render_template('variant/classification_history.html', 
                            variant_oi = variant_oi,
                            most_recent_consensus_classification=most_recent_consensus_classification, 
                            recorded_classifications=recorded_classifications)



