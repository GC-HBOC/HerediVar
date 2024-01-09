from calendar import c
from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort, jsonify
from flask_paginate import Pagination
from ..utils import *
import sys
from os import path
from .variant_functions import *
from ..tasks import generate_consensus_only_vcf_task, start_annotation_service, validate_and_insert_variant, map_hg38, validate_and_insert_cnv

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

    modal_args = {}
    for arg in request.args:
        nargs = len(request.args.getlist(arg))
        if nargs > 1:
            modal_args[arg] = request.args.getlist(arg)
        elif nargs == 1:
            modal_args[arg] = request.args.get(arg)
    user_id = session['user']['user_id']

    allowed_user_classes = functions.order_classes(conn.get_enumtypes('user_classification', 'classification'))
    allowed_consensus_classes = functions.order_classes(conn.get_enumtypes('consensus_classification', 'classification'))
    allowed_automatic_classes = functions.order_classes(conn.get_enumtypes('automatic_classification', 'classification_splicing'))
    annotation_types = conn.get_annotation_types(exclude_groups = ['ID'])
    annotation_types = preprocess_annotation_types_for_search(annotation_types)

    genes = extract_genes(request)
    ranges = extract_ranges(request)
    consensus_classifications, include_heredicare_consensus = extract_consensus_classifications(request, allowed_consensus_classes)
    user_classifications = extract_user_classifications(request, allowed_user_classes)
    automatic_classifications_splicing = extract_automatic_classifications(request, allowed_automatic_classes, which="automatic_splicing")
    automatic_classifications_protein = extract_automatic_classifications(request, allowed_automatic_classes, which="automatic_protein")
    hgvs = extract_hgvs(request)
    variant_ids_oi = extract_lookup_list(request, user_id, conn)
    external_ids = extract_external_ids(request)
    cdna_ranges = extract_cdna_ranges(request)
    annotation_restrictions = extract_annotations(request, conn)
    page = int(request.args.get('page', 1))

    sort_bys, page_sizes, selected_page_size, selected_sort_by, include_hidden = extract_search_settings(request)
    
    # insert variants to list 
    if request.method == 'POST':
        list_id = request.args.get('selected_list_id')
        
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
                    variants_for_list, _ = conn.get_variants_page_merged(1, "unlimited", sort_by=selected_sort_by, 
                                                include_hidden=include_hidden, 
                                                user_id=user_id, 
                                                ranges=ranges, 
                                                genes = genes, 
                                                consensus=consensus_classifications, 
                                                user=user_classifications, 
                                                automatic_splicing=automatic_classifications_splicing,
                                                automatic_protein=automatic_classifications_protein,
                                                hgvs=hgvs, 
                                                variant_ids_oi=variant_ids_oi,
                                                include_heredicare_consensus = include_heredicare_consensus,
                                                external_ids = external_ids,
                                                cdna_ranges = cdna_ranges,
                                                annotation_restrictions = annotation_restrictions
                                            )
                    variant_ids = [variant.id for variant in variants_for_list]
                    for variant_id in variant_ids:
                        if str(variant_id) not in selected_variants:
                            num_new_variants = conn.add_variant_to_list(list_id, variant_id)
                            num_inserted = num_inserted + num_new_variants
                else:
                    for variant_id in selected_variants:
                        variant = conn.get_variant(variant_id)
                        if variant is not None:
                            num_new_variants = conn.add_variant_to_list(list_id, variant_id)
                            num_inserted = num_inserted + num_new_variants
                flash(Markup("Successfully inserted " + str(num_inserted) + " variant(s) from the current search to the list. You can view your list <a class='alert-link' href='" + url_for('user.my_lists', view=list_id) + "'>here</a>."), "alert-success")

                return redirect(url_for('variant.search', 
                                        genes = request.args.get('genes'), 
                                        ranges = request.args.get('ranges'), 
                                        consensus = request.args.getlist('consensus'), 
                                        user = request.args.getlist('user'), 
                                        automatic = request.args.getlist('automatic'),
                                        hgvs = request.args.get('hgvs'),
                                        cdna_ranges = request.args.get('cdna_ranges'),
                                        external_ids = request.args.get('external_ids'),
                                        annotation_type_id = request.args.getlist("annotation_type_id"),
                                        annotation_operation = request.args.getlist("annotation_operation"),
                                        annotation_value = request.args.getlist("annotation_value"),
                                        select_all_variants = request.args.get("select_all_variants", "false"),
                                        selected_variants = request.args.get("selected_variants", ""),
                                        lookup_list_id = request.args.getlist("lookup_list_id"),
                                        lookup_list_name = request.args.getlist("lookup_list_name"),
                                        page_size = request.args.get('page_size', page_sizes[1]),
                                        sort_by = request.args.get('sort_by', sort_bys[0]),
                                        include_hidden = request.args.get('include_hidden')
                                    )
                                )
            
    variants, total = conn.get_variants_page_merged(
        page=page, 
        page_size=selected_page_size, 
        sort_by=selected_sort_by, 
        include_hidden=include_hidden, 
        user_id=user_id, 
        ranges=ranges, 
        genes = genes, 
        consensus=consensus_classifications, 
        user=user_classifications, 
        automatic_splicing=automatic_classifications_splicing,
        automatic_protein=automatic_classifications_protein,
        hgvs=hgvs, 
        variant_ids_oi=variant_ids_oi,
        include_heredicare_consensus = include_heredicare_consensus,
        external_ids = external_ids,
        cdna_ranges = cdna_ranges,
        annotation_restrictions = annotation_restrictions
    )
    lists = conn.get_lists_for_user(user_id)
    pagination = Pagination(page=page, per_page=selected_page_size, total=total, css_framework='bootstrap5')

    return render_template('variant/search.html',
                           variants=variants, page=page, 
                           per_page=selected_page_size, 
                           pagination=pagination, 
                           lists=lists, 
                           sort_bys=sort_bys, 
                           page_sizes=page_sizes,
                           allowed_user_classes = allowed_user_classes,
                           allowed_consensus_classes = allowed_consensus_classes,
                           allowed_automatic_classes = allowed_automatic_classes,
                           annotation_types = annotation_types,
                           modal_args = modal_args # for add all to list
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
                    conn = get_connection()
                    was_successful, message, variant_id = validate_and_insert_variant(chr, pos, ref, alt, genome_build, conn = conn, user_id = session['user']['user_id'])
                    new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                    if 'already in database' in message:
                        flash(Markup("Variant not imported: already in database!! View it " + 
                                     "<a href=" + url_for("variant.display", chr=str(new_variant.chrom), pos=str(new_variant.pos), ref=str(new_variant.ref), alt=str(new_variant.alt)) + 
                                     " class=\"alert-link\">here</a>"), "alert-danger")
                    elif was_successful:
                        flash(Markup("Successfully inserted variant: " + str(new_variant.chrom) + ' ' + str(new_variant.pos) + ' ' + new_variant.ref + ' ' + new_variant.alt + 
                                     ' (view your variant <a href="' + url_for("variant.display", chr=str(new_variant.chrom), pos=str(new_variant.pos), ref=str(new_variant.ref), alt=str(new_variant.alt)) + 
                                     '" class="alert-link">here</a>)'), "alert-success")
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant from vcf which resulted in this vcf-style variant: " + ' '.join([str(new_variant.chrom), str(new_variant.pos), new_variant.ref, new_variant.alt, "GRCh38"]))
                        return redirect(url_for('variant.create'))

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
                    conn = get_connection()
                    was_successful, message, variant_id = validate_and_insert_variant(chr, pos, ref, alt, 'GRCh38', conn = conn, user_id = session['user']['user_id'])
                    new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                    if 'already in database' in message:
                        flash(Markup("Variant not imported: already in database!! View it " + 
                                     "<a href=" + url_for("variant.display", variant_id = variant_id) + 
                                     " class=\"alert-link\">here</a>"), "alert-danger")
                    elif was_successful:
                        flash(Markup("Successfully inserted variant: " + new_variant.get_string_repr() + 
                                     ' (view your variant <a href="' + url_for("variant.display", variant_id = variant_id) + 
                                     '" class="alert-link">here</a>)'), "alert-success")
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant from hgvs: " + hgvsc + "Which resulted in this vcf-style variant: " + ' '.join([str(new_variant.chrom), str(new_variant.pos), new_variant.ref, new_variant.alt, "GRCh38"]))
                        return redirect(url_for('variant.create'))

                    else:
                        flash(message, 'alert-danger')

    return render_template('variant/create.html', chrs=chrs)



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

            hgvs_strings = request.form.get('hgvs_strings', '')
            hgvs_strings = re.split('[\n,]', hgvs_strings)
            hgvs_strings = [x for x in hgvs_strings if x.strip() != '']

            if not chrom or not start or not end or not sv_type or 'genome' not in request.form:
                flash('All fields are required!', 'alert-danger')
            else: # all valid
                genome_build = request.form['genome']
                was_successful, message, variant_id = validate_and_insert_cnv(chrom = chrom, start = start, end = end, sv_type = sv_type, hgvs_strings = hgvs_strings, conn = conn, genome_build = genome_build)
                variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                if 'already in database' in message:
                        flash(Markup("Variant not imported: already in database!! Missing hgvs strings were added. View it " + 
                                     "<a href=" + url_for("variant.display", variant_id = variant_id) + 
                                     " class=\"alert-link\">here</a>"), "alert-danger")
                elif was_successful:
                    flash(Markup("Successfully inserted structural variant: " + variant.get_string_repr() + 
                                     ' (view your variant <a href="' + url_for("variant.display", variant_id = variant_id) + 
                                     '" class="alert-link">here</a>)'), "alert-success")
                    return redirect(url_for('variant.create_sv'))
                else:
                    flash("There was an error while importing the variant: " + message, "alert-danger")

    return render_template('variant/create_sv.html', chroms=chroms, sv_types=sv_types)



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
    allowed_classes = functions.order_classes(allowed_classes)

    user_id = session['user']['user_id']
    previous_classifications = {user_id: functions.list_of_objects_to_dict(variant.get_user_classifications(user_id), key_func = lambda a : a.scheme.id, val_func = lambda a : a.to_dict())}
    classification_schemas = conn.get_classification_schemas()

    #print(previous_classification)


    do_redirect = False
    if request.method == 'POST':
        ####### classification based on classification scheme submit
        scheme_id = int(request.form['scheme'])

        classification = request.form['final_class']
        comment = request.form.get('comment', '').strip()
        pmids = request.form.getlist('pmid')
        text_passages = request.form.getlist('text_passage')

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form, scheme_id, conn)
        scheme_classification_is_valid, scheme_message = is_valid_scheme(criteria, classification_schemas.get(scheme_id))
        pmids, text_passages = remove_empty_literature_rows(pmids, text_passages)
        literature_is_valid, literature_message = is_valid_literature(pmids, text_passages)
        
        without_scheme = scheme_id == 1
        classification_is_valid = str(classification) in allowed_classes

        scheme_class = '-'
        scheme_id_is_valid = True
        if not without_scheme:
            if scheme_id in classification_schemas:
                scheme_class = get_scheme_class(criteria, classification_schemas[scheme_id]['scheme_type'])
                scheme_class = scheme_class.json['final_class']
            else:
                flash("Unknown or deprecated classification scheme provided. Please provide a different one.", "alert-danger")
                scheme_id_is_valid = False

        # flash error messages
        if (not scheme_classification_is_valid) and (not without_scheme): # error in scheme
            flash(scheme_message, "alert-danger")
        if not classification_is_valid: # error in user classification
            flash("Please provide a class to submit a user classification!", "alert-danger")
        if not literature_is_valid:
            flash(literature_message, "alert-danger")

        # actually submit the data to the database
        if classification_is_valid and scheme_classification_is_valid and literature_is_valid and scheme_id_is_valid:
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


