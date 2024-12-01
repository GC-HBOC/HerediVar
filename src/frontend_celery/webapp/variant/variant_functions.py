from ..utils import *
from ..download.download_routes import calculate_class
from flask import render_template
import io
from webapp import tasks



def convert_scheme_criteria_to_dict(criteria):
    criteria_dict = {} # convert to dict criterium->criterium_id,strength,evidence
    for entry in criteria:
        criterium_id = entry[2]
        criteria_dict[criterium_id] = {'id':entry[0], 'strength_id':entry[3], 'evidence':entry[4], 'state':entry[9]}
    return criteria_dict


def handle_scheme_classification(classification_id, criteria, conn: Connection, where = "user"):
    previous_criteria = conn.get_scheme_criteria_applied(classification_id, where = where)
    previous_criteria_dict = convert_scheme_criteria_to_dict(previous_criteria)
    
    scheme_classification_got_update = False
    for criterium_id in criteria:
        evidence = criteria[criterium_id]['evidence']
        strength_id = criteria[criterium_id]['criterium_strength_id']
        state = criteria[criterium_id]['state']
        # insert new criteria
        if criterium_id not in previous_criteria_dict:
            conn.insert_scheme_criterium_applied(classification_id, criterium_id, strength_id, evidence, state, where=where)
        else: # update records if they were present before
            conn.update_scheme_criterium_applied(previous_criteria_dict[criterium_id]['id'], strength_id, evidence, state, where=where)
            scheme_classification_got_update = True
    
    # delete unselected criterium tags
    criteria_to_delete = [x for x in previous_criteria_dict if x not in criteria]
    for criterium in criteria_to_delete:
        conn.delete_scheme_criterium_applied(previous_criteria_dict[criterium]['id'], where=where)
        scheme_classification_got_update = True
    
    # make sure that the date corresponds to the date last edited!
    if scheme_classification_got_update:
        if where != "consensus":
            current_datetime = functions.get_now()
            conn.update_classification_date(classification_id, current_datetime)
        #flash("Successfully inserted/updated classification based on classification scheme", 'alert-success')
    
    return scheme_classification_got_update


def handle_user_classification(variant, user_id, new_classification, new_comment, scheme_id, scheme_class, conn: Connection):
    current_datetime = functions.get_now()
    received_update = False
    is_new_classification = False
    previous_classification_oi = variant.get_recent_user_classification(user_id, scheme_id)
    if previous_classification_oi is not None: # user already has a classification -> he requests an update
        if previous_classification_oi.comment != new_comment or previous_classification_oi.selected_class != new_classification or previous_classification_oi.scheme.selected_class != scheme_class:
            conn.update_user_classification(previous_classification_oi.id, new_classification, new_comment, date = current_datetime, scheme_class = scheme_class)
            received_update = True
        return None, received_update, is_new_classification
    else: # user does not yet have a classification for this variant -> he wants to create a new one
        is_new_classification = True
        conn.insert_user_classification(variant.id, new_classification, user_id, new_comment, current_datetime, scheme_id, scheme_class)
        return conn.get_last_insert_id(), received_update, is_new_classification
    


def handle_consensus_classification(variant, classification, comment, scheme_id, pmids, text_passages, criteria, scheme_description, scheme_class, conn: Connection):
    current_datetime = functions.get_now()

    ## compute pdf containing all annotations
    for criterium_id in criteria:
        criteria[criterium_id]['strength_description'] = conn.get_classification_criterium_strength(criteria[criterium_id]['criterium_strength_id'])[3]
    evidence_b64 = functions.buffer_to_base64(io.BytesIO())

    conn.insert_consensus_classification(session['user']['user_id'], variant.id, classification, comment, evidence_document=evidence_b64, date = current_datetime, scheme_id = scheme_id, scheme_class = scheme_class)
    return conn.get_last_insert_id() # returns the consensus_classification_id


