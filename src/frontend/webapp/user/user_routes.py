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
    conn = Connection()
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
        if not is_list_owner:
            return abort(403)

    #user = session['user']['given_name'] + ' ' + session['user']['family_name']
    if request.method == 'POST':
        request_type = request.args['type']
        
        # actions on the lists themselves
        if request_type == 'create':
            list_name = request.form['list-name']
            conn.insert_user_variant_list(user_id, list_name)
            flash("Successfully created new list: \"" + list_name + "\"", "alert-success")
            conn.close()
            return redirect(url_for('user.my_lists'))
        if request_type == 'edit':
            list_name = request.form['list-name']
            list_id = request.form['list-id']
            if list_id is not None:
                is_list_owner = conn.check_user_list_ownership(user_id, list_id)
                if not is_list_owner:
                    return abort('403')
            conn.update_user_variant_list(list_id, user_id, list_name)
            flash("Successfully changed list name to \"" + list_name + "\"", "alert-success")
            conn.close()
            return redirect(url_for('user.my_lists'))
        if request_type == 'delete_list':
            list_id = request.form['list-id']
            if list_id is not None:
                is_list_owner = conn.check_user_list_ownership(user_id, list_id)
                if not is_list_owner:
                    return abort('403')
            conn.delete_user_variant_list(list_id)
            flash("Successfully removed list", "alert-success")
            conn.close()
            return redirect(url_for('user.my_lists'))

        # actions on variant list view
        if request_type == 'search':
            pass

        if request_type == 'delete_variant':
            variant_id_to_delete = request.args['variant_id']
            conn.delete_variant_from_list(view_list_id, variant_id_to_delete)
            url_to_deleted_variant = url_for('variant.display', variant_id=variant_id_to_delete)
            conn.close()
            flash(Markup("Successfully removed variant from list! Go <a href='" + url_to_deleted_variant + "'>here</a> to undo this action."), "alert-success")
            return redirect(url_for('user.my_lists', view=view_list_id))




    genes = request.args.get('genes', '')
    ranges = request.args.get('ranges', '')
    consensus = request.args.getlist('consensus')
    consensus = ';'.join(consensus)
    hgvs = request.args.get('hgvs', '')
    variant_ids_oi = request.args.get('variant_ids_oi', '')
    if view_list_id is not None:
        variant_ids_oi = conn.get_variant_ids_from_list(view_list_id) # need to check if this list belongs the currently logged in user!
        variant_ids_oi = ';'.join(variant_ids_oi)
        if variant_ids_oi != '':
            variants, total = conn.get_variants_page_merged(page, per_page, user_id=user_id, ranges=ranges, genes = genes, consensus=consensus, hgvs=hgvs, variant_ids_oi=variant_ids_oi)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')


    
    conn.close()
    return render_template('user/my_lists.html', 
                            user_lists = user_lists,
                            variants=variants, 
                            page=page, 
                            per_page=per_page, 
                            pagination=pagination, 
                            view_list_id=view_list_id)