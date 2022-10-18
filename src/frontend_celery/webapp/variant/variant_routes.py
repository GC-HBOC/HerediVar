from calendar import c
from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort, jsonify
from flask_paginate import Pagination
from ..utils import *
import sys
from os import path
from .variant_functions import *

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions


variant_blueprint = Blueprint(
    'variant',
    __name__
)


#http:#srv018.img.med.uni-tuebingen.de:5000/search?ranges=chr1%3A0-9999999999999%3Bchr2%3A0-99999999999999999999%3BchrMT%3A0-9999999999999999
@variant_blueprint.route('/search')  # CDH1  chr1:10295758-17027834; chr11:108229378-108229378
@require_login
def search():

    genes = request.args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")

    ranges = request.args.get('ranges', '')
    ranges = preprocess_query(ranges, pattern= r"chr.+:\d+-\d+")
    if ranges is None:
        flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    
    consensus = request.args.getlist('consensus')
    consensus = ';'.join(consensus)
    consensus = preprocess_query(consensus, r'[12345-]?')
    if consensus is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")

    user = request.args.getlist('user')
    user = ';'.join(user)
    user = preprocess_query(user, r'[12345-]?')
    if user is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")

    hgvs = request.args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = r".*:?c\..+")
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! c.HGVS should be prefixed by this pattern: 'transcript:c.' Results are not filtered by hgvs.", "alert-danger")
    if any(not(x.startswith('ENST') or x.startswith('NM') or x.startswith('NR') or x.startswith('XM') or x.startswith('XR')) for x in hgvs):
        flash("You are probably searching for a HGVS c-dot string without knowing its transcript. Be careful with the search results as they might not contain the variant you are looking for!", "alert-warning")

    variant_ids_oi = request.args.get('variant_ids_oi', '')
    variant_ids_oi = preprocess_query(variant_ids_oi, r'\d*')
    if variant_ids_oi is None:
        flash("You have an error in your variant id query(s). It must contain only numbers. Results are not filtered by variants.", "alert-danger")

    page = int(request.args.get('page', 1))
    per_page = 20
    conn = get_connection()
    variants, total = conn.get_variants_page_merged(page, per_page, user_id=session['user']['user_id'], ranges=ranges, genes = genes, consensus=consensus, user=user, hgvs=hgvs, variant_ids_oi=variant_ids_oi)

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('variant/search.html', variants=variants, page=page, per_page=per_page, pagination=pagination)


# chr1-17027834-G-A
@variant_blueprint.route('/create', methods=('GET', 'POST'))
@require_login
def create():
    chrs = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13',
            'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT']
    
    if request.method == 'POST':
        create_variant_from = request.args.get("type")
        
        if create_variant_from == 'vcf':
            chr = request.form.get('chr', '')
            pos = ''.join(request.form['pos'].split())
            ref = request.form.get('ref', '').upper().strip()
            alt = request.form.get('alt', '').upper().strip()

            if not chr or not pos or not ref or not alt or 'genome' not in request.form:
                flash('All fields are required!', 'alert-danger')
            else:
                #try:
                #    pos = int(pos)
                #except:
                #    flash('ERROR: Genomic position is not a valid integer.', 'alert-danger')
                    
                if int(pos) < 0:
                    flash('ERROR: Negative genomic position given, but must be positive.', 'alert-danger')
                else:
                    genome_build = request.form['genome']
                    was_successful = validate_and_insert_variant(chr, pos, ref, alt, genome_build)
                    if was_successful:
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant: " + ' '.join([chr, pos, ref, alt, genome_build]) + ". This information is the unprocessed user input.") 
                        return redirect(url_for('variant.create'))

        if create_variant_from == 'hgvsc':
            reference_transcript = request.form.get('transcript')
            hgvsc = request.form.get('hgvsc')
            if not hgvsc or not reference_transcript:
                flash('All fields are required!', 'alert-danger')
            else:
                chr, pos, ref, alt, possible_errors = functions.hgvsc_to_vcf(reference_transcript + ':' + hgvsc)
                if possible_errors != '':
                    flash(possible_errors, "alert-danger")
                else:
                    was_successful = validate_and_insert_variant(chr, pos, ref, alt, 'GRCh38')
                    if was_successful:
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant from hgvs: " + hgvsc + "Which resulted in this vcf-style variant: " + ' '.join([chr, pos, ref, alt, "GRCh38"]))
                        return redirect(url_for('variant.create'))

    return render_template('variant/create.html', chrs=chrs)