def add_classification_report(variant_id, conn: Connection):
    variant = conn.get_variant(variant_id)
    consensus_classification_id = variant.get_recent_consensus_classification().id
    
    evidence_document_str = render_template("variant/classification_report.html", variant = variant, is_classification_report = True)
    
    static_folder = current_app.static_folder
    # add local scripts
    script_folder = os.path.join(static_folder, "js")
    package_folder = os.path.join(static_folder, "packages")
    insert_scripts = [os.path.join(script_folder, "utils.js"),
                      os.path.join(script_folder, "startup.js"),
                      os.path.join(script_folder, "variant.js"),
                      os.path.join(package_folder, "bootstrap/js/bootstrap.bundle.min.js"),
                      os.path.join(package_folder, "jquery/jquery.min.js"),
                      os.path.join(package_folder, "datatables/jquery.dataTables.min.js")
                      ]
    
    for path in insert_scripts:
        file_content = ""
        with open(path, 'r') as the_file:
            print(path)
            file_content = the_file.read()
        str_replace = "<script type='text/javascript'>" + file_content + "</script>"
        
        filename = os.path.basename(path)
        matches = re.finditer(r"<script.*src=['\"].*" + filename + r"['\"]>\s*</script>", evidence_document_str)
        
        for match in matches:
            str_match = match.group(0)
            print(str_match)
            evidence_document_str = evidence_document_str.replace(str_match, str_replace)
            str_replace = "" # delete all further occurances...
    
    # add local css
    css_folder = os.path.join(static_folder, "css")
    insert_css = [os.path.join(css_folder, "styles.css"),
                  os.path.join(css_folder, "colors.css"),
                  os.path.join(css_folder, "utils.css"),
                  os.path.join(package_folder, "bootstrap/css/bootstrap.min.css"),
                  os.path.join(package_folder, "datatables/jquery.dataTables.min.css")
                ]

    for path in insert_css:
        file_content = ""
        with open(path, 'r') as the_file:
            print(path)
            file_content = the_file.read()
        str_replace = "<style>" + file_content + "</style>"

        filename = os.path.basename(path)
        matches = re.finditer(r"<link rel=['\"]stylesheet['\"] href=['\"].*" + filename + r"['\"]>", evidence_document_str)
    
        for match in matches:
            str_match = match.group(0)
            print(str_match)
            evidence_document_str = evidence_document_str.replace(str_match, str_replace)
            str_replace = "" # delete all further occurances...

    # remove links
    matches = re.finditer(r"<.*class=['\"].*remove_link.*['\"].*>.*</.*>", evidence_document_str)
    for match in matches:
        str_match = match.group(0)
        evidence_document_str = evidence_document_str.replace(str_match, "")

    evidence_document_bytes = bytes(evidence_document_str, 'utf-8')
    print(len(evidence_document_bytes))
    conn.update_consensus_classification_report(consensus_classification_id, evidence_document_bytes)


def extract_criteria_from_request(request_obj, scheme_id, conn: Connection):
    criteria = {}
    non_criterium_form_fields = ['scheme', 'classification_type', 'final_class', 'comment', 'strength_select', 'pmid', 'text_passage']
    for criterium_name in request_obj:
        if criterium_name not in non_criterium_form_fields and '_strength' not in criterium_name and '_state' not in criterium_name:
            evidence = request_obj[criterium_name]
            strength = request_obj[criterium_name + '_strength']
            state = request_obj[criterium_name + '_state']
            criterium_id = conn.get_classification_criterium_id(scheme_id, criterium_name.upper())
            if criterium_id is None:
                abort(500, "A criterium was selected that does not exist for this scheme.")
            if state in ["unchecked"]:
                continue
            criterium_strength_id = conn.get_classification_criterium_strength_id(criterium_id, strength)
            criteria[criterium_id] = {'evidence':evidence, 'strength':strength, 'criterium_name': criterium_name.upper(), 'criterium_strength_id': criterium_strength_id, 'state': state}
    return criteria

# criteria dict from the extract criteria request function is the input
def get_scheme_class(criteria_dict, scheme_type, version):
    all_criteria_strengths = []
    keyval = 'strength'
    if scheme_type == 'task-force':
        keyval = 'criterium_name'
    for key in criteria_dict:
        if criteria_dict[key]['state'] == 'selected':
            #special cases
            if criteria_dict[key]["criterium_name"] == "BP1" and scheme_type in ["acmg-enigma-brca1", "acmg-enigma-brca2"]:
                all_criteria_strengths.append(criteria_dict[key]["criterium_name"] + '_' + criteria_dict[key][keyval])
            elif criteria_dict[key]["criterium_name"] == "PM2" and scheme_type in ["acmg-enigma-atm"]:
                all_criteria_strengths.append(criteria_dict[key]["criterium_name"] + '_' + criteria_dict[key][keyval])
            # default case
            else:
                all_criteria_strengths.append(criteria_dict[key][keyval])
    all_criteria_string = '+'.join(all_criteria_strengths)
    scheme_class = calculate_class(scheme_type, version, all_criteria_string)
    return scheme_class


