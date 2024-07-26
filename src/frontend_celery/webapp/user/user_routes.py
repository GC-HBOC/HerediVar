from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session, jsonify
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from werkzeug.exceptions import abort
import common.functions as functions
from datetime import datetime
from ..utils import *
from flask_paginate import Pagination
import annotation_service.main as annotation_service
import frontend_celery.webapp.tasks as tasks
import random

from . import user_functions

user_blueprint = Blueprint(
    'user',
    __name__
)

@user_blueprint.route('/mylists/modify_content', methods=['POST'])
@require_permission(['read_resources'])
def modify_list_content():
    conn = get_connection()

    next_url = request.args.get('next')
    if next_url is None:
        next_url = url_for('main.index')

    if request.method == 'POST':
        # extract and check data
        user_action = request.args.get('action')
        list_id = request.args.get('selected_list_id')
        variant_id = request.args.get('variant_id')
        require_set(user_action)
        require_valid(list_id, "user_variant_lists", conn)
        require_list_permission(list_id, required_permissions = ['edit'], conn = conn)

        # perform the action -> either add or remove
        if user_action == 'add_to_list':
            conn.add_variant_to_list(list_id, variant_id)
            flash({"message": "Successfully inserted variant to the list. You can view your list",
               "link": url_for('user.my_lists', view=list_id)}, "alert-success")
        elif user_action == 'remove_from_list':
            conn.delete_variant_from_list(list_id, variant_id)
            flash({"message": "Successfully removed variant from the list. You can view your list",
               "link": url_for('user.my_lists', view=list_id)}, "alert-success")
        else:
            flash("Action not allowed: " + str(user_action), "alert-danger")
    return save_redirect(next_url)


