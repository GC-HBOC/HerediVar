from calendar import c
from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort, jsonify
from flask_paginate import Pagination
from ..utils import *
import sys
from os import path
from .variant_functions import *
from ..tasks import generate_consensus_only_vcf_task, start_annotation_service, validate_and_insert_variant, map_hg38

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions


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

    allowed_user_classes = functions.order_classes(conn.get_enumtypes('user_classification', 'classification'))
    allowed_consensus_classes = functions.order_classes(conn.get_enumtypes('consensus_classification', 'classification'))

    genes = extract_genes(request)
    ranges = extract_ranges(request)
    consensus_classifications = extract_consensus_classifications(request, allowed_consensus_classes)
    user_classifications = extract_user_classifications(request, allowed_user_classes)
    hgvs = extract_hgvs(request)
    variant_ids_oi = extract_lookup_list(request, user_id, conn)
    page = int(request.args.get('page', 1))

    sort_bys, page_sizes, selected_page_size, selected_sort_by, include_hidden = extract_search_settings(request)
    
    variants, total = conn.get_variants_page_merged(page=page, page_size=selected_page_size, sort_by=selected_sort_by, include_hidden=include_hidden, user_id=user_id, ranges=ranges, genes = genes, consensus=consensus_classifications, user=user_classifications, hgvs=hgvs, variant_ids_oi=variant_ids_oi)
    lists = conn.get_lists_for_user(user_id)
    pagination = Pagination(page=page, per_page=selected_page_size, total=total, css_framework='bootstrap5')



    # insert variants to list 
    if request.method == 'POST':
        list_id = request.args.get('selected_list_id')
        #print(list_id)
        
        selected_variants = request.args.get('selected_variants', "").split(',')
        select_all_variants = True if request.args.get('select_all_variants', "false") == "true" else False

        if list_id:
            list_permission = conn.check_list_permission(user_id, list_id)
            if not list_permission['owner'] and not list_permission['edit']:
                flash("You attempted to insert variants to a list which you do not have access to.", "alert-danger")
                current_app.logger.info(session['user']['preferred_username'] + " attempted to insert variants from the browse variants page to list: " + str(list_id) + ", but he did not have access to it.")
            else:
                num_inserted = 0
                if select_all_variants:
                    variants_for_list, _ = conn.get_variants_page_merged(1, "unlimited", sort_by=selected_sort_by, include_hidden=include_hidden, user_id=user_id, ranges=ranges, genes = genes, consensus=consensus_classifications, user=user_classifications, hgvs=hgvs, variant_ids_oi=variant_ids_oi)
                    variant_ids = [variant.id for variant in variants_for_list]
                    for variant_id in variant_ids:
                        if str(variant_id) not in selected_variants:
                            conn.add_variant_to_list(list_id, variant_id)
                            num_inserted = num_inserted + 1
                else:
                    for variant_id in selected_variants:
                        variant = conn.get_variant(variant_id)
                        if variant is not None:
                            conn.add_variant_to_list(list_id, variant_id)
                            num_inserted = num_inserted + 1
                flash(Markup("Successfully inserted " + str(num_inserted) + " variant(s) from the current search to the list. You can view your list <a class='alert-link' href='" + url_for('user.my_lists', view=list_id) + "'>here</a>."), "alert-success")
                return redirect(url_for('variant.search', genes=request.args.get('genes'), ranges=request.args.get('ranges'), consensus=request.args.getlist('consensus'), user = request.args.getlist('user'), hgvs= request.args.get('hgvs')))
    return render_template('variant/search.html',
                           variants=variants, page=page, 
                           per_page=selected_page_size, 
                           pagination=pagination, 
                           lists=lists, 
                           sort_bys=sort_bys, 
                           page_sizes=page_sizes,
                           allowed_user_classes = allowed_user_classes,
                           allowed_consensus_classes = allowed_consensus_classes
                        )


