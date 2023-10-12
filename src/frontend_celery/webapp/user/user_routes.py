from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session, jsonify
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from werkzeug.exceptions import abort
import common.functions as functions
import annotation_service.fetch_heredicare_variants as heredicare
from datetime import datetime
from ..utils import *
from flask_paginate import Pagination
import annotation_service.main as annotation_service
from ..tasks import start_annotation_service, start_variant_import, start_import_one_variant


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
            return abort(403)

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
    user_lists = conn.get_lists_for_user(user_id)

    allowed_user_classes = conn.get_enumtypes('user_classification', 'classification')
    allowed_consensus_classes = conn.get_enumtypes('consensus_classification', 'classification')


    # variant view table of lists in pagination
    view_list_id = request.args.get('view', None)
    variants = []
    page = int(request.args.get('page', 1))
    per_page = 20
    total = 0

    # just some dummy vars they will be dragged from search_utils.py -> extract_search_settings if needed
    sort_bys = []
    page_sizes = []


    if view_list_id == '':
        return abort(404)

    if view_list_id is not None: # the user wants to see the list
        list_permissions = conn.check_list_permission(user_id, view_list_id)
        if list_permissions is None:
            return abort(404)
        if not list_permissions['read']:
            current_app.logger.error(session['user']['preferred_username'] + " attempted view list with id " + str(view_list_id) + ", but this list was neither created by him nor is it public.")
            return abort(403)


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
                flash("Successfully created new list: \"" + list_name + "\"", "alert-success")
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
            flash("Successfully changed list settings.", "alert-success")
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


    if view_list_id is not None:
        genes = extract_genes(request)
        ranges = extract_ranges(request)
        consensus_classifications = extract_consensus_classifications(request, allowed_consensus_classes)
        user_classifications = extract_user_classifications(request, allowed_user_classes)
        hgvs = extract_hgvs(request)
        variant_ids_from_lookup_list = extract_lookup_list(request, user_id, conn)
        variant_ids_oi = conn.get_variant_ids_from_list(view_list_id)

        sort_bys, page_sizes, selected_page_size, selected_sort_by, include_hidden = extract_search_settings(request)

        if variant_ids_from_lookup_list is not None and len(variant_ids_from_lookup_list) != 0:
            variant_ids_oi = list(set(none_to_empty_list(variant_ids_from_lookup_list)) & set(none_to_empty_list(variant_ids_oi))) # take the intersection of the two lists

        if len(variant_ids_oi) > 0:
            variants, total = conn.get_variants_page_merged(page=page, page_size=selected_page_size,
                                                            sort_by=selected_sort_by,
                                                            include_hidden=include_hidden,
                                                            user_id=user_id, 
                                                            ranges=ranges, 
                                                            genes = genes, 
                                                            consensus=consensus_classifications, 
                                                            user=user_classifications, 
                                                            hgvs=hgvs, 
                                                            variant_ids_oi=variant_ids_oi
                                                        )
    #print(variants)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    
    return render_template('user/my_lists.html', 
                            user_lists = user_lists,
                            variants=variants, 
                            page=page, 
                            per_page=per_page, 
                            pagination=pagination,
                            sort_bys=sort_bys, page_sizes=page_sizes,
                            allowed_user_classes = allowed_user_classes,
                            allowed_consensus_classes = allowed_consensus_classes)


#
@user_blueprint.route('/admin_dashboard', methods=('GET', 'POST'))
@require_permission(['admin_resources'])
def admin_dashboard():
    conn = get_connection()
    job_config = annotation_service.get_default_job_config()
    annotation_stati, errors, warnings, total_num_variants = conn.get_annotation_statistics()
    do_redirect = False

    most_recent_import_request = conn.get_most_recent_import_request()
    if most_recent_import_request is None:
        status = 'finished'
    else:
        status = most_recent_import_request.status

    if request.method == 'POST':
        request_type = request.args.get("type")
        if request_type == 'update_variants':
            if status == 'finished':
                import_queue_id = conn.insert_import_request(user_id = session['user']['user_id'])
                requested_at = conn.get_import_request(import_queue_id = import_queue_id)[2]
                requested_at = datetime.strptime(str(requested_at), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d-%H-%M-%S')

                logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
                log_file_path = logs_folder + 'heredicare_import:' + requested_at + '.log'
                heredicare.process_all(log_file_path, user_id=session['user']['user_id'])
                log_file_path = heredicare.get_log_file_path()
                date = log_file_path.strip('.log').split(':')[1].split('-')

                conn.close_import_request(import_queue_id)
                current_app.logger.info(session['user']['preferred_username'] + " issued a full HerediCare import.")
                return redirect(url_for('variant_io.import_summary', year=date[0], month=date[1], day=date[2], hour=date[3], minute=date[4], second=date[5]))

        elif request_type == 'reannotate':
            selected_jobs = request.form.getlist('job')
            selected_job_config = annotation_service.get_job_config(selected_jobs)
            variant_ids = conn.get_all_valid_variant_ids()
            for variant_id in variant_ids:
                start_annotation_service(variant_id = variant_id, user_id = session['user']['user_id'], job_config = selected_job_config, conn = conn) # inserts a new annotation queue entry before submitting the task to celery
                #conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])
            current_app.logger.info(session['user']['preferred_username'] + " issued a reannotation of all variants") 
            flash('Variant reannotation requested. It will be computed in the background.', 'alert-success')
            do_redirect = True
        
        if request_type == 'reannotate_erroneous':
            for variant_id in annotation_stati['error']:
                start_annotation_service(variant_id = variant_id, user_id = session['user']['user_id'], job_config = job_config, conn = conn)
            flash('Variant reannotation issued for ' + str(len(annotation_stati['error'])) + ' variants', 'alert-success')
            do_redirect = True

        if request_type == 'import_variants': # mass import from heredicare
            #heredicare_interface = current_app.extensions['heredicare_interface']
            #start_variant_import(conn)
            #heredicare_variant_import.apply_async(args=[session['user']['user_id'], session['user']['roles']])
            import_queue_id = start_variant_import(session['user']['user_id'], session['user']['roles'], conn = conn)
            #task = import_one_variant_heredicare.apply_async(args=[12, 30, ["super_user"], 169])
            
            return redirect(url_for('user.variant_import_summary', import_queue_id = import_queue_id))

        if request_type == 'import_one_variant':
            import_queue_id = request.form.get('import_queue_id')
            vid = request.form.get('vid')
            
            if import_queue_id is not None: # if import queue id is None we are inserting one by hand without import request if it is not none we are retrying the import!
                import_request = conn.get_import_request(import_queue_id)
                if import_request is None:
                    abort(404)
            if vid is None:
                abort(404)
            start_import_one_variant(vid, import_queue_id, session['user']['user_id'], session['user']['roles'], conn)
            flash("Successfully requested variant import of HerediCare VID: " + str(vid), "alert-success")
            return redirect(url_for('user.single_vid_imports'))


    
    if do_redirect:
        return redirect(url_for('user.admin_dashboard'))
    return render_template('user/admin_dashboard.html', most_recent_import_request=most_recent_import_request, job_config = job_config, annotation_stati = annotation_stati, errors = errors, warnings = warnings, total_num_variants = total_num_variants)



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




