import sys
from os import path

from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort, jsonify
from flask_paginate import Pagination

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from webapp import tasks
from ..utils import *
from . import variant_functions


variant_blueprint = Blueprint(
    'variant',
    __name__
)


#http:#srv018.img.med.uni-tuebingen.de:5000/search?ranges=chr1%3A0-9999999999999%3Bchr2%3A0-99999999999999999999%3BchrMT%3A0-9999999999999999
# examples range search:
#chr1	10295758	17027835	Pos5	0	+	127479365	127480532	255,0,0
#chr11	108229378	108229379	Neg4	0	-	127480532	127481699	0,0,255
# CDH1  chr1:10295758-17027834; chr11:108229378-108229378
@variant_blueprint.route('/search', methods=('GET', 'POST'))  
@require_permission(['read_resources'])
def search():
    conn = get_connection()
    
    user_id = session['user']['user_id']
    request_args = request.args.to_dict(flat=False)
    request_args = {key: ';'.join(value) for key, value in request_args.items()}

    static_information = search_utils.get_static_search_information(user_id, conn)
    variants, total, page, selected_page_size = search_utils.get_merged_variant_page(request_args, user_id, static_information, conn, flash_messages = True)
    pagination = Pagination(page=page, per_page=selected_page_size, total=total, css_framework='bootstrap5')
    
    # insert variants to list 
    if request.method == 'POST':
        list_id = request.args.get('selected_list_id')
        require_valid(list_id, "user_variant_lists", conn)
        require_list_permission(list_id, ["edit"], conn)
        
        list_variant_import_queue_id = tasks.start_variant_list_import(user_id, list_id, request_args, conn)
        flash("Successfully requested insertion of variants to list from the current search.", "alert-success")
        del request_args["selected_list_id"]
        return redirect(url_for('variant.search', **request_args))

    return render_template('variant/search.html',
                           variants=variants,
                           page=page, 
                           per_page=selected_page_size, 
                           pagination=pagination,
                           static_information = static_information,
                           request_args = request_args
                        )


# chr1-17027834-G-A
@variant_blueprint.route('/create', methods=('GET', 'POST'))
@require_permission(['edit_resources'])
def create():
    conn = get_connection()
    chroms = conn.get_enumtypes("variant", "chr")
    do_redirect = False
    
    if request.method == 'POST':
        user = conn.parse_raw_user(conn.get_user(session["user"]["user_id"]))
        create_result, do_redirect = variant_functions.create_variant_from_request(request, user, conn)
        if not create_result["flash_link"]:
            flash_message = create_result["flash_message"]
        else:
            flash_message = {"message": create_result["flash_message"] + " view the variant ", "link": create_result["flash_link"]}
        flash(flash_message, create_result["flash_class"])

    if do_redirect:
        return redirect(url_for('variant.create'))
    return render_template('variant/create.html', chrs=chroms, vcf_file_import_active=current_app.config["VCF_FILE_IMPORT_ACTIVE"])




@variant_blueprint.route('/create_sv', methods=('GET', 'POST'))
@require_permission(['edit_resources'])
def create_sv():
    conn = get_connection()
    chroms = conn.get_enumtypes("sv_variant", "chrom")
    sv_types = conn.get_enumtypes("sv_variant", "sv_type")
    
    if request.method == 'POST':
        variant_type = request.args.get("type")
        
        if variant_type == 'cnv':
            chrom = request.form.get('chrom', '')
            start = request.form['start']
            end = request.form['end']
            sv_type = request.form.get('sv_type', '')
            imprecise = 1 if request.form.get('imprecise', 'off') == 'on' else 0

            hgvs_strings = request.form.get('hgvs_strings', '')
            hgvs_strings = re.split('[\n,]', hgvs_strings)
            hgvs_strings = [x for x in hgvs_strings if x.strip() != '']

            if not chrom or not start or not end or not sv_type or 'genome' not in request.form:
                flash('All fields are required!', 'alert-danger')
            else: # all valid
                genome_build = request.form['genome']
                was_successful, message, variant_id = tasks.validate_and_insert_cnv(chrom = chrom, start = start, end = end, sv_type = sv_type, imprecise = imprecise, hgvs_strings = hgvs_strings, conn = conn, genome_build = genome_build)
                new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                if 'already in database' in message:
                    flash({"message": "Variant not imported: " + new_variant.get_string_repr() + " already in database! View your variant",
                       "link": url_for("variant.display", variant_id = new_variant.id)}, "alert-danger")
                elif was_successful:
                    flash({"message": "Successfully inserted variant: " + new_variant.get_string_repr() + ". View your variant",
                       "link": url_for("variant.display", variant_id = new_variant.id)}, "alert-success")
                    return redirect(url_for('variant.create_sv'))
                else:
                    flash("There was an error while importing the variant: " + message, "alert-danger")

    return render_template('variant/create_sv.html', chroms=chroms, sv_types=sv_types)