@variant_blueprint.route('/delete_classification', methods=['GET'])
@require_permission(['edit_resources'])
def delete_classification():
    conn = get_connection()

    user_classification_id = request.args.get('user_classification_id')
    variant_id = request.args.get('variant_id')

    if user_classification_id is None or variant_id is None:
        abort(404)

    variant = conn.get_variant(variant_id, include_annotations=False, include_consensus=False, include_heredicare_classifications=False, include_clinvar=False, include_consequences=False, include_assays=False, include_literature=False, include_external_ids=False)

    if variant is None:
        abort(404)

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
            comment = request.form.get('comment', '').strip()
            pmids = request.form.getlist('pmid')
            text_passages = request.form.getlist('text_passage')

            # test if the input is valid
            criteria = extract_criteria_from_request(request.form, scheme_id, conn)
            pmids, text_passages = remove_empty_literature_rows(pmids, text_passages)
            literature_is_valid, literature_message = is_valid_literature(pmids, text_passages)
            scheme_classification_is_valid, scheme_message = is_valid_scheme(criteria, classification_schemas[scheme_id])
            classification_is_valid = str(classification) in allowed_classes

            scheme_id_is_valid = True
            if scheme_id in classification_schemas:
                scheme_class = get_scheme_class(criteria, classification_schemas[scheme_id]['scheme_type']) # always calculate scheme class because no scheme is not allowed here!
                scheme_class = scheme_class.json['final_class']
            else:
                flash("Unknown or deprecated classification scheme provided. Please provide a different one.", "alert-danger")
                scheme_id_is_valid = False

            # actually submit the data to the database
            if not scheme_classification_is_valid: # error in scheme
                flash(scheme_message, "alert-danger")
            if not classification_is_valid: # error in user classification
                flash("Please provide a final classification and a comment to submit the consensus classification. The classification was not submitted.", "alert-danger")
            if not literature_is_valid:
                flash(literature_message, "alert-danger")

            if classification_is_valid and scheme_classification_is_valid and literature_is_valid and scheme_id_is_valid:
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