# chr1-17027834-G-A
@variant_blueprint.route('/create', methods=('GET', 'POST'))
@require_permission(['edit_resources'])
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
                    was_successful, message, variant_id = validate_and_insert_variant(chr, pos, ref, alt, genome_build, conn = get_connection(), user_id = session['user']['user_id'])
                    conn = get_connection()
                    new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                    if was_successful:
                        flash(Markup("Successfully inserted variant: " + str(new_variant.chrom) + ' ' + str(new_variant.pos) + ' ' + new_variant.ref + ' ' + new_variant.alt + 
                                     ' (view your variant <a href="' + url_for("variant.display", chr=str(new_variant.chrom), pos=str(new_variant.pos), ref=str(new_variant.ref), alt=str(new_variant.alt)) + 
                                     '" class="alert-link">here</a>)'), "alert-success")
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant from vcf which resulted in this vcf-style variant: " + ' '.join([str(new_variant.chrom), str(new_variant.pos), new_variant.ref, new_variant.alt, "GRCh38"]))
                        return redirect(url_for('variant.create'))
                    elif 'already in database' in message:
                        flash(Markup("Variant not imported: already in database!! View it " + 
                                     "<a href=" + url_for("variant.display", chr=str(new_variant.chrom), pos=str(new_variant.pos), ref=str(new_variant.ref), alt=str(new_variant.alt)) + 
                                     " class=\"alert-link\">here</a>"), "alert-danger")
                    else:
                        flash(message, 'alert-danger')

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
                    was_successful, message, variant_id = validate_and_insert_variant(chr, pos, ref, alt, 'GRCh38', conn = get_connection(), user_id = session['user']['user_id'])
                    conn = get_connection()
                    new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                    if was_successful:
                        flash(Markup("Successfully inserted variant: " + str(new_variant.chrom) + ' ' + str(new_variant.pos) + ' ' + new_variant.ref + ' ' + new_variant.alt + 
                                     ' (view your variant <a href="' + url_for("variant.display", chr=str(new_variant.chrom), pos=str(new_variant.pos), ref=str(new_variant.ref), alt=str(new_variant.alt)) + 
                                     '" class="alert-link">here</a>)'), "alert-success")
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant from hgvs: " + hgvsc + "Which resulted in this vcf-style variant: " + ' '.join([str(new_variant.chrom), str(new_variant.pos), new_variant.ref, new_variant.alt, "GRCh38"]))
                        return redirect(url_for('variant.create'))
                    elif 'already in database' in message:
                        flash(Markup("Variant not imported: already in database!! View it " + 
                                     "<a href=" + url_for("variant.display", chr=str(new_variant.chrom), pos=str(new_variant.pos), ref=str(new_variant.ref), alt=str(new_variant.alt)) + 
                                     " class=\"alert-link\">here</a>"), "alert-danger")
                    else:
                        flash(message, 'alert-danger')

    return render_template('variant/create.html', chrs=chrs)



@variant_blueprint.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http:#srv018.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http:#srv018.img.med.uni-tuebingen.de:5000/display/17
@require_permission(['read_resources'])
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = get_connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    current_annotation_status = conn.get_current_annotation_status(variant_id)
    if current_annotation_status is not None:
        if current_annotation_status[4] == 'pending' and current_annotation_status[7] is None:
            celery_task_id = start_annotation_service(variant_id = variant_id, conn = conn, user_id = session['user']['user_id'])
            current_annotation_status = current_annotation_status[0:7] + (celery_task_id, )

    variant = conn.get_variant(variant_id)
    if variant is None:
        # show another error message if the variant was deleted vs the variant does not exist anyway
        if request.args.get('from_reannotate', 'False') == 'True': 
            return redirect(url_for('doc.deleted_variant'))
        else:
            abort(404)  
    
    vids = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
    if len(vids) > 1:
        has_multiple_vids = True
    else:
        has_multiple_vids = False
    
    lists = conn.get_lists_for_user(user_id = session['user']['user_id'], variant_id=variant_id)

    clinvar_submission = check_update_clinvar_status(variant_id, conn)

    print(variant.heredicare_annotations)

    return render_template('variant/variant.html',
                            current_annotation_status=current_annotation_status,
                            clinvar_submission = clinvar_submission,
                            has_multiple_vids=has_multiple_vids,
                            lists = lists,
                            variant = variant,
                            is_classification_report = False
                        )


