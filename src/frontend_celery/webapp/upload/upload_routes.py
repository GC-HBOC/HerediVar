from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session
from werkzeug.exceptions import abort
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
import common.paths as paths

from . import upload_tasks
from . import upload_functions
from ..utils import *


upload_blueprint = Blueprint(
    'upload',
    __name__
)


# listens on get parameter: variant_ids (+ separated list of variant ids)
@upload_blueprint.route('/publish', methods=['GET', 'POST'])
@require_permission(['admin_resources'])
def publish():
    conn = get_connection()
    user_id = session['user']['user_id']
    user_roles = session['user']['roles']

    variant_ids = upload_functions.extract_variant_ids(request.args, conn)

    variants = []
    for variant_id in variant_ids:
        variant = conn.get_variant(variant_id, include_annotations=False,include_user_classifications=False, include_heredicare_classifications=False, include_automatic_classification=False, include_clinvar=False, include_assays=False, include_literature=False)
        if variant is None:
            return abort(404)
        else:
            variants.append(variant)

    if request.method == 'POST':
        options = {
            "do_clinvar": request.form.get('publish_clinvar', 'off') == 'on',
            "clinvar_selected_genes": upload_functions.extract_clinvar_selected_genes(variant_ids, request.form),
            "do_heredicare": request.form.get('publish_heredicare', 'off') == 'on',
            "post_consensus_classification": request.form.get('post_consensus_classification', 'off') == 'on'
        }
        print(options)

        if not options['post_consensus_classification']: # might be removed if it is allowed to only post the variant to HerediCaRe without consensus classification
            flash("You have to post the consensus classification to HerediCaRe.", "alert-danger")
        else:
            upload_tasks.start_publish(variant_ids, options, user_id, user_roles, conn) # (variant_ids, options, user_id, user_roles, conn: Connection):
            flash("Successfully requested data upload. It will be processed in the background.", "alert-success")
        return save_redirect(request.args.get('next', url_for('main.index')))

    return render_template("upload/publish.html",
                           variants = variants
                        )


@upload_blueprint.route('/upload/assay/<int:variant_id>', methods=['GET', 'POST'])
@require_permission(['edit_resources'])
def submit_assay(variant_id):
    conn = get_connection()

    require_valid(variant_id, "variant", conn)

    assay_types = conn.get_assay_types()

    do_redirect = False
    if request.method == 'POST':
        assay_type_id = request.form.get('assay_type_id')
        require_valid(assay_type_id, "assay_type", conn)
        
        # extract selected data from request and make sure that only valid data is submitted
        status, assay_metadata = upload_functions.extract_assay_metadata(assay_types[int(assay_type_id)]["metadata_types"], request)
        if status == "success":
            status, assay_filename, b_64_assay_report = upload_functions.extract_assay_report(request)

        # insert assay if all data is ok
        if status == "success":
            assay_id = conn.insert_assay(variant_id, assay_type_id, b_64_assay_report, assay_filename, link = None, date = functions.get_today(), user_id = session["user"]["user_id"])
            for metadata_type_id in assay_metadata:
                conn.insert_assay_metadata(assay_id, metadata_type_id, assay_metadata[metadata_type_id])
            variant = conn.get_variant(variant_id)
            flash({'message': "Successfully inserted new assay for variant " + variant.get_string_repr() + ". View the assay",
                   'link': url_for('variant.display', variant_id=variant_id)}, "alert-success")
            do_redirect = True
    
    if do_redirect :
        return redirect(url_for('upload.submit_assay', variant_id = variant_id))
    return render_template('upload/submit_assay.html', assay_types = assay_types)