@variant_blueprint.route('/classify/<int:variant_id>/automatic', methods=['GET'])
@require_permission(['read_resources'])
def automatic_classification(variant_id):
    #{user_id: functions.list_of_objects_to_dict(variant.get_user_classifications(user_id), key_func = lambda a : a.scheme.id, val_func = lambda a : a.to_dict())}
    conn = get_connection()
    variant = conn.get_variant(variant_id, include_annotations=False, include_consensus=False, include_user_classifications=False, include_heredicare_classifications=False, include_clinvar=False, include_consequences=False, include_assays=False, include_literature=False, include_external_ids=False)
    if variant is None:
        abort(404)
    
    evidence_type = request.args.get('evidence_type')
    if evidence_type is None:
        abort(404)
    
    variant.automatic_classification.criteria = variant.automatic_classification.filter_criteria(evidence_type)
    result = variant.automatic_classification.to_dict()
    return result



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



@variant_blueprint.route('/hide_scheme', methods=['POST'])
@require_permission(['admin_resources'])
def hide_scheme():
    conn = get_connection()

    scheme_id = request.form.get('scheme_id')
    is_active = request.form.get('is_active')
    is_active = 1 if is_active == 'true' else 0

    classification_scheme = conn.get_classification_scheme(scheme_id)

    if classification_scheme is None:
        return abort(404)

    conn.update_active_state_classification_scheme(scheme_id, is_active)

    return "success"


@variant_blueprint.route('/set_default_scheme', methods=['POST'])
@require_permission(['admin_resources'])
def set_default_scheme():
    conn = get_connection()

    scheme_id = request.form.get('scheme_id')

    classification_scheme = conn.get_classification_scheme(scheme_id)

    if classification_scheme is None:
        return abort(404)

    conn.set_default_scheme(scheme_id)

    return "success"