def is_valid_scheme(selected_criteria, scheme, possible_states):
    is_valid = True
    message = ''

    if scheme is None:
        is_valid = False
        message = "Unknown scheme"
        return is_valid, message

    scheme_criteria = scheme['criteria']
    scheme_description = scheme['description']

    if scheme['scheme_type'] == 'none': # abort, always valid, never insert data
        return is_valid, message

    ## ensure that at least one criterium is selected
    #if len(selected_criteria) == 0:
    #    is_valid = False
    #    message = "You must select at least one of the classification scheme criteria to submit a classification scheme based classification. The classification was not submitted."

    all_selected_criteria_names = [selected_criteria[x]['criterium_name'] for x in selected_criteria if selected_criteria[x]['state'] == 'selected']

    mutually_inclusive_target_to_source = {}
    for source in scheme_criteria:
        current_mutually_inclusive_criteria = scheme_criteria[source]["mutually_inclusive_criteria"]
        for target in current_mutually_inclusive_criteria:
            functions.extend_dict(mutually_inclusive_target_to_source, target, source)

    # ensure that only valid criteria were submitted
    for criterium_id in selected_criteria:
        current_criterium = selected_criteria[criterium_id]
        criterium_name = current_criterium['criterium_name']
        # ensure that the criterium state is valid
        if current_criterium['state'] not in possible_states:
            is_valid = False
            message = "Criterium " + str(criterium_name) + " has an unknown state: " + str(current_criterium["state"])
            break
        # ensure that each criterum has some evidence
        if current_criterium['evidence'].strip() == '':
            is_valid = False
            message = "Criterium " + str(criterium_name) + " is missing evidence. The classification was not submitted."
            break
        # ensure that only valid criteria were submitted
        if criterium_name not in scheme_criteria:
            is_valid = False
            message = "Criterium " + str(criterium_name) + " is not a valid criterium for the " + scheme_description + " scheme. The classification was not submitted."
            break
        # ensure that the criteria are selectable in the selected scheme
        if scheme_criteria[criterium_name]['is_selectable'] == 0:
            is_valid = False
            message = "Criterium " + str(criterium_name) + " can not be selected for the " + scheme_description + " scheme. The classification was not submitted."
            break
        # ensure that the strength properties are valid
        current_possible_strengths = scheme_criteria[criterium_name]['possible_strengths']
        selected_strength = selected_criteria[criterium_id]['strength']
        if selected_strength not in current_possible_strengths:
            is_valid = False
            message = "Criterium " + str(criterium_name) + " received the strength: " + str(selected_strength) + " which is not valid for this criterium. Valid values are: " + str(current_possible_strengths) + ". The classification was not submitted."
            break
        # ensure that no mutually exclusive criteria are selected
        current_mutually_exclusive_criteria = scheme_criteria[criterium_name]['mutually_exclusive_criteria']
        if criterium_name in all_selected_criteria_names: # skip unselected criteria
            if any([x in current_mutually_exclusive_criteria for x in all_selected_criteria_names]):
                is_valid = False
                message = "A mutually exclusive criterium to " + str(criterium_name) + " was selected. Remember to not select " + str(criterium_name) + " together with any of " + str(current_mutually_exclusive_criteria) + ". The classification was not submitted."
                break
        # ensure that mutually inclusive criteria were only selected when their target is present
        current_mutually_inclusive_sources = mutually_inclusive_target_to_source.get(criterium_name, [])
        if not all([x in all_selected_criteria_names for x in current_mutually_inclusive_sources]):
            is_valid = False
            message = "If you want to select " + str(criterium_name) + " You also have to provide evidence for " + str(current_mutually_inclusive_sources) + ". The classification was not submitted."
            break
    
    return is_valid, message


