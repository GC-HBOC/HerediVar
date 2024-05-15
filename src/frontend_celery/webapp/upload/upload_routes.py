from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
import common.paths as paths

from ..utils import *
import jsonschema
import json
import requests
import io

from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session
from flask_paginate import Pagination

from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from . import upload_tasks
from . import upload_functions


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

        return save_redirect(request.args.get('next', url_for('upload.publish', variant_ids = ','.join(variant_ids))))



    return render_template("upload/publish.html",
                           variants = variants
                        )





#@upload_blueprint.route('/upload/variant/heredicare/<int:variant_id>', methods=['POST'])
#@require_permission(['admin_resources'])
#def upload_variant_heredicare(variant_id):
#    conn = get_connection()

#    variant = conn.get_variant(variant_id, include_annotations = False, include_user_classifications = False, include_clinvar = False, include_assays = False, include_literature = False, include_external_ids=True)
#    if variant is None:
#        return abort(404)

#    consensus_classification = variant.get_recent_consensus_classification()
#    if consensus_classification is None:
#        flash("There is no consensus classification for this variant! Please create one before submitting to HerediCaRe!", "alert-danger")
#        return redirect(url_for('variant.display', variant_id = variant_id))

#    celery_task_id = upload_tasks.start_upload_one_variant_heredicare(variant_id, upload_queue_id = None, user_id = session['user']['user_id'], user_roles = session['user']['roles'], conn = conn)






@upload_blueprint.route('/upload/variant/clinvar/<int:variant_id>', methods=['GET', 'POST'])
@require_permission(['admin_resources'])
def submit_clinvar(variant_id):
    conn = get_connection()

    # get variant information & abort if the variant does not exist
    variant = conn.get_variant(variant_id, include_annotations = True, include_user_classifications=False, include_heredicare_classifications=False,include_clinvar=True, include_assays=False)
    if variant is None:
        return abort(404)
    genes = variant.get_genes()
    if genes is None:
        genes = []

    # get current consensus classification & abort if the variant does not have a consensus classification
    consensus_classification = variant.get_recent_consensus_classification()
    if consensus_classification is None:
        flash("There is no consensus classification for this variant! Please create one before submitting to ClinVar!", "alert-danger")
        return redirect(url_for('variant.display', variant_id = variant_id))

    # check for previous heredivar clinvar submissions
    clinvar_accession = None
    previous_clinvar_submission = check_update_clinvar_status(variant_id, conn) # is None if there is no previous clinvar accession
    if previous_clinvar_submission is not None:
        clinvar_accession = previous_clinvar_submission[3]
        if previous_clinvar_submission[4] not in ['processed', 'error', 'deleted']:
            flash("This variant still has an unfinished ClinVar submission. Please wait for ClinVar to finish processing it before submitting making changes to it.", 'alert-danger')
            return redirect(url_for('variant.display', variant_id=variant_id))


    if request.method == 'POST':
        # extract submitted information
        selected_gene = request.form.get('gene', "")
        if selected_gene.strip() == "":
            selected_gene = None
        
        # submit to clinvar api
        #base_url = 'https://submit.ncbi.nlm.nih.gov/api/v1/submissions/?dry-run=true'
        #base_url = 'https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions'
        base_url = current_app.config['CLINVAR_API_ENDPOINT']

        # prepare json data to be submitted to ClinVar
        schema = json.loads(open(paths.clinvar_submission_schema).read())
        data = upload_functions.get_clinvar_submission_json(variant, selected_gene, clinvar_accession)
        #print(data)
        #with open("/mnt/storage2/users/ahdoebm1/HerediVar/testdat.json", "w") as jfile:
        #    jfile.write(json.dumps(data, indent=4))

        # check that the generated data is valid by checking against json schema
        try:
            jsonschema.validate(instance = data, schema = schema)
        except jsonschema.exceptions.ValidationError as ex:
            current_app.logger.error('There is an error in the JSON for ClinVar api submission!' + str(ex) + " For variant " + str(variant_id))
            abort(500, 'There is an error in the JSON for ClinVar api submission! ' + str(ex))

        # post to ClinVar
        api_key = current_app.config['CLINVAR_API_KEY']
        headers = {'SP-API-KEY': api_key, 'Content-type': 'application/json'}
        postable_data = {
            "actions": [{
                "type": "AddData",
                "targetDb": "clinvar",
                "data": {"content": data}
            }]
        }
        #print(json.dumps(postable_data))
        resp = requests.post(base_url, headers = headers, data=json.dumps(postable_data))
        #print(resp.json())
        if str(resp.status_code) not in ['200', '201']:
            abort(500, 'Status code of ClinVar submission API endpoint was: ' + str(resp.status_code) + ': ' + str(resp.json()))
            
        submission_id = resp.json()['id']
        clinvar_status = check_clinvar_status(submission_id)
        #print("Clinvar status: " + str(clinvar_status))

        # insert a new heredivar_clinvar_submission if the variant was not submitted previously or update if it was there previously
        conn.insert_update_heredivar_clinvar_submission(variant_id, submission_id, clinvar_status['accession_id'], clinvar_status['status'], clinvar_status['message'], clinvar_status['last_updated'], previous_clinvar_accession = clinvar_accession)
            
        # some user feedback that the submission was successful or not
        if resp.status_code == 200 or resp.status_code == 201:
            flash("Successfully uploaded consensus classification to ClinVar.", "alert-success")
            current_app.logger.info(session['user']['preferred_username'] + " successfully uploaded variant " + str(variant_id) + " to ClinVar.")
            return redirect(url_for('variant.display', variant_id=variant_id))
        flash("There was an error during submission to ClinVar. It ended with status code: " + str(resp.status_code), "alert-danger")
        current_app.logger.error(session['user']['preferred_username'] + " tried to upload a consensus classification for variant " + str(variant_id) + " to ClinVar, but it resulted in an error with status code: " + str(resp.status_code))

    return render_template('upload/submit_clinvar.html', 
                            variant = variant,
                            genes = genes)