@variant_blueprint.route('/display/<int:variant_id>', methods=['GET'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET']) # alternative url using vcf information
# example: http:#srv018.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http:#srv018.img.med.uni-tuebingen.de:5000/display/17
@require_permission(['read_resources'])
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = get_connection()

    # get variant id from parameters or pull from genomic coordinates
    if variant_id is None:
        require_set(chr, pos, ref, alt)
        variant_id = conn.get_variant_id(chr, pos, ref, alt)
    require_valid(variant_id, "variant", conn)
    
    # get available lists for user
    lists = conn.get_lists_for_user(user_id = session['user']['user_id'], variant_id=variant_id)

    # get current status of clinvar submission
    most_recent_publish_queue = conn.get_most_recent_publish_queue(variant_id = variant_id, upload_clinvar = True)
    publish_queue_ids_oi = conn.get_most_recent_publish_queue_ids_clinvar(variant_id)
    clinvar_queue_entries = check_update_clinvar_status(variant_id, publish_queue_ids_oi, conn)
    clinvar_queue_entry_summary = variant_functions.summarize_clinvar_status(clinvar_queue_entries, most_recent_publish_queue)

    # get current status of heredicare submission
    most_recent_publish_queue = conn.get_most_recent_publish_queue(variant_id = variant_id, upload_heredicare = True)
    publish_queue_ids_oi = conn.get_most_recent_publish_queue_ids_heredicare(variant_id)
    heredicare_queue_entries = check_update_heredicare_status(variant_id, publish_queue_ids_oi, conn)
    heredicare_queue_entry_summary = variant_functions.summarize_heredicare_status(heredicare_queue_entries, most_recent_publish_queue)

    # get the variant and all its annotations
    # get this after updating the upload stati to display the most recent status of each upload
    variant = conn.get_variant(variant_id)

    return render_template('variant/variant.html',
                            lists = lists,
                            variant = variant,
                            is_classification_report = False,
                            clinvar_queue_entries = clinvar_queue_entries,
                            clinvar_queue_entry_summary = clinvar_queue_entry_summary,
                            heredicare_queue_entries = heredicare_queue_entries,
                            heredicare_queue_entry_summary = heredicare_queue_entry_summary
                        )


@variant_blueprint.route('/start_annotation_service', methods=['POST'])
@require_permission(['edit_resources'])
def start_annotation_service():
    conn = get_connection()
    variant_id = request.form.get('variant_id')
    require_valid(variant_id, "variant", conn)

    celery_task_id = tasks.start_annotation_service(variant_id, user_id = session['user']['user_id'], conn = conn)
    return jsonify({}), 202


@variant_blueprint.route('/annotation_status')
@require_permission(['read_resources'])
def annotation_status():
    conn = get_connection()

    variant_id = request.args.get('variant_id')
    require_valid(variant_id, "variant", conn)
    annotation_status = conn.get_current_annotation_status(variant_id) #id, variant_id, user_id, requested, status, finished_at, error_message, celery_task_id

    result = {"status": "no annotation", "requested_at": "", "finished_at": "", "error_message": ""}
    if annotation_status is not None:
        status = annotation_status[4]
        requested_at = annotation_status[3]
        finished_at = annotation_status[5]
        error_message = annotation_status[6]

        result = jsonify({
            "status": status,
            "requested_at": requested_at,
            "finished_at": finished_at,
            "error_message": error_message
        })

    return result






@variant_blueprint.route('/hide_variant/<int:variant_id>', methods=['POST'])
@require_permission(['edit_resources'])
def hide_variant(variant_id):
    conn = get_connection()
    variant = conn.get_variant(variant_id, 
                               include_annotations = False, 
                               include_consensus = False, 
                               include_user_classifications = False, 
                               include_heredicare_classifications = False,
                               include_automatic_classification = False,
                               include_clinvar = False, 
                               include_consequences = False, 
                               include_assays = False, 
                               include_literature = False
                            )
    is_hidden = variant.is_hidden
    conn.hide_variant(variant_id, is_hidden)
    return str(not is_hidden)



@variant_blueprint.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
@require_permission(['edit_resources'])
def classify(variant_id):
    conn = get_connection()

    require_valid(variant_id, "variant", conn)

    variant = conn.get_variant(variant_id)
    user_id = session['user']['user_id']
    previous_classifications = {user_id: functions.list_of_objects_to_dict(variant.get_user_classifications(user_id), key_func = lambda a : a.scheme.id, val_func = lambda a : a.to_dict())}
    classification_schemas = conn.get_classification_schemas()

    #print(previous_classification)

    do_redirect = False
    if request.method == 'POST':
        scheme_id = int(request.form['scheme'])
        classification = request.form['final_class']
        comment = request.form.get('comment', '').strip()
        pmids = request.form.getlist('pmid')
        text_passages = request.form.getlist('text_passage')

        # test if the input is valid
        criteria = variant_functions.extract_criteria_from_request(request.form, scheme_id, conn)
        possible_states = conn.get_enumtypes("user_classification_criteria_applied", "state")
        scheme_classification_is_valid, scheme_message = variant_functions.is_valid_scheme(criteria, classification_schemas.get(scheme_id), possible_states)
        pmids, text_passages = variant_functions.remove_empty_literature_rows(pmids, text_passages)
        literature_is_valid, literature_message = variant_functions.is_valid_literature(pmids, text_passages)
        classification_is_valid = str(classification) in classification_schemas[scheme_id]["final_classes"]

        scheme_id_is_valid = True
        if scheme_id in classification_schemas:
            scheme_class = variant_functions.get_scheme_class(criteria, classification_schemas[scheme_id]['scheme_type'], classification_schemas[scheme_id]['version'])
            scheme_class = scheme_class.json['final_class']
        else:
            flash("Unknown or deprecated classification scheme provided. Please provide a different one.", "alert-danger")
            scheme_id_is_valid = False

        # flash error messages
        if not scheme_classification_is_valid: # error in scheme
            flash(scheme_message, "alert-danger")
        if not classification_is_valid: # error in user classification
            flash("Please provide a valid class to submit a user classification!", "alert-danger")
        if not literature_is_valid:
            flash(literature_message, "alert-danger")

        # actually submit the data to the database
        if classification_is_valid and scheme_classification_is_valid and literature_is_valid and scheme_id_is_valid:
            # insert/update the classification itself
            user_classification_id, classification_received_update, is_new_classification = variant_functions.handle_user_classification(variant, user_id, classification, comment, scheme_id, scheme_class, conn)

            # insert/update selected literature
            previous_selected_literature = [] # a new classification -> no previous sleected literature
            if user_classification_id is None: # we are processing an update -> pull the classification id from the schemes with info
                user_classification_id = previous_classifications[user_id][scheme_id]['id']
                previous_selected_literature = previous_classifications[user_id][scheme_id]['literature']
            literature_received_update = variant_functions.handle_selected_literature(previous_selected_literature, user_classification_id, pmids, text_passages, conn)

            # handle scheme classification -> insert / update criteria
            scheme_received_update = variant_functions.handle_scheme_classification(user_classification_id, criteria, conn)

            if any([classification_received_update, literature_received_update, scheme_received_update]) and not is_new_classification:
                flash({"message": "Successfully updated user classification! View your classification",
                   "link": url_for("variant.display", variant_id = variant.id)}, "alert-success flash_id:successful_user_classification_update")
            else:
                flash({"message": "Successfully inserted new user classification! View your classification",
                   "link": url_for("variant.display", variant_id = variant.id)}, "alert-success flash_id:successful_classification")

            do_redirect = True

    # either redirect or show the webpage depending on success of submission / page reload
    if do_redirect: # do redirect if the submission was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully user-classified variant " + str(variant_id) + " with class " + str(classification))
        return redirect(url_for('variant.classify', variant_id = variant_id))
    else:
        return render_template('variant/classify.html',
                                classification_type='user',
                                variant=variant, 
                                logged_in_user_id = user_id,
                                classification_schemas=classification_schemas,
                                previous_classifications=previous_classifications
                            )




@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission(['admin_resources'])
def consensus_classify(variant_id):
    conn = get_connection()

    require_valid(variant_id, "variant", conn)

    variant = conn.get_variant(variant_id)
    classification_schemas = conn.get_classification_schemas()
    #classification_schemas = {schema_id: classification_schemas[schema_id] for schema_id in classification_schemas} # remove no-scheme classification as this can not be submitted to clinvar

    # this is also used to preselect from previous user classify submissions
    # -1 is the imaginary user id for the consensus classifications
    previous_classifications = {-1: variant.get_recent_consensus_classification_all_schemes(convert_to_dict = True)} 

    # get dict of all previous user classifications
    user_classifications = variant.user_classifications
    if user_classifications is not None:
        for classification in user_classifications:
            current_user_id = classification.submitter.id
            previous_classifications[current_user_id] = functions.list_of_objects_to_dict(variant.get_user_classifications(current_user_id), key_func = lambda a : a.scheme.id, val_func = lambda a : a.to_dict())

    #print(schemes_with_info)

    do_redirect=False
    if request.method == 'POST':
        scheme_id = int(request.form['scheme'])
        classification = request.form['final_class']
        comment = request.form.get('comment', '').strip()
        pmids = request.form.getlist('pmid')
        text_passages = request.form.getlist('text_passage')

        # test if the input is valid
        criteria = variant_functions.extract_criteria_from_request(request.form, scheme_id, conn)
        pmids, text_passages = variant_functions.remove_empty_literature_rows(pmids, text_passages)
        literature_is_valid, literature_message = variant_functions.is_valid_literature(pmids, text_passages)
        possible_states = conn.get_enumtypes("consensus_classification_criteria_applied", "state")
        scheme_classification_is_valid, scheme_message = variant_functions.is_valid_scheme(criteria, classification_schemas[scheme_id], possible_states)

        classification_is_valid = str(classification) in classification_schemas[scheme_id]["final_classes"]

        scheme_id_is_valid = True
        if scheme_id in classification_schemas:
            scheme_class = variant_functions.get_scheme_class(criteria, classification_schemas[scheme_id]['scheme_type'], classification_schemas[scheme_id]['version']) # always calculate scheme class because no scheme is not allowed here!
            scheme_class = scheme_class.json['final_class']
        else:
            flash("Unknown or deprecated classification scheme provided. Please provide a different one.", "alert-danger")
            scheme_id_is_valid = False

        # flash error messages
        if not scheme_classification_is_valid: # error in scheme
            flash(scheme_message, "alert-danger")
        if not classification_is_valid: # error in user classification
            flash("Please provide a final classification and a comment to submit the consensus classification. The classification was not submitted.", "alert-danger")
        if not literature_is_valid:
            flash(literature_message, "alert-danger")

        # actually submit the data to the database
        if classification_is_valid and scheme_classification_is_valid and literature_is_valid and scheme_id_is_valid:
            # insert consensus classification
            classification_id = variant_functions.handle_consensus_classification(variant, classification, comment, scheme_id, pmids, text_passages, criteria, classification_schemas[scheme_id]['description'], scheme_class, conn)

            # insert literature passages
            # classification id never none because we always insert a new classification
            previous_selected_literature = [] # always empty because we always insert a new classification
            _ = variant_functions.handle_selected_literature(previous_selected_literature, classification_id, pmids, text_passages, conn, is_user = False)

            # insert scheme criteria
            _ = variant_functions.handle_scheme_classification(classification_id, criteria, conn, where = "consensus") # always do that because no scheme is not allowed
            variant_functions.add_classification_report(variant.id, conn)
            flash({"message": "Successfully inserted consensus classification! View your classification",
               "link": url_for("variant.display", variant_id = variant.id)}, "alert-success flash_id:successful_classification")
            do_redirect = True

    if do_redirect: # do redirect if the submission was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully consensus-classified variant " + str(variant_id) + " with class " + str(classification) + " from scheme_id " + str(scheme_id))
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))
    else:
        return render_template('variant/classify.html', 
                                classification_type='consensus',
                                variant=variant,
                                classification_schemas=classification_schemas,
                                previous_classifications=previous_classifications
                            )