@variant_blueprint.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http:#srv023.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http:#srv023.img.med.uni-tuebingen.de:5000/display/17
@require_login
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = get_connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    current_annotation_status = conn.get_current_annotation_status(variant_id)
    if current_annotation_status is not None:
        if current_annotation_status[4] == 'pending' and current_annotation_status[7] is None:
            celery_task_id = start_annotation_service(variant_id = variant_id)
            current_annotation_status = current_annotation_status[0:7] + (celery_task_id, )

    if request.method == 'POST':
        user_action = request.args.get('action')
        if user_action == 'add_to_list':
            list_id = request.form['list_id']
            conn.add_variant_to_list(list_id, variant_id) # MAYBE add a check that this list belongs to you!
            return redirect(url_for('variant.display', variant_id=variant_id))
        if user_action == 'remove_from_list':
            list_id = request.form['list_id']
            user_id = session['user']['user_id']
            is_list_owner = conn.check_user_list_ownership(user_id, list_id)
            if not is_list_owner:
                current_app.logger.error(session['user']['preferred_username'] + " attempted view list with id " + str(list_id) + ", but this list was not created by him.")
                return abort(403)
            conn.delete_variant_from_list(list_id, variant_id)

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
    if annotations.get('consensus_classification', None) is not None:
        annotations['consensus_classification'] = add_scheme_classes(annotations['consensus_classification'], 14)
        annotations['consensus_classification'] = prepare_scheme_criteria(annotations['consensus_classification'], 14)[0]

    if annotations.get('user_classifications', None) is not None:
        annotations['user_classifications'] = add_scheme_classes(annotations['user_classifications'], 13)
        annotations['user_classifications'] = prepare_scheme_criteria(annotations['user_classifications'], 13)

    lists = conn.get_lists_for_user(user_id = session['user']['user_id'], variant_id=variant_id)

    clinvar_submission = get_clinvar_submission(variant_id, conn)

    return render_template('variant/variant.html', 
                            variant=variant_oi, 
                            annotations = annotations,
                            current_annotation_status=current_annotation_status,
                            clinvar_submission = clinvar_submission,
                            has_multiple_vids=has_multiple_vids,
                            lists = lists
                        )