def remove_empty_literature_rows(pmids, text_passages):
    new_pmids = []
    new_text_passages = []
    for pmid, text_passage in zip(pmids, text_passages):
        pmid = pmid.strip()
        text_passage = text_passage.strip()
        if pmid != '' or text_passage != '': # remove all completely empty lines (ie pmid and text passage is missing)
            new_pmids.append(pmid)
            new_text_passages.append(text_passage)
    return new_pmids, new_text_passages


def is_valid_literature(pmids, text_passages):
    message = ''
    is_valid = True
    
    # make sure each paper is only submitted once
    if len(list(set(pmids))) < len(pmids):
        message = 'ERROR: Some pmids are duplicated in the selected literature section. Please make them unique.'
        is_valid = False

    # make sure all information is present
    for pmid, text_passage in zip(pmids, text_passages):
        if pmid == '' or text_passage == '': # both empty already filtered out by remove_empty_literature_rows
            message = 'ERROR: Some of the selected literature is missing information. Please fill both, the pmid and the text passage for all selected papers.'
            is_valid = False

    return is_valid, message


def handle_selected_literature(previous_selected_literature, classification_id, pmids, text_passages, conn: Connection, is_user = True):
    received_update = False
    # insert and update
    for pmid, text_passage in zip(pmids, text_passages):
        conn.insert_update_selected_literature(is_user = is_user, classification_id = classification_id, pmid = pmid, text_passage = text_passage)
        received_update = True
    
    if previous_selected_literature is not None:
        # delete if missing in pmids
        for entry in previous_selected_literature:
            previously_selected_pmid = str(entry['pmid'])
            if previously_selected_pmid not in pmids:
                #classification_id = entry[1]
                conn.delete_selected_literature(is_user = is_user, classification_id=classification_id, pmid=previously_selected_pmid)
                received_update = True
    
    return received_update




#heredicare_queue_entries: ALL heredicare queue entries until error or success is hit
#publish_queue_heredicare_queue_entries: ONLY entries of publish_queue
def summarize_heredicare_status(heredicare_queue_entries, publish_queue, mrcc):
    summary = {"status": "unknown", "max_requested_at": "unknown", "insert_tasks_message": "", "needs_upload": False, "queue_entries": heredicare_queue_entries}

    if mrcc is not None:
        if mrcc.needs_heredicare_upload:
            summary["needs_upload"] = True

    if publish_queue is not None: # fresh upload - preferred
        prefer_publish_queue_status = True
        if publish_queue.insert_tasks_status in ["pending"]:
            summary["status"] = "waiting"
        elif publish_queue.insert_tasks_status in ["progress", "error"]:
            if heredicare_queue_entries is not None:
                for entry in heredicare_queue_entries: # id, status, requested_at, finished_at, message, vid, variant_id, submission_id, consensus_classification_id, publish_queue_id
                    if entry[9] == publish_queue.id: # current publish queue already issued job(s) for this variant
                        prefer_publish_queue_status = False
            if prefer_publish_queue_status and publish_queue.insert_tasks_status == "progress":
                summary["status"] = "requesting"
            if prefer_publish_queue_status and publish_queue.insert_tasks_status == "error":
                if mrcc.needs_heredicare_upload:
                    summary["status"] = "error"
                    summary["insert_tasks_message"] = publish_queue.insert_tasks_message
                else:
                    prefer_publish_queue_status = False
        elif publish_queue.insert_tasks_status in ["success"]:
            prefer_publish_queue_status = False
        if not prefer_publish_queue_status:
            if heredicare_queue_entries is not None: # prefer the status of the heredicare submission if they are available
                all_skipped = True
                for heredicare_queue_entry in heredicare_queue_entries:
                    current_status = heredicare_queue_entry[1]
                    current_requested_at = heredicare_queue_entry[2]
                    if current_status == 'skipped':
                        continue
                    all_skipped = False
                    if summary["status"] == "unknown":
                        summary["status"] = current_status
                    elif summary["status"] != current_status:
                        summary["status"] = "multiple stati"

                    if summary["max_requested_at"] == "unknown":
                        summary["max_requested_at"] = current_requested_at
                    elif summary["max_requested_at"] < current_requested_at:
                        summary["max_requested_at"] = current_requested_at
                if all_skipped:
                    summary["status"] = "skipped"

    #print(publish_queue)
    #print(heredicare_queue_entries)
    #print(summary)

    return summary