@variant_blueprint.route('/delete_classification', methods=['GET'])
@require_permission(['edit_resources'])
def delete_classification():
    conn = get_connection()

    user_classification_id = request.args.get('user_classification_id')
    variant_id = request.args.get('variant_id')

    require_valid(variant_id, "variant", conn)
    require_valid(user_classification_id, "user_classification", conn)

    variant = conn.get_variant(variant_id, include_annotations=False, include_consensus=False, include_heredicare_classifications=False, include_clinvar=False, include_consequences=False, include_assays=False, include_literature=False, include_external_ids=False)

    user_classification = None
    for cl in variant.user_classifications:
        if str(cl.id) == str(user_classification_id):
            user_classification = cl
    
    if user_classification is None:
        abort(404)
    if user_classification.submitter.id != session['user']['user_id']:
        abort(405, "You are not allowed to delete this classification!")

    conn.delete_user_classification(user_classification_id)

    return "success"


# essentially returns the automatic classification calculated by herediclassify
# this simply reads from the database and does not calculate from scratch!
@variant_blueprint.route('/classify/<int:variant_id>/automatic', methods=['GET'])
@require_permission(['read_resources'])
def automatic_classification(variant_id):
    conn = get_connection()
    
    evidence_type = request.args.get('evidence_type')

    require_valid(variant_id, "variant", conn)
    require_set(evidence_type)

    variant = conn.get_variant(variant_id, include_annotations=False, include_consensus=False, include_user_classifications=False, include_heredicare_classifications=False, include_clinvar=False, include_consequences=False, include_assays=False, include_literature=False, include_external_ids=False)
    
    if variant.automatic_classification is None:
        result = {"scheme_id": None}
    else:
        variant.automatic_classification.criteria = variant.automatic_classification.filter_criteria(evidence_type)
        result = variant.automatic_classification.to_dict()
    return result