@upload_blueprint.route('/upload/assay/<int:variant_id>', methods=['GET', 'POST'])
@require_permission(['edit_resources'])
def submit_assay(variant_id):
    conn = get_connection()

    assay_type2id = conn.get_assay_type_id_dict()
    possible_assays = {}
    for assay_type in assay_type2id:
        assay_type_id = assay_type2id[assay_type]
        metadata_types = conn.get_assay_metadata_types(assay_type_id, format = "dict")
        possible_assays[assay_type] = {"id": assay_type_id, "metadata_types": metadata_types}

    do_redirect = False
    if request.method == 'POST':
        assay_type = request.form.get('assay_type')

        selected_assay = possible_assays.get(assay_type)

        if selected_assay is None:
            flash("Assay type is not supported!", "alert-danger")
        else:
            # extract selected data from request and make sure that only valid data is submitted
            metadata_types = selected_assay["metadata_types"]
            status = "success"
            extracted_data = {}
            for metadata_type_name in metadata_types:
                metadata_type = metadata_types[metadata_type_name]
                
                current_data = request.form.get(str(metadata_type.id))
                if metadata_type.is_required and metadata_type.value_type != 'bool' and (current_data is None or current_data.strip() == ''):
                    flash("The metadata " + str(metadata_type.display_title) + " is required", "alert-danger")
                    status = "error"
                    break
                if metadata_type.value_type == "text" and current_data.strip() != '':
                    extracted_data[metadata_type.id] = str(current_data)
                elif metadata_type.value_type == "bool":
                    current_data = str(current_data)
                    if current_data not in ["None", "on"]:
                        flash("The value " + str(current_data) + " is not allowed for a boolean input field", "alert-danger")
                        status = "error"
                        break
                    extracted_data[metadata_type.id] = str(current_data == "on")
                elif metadata_type.value_type == "float" and current_data.strip() != '':
                    try:
                        extracted_data[metadata_type.id] = float(current_data)
                    except:
                        flash("The metadata " + str(metadata_type.display_title) + " is not numeric.", "alert-danger")
                        status = "error"
                        break
                elif "ENUM" in metadata_type.value_type:
                    possible_values = metadata_type.value_type.split(':')[1].split(',')
                    if current_data not in possible_values:
                        flash("The value " + str(current_data) + " is not allowed for field " + str(metadata_type.display_title), "alert-danger")
                        status = "error"
                        break
                    extracted_data[metadata_type.id] = current_data

            if status == "success":
                # extract report
                assay_report = request.files.get("report")
                if not assay_report or not assay_report.filename:
                    flash("No assay report provided or filename is missing", "alert-danger")
                    status = "error"

            if status == "success":
                assay_report.filename = secure_filename(assay_report.filename)
                # the buffer is required as larger files (>500kb) are saved to /tmp upon upload
                # this file must be read back in
                buffer = io.BytesIO()
                for line in assay_report:
                    buffer.write(line)
                buffer.seek(0)

                b_64_assay_report = functions.buffer_to_base64(buffer)

                if len(b_64_assay_report) > 16777215: # limited by the database mediumblob
                    current_app.logger.error(session['user']['preferred_username'] + " attempted uploading an assay which excedes the maximum filesize. The filesize was: " + str(len(b_64_assay_report)))
                    abort(500, "The uploaded file is too large. Please upload a smaller file.")

                assay_id = conn.insert_assay(variant_id, assay_type_id, b_64_assay_report, assay_report.filename, link = None, date = functions.get_today(), user_id = session["user"]["user_id"])
                for metadata_type_id in extracted_data:
                    conn.insert_assay_metadata(assay_id, metadata_type_id, extracted_data[metadata_type_id])

                flash("Successfully inserted new assay for variant " + str(variant_id), "alert-success")
                do_redirect = True

    if do_redirect :
        return redirect(url_for('upload.submit_assay', variant_id = variant_id))
    return render_template('upload/submit_assay.html', possible_assays = possible_assays)