def summarize_clinvar_status(clinvar_queue_entries, publish_queue, mrcc):
    summary = {"status": "unknown", "insert_tasks_message": "", "needs_upload": False, "queue_entries": clinvar_queue_entries}

    if mrcc is not None:
        if mrcc.needs_clinvar_upload:
            summary["needs_upload"] = True

    if publish_queue is not None: # fresh upload - preferred
        prefer_publish_queue_status = True
        if publish_queue.insert_tasks_status in ["pending"]:
            summary["status"] = "waiting"
        elif publish_queue.insert_tasks_status in ["progress", "error"]:
            if clinvar_queue_entries is not None:
                for entry in clinvar_queue_entries: # id, status, requested_at, finished_at, message, vid, variant_id, submission_id, consensus_classification_id, publish_queue_id
                    if entry[1] == publish_queue.id: # current publish queue already issued job(s) for this variant
                        prefer_publish_queue_status = False
            if prefer_publish_queue_status and publish_queue.insert_tasks_status == "progress":
                summary["status"] = "requesting"
            if prefer_publish_queue_status and publish_queue.insert_tasks_status == "error":
                if mrcc.needs_clinvar_upload:
                    summary["status"] = "error"
                    summary["insert_tasks_message"] = publish_queue.insert_tasks_message
                else:
                    prefer_publish_queue_status = False
        elif publish_queue.insert_tasks_status in ["success"]:
            prefer_publish_queue_status = False
        if not prefer_publish_queue_status:
            if clinvar_queue_entries is not None: # prefer the status of the heredicare submission if they are available
                all_skipped = True
                for entry in clinvar_queue_entries:
                    current_status = entry[3]
                    if current_status == 'skipped':
                        continue
                    all_skipped = False
                    if summary["status"] == "unknown":
                        summary["status"] = current_status
                    elif summary["status"] != current_status:
                        summary["status"] = "multiple stati"
                if all_skipped:
                    summary["status"] = "skipped"

    return summary




