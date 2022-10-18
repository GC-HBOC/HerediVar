from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session
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


user_blueprint = Blueprint(
    'user',
    __name__
)


@user_blueprint.route('/mylists', methods=['GET', 'POST'])
@require_login
def my_lists():
    user_id = session['user']['user_id']
    conn = get_connection()
    user_lists = conn.get_lists_for_user(user_id)

    # variant view table of lists in pagination
    view_list_id = request.args.get('view', None)
    variants = []
    page = int(request.args.get('page', 1))
    per_page = 20
    total = 0


    if view_list_id == '':
        return abort(404)

    if view_list_id is not None:
        is_list_owner = conn.check_user_list_ownership(user_id, view_list_id)
        #print(is_list_owner)
        if not is_list_owner:
            current_app.logger.error(session['user']['preferred_username'] + " attempted view list with id " + str(view_list_id) + ", but this list was not created by him.")
            return abort(403)

    #user = session['user']['given_name'] + ' ' + session['user']['family_name']
    if request.method == 'POST':
        request_type = request.args['type']
        
        # actions on the lists themselves
        if request_type == 'create':
            list_name = request.form['list_name']
            conn.insert_user_variant_list(user_id, list_name)
            flash("Successfully created new list: \"" + list_name + "\"", "alert-success")
            current_app.logger.info(session['user']['preferred_username'] + " successfully created list " + list_name)
            return redirect(url_for('user.my_lists'))
        if request_type == 'edit':
            list_name = request.form['list_name']
            list_id = request.form['list_id']
            if list_id is not None:
                is_list_owner = conn.check_user_list_ownership(user_id, list_id)
                if not is_list_owner:
                    return abort(403)
            conn.update_user_variant_list(list_id, user_id, list_name)
            flash("Successfully changed list name to \"" + list_name + "\"", "alert-success")
            current_app.logger.info(session['user']['preferred_username'] + " successfully changed list " + str(list_id) +" name to " + list_name)
            return redirect(url_for('user.my_lists'))
        if request_type == 'delete_list':
            list_id = request.form['list_id']
            if list_id == "":
                return abort(404)
            if list_id is not None:
                is_list_owner = conn.check_user_list_ownership(user_id, list_id)
                if not is_list_owner:
                    return abort(403)
            conn.delete_user_variant_list(list_id)
            flash("Successfully removed list", "alert-success")
            current_app.logger.info(session['user']['preferred_username'] + " successfully deleted list " + str(list_id)) 
            return redirect(url_for('user.my_lists'))

        # actions on variant list view
        if request_type == 'search':
            pass

        if request_type == 'delete_variant':
            variant_id_to_delete = request.args['variant_id']
            conn.delete_variant_from_list(view_list_id, variant_id_to_delete) # list ownership is already tested at the top of this function
            url_to_deleted_variant = url_for('variant.display', variant_id=variant_id_to_delete)
            flash(Markup("Successfully removed variant from list! Go <a href='" + url_to_deleted_variant + "'>here</a> to undo this action."), "alert-success")

            return redirect(url_for('user.my_lists', view=view_list_id))




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



    if view_list_id is not None:
        variant_ids_oi = conn.get_variant_ids_from_list(view_list_id)
        if len(variant_ids_oi) > 0:
            variants, total = conn.get_variants_page_merged(page, per_page, user_id=user_id, ranges=ranges, genes = genes, consensus=consensus, hgvs=hgvs, variant_ids_oi=variant_ids_oi)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    
    return render_template('user/my_lists.html', 
                            user_lists = user_lists,
                            variants=variants, 
                            page=page, 
                            per_page=per_page, 
                            pagination=pagination, 
                            view_list_id=view_list_id)


#
@user_blueprint.route('/admin_dashboard', methods=('GET', 'POST'))
@require_permission
def admin_dashboard():
    conn = get_connection()
    most_recent_import_request = conn.get_most_recent_import_request()
    if most_recent_import_request is None:
        status = 'finished'
    else:
        status = most_recent_import_request[3]

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
            variant_ids = conn.get_all_valid_variant_ids()
            for variant_id in variant_ids:
                start_annotation_service(variant_id = variant_id) # inserts a new annotation queue entry before submitting the task to celery
                #conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])
            current_app.logger.info(session['user']['preferred_username'] + " issued a reannotation of all variants") 
            flash('Variant reannotation requested. It will be computed in the background.', 'alert-success')
        
    return render_template('user/admin_dashboard.html', most_recent_import_request=most_recent_import_request)