@user_blueprint.route('/mylists', methods=['GET', 'POST'])
@require_permission(['read_resources'])
def my_lists():
    user_id = session['user']['user_id']
    conn = get_connection()

    # variant view table of lists in pagination
    view_list_id = request.args.get('view', None)
    list_import_status = None
    if view_list_id is not None: # the user wants to view a list
        require_valid(view_list_id, "user_variant_lists", conn)
        require_list_permission(view_list_id, required_permissions = ['read'], conn = conn)
        list_import_status = conn.get_most_recent_list_variant_import_queue(view_list_id)

    request_args = request.args.to_dict(flat=False)
    request_args = {key: ';'.join(value) for key, value in request_args.items()}
    static_information = search_utils.get_static_search_information(user_id, conn)
    variants, total, page, selected_page_size = search_utils.get_merged_variant_page(request_args, user_id, static_information, conn, flash_messages = True, empty_if_no_variants_oi = True)
    pagination = Pagination(page=page, per_page=selected_page_size, total=total, css_framework='bootstrap5')

    if request.method == 'POST':
        request_type = request.args['type']
        
        # actions on the lists themselves
        if request_type == 'create':
            list_name = request.form['list_name']
            public_read = True if request.form.get('public_read') else False
            public_edit = True if request.form.get('public_edit') else False

            if not public_read and public_edit:
                flash("You can not add a public list which is not publicly readable but publicly editable. List was not created.", 'alert-danger')
            elif ';' in list_name:
                flash("List names can not contain a semicolon ';' character.", 'alert-danger')
            else:
                conn.insert_user_variant_list(user_id, list_name, public_read, public_edit)
                flash("Successfully created new list: \"" + list_name + "\"", "alert-success flash_id:list_add_success")
                current_app.logger.info(session['user']['preferred_username'] + " successfully created list " + list_name)
                return redirect(url_for('user.my_lists'))
            
        if request_type == 'edit':
            list_name = request.form['list_name']
            list_id = request.form['list_id']
            public_read = True if request.form.get('public_read') else False
            public_edit = True if request.form.get('public_edit') else False

            if list_id is not None:
                list_permissions = conn.check_list_permission(user_id, list_id)
                if not list_permissions['owner']:
                    return abort(403)
            if not public_read and public_edit:
                flash("You can not add a public list which is not publicly readable but publicly editable. List was not created.", 'alert-danger')
            elif ';' in list_name:
                flash("List names can not contain a semicolon ';' character.", 'alert-danger')
            else:
                conn.update_user_variant_list(list_id, list_name, public_read, public_edit)
                flash("Successfully changed list settings.", "alert-success flash_id:list_edit_permissions_success")
                current_app.logger.info(session['user']['preferred_username'] + " successfully adopted settings for list: " + str(list_id))
                return redirect(url_for('user.my_lists', view=list_id))
            
        if request_type == 'delete_list':
            list_id = request.form['list_id']
            require_valid(list_id, "user_variant_lists", conn)
            if list_id is not None:
                list_permissions = conn.check_list_permission(user_id, list_id)
                if not list_permissions['owner']:
                    return abort(403)
            conn.delete_user_variant_list(list_id)
            flash("Successfully removed list", "alert-success flash_id:list_delete_success")
            current_app.logger.info(session['user']['preferred_username'] + " successfully deleted list " + str(list_id)) 
            return redirect(url_for('user.my_lists'))
        
        if request_type == 'duplicate':
            list_id = request.form['list_id']
            list_name = request.form['list_name']
            public_read = True if request.form.get('public_read') else False
            public_edit = True if request.form.get('public_edit') else False
            if not public_read and public_edit:
                flash("You can not add a public list which is not publicly readable but publicly editable. List was not created.", 'alert-danger')
            else:
                require_valid(list_id, "user_variant_lists", conn)
                if list_id is not None:
                    list_permissions = conn.check_list_permission(user_id, list_id)
                    if not list_permissions["read"]:
                        return abort(403)
                    new_list_id = conn.duplicate_list(list_id, user_id, list_name, public_read, public_edit)
                    flash("Successfully duplicated list", 'alert-success flash_id:duplicate_list_success')
                    current_app.logger.info(session['user']['preferred_username'] + " successfully duplicated list " + str(list_id))
                    return redirect(url_for('user.my_lists', view=list_id))
                
        if request_type == 'intersect':
            list_id = request.form['list_id']
            target_list_id = list_id
            inplace = True if request.form.get('inplace') else False
            other_list_id = request.form['other_list_id']
            other_list_name = request.form['other_list_name']
            require_valid(list_id, "user_variant_lists", conn)
            if (other_list_name.strip() != '' and other_list_id.strip() == ''):
                flash("The other list which you tried to intersect does not exist", 'alert-danger flash_id:intersect_not_exist')
                return redirect(url_for('user.my_lists', view=list_id))
            list_permissions = conn.check_list_permission(user_id, list_id)
            if not list_permissions['read']:
                return abort(403)
            if not inplace:
                new_list_name = request.form.get('list_name')
                new_list_public_read = True if request.form.get('public_read') else False
                new_list_public_edit = True if request.form.get('public_edit') else False
                target_list_id = conn.insert_user_variant_list(user_id, new_list_name, new_list_public_read, new_list_public_edit)
                #list_id = conn.duplicate_list(list_id, user_id, new_list_name, new_list_public_read, new_list_public_edit)
            if list_id is not None:
                list_permissions = conn.check_list_permission(user_id, target_list_id)
                if not list_permissions["edit"]:
                    return abort(403)
                conn.intersect_lists(first_list_id = list_id, second_list_id = other_list_id, target_list_id = target_list_id)
                flash("Successfully intersected the two lists", 'alert-success flash_id:intersect_list_success')
            return redirect(url_for('user.my_lists', view=target_list_id))
        
        if request_type == 'subtract':
            list_id = request.form['list_id']
            target_list_id = list_id
            inplace = True if request.form.get('inplace') else False
            other_list_id = request.form['other_list_id']
            other_list_name = request.form['other_list_name']
            require_valid(list_id, "user_variant_lists", conn)
            if (other_list_name.strip() != '' and other_list_id.strip() == ''):
                flash("The other list which you tried to subtract does not exist", 'alert-danger flash_id:subtract_not_exist')
                return redirect(url_for('user.my_lists', view=list_id))
            list_permissions = conn.check_list_permission(user_id, list_id)
            if not list_permissions['read']:
                return abort(403)
            if not inplace:
                new_list_name = request.form.get('list_name')
                new_list_public_read = True if request.form.get('public_read') else False
                new_list_public_edit = True if request.form.get('public_edit') else False
                target_list_id = conn.insert_user_variant_list(user_id, new_list_name, new_list_public_read, new_list_public_edit)
            if list_id is not None:
                list_permissions = conn.check_list_permission(user_id, target_list_id)
                if not list_permissions["edit"]:
                    return abort(403)
                conn.subtract_lists(first_list_id = list_id, second_list_id = other_list_id, target_list_id = target_list_id)
                flash("Successfully subtracted the two lists", 'alert-success flash_id:subtract_list_success')
            return redirect(url_for('user.my_lists', view=target_list_id))
        
        if request_type == 'add':
            list_id = request.form['list_id']
            target_list_id = list_id
            inplace = True if request.form.get('inplace') else False
            other_list_id = request.form['other_list_id']
            other_list_name = request.form['other_list_name']
            require_valid(list_id, "user_variant_lists", conn)
            if (other_list_name.strip() != '' and other_list_id.strip() == ''):
                flash("The other list which you tried to add does not exist", 'alert-danger flash_id:add_not_exist')
                return redirect(url_for('user.my_lists', view=list_id))
            list_permissions = conn.check_list_permission(user_id, list_id)
            if not list_permissions['read']:
                return abort(403)
            if not inplace:
                new_list_name = request.form.get('list_name')
                new_list_public_read = True if request.form.get('public_read') else False
                new_list_public_edit = True if request.form.get('public_edit') else False
                target_list_id = conn.insert_user_variant_list(user_id, new_list_name, new_list_public_read, new_list_public_edit)
            if list_id is not None:
                list_permissions = conn.check_list_permission(user_id, target_list_id)
                if not list_permissions["edit"]:
                    return abort(403)
                conn.add_lists(first_list_id = list_id, second_list_id = other_list_id, target_list_id = target_list_id)
                flash("Successfully added the two lists", 'alert-success flash_id:add_list_success')
            return redirect(url_for('user.my_lists', view=target_list_id))
    
    return render_template('user/my_lists.html', 
                            variants=variants,
                            pagination=pagination,
                            static_information = static_information,
                            list_import_status = list_import_status
                        )