#user = self.parse_raw_user(conn.get_user(user_id))
# session["user"]["user_id"]
def create_variant_from_request(request_obj, user, conn):
    result = {
        "flash_message": "",
        "flash_class": "",
        "flash_link": "",
        "status": ""
    }
    do_redirect = False
    
    create_variant_from = request_obj.args.get("type")

    if not create_variant_from:
        result["flash_message"] = "Missing type of variant information. Either vcf or hgvs."
        result["flash_class"] = "alert-danger"
        result["status"] = "error"
        
    if create_variant_from == 'vcf':
        chrom = request_obj.form.get('chr', '')
        pos = ''.join(request_obj.form.get('pos', '').split())
        ref = request_obj.form.get('ref', '').upper().strip()
        alt = request_obj.form.get('alt', '').upper().strip()
        genome_build = request_obj.form.get('genome')

        # we do not have to check the input parameters in depth here because 
        # they are checked by the validate_and_insert_variant function anyway
        # here we just make sure that the user submitted **something**
        # -> better understanding/readability of the error message
        if not chrom or not pos or not ref or not alt or 'genome' not in request_obj.form:
            result["flash_message"] = 'All fields are required!'
            result["flash_class"] = 'alert-danger flash_id:missing_data_vcf'
            result["status"] = "error"
        else:
            was_successful, message, variant_id = tasks.validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn = conn, user_id = user.id)
            new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_automatic_classification=False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False, include_external_ids=False)
            if 'already in database' in message:
                result["flash_message"] = "Variant not imported: " + new_variant.get_string_repr() + " already in database!"
                result["flash_class"] = 'alert-danger flash_id:variant_already_in_database'
                result["flash_link"] = url_for("variant.display", variant_id = new_variant.id)
                result["status"] = "skipped"
            elif was_successful:
                result["flash_message"] = "Successfully inserted variant: " + new_variant.get_string_repr()
                result["flash_class"] = 'alert-success flash_id:successful_variant_from_vcf'
                result["flash_link"] = url_for("variant.display", variant_id = new_variant.id)
                result["status"] = "success"
                current_app.logger.info(str(user.id) + " successfully created a new variant from vcf which resulted in this vcf-style variant: " + ' '.join([str(new_variant.chrom), str(new_variant.pos), new_variant.ref, new_variant.alt, "GRCh38"]))
                do_redirect = True
            else: # import had an error
                result["flash_message"] = message
                result["flash_class"] = 'alert-danger flash_id:variant_from_vcf_error'
                result["status"] = "error"

    if create_variant_from == 'hgvsc':
        reference_transcript = request_obj.form.get('transcript')
        hgvsc = request_obj.form.get('hgvsc')

        if not hgvsc or not reference_transcript:
            result["flash_message"] = 'All fields are required!'
            result["flash_class"] = 'alert-danger flash_id:missing_data_hgvs'
            result["status"] = "error"
        else:
            chrom, pos, ref, alt, possible_errors = functions.hgvsc_to_vcf(reference_transcript + ':' + hgvsc)
            if possible_errors != '':
                flash_message = possible_errors
                flash_class = 'alert-danger flash_id:variant_from_hgvs_error'
            else:
                was_successful, message, variant_id = tasks.validate_and_insert_variant(chrom, pos, ref, alt, 'GRCh38', conn = conn, user_id = session['user']['user_id'])
                new_variant = conn.get_variant(variant_id, include_annotations=False, include_consensus = False, include_user_classifications = False, include_heredicare_classifications = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
                if 'already in database' in message:
                    result["flash_message"] = "Variant not imported: " + new_variant.get_string_repr() + " already in database!"
                    result["flash_class"] = 'alert-danger flash_id:variant_already_in_database'
                    result["flash_link"] = url_for("variant.display", variant_id = new_variant.id)
                    result["status"] = "skipped"
                elif was_successful:
                    result["flash_message"] = "Successfully inserted variant: " + new_variant.get_string_repr()
                    result["flash_class"] = 'alert-success flash_id:successful_variant_from_hgvs'
                    result["flash_link"] = url_for("variant.display", variant_id = new_variant.id)
                    result["status"] = "success"
                    current_app.logger.info(str(user.id) + " successfully created a new variant from hgvs: " + hgvsc + "Which resulted in this vcf-style variant: " + ' '.join([str(new_variant.chrom), str(new_variant.pos), new_variant.ref, new_variant.alt, "GRCh38"]))
                    do_redirect = True
                else:
                    result["flash_message"] = message
                    result["flash_class"] = "alert-danger flash_id:variant_from_hgvs_error"
                    result["status"] = "error"

    if create_variant_from == 'vcf_file' and current_app.config["VCF_FILE_IMPORT_ACTIVE"]:
        genome_build = request_obj.form.get('genome')
        if 'file' not in request_obj.files or genome_build is None:
            result["flash_message"] = 'You must specify the genome build and select a vcf file.'
            result["flash_class"] = "alert-danger"
            result["status"] = "error"
        else:
            file = request_obj.files['file']
            filename = file.filename

            if file.filename.strip() == '' or not functions.filename_allowed(file.filename, allowed_extensions = {"vcf", "txt"}):
                result["flash_message"] = 'No valid file selected.'
                result["flash_class"] = "alert-danger"
                result["status"] = "error"
            else:
                filepath = functions.get_random_temp_file(fileending = "tsv", filename_ext = "import_vcf")
                with open(filepath, "w") as f: # file is deleted in task + we have to write to disk because filehandle can not be json serialized and thus, can not be given to a celery task
                    f.write(file.read().decode("utf-8"))
                user_id = session["user"]["user_id"]
                user_roles = session["user"]["roles"]
                #inserted_variants, skipped_variants = variant_functions.insert_variants_vcf_file(vcf_file, genome_build, conn)
                import_queue_id = tasks.start_variant_import_vcf(user_id, user_roles, conn, filename, filepath, genome_build)
                result["flash_message"] = 'Successfully submitted vcf file. The import is processed in the background".'
                result["flash_class"] = "alert-success"
                result["status"] = "success"
                #flash("Successfully submitted vcf file. The import is processed in the background", "alert-success")
                do_redirect = True
    
    return result, do_redirect
