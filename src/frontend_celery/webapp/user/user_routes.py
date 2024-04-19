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
        user_action = request.args.get('action')
        list_id = request.args.get('selected_list_id')
        variant_id = request.args.get('variant_id')
        if not user_action or not list_id or not variant_id:
            flash('Please specify an action (either add_to_list or remove_from_list) and a list_id as well as a variant_id.', 'alert-danger')
            abort(404)
        user_id = session['user']['user_id']
        list_permissions = conn.check_list_permission(user_id, list_id)
        if not list_permissions['owner'] and not list_permissions['edit']:
            current_app.logger.error(session['user']['preferred_username'] + " attempted edit list with id " + str(list_id) + ", but this list was not created by him and did not have the right to edit it.")
            flash('This action is not allowed', 'alert-danger')
            abort(403)

        if user_action == 'add_to_list':
            conn.add_variant_to_list(list_id, variant_id)
            flash(Markup("Successfully inserted variant to the list. You can view your list <a class='alert-link' href='" + url_for('user.my_lists', view=list_id) + "'>here</a>."), "alert-success")
        if user_action == 'remove_from_list':
            conn.delete_variant_from_list(list_id, variant_id)
            flash(Markup("Successfully removed variant to the list. You can view your list <a class='alert-link' href='" + url_for('user.my_lists', view=list_id) + "'>here</a>."), "alert-success")
    return save_redirect(next_url)