#
@user_blueprint.route('/admin_dashboard', methods=('GET', 'POST'))
@require_permission(['admin_resources'])
def admin_dashboard():
    conn = get_connection()
    job_config = annotation_service.get_default_job_config()
    annotation_stati, errors, warnings, total_num_variants = conn.get_annotation_statistics(exclude_sv=True)
    schemes = conn.get_all_classification_schemes()
    do_redirect = False

    most_recent_import_request = conn.get_most_recent_import_request(source = "heredicare")

    if request.method == 'POST':
        request_type = request.args.get("type")

        # mass reannotation based on current annotation status
        if request_type == 'reannotate':
            selected_jobs = request.form.getlist('job')
            reannotate_which = request.form.get('reannotate_which')
            require_set(reannotate_which)
            selected_job_config = annotation_service.get_job_config(selected_jobs)

            if reannotate_which == 'all':
                variant_ids = conn.get_all_valid_variant_ids(exclude_sv=True)
            elif reannotate_which == 'erroneous':
                variant_ids = annotation_stati['error']
            elif reannotate_which == 'aborted':
                variant_ids = annotation_stati['aborted']
            elif reannotate_which == 'unannotated':
                variant_ids = annotation_stati['unannotated']
            elif reannotate_which == 'specific':
                raw = request.form.get('specific_variants', '')
                variant_ids = search_utils.preprocess_query(raw, pattern = "\d+")

            tasks.annotate_all_variants.apply_async(args=[variant_ids, selected_job_config, session['user']['user_id'], session['user']['roles']])
            current_app.logger.info(session['user']['preferred_username'] + " issued a reannotation of " + reannotate_which + " variants") 
            flash('Variant reannotation of ' + reannotate_which + ' variants requested. It will be computed in the background.', 'alert-success')
            do_redirect = True

        # abort annotations based on annotation status
        elif request_type == 'abort_annotations':
            annotation_statuses_to_abort = request.form.getlist('annotation_statuses')
            annotation_requests = conn.get_annotation_queue(annotation_statuses_to_abort)
            tasks.abort_annotation_tasks(annotation_requests, conn)
            flash("Aborted " + str(len(annotation_requests)) + " annotation requests.", "alert-success")
            do_redirect = True

        # mass import from heredicare: consider ALL HerediCaRe VIDs independent of last import date / last updated
        elif request_type == 'import_variants':
            vids = "all" # start task importing all updated heredicare vids
            import_queue_id = tasks.start_variant_import(vids, session['user']['user_id'], session['user']['roles'], conn)
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id))

        # mass import from heredicare: only imports updated heredicare vids based on the last mass import
        elif request_type == 'import_variants_update':
            vids = "update" # start task importing all updated heredicare vids
            import_queue_id = tasks.start_variant_import(vids, session['user']['user_id'], session['user']['roles'], conn)
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id))

        # specific vid import from heredicare
        elif request_type == 'import_specific_vids':
            vids = request.form.get('vids', "")
            vids = re.split(r"[,;]", vids)
            require_set(vids)
            
            import_queue_id = tasks.start_variant_import(vids, session['user']['user_id'], session['user']['roles'], conn)
            flash("Successfully requested variant import of HerediCare VID: " + str(vids), "alert-success")
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id))

    if do_redirect:
        return redirect(url_for('user.admin_dashboard'))
    return render_template('user/admin_dashboard.html', 
                           most_recent_import_request=most_recent_import_request, 
                           job_config = job_config, 
                           annotation_stati = annotation_stati, 
                           errors = errors, 
                           warnings = warnings, 
                           total_num_variants = total_num_variants,
                           schemes = schemes
                        )