@variant_blueprint.route('/display/<int:variant_id>/classification_history')
@require_permission(['read_resources'])
def classification_history(variant_id):
    conn = get_connection()
    require_valid(variant_id, "variant", conn)
    variant = conn.get_variant(variant_id)
    return render_template('variant/classification_history.html', 
                            variant = variant
                        )


# utility for checking a variant for correctness
# essentially uses the same procedure as the import from heredicare
# If this returns a success it is possible to add this variant to 
# heredivar
@variant_blueprint.route('/check', methods=["GET","POST"])
def check():
    conn = get_connection()
    chroms = conn.get_enumtypes("variant", "chr")

    if request.method == "POST":
        variant = {
            'VID': None,
            'CHROM': None,
            'POS_HG19': None,
            'REF_HG19': None,
            'ALT_HG19': None,
            'POS_HG38': None,
            'REF_HG38': None,
            'ALT_HG38': None,
            'REFSEQ': request.form.get('transcript'),
            'CHGVS': request.form.get('hgvsc'),
            'CGCHBOC': None,
            'VISIBLE': 1,
            'GEN': request.form.get("gene"),
            'canon_chrom': '',
            'canon_pos': '',
            'canon_ref': '',
            'canon_alt': '',
            'comment': ''
        }
        genome_build = request.form.get('genome')
        if genome_build == "GRCh38":
            variant["CHROM"] = request.form.get('chrom')
            variant["POS_HG38"] = request.form.get('pos')
            variant["REF_HG38"] = request.form.get('ref')
            variant["ALT_HG38"] = request.form.get('alt')
        elif genome_build == "GRCh37":
            variant["CHROM"] = request.form.get('chrom')
            variant["POS_HG19"] = request.form.get('pos')
            variant["REF_HG19"] = request.form.get('ref')
            variant["ALT_HG19"] = request.form.get('alt')

        status, message = tasks.map_hg38(variant, -1, conn, insert_variant = False, perform_annotation = False, external_ids = None)

        alert_class = "alert-success"
        if status == "error":
            alert_class = "alert-danger"
        flash("Status: " + status, alert_class)
        flash("Message: " + message, alert_class)

    return render_template('variant/check.html',
                            chroms = chroms
                        )