@user_blueprint.route('/mylists', methods=['GET', 'POST'])
@require_permission(['read_resources'])
def my_lists():
    user_id = session['user']['user_id']
    conn = get_connection()

    static_information = search_utils.get_static_search_information(user_id, conn)

    # variant view table of lists in pagination
    view_list_id = request.args.get('view', None)

    if view_list_id == '':
        return abort(404)

    list_import_status = None
    if view_list_id is not None: # the user wants to see the list
        list_permissions = conn.check_list_permission(user_id, view_list_id)
        if list_permissions is None:
            return abort(404)
        if not list_permissions['read']:
            current_app.logger.error(session['user']['preferred_username'] + " attempted view list with id " + str(view_list_id) + ", but this list was neither created by him nor is it public.")
            return abort(403)
        list_import_status = conn.get_most_recent_list_variant_import_queue(view_list_id)

    variants, total, page, selected_page_size = search_utils.get_merged_variant_page(request.args, user_id, static_information, conn, flash_messages = True, empty_if_no_variants_oi = True)
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
            conn.update_user_variant_list(list_id, list_name, public_read, public_edit)
            flash("Successfully changed list settings.", "alert-success flash_id:list_edit_permissions_success")
            current_app.logger.info(session['user']['preferred_username'] + " successfully adopted settings for list: " + str(list_id))
            return redirect(url_for('user.my_lists', view=list_id))
        if request_type == 'delete_list':
            list_id = request.form['list_id']
            if list_id == "":
                return abort(404)
            if list_id is not None:
                list_permissions = conn.check_list_permission(user_id, list_id)
                if not list_permissions['owner']:
                    return abort(403)
            conn.delete_user_variant_list(list_id)
            flash("Successfully removed list", "alert-success")
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
                if list_id == "":
                    return abort(404)
                if list_id is not None:
                    list_permissions = conn.check_list_permission(user_id, list_id)
                    if not list_permissions["read"]:
                        return abort(403)
                    new_list_id = conn.duplicate_list(list_id, user_id, list_name, public_read, public_edit)
                    flash("Successfully duplicated list", 'alert-success')
                    current_app.logger.info(session['user']['preferred_username'] + " successfully duplicated list " + str(list_id))
                    return redirect(url_for('user.my_lists', view=list_id))
        
        if request_type == 'intersect':
            list_id = request.form['list_id']
            target_list_id = list_id
            inplace = True if request.form.get('inplace') else False
            other_list_id = request.form['other_list_id']
            other_list_name = request.form['other_list_name']

            if list_id == "":
                return abort(404)
            if (other_list_name.strip() != '' and other_list_id.strip() == ''):
                flash("The other list which you tried to intersect does not exist", 'alert-danger')
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
                flash("Successfully intersected the two lists", 'alert-success')
            return redirect(url_for('user.my_lists', view=target_list_id))
        
        if request_type == 'subtract':
            list_id = request.form['list_id']
            target_list_id = list_id
            inplace = True if request.form.get('inplace') else False
            other_list_id = request.form['other_list_id']
            other_list_name = request.form['other_list_name']

            if list_id == "":
                return abort(404)
            if (other_list_name.strip() != '' and other_list_id.strip() == ''):
                flash("The other list which you tried to subtract does not exist", 'alert-danger')
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
                flash("Successfully subtracted the two lists", 'alert-success')
            return redirect(url_for('user.my_lists', view=target_list_id))
        

        if request_type == 'add':
            list_id = request.form['list_id']
            target_list_id = list_id
            inplace = True if request.form.get('inplace') else False
            other_list_id = request.form['other_list_id']
            other_list_name = request.form['other_list_name']

            if list_id == "":
                return abort(404)
            if (other_list_name.strip() != '' and other_list_id.strip() == ''):
                flash("The other list which you tried to add does not exist", 'alert-danger')
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
                flash("Successfully added the two lists", 'alert-success')
            return redirect(url_for('user.my_lists', view=target_list_id))

        # actions on variant list view
        if request_type == 'search':
            pass

        if request_type == 'delete_variant': 
            variant_id_to_delete = request.args['variant_id']
            if not list_permissions['edit']:
                return abort(403)
            conn.delete_variant_from_list(view_list_id, variant_id_to_delete)
            url_to_deleted_variant = url_for('variant.display', variant_id=variant_id_to_delete)
            flash(Markup("Successfully removed variant from list! Go <a class='alert-link' href='" + url_to_deleted_variant + "'>here</a> to undo this action."), "alert-success")

            return redirect(url_for('user.my_lists', view=view_list_id))
    
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
    if most_recent_import_request is None:
        status = 'finished'
    else:
        status = most_recent_import_request.status

    if request.method == 'POST':
        request_type = request.args.get("type")
        if request_type == 'reannotate':
            selected_jobs = request.form.getlist('job')
            reannotate_which = request.form.get('reannotate_which')
            if reannotate_which is None:
                abort(404)
            selected_job_config = annotation_service.get_job_config(selected_jobs)

            if reannotate_which == 'all':
                variant_ids = conn.get_all_valid_variant_ids(exclude_sv=True)
                #variant_ids = conn.get_variant_ids_from_list(77)
                #variant_ids = conn.get_variant_ids_without_automatic_classification()
                #variant_ids = random.sample(variant_ids, 50)
            elif reannotate_which == 'erroneous':
                variant_ids = annotation_stati['error']
            elif reannotate_which == 'aborted':
                variant_ids = annotation_stati['aborted']
            elif reannotate_which == 'unannotated':
                variant_ids = annotation_stati['unannotated']

            tasks.annotate_all_variants.apply_async(args=[variant_ids, selected_job_config, session['user']['user_id'], session['user']['roles']])
            current_app.logger.info(session['user']['preferred_username'] + " issued a reannotation of " + reannotate_which + " variants") 
            flash('Variant reannotation of ' + reannotate_which + ' variants requested. It will be computed in the background.', 'alert-success')
            do_redirect = True

        elif request_type == 'abort_annotations':
            annotation_statuses_to_abort = request.form.getlist('annotation_statuses')
            annotation_requests = conn.get_annotation_queue(annotation_statuses_to_abort)
            tasks.abort_annotation_tasks(annotation_requests, conn)
            flash("Aborted " + str(len(annotation_requests)) + " annotation requests.", "alert-success")
            do_redirect = True

        elif request_type == 'import_variants': # mass import from heredicare
            #heredicare_interface = current_app.extensions['heredicare_interface']
            #start_variant_import(conn)
            #heredicare_variant_import.apply_async(args=[session['user']['user_id'], session['user']['roles']])
            import_queue_id = tasks.start_variant_import(session['user']['user_id'], session['user']['roles'], conn = conn)
            #task = import_one_variant_heredicare.apply_async(args=[12, 30, ["super_user"], 169])
            
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id))

        elif request_type == 'import_one_variant':
            import_queue_id = request.form.get('import_queue_id')
            vid = request.form.get('vid')
            
            if import_queue_id is not None: # if import queue id is None we are inserting one by hand without import request if it is not none we are retrying the import!
                import_request = conn.get_import_request(import_queue_id)
                if import_request is None:
                    abort(404)
            if vid is None:
                abort(404)
            tasks.start_import_one_variant(vid, import_queue_id, session['user']['user_id'], session['user']['roles'], conn)
            flash("Successfully requested variant import of HerediCare VID: " + str(vid), "alert-success")
            return redirect(url_for('user.single_vid_imports'))

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



@user_blueprint.route('/get_single_vid_imports/')
@require_permission(['admin_resources'])
def single_vid_imports():
    conn = get_connection()
    variant_imports = conn.get_single_vid_imports()
    return render_template('user/single_vid_imports.html', variant_imports = variant_imports)


@user_blueprint.route('/variant_import_summary/<int:import_queue_id>', methods=('GET', 'POST'))
@require_permission(['admin_resources'])
def variant_import_summary(import_queue_id):
    conn = get_connection()
    import_request = conn.get_import_request(import_queue_id)
    if import_request is None:
        abort(404)
    return render_template('user/variant_import_summary.html', import_queue_id = import_queue_id)


@user_blueprint.route('/variant_import_summary_data/<int:import_queue_id>', methods=('GET', 'POST'))
@require_permission(['admin_resources'])
def variant_import_summary_data(import_queue_id):
    conn = get_connection()

    import_request = conn.get_import_request(import_queue_id)
    imported_variants = conn.get_imported_variants(import_queue_id, status = ["error"])

    return jsonify({'import_request': import_request, 'imported_variants': imported_variants})


@user_blueprint.route('/variant_import_history', methods=('GET', 'POST'))
@require_permission(['admin_resources'])
def variant_import_history():
    conn = get_connection()

    overview = conn.get_import_request_overview()

    return render_template('user/variant_import_history.html', overview = overview)