# api endpoint for hiding schemes
# not to be redirected to directly
@user_blueprint.route('/hide_scheme', methods=['POST'])
@require_permission(['admin_resources'])
def hide_scheme():
    conn = get_connection()

    scheme_id = request.form.get('scheme_id')
    is_active = request.form.get('is_active', "false") == "true"

    require_valid(scheme_id, "classification_scheme", conn)

    conn.update_active_state_classification_scheme(scheme_id, is_active)

    return "success"


# api endpoint for setting the default scheme
# the default scheme will be selected if none of the gene specific ones match
@user_blueprint.route('/set_default_scheme', methods=['POST'])
@require_permission(['admin_resources'])
def set_default_scheme():
    conn = get_connection()

    scheme_id = request.form.get('scheme_id')
    require_valid(scheme_id, "classification_scheme", conn)

    conn.set_default_scheme(scheme_id)

    return "success"



# shows all variant import requests from heredicare in server sided pagination
@user_blueprint.route('/variant_import_history')
@require_permission(['admin_resources'])
def variant_import_history():
    page = request.args.get('page', 1)
    page_size = 10

    conn = get_connection()
    import_queue_requests, total = conn.get_import_requests_page(page, page_size)
    pagination = Pagination(page=page, per_page=page_size, total=total, css_framework='bootstrap5')
    return render_template('user/variant_import_history.html',
                           import_queue_requests = import_queue_requests,
                           pagination = pagination,
                           page = page,
                           page_size = page_size 
                        )

# shows all data of an import - is used for both bulk and single vid imports from heredicare
@user_blueprint.route('/variant_import_summary/<int:import_queue_id>', methods=['GET', 'POST'])
@require_permission(['admin_resources'])
def variant_import_summary(import_queue_id):
    conn = get_connection()
    import_request = conn.get_import_request(import_queue_id)
    require_set(import_request)

    static_information = get_static_vis_information(conn)

    if request.method == 'POST':
        action = request.form.get('action')
        require_set(action)
        if action == "retry_one":
            import_variant_queue_id = request.form.get('import_variant_queue_id')
            require_valid(import_variant_queue_id, 'import_variant_queue', conn)

            tasks.retry_variant_import(import_variant_queue_id, session['user']['user_id'], session['user']['roles'], conn)
            vid = conn.get_vid_from_import_variant_queue(import_variant_queue_id)
            flash("Successfully requested reimport of vid " + str(vid) + ". It is processed in the background. If this page does not show a pending variant refresh to view changes.", "alert-success")
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id, **request.args))
        if action == "retry_search":
            imported_variants, total, page, page_size = get_vis_page(request.args, import_queue_id, static_information, conn, paginate = False)
            for imported_variant in imported_variants:
                import_variant_queue_id = imported_variant.id
                tasks.retry_variant_import(import_variant_queue_id, session['user']['user_id'], session['user']['roles'], conn)
            flash("Successfully requested reimport of " + str(len(imported_variants)) + " VIDs. If this page does not show a pending variant refresh to view changes.", "alert-success")
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id, **request.args))

    
    imported_variants, total, page, page_size = get_vis_page(request.args, import_queue_id, static_information, conn)
    pagination = Pagination(page=page, per_page=page_size, total=total, css_framework='bootstrap5')

    return render_template('user/variant_import_summary.html', 
                           import_queue_id = import_queue_id,
                           static_information = static_information,
                           imported_variants = imported_variants,
                           pagination = pagination,
                           page = page,
                           page_size = page_size
                        )