@variant_blueprint.route('/hide_variant/<int:variant_id>', methods=['POST'])
@require_permission(['admin_resources'])
def hide_variant(variant_id):
    conn = get_connection()
    variant = conn.get_variant(variant_id, 
                               include_annotations = False, 
                               include_consensus = False, 
                               include_user_classifications = False, 
                               include_heredicare_classifications = False, 
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

    variant = conn.get_variant(variant_id, include_annotations=True, include_heredicare_classifications=True, include_clinvar=True, include_assays=True)
    if variant is None:
        return abort(404)

    allowed_classes = conn.get_enumtypes('user_classification', 'classification')

    user_id = session['user']['user_id']
    previous_classifications = {user_id: functions.list_of_objects_to_dict(variant.get_user_classifications(user_id), key_func = lambda a : a.scheme.id, val_func = lambda a : a.to_dict())}
    classification_schemas = conn.get_classification_schemas()

    #print(previous_classification)


    do_redirect = False
    if request.method == 'POST':
        ####### classification based on classification scheme submit
        scheme_id = int(request.form['scheme'])

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        pmids = request.form.getlist('pmid')
        text_passages = request.form.getlist('text_passage')

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form, scheme_id, conn)
        scheme_classification_is_valid, scheme_message = is_valid_scheme(criteria, classification_schemas[scheme_id])
        pmids, text_passages = remove_empty_literature_rows(pmids, text_passages)
        literature_is_valid, literature_message = is_valid_literature(pmids, text_passages)
        
        without_scheme = scheme_id == 1
        user_classification_is_valid = (str(classification) in allowed_classes) and comment

        scheme_class = '-'
        if not without_scheme:
            scheme_class = get_scheme_class(criteria, classification_schemas[scheme_id]['scheme_type'])
            scheme_class = scheme_class.json['final_class']

        # flash error messages
        if (not scheme_classification_is_valid) and (not without_scheme): # error in scheme
            flash(scheme_message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a user classification!", "alert-danger")
        if not literature_is_valid:
            flash(literature_message, "alert-danger")

        # actually submit the data to the database
        if user_classification_is_valid and scheme_classification_is_valid and literature_is_valid:
            # always handle the user classification & literature
            user_classification_id, classification_received_update, is_new_classification = handle_user_classification(variant, user_id, classification, comment, scheme_id, scheme_class, conn)
            previous_selected_literature = [] # a new classification -> no previous sleected literature
            if user_classification_id is None: # we are processing an update -> pull the classification id from the schemes with info
                user_classification_id = previous_classifications[user_id][scheme_id]['id']
                previous_selected_literature = previous_classifications[user_id][scheme_id]['literature']
            literature_received_update = handle_selected_literature(previous_selected_literature, user_classification_id, pmids, text_passages, conn)

            # handle scheme classification -> insert / update criteria
            scheme_received_update = False
            if not without_scheme:
                scheme_received_update = handle_scheme_classification(user_classification_id, criteria, conn)

            if any([classification_received_update, literature_received_update, scheme_received_update]) and not is_new_classification:
                flash(Markup("Successfully updated user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")

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
                                previous_classifications=previous_classifications,
                                allowed_classes = allowed_classes
                            )




@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission(['admin_resources'])
def consensus_classify(variant_id):
    conn = get_connection()

    allowed_classes = conn.get_enumtypes('consensus_classification', 'classification')

    #literature = conn.get_variant_literature(variant_id)
    classification_schemas = conn.get_classification_schemas()
    classification_schemas = {schema_id: classification_schemas[schema_id] for schema_id in classification_schemas if classification_schemas[schema_id]['scheme_type'] != "none"} # remove no-scheme classification as this can not be submitted to clinvar
    variant = conn.get_variant(variant_id)
    if variant is None:
        return abort(404)

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

        if scheme_id == 1:
            flash("No consensus classifications without scheme allowed!")
        else:
            classification = request.form['final_class']
            comment = request.form['comment'].strip()
            pmids = request.form.getlist('pmid')
            text_passages = request.form.getlist('text_passage')

            # test if the input is valid
            criteria = extract_criteria_from_request(request.form, scheme_id, conn)
            pmids, text_passages = remove_empty_literature_rows(pmids, text_passages)
            literature_is_valid, literature_message = is_valid_literature(pmids, text_passages)
            scheme_classification_is_valid, scheme_message = is_valid_scheme(criteria, classification_schemas[scheme_id])
            user_classification_is_valid = (str(classification) in allowed_classes) and comment

            scheme_class = get_scheme_class(criteria, classification_schemas[scheme_id]['scheme_type']) # always calculate scheme class because no scheme is not allowed here!
            scheme_class = scheme_class.json['final_class']

            # actually submit the data to the database
            if not scheme_classification_is_valid: # error in scheme
                flash(scheme_message, "alert-danger")
            if not user_classification_is_valid: # error in user classification
                flash("Please provide a final classification and a comment to submit the consensus classification. The classification was not submitted.", "alert-danger")
            if not literature_is_valid:
                flash(literature_message, "alert-danger")

            if user_classification_is_valid and scheme_classification_is_valid and literature_is_valid:
                # insert consensus classification
                classification_id = handle_consensus_classification(variant, classification, comment, scheme_id, pmids, text_passages, criteria, classification_schemas[scheme_id]['description'], scheme_class, conn)

                # insert literature passages
                # classification id never none because we always insert a new classification
                previous_selected_literature = [] # always empty because we always insert a new classification
                handle_selected_literature(previous_selected_literature, classification_id, pmids, text_passages, conn, is_user = False)

                # insert scheme criteria
                handle_scheme_classification(classification_id, criteria, conn, where = "consensus") # always do that because no scheme is not allowed
                add_classification_report(variant.id, conn)
                flash(Markup("Successfully inserted new consensus classification return <a href=/display/" + str(variant.id) + " class='alert-link'>here</a> to view it!"), "alert-success")
                do_redirect = True

    if do_redirect: # do redirect if the submission was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully consensus-classified variant " + str(variant_id) + " with class " + str(classification) + " from scheme_id " + str(scheme_id))
        task = generate_consensus_only_vcf_task.apply_async()
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))
    else:
        return render_template('variant/classify.html', 
                                classification_type='consensus',
                                variant=variant,
                                #logged_in_user_id = session['user']['user_id'],
                                classification_schemas=classification_schemas,
                                previous_classifications=previous_classifications,
                                allowed_classes = allowed_classes
                            )



@variant_blueprint.route('/display/<int:variant_id>/classification_history')
@require_permission(['read_resources'])
def classification_history(variant_id):
    conn = get_connection()
    variant = conn.get_variant(variant_id)
    if variant is None:
        return abort(404)

    return render_template('variant/classification_history.html', 
                            variant = variant
                            )



@variant_blueprint.route('/check', methods=["GET","POST"])
def check():
    status=""
    message = ""
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

        status, message = map_hg38(variant, -1, conn, insert_variant = False, perform_annotation = False, external_ids = None)

    return render_template('variant/check.html',
                            chroms = chroms,
                            status = status,
                            message = message
                            )

