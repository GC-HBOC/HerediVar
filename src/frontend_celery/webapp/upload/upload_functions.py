import io
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common import functions
from common.heredicare_interface import Heredicare
from common.db_IO import Connection
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils import *
from werkzeug.utils import secure_filename

# searches for the tag variant_ids in a request.args.
# two special cases: heredicare and clinvar which, when found, returns a variant_id list
# also watches for list_ids and extracts the variants from them
# of all variants which need a heredicare/clinvar upload
def extract_variant_ids(request_args, conn: Connection) -> list:
    result = []

    variant_ids_strs = request_args.getlist('variant_ids')
    if 'heredicare' in variant_ids_strs:
        variant_ids = conn.get_variant_ids_by_publish_heredicare_status(stati = ['pending', 'progress', 'submitted'])
        check_update_all_most_recent_heredicare(variant_ids, conn)
        result = conn.get_variant_ids_which_need_heredicare_upload()
    elif 'clinvar' in variant_ids_strs:
        variant_ids = conn.get_variant_ids_by_publish_clinvar_status(stati = ['pending', 'progress', 'submitted'])
        check_update_all_most_recent_clinvar(variant_ids, conn)
        result = conn.get_variant_ids_which_need_clinvar_upload()
    else:
        for variant_ids_str in variant_ids_strs:
            result.extend(variant_ids_str.split(','))

    list_ids_strs = request.args.getlist('list_id')
    for list_id in list_ids_strs:
        require_valid(list_id, "user_variant_lists", conn)
        require_list_permission(list_id, required_permissions = ['read'], conn = conn)
        list_variant_ids = conn.get_variant_ids_from_list(list_id)
        check_update_all_most_recent_heredicare(list_variant_ids, conn)
        check_update_all_most_recent_clinvar(list_variant_ids, conn)

        result.extend(conn.get_variant_ids_which_need_heredicare_upload(variant_ids_oi = list_variant_ids))
        result.extend(conn.get_variant_ids_which_need_clinvar_upload(variant_ids_oi = list_variant_ids))
    return list(set(result)) # make unique

# this function searches for clinvar_gene_{variant_id} tags of variants 
# of interest in a request form and saves it to a dictionary
def extract_clinvar_selected_genes(variant_ids, request_form) -> dict:
    result = {}
    for variant_id in variant_ids:
        selected_gene_id = request_form.get("clinvar_gene_" + str(variant_id))
        if selected_gene_id is not None:
            result[variant_id] = selected_gene_id
    return result

# search for assay metadata within a request
def extract_assay_metadata(metadata_types, request):
    status = "success"
    extracted_data = {}
    for metadata_type_name in metadata_types:
        metadata_type = metadata_types[metadata_type_name]
        current_data = request.form.get(str(metadata_type.id))

        # error if data is missing, but required
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
    return status, extracted_data

# search for the assay report within a request
def extract_assay_report(request):
    status = "success"

    assay_report = request.files.get("report")
    if not assay_report or not assay_report.filename:
        flash("No assay report provided or filename is missing", "alert-danger")
        status = "error"

    b_64_assay_report = None
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
            flash("The uploaded file is too large. Please upload a smaller file.")
            status = "error"

    return status, assay_report.filename, b_64_assay_report