@variant_blueprint.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
@require_login
def classify(variant_id):
    conn = get_connection()

    user_id = session['user']['user_id']
    schemes_with_info = {user_id: get_schemes_with_info(variant_id, user_id, conn)}
    previous_classification = get_previous_user_classification(variant_id, user_id, conn)
    classification_schemas = conn.get_classification_schemas()
    variant_oi = conn.get_variant_more_info(variant_id)
    if variant_oi is None:
        abort(404)

    do_redirect = False

    if request.method == 'POST':
        ####### classification based on classification scheme submit 
        scheme_id = int(request.form['scheme'])

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        possible_classifications = ["1","2","3","4","5"]

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form, scheme_id, conn)
        scheme_classification_is_valid, message = is_valid_scheme(criteria, classification_schemas[scheme_id])
        without_scheme = scheme_id == 1
        user_classification_is_valid = (str(classification) in possible_classifications) and comment
        
        # actually submit the data to the database
        if (not scheme_classification_is_valid) and (not without_scheme): # error in scheme
            flash(message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a user classification!", "alert-danger")

        if user_classification_is_valid and scheme_classification_is_valid:
            # always handle the user classification
            user_classification_id = handle_user_classification(variant_id, user_id, previous_classification, classification, comment, scheme_id, conn)

            # handle scheme classification -> insert / update criteria
            if not without_scheme:
                if user_classification_id is None: # we are processing an update -> pull the classification id from the schemes with info
                    user_classification_id = schemes_with_info[user_id][scheme_id]['classification_id']
                handle_scheme_classification(user_classification_id, criteria, conn)

            do_redirect = True

    # either redirect or show the webpage depending on success of submission / page reload
    if do_redirect: # do redirect if the submission was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully user-classified variant " + str(variant_id) + " with class " + str(classification))
        return redirect(url_for('variant.classify', variant_id = variant_id))
    else:
        return render_template('variant/classify.html',
                                classification_type='user',
                                variant_oi=variant_oi, 
                                classification_schemas=json.dumps(classification_schemas),
                                schemes_with_info=json.dumps(schemes_with_info), 
                                previous_classification=json.dumps(previous_classification)
                            )




@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission
def consensus_classify(variant_id):
    conn = get_connection()

    classification_schemas = conn.get_classification_schemas()
    variant_oi = conn.get_variant_more_info(variant_id)
    if variant_oi is None:
        abort(404)

    previous_classification = {} # keep empty because we always submit a new consensus classification 
    schemes_with_info = {} # this is used to preselect from previous classify submissions

    # get dict of all previous user classifications
    user_classifications = conn.get_user_classifications(variant_id = variant_id, user_id='all', scheme_id='all')
    if user_classifications is not None:
        for classification in user_classifications:
            current_user_id = classification[3]
            current_schemes_with_info = get_schemes_with_info(variant_id, current_user_id, conn)
            current_schemes_with_info['user'] = conn.get_user(current_user_id)
            schemes_with_info[current_user_id] = current_schemes_with_info

    #print(schemes_with_info)

    do_redirect=False
    if request.method == 'POST':
        ####### classification based on classification scheme submit 
        scheme_id = request.form['scheme']

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        possible_classifications = ["1","2","3","4","5"]

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form, scheme_id, conn)
        scheme_classification_is_valid, message = is_valid_scheme(criteria, classification_schemas[scheme_id])
        without_scheme = scheme_id == 1
        user_classification_is_valid = (str(classification) in possible_classifications) and comment
        
        # actually submit the data to the database
        if (not scheme_classification_is_valid) and (not without_scheme): # error in scheme
            flash(message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a consensus classification", "alert-danger")

        if user_classification_is_valid and scheme_classification_is_valid:
            # insert consensus classification
            classification_id = handle_consensus_classification(variant_id, classification, comment, scheme_id, conn)
            
            # insert scheme criteria
            if not without_scheme:
                handle_scheme_classification(classification_id, criteria, conn, where = "consensus")
            do_redirect = True

    if do_redirect: # do redirect if the submissions was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully consensus-classified variant " + str(variant_id) + " with class " + str(classification) + " from scheme_id " + str(scheme_id))
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))
    else:
        return render_template('variant/classify.html', 
                                classification_type='consensus',
                                variant_oi=variant_oi, 
                                classification_schemas=json.dumps(classification_schemas),
                                schemes_with_info=json.dumps(schemes_with_info), 
                                previous_classification=json.dumps(previous_classification)
                            )



@variant_blueprint.route('/display/<int:variant_id>/classification_history')
@require_login
def classification_history(variant_id):
    conn = get_connection()
    variant_oi = conn.get_variant_more_info(variant_id)
    if variant_oi is None:
        abort(404)
    consensus_classifications = conn.get_consensus_classifications_extended(variant_id, most_recent=False)
    user_classifications = conn.get_user_classifications_extended(variant_id)
    
    recorded_classifications = []
    most_recent_consensus_classification = None
    if consensus_classifications is not None:
        most_recent_consensus_classification = [x for x in consensus_classifications if x[6] == 1][0]
        consensus_classifications = add_scheme_classes(consensus_classifications, 14)
        consensus_classifications = prepare_scheme_criteria(consensus_classifications, 14)
        recorded_classifications.extend([{'type':'consensus classification', 
                                     'submitter': x[9] + ' ' + x[10],
                                     'affiliation':x[11],
                                     'class':x[3], 
                                     'date':x[5], 
                                     # additional information
                                     'comment':x[4], 
                                     'evidence_document_url':url_for('download.evidence_document', consensus_classification_id=x[0]),
                                     'scheme':x[12].replace('_', ' '),
                                     'selected_criteria':x[14],
                                     'class_by_scheme': x[15]
                                    } for x in consensus_classifications])
    if user_classifications is not None:
        user_classifications = add_scheme_classes(user_classifications, 13)
        user_classifications = prepare_scheme_criteria(user_classifications, 13)
        recorded_classifications.extend([{'type':'user classification',
                                          'submitter':x[8] + ' ' + x[9],
                                          'affiliation':x[10],
                                          'class':x[1],
                                          'date':x[5], 
                                          # additional information
                                          'comment':x[4],
                                          'scheme':x[11].replace('_', ' '),
                                          'selected_criteria':x[13],
                                          'class_by_scheme': x[14]
                                        } for x in user_classifications])

    return render_template('variant/classification_history.html', 
                            variant_oi = variant_oi,
                            most_recent_consensus_classification=most_recent_consensus_classification, 
                            recorded_classifications=recorded_classifications)