def get_static_vis_information(conn: Connection):
    result = {}
    result["default_page"] = 1
    result["default_page_size"] = "20"
    result["allowed_stati"] = conn.get_enumtypes("import_variant_queue", "status")
    return result

def get_vis_page(request_args, import_queue_id, static_information, conn: Connection, paginate = True):
    page = request.args.get('page', static_information["default_page"])
    page_size = "all"
    if paginate:
        page_size = request.args.get('page_size', static_information["default_page_size"])

    comments = extract_comments_vis(request_args)
    stati = extract_stati_vis(request_args, static_information["allowed_stati"])
    vids = extract_vids_vids(request_args)

    imported_variants, total = conn.get_imported_variants_page(comments, stati, vids, import_queue_id, page, page_size)
    

    return imported_variants, total, page, page_size


def extract_stati_vis(request_args, allowed_stati):
    raw = request_args.getlist('status')#
    raw = ';'.join(raw)
    regex_inner = '|'.join(allowed_stati)
    processed = search_utils.preprocess_query(raw, r'(' + regex_inner + r')?')
    if processed is None:
        flash("You have an error in your status queries. Results are not filtered by stati.", "alert-danger")
    return processed

def extract_comments_vis(request_args):
    raw = request_args.get('comment', '')
    processed = search_utils.preprocess_query(raw, pattern=r".*", seps = "[;]", remove_whitespace = False)
    if processed is None:
        flash("You have an error in your comment query(s). Results are not filtered by comment.", "alert-danger")
    return processed

def extract_vids_vids(request_args):
    raw = request_args.get('vid', '')
    processed = search_utils.preprocess_query(raw, pattern=r"\d+")
    if processed is None:
        flash("You have an error in your VID query(s). Results are not filtered by VIDs.", "alert-danger")
    return processed


# api endpoint for fetching the data for the import summary
# the import summary endpoint uses ajax to get information from this endpoint
@user_blueprint.route('/variant_import_summary_data/<int:import_queue_id>')
@require_permission(['admin_resources'])
def variant_import_summary_data(import_queue_id):
    conn = get_connection()
    import_request = conn.get_import_request(import_queue_id)
    require_set(import_request)
    #imported_variants = conn.get_imported_variants(import_queue_id, status = ["error"])
    return jsonify({'import_request': import_request})





# shows asll variant publish requests in server sided pagination
# for both, clinvar and heredicare
@user_blueprint.route('/variant_publish_history')
@require_permission(['admin_resources'])
def variant_publish_history():
    page = request.args.get('page', 1)
    page_size = 10

    conn = get_connection()
    publish_queue_requests, total = conn.get_publish_requests_page(page, page_size)
    pagination = Pagination(page=page, per_page=page_size, total=total, css_framework='bootstrap5')
    return render_template('user/variant_publish_history.html',
                           publish_queue_requests = publish_queue_requests,
                           pagination = pagination,
                           page = page,
                           page_size = page_size 
                        )


# shows information about a variant publish request to clinvar/heredicare
# does not update automatically -- maybe should be changed to dynamic updates like the import summary page...?
@user_blueprint.route('/variant_publish_summary')
@require_permission(['admin_resources'])
def variant_publish_summary():
    conn = get_connection()

    publish_queue_id = request.args.get('publish_queue_id')
    require_valid(publish_queue_id, "publish_queue", conn)

    variant_ids = conn.get_variant_ids_from_publish_request(publish_queue_id)
    publish_queue_ids_oi = [publish_queue_id]
    check_update_all(variant_ids, publish_queue_ids_oi, conn)

    publish_request = conn.get_publish_request(publish_queue_id)
    heredicare_uploads = conn.get_published_variants_heredicare(publish_queue_id, status = ["error", "api_error", "skipped"])
    clinvar_uploads = conn.get_published_variants_clinvar(publish_queue_id, status = ["error", "skipped"])

    return render_template('user/variant_publish_summary.html', publish_request = publish_request, heredicare_uploads = heredicare_uploads, clinvar_uploads = clinvar_uploads)