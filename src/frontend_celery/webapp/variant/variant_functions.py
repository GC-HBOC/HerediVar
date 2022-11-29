from ..utils import *
import datetime
import io
from common.pdf_generator import pdf_gen
from ..io.download_routes import calculate_class
from functools import cmp_to_key



def validate_and_insert_variant(chr, pos, ref, alt, genome_build):
    was_successful = True
    # validate request
    tmp_file_path = tempfile.gettempdir() + "/new_variant.vcf"
    tmp_vcfcheck_out_path = tempfile.gettempdir() + "/frontend_variant_import_vcf_errors.txt"
    functions.variant_to_vcf(chr, pos, ref, alt, tmp_file_path)

    do_liftover = genome_build == 'GRCh37'
    returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post = functions.preprocess_variant(tmp_file_path, do_liftover = do_liftover)
    

    #command = ['/mnt/users/ahdoebm1/HerediVar/src/common/scripts/preprocess_variant.sh', '-i', tmp_file_path, '-o', tmp_vcfcheck_out_path]

    #if genome_build == 'GRCh37':
    #    command.append('-l') # enable liftover
        
    #returncode, err_msg, command_output = functions.execute_command(command, 'preprocess_variant')
    #print(err_msg)
    #print(command_output)
    
    if returncode != 0:
        flash(err_msg, 'alert-danger')
        was_successful = False
        return was_successful
    if 'ERROR:' in vcf_errors_pre:
        flash(vcf_errors_pre.replace('\n', ' '), 'alert-danger')
        was_successful = False
        return was_successful
    if genome_build == 'GRCh37':
        unmapped_variants_vcf = open(tmp_file_path + '.lifted.unmap', 'r')
        unmapped_variant = None
        for line in unmapped_variants_vcf:
            if line.startswith('#') or line.strip() == '':
                continue
            unmapped_variant = line
            break
        unmapped_variants_vcf.close()
        if unmapped_variant is not None:
            flash('ERROR: could not lift variant ' + unmapped_variant, ' alert-danger')
            was_successful = False
            return was_successful
    if 'ERROR:' in vcf_errors_post:
        flash(vcf_errors_post.replace('\n', ' '), 'alert-danger')
        was_successful = False
        return was_successful

    if was_successful:
        tmp_file = open(tmp_file_path, 'r')
        for line in tmp_file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            parts = line.split('\t')
            new_chr = parts[0]
            new_pos = parts[1]
            new_ref = parts[3]
            new_alt = parts[4]
            break # there is only one variant in the file
        tmp_file.close()


        conn = get_connection()
        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt) # check if variant is already contained
        if not is_duplicate:
            # insert it & capture the annotation_queue_id of the newly inserted variant to start the annotation service in celery
            annotation_queue_id = conn.insert_variant(new_chr, new_pos, new_ref, new_alt, chr, pos, ref, alt, user_id = session['user']['user_id'])
            if not current_app.config['TESTING']:
                celery_task_id = start_annotation_service(annotation_queue_id = annotation_queue_id) # starts the celery background task
            flash(Markup("Successfully inserted variant: " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + 
                        ' (view your variant <a href="' + url_for("variant.display", chr=str(new_chr), pos=str(new_pos), ref=str(new_ref), alt=str(new_alt)) + '" class="alert-link">here</a>)'), "alert-success")
        else:
            flash(Markup("Variant not imported: already in database!! View it " + "<a href=" + url_for("variant.display", chr=str(new_chr), pos=str(new_pos), ref=str(new_ref), alt=str(new_alt)) + " class=\"alert-link\">here</a>"), "alert-danger")
            was_successful = False

    return was_successful




def add_scheme_classes(classifications, index): # the index is the index where the classification criteria are located
    annotated_classifications = []
    for classification in classifications:
        current_class = get_scheme_classification(classification[index], classification[index-1])
        classification.append(current_class)
        annotated_classifications.append(classification)
    return annotated_classifications



# sort & append strength to text
def prepare_scheme_criteria(classifications, index):
    new_classifications = []
    for classification in classifications:
        classification = list(classification) # needed because of append
        current_criteria = classification[index]

        current_criteria = sorted(current_criteria, key=cmp_to_key(compare))
        #current_scheme = classification[3]
        #for i in range(len(current_criteria)):
            #current_criteria[i] = list(current_criteria[i])
            #current_criteria[i].append(strength_to_text(current_criteria[i][3], current_scheme))
        classification[index] = current_criteria
        new_classifications.append(classification)
    return new_classifications

def compare(a, b):
    a = criterium_to_num(a[5])
    b = criterium_to_num(b[5])
    return a - b

def criterium_to_num(criterium):
    if 'pvs' in criterium:
        return 1
    if 'ps' in criterium:
        return 2
    if 'pm' in criterium:
        return 3
    if 'pp' in criterium:
        return 4
    if 'bp' in criterium:
        return 5
    if 'bs' in criterium:
        return 6
    if 'ba' in criterium:
        return 7
    if '1.' in criterium:
        return 5
    if '2.' in criterium:
        return 4
    if '3.' in criterium:
        return 3
    if '4.' in criterium:
        return 2
    if '5.' in criterium:
        return 1





def get_previous_user_classification(variant_id, user_id, conn):
    user_classifications = conn.get_user_classifications_extended(variant_id = variant_id, user_id=user_id)
    if user_classifications is not None:
        result = {}
        for user_classification in user_classifications:
            previous_classification=user_classification[1]
            previous_comment=user_classification[4]
            previous_classification_id=user_classification[0]
            scheme_id = user_classification[6]
            new_entry = {'class': previous_classification, 'comment':previous_comment, 'id':previous_classification_id}
            result[scheme_id] = new_entry
        return result
    else:
        return {}

def get_default_previous_classification():
    return {'has_classification': False, 'class': 3, 'comment':'', 'id':None}

def convert_scheme_criteria_to_dict(criteria):
    criteria_dict = {} # convert to dict criterium->criterium_id,strength,evidence
    for entry in criteria:
        criterium_id = entry[2]
        criteria_dict[criterium_id] = {'id':entry[0], 'strength_id':entry[3], 'evidence':entry[4]}
    return criteria_dict



def get_schemes_with_info(variant_id, user_id, conn):
    # fetch previous scheme classifications (could be multiple because of different schemes)
    # 0id, 1variant_id, 2user_id, 3scheme, 4date
    previous_classifications = conn.get_user_classifications_extended(variant_id = variant_id, user_id = user_id)
    # extract scheme and convert to scheme->scheme_classification_id dict
    schemes_with_info = {}
    if previous_classifications is not None:
        for entry in previous_classifications:
            scheme_id = entry[6]
            if scheme_id in schemes_with_info:
                raise RuntimeError("ERROR: There are multiple user scheme classifications for variant_id: " + str(variant_id) + ", scheme: " + scheme_id + ", user_id: " + str(user_id))
            schemes_with_info[scheme_id] = {'classification_id':entry[0], 
                                            'date':entry[5].strftime('%Y-%m-%d'), 
                                            'selected_criteria':conn.get_scheme_criteria_applied(entry[0]), 
                                            'literature':entry[14], 
                                            'full_name': entry[8] + ' ' + entry[9], 
                                            'affiliation': entry[10]
                                        }
    return schemes_with_info



def handle_scheme_classification(classification_id, criteria, conn, where = "user"):
    previous_criteria = conn.get_scheme_criteria_applied(classification_id, where = where)
    previous_criteria_dict = convert_scheme_criteria_to_dict(previous_criteria)
    
    scheme_classification_got_update = False
    for criterium_id in criteria:
        evidence = criteria[criterium_id]['evidence']
        strength_id = criteria[criterium_id]['criterium_strength_id']
        # insert new criteria
        if criterium_id not in previous_criteria_dict:
            conn.insert_scheme_criterium_applied(classification_id, criterium_id, strength_id, evidence, where=where)
            #scheme_classification_got_update = True
        # update records if they were present before
        elif evidence != previous_criteria_dict[criterium_id]['evidence'] or strength_id != previous_criteria_dict[criterium_id]['strength_id']:
            conn.update_scheme_criterium_applied(previous_criteria_dict[criterium_id]['id'], strength_id, evidence, where="user")
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


def handle_user_classification(variant_id, user_id, previous_classifications, new_classification, new_comment, scheme_id, conn):
    current_datetime = functions.get_now()
    received_update = False
    if scheme_id in previous_classifications: # user already has a classification -> he requests an update
        previous_classification = previous_classifications[scheme_id]
        if previous_classification['comment'] != new_comment or previous_classification['class'] != new_classification:
            conn.update_user_classification(previous_classification['id'], new_classification, new_comment, date = current_datetime)
            received_update = True
        return None, received_update
    else: # user does not yet have a classification for this variant -> he wants to create a new one
        conn.insert_user_classification(variant_id, new_classification, user_id, new_comment, current_datetime, scheme_id)
        flash(Markup("Successfully inserted new user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
        return conn.get_last_insert_id(), received_update
    


def handle_consensus_classification(variant_id, classification, comment, scheme_id, pmids, text_passages, criteria, scheme_description, conn):
    ## get relevant information
    annotations = conn.get_all_variant_annotations(variant_id)
    annotations.pop('consensus_classification', None)
    variant_oi = get_variant(conn, variant_id)
    current_datetime = functions.get_now()

    ## compute pdf containing all annotations
    for criterium_id in criteria:
        criteria[criterium_id]['strength_description'] = conn.get_classification_criterium_strength(criteria[criterium_id]['criterium_strength_id'])[3]
    evidence_b64 = get_evidence_pdf(variant_oi, annotations, classification, comment, current_datetime, pmids, text_passages, scheme_description, criteria)

    #functions.base64_to_file(evidence_b64, '/mnt/users/ahdoebm1/HerediVar/src/frontend/downloads/consensus_classification_reports/testreport.pdf')
    conn.insert_consensus_classification_from_variant_id(session['user']['user_id'], variant_id, classification, comment, evidence_document=evidence_b64, date = current_datetime, scheme_id=scheme_id)
    flash(Markup("Successfully inserted new consensus classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
    return conn.get_last_insert_id() # returns the consensus_classification_id


def get_evidence_pdf(variant_oi, annotations, classification, comment, current_date, pmids, text_passages, scheme_description, selected_criteria):
    buffer = io.BytesIO()
    generator = pdf_gen(buffer)
    generator.add_title('Classification report')
    v = str(variant_oi[1]) + '-' + str(variant_oi[2]) + '-' + str(variant_oi[3]) + '-' + str(variant_oi[4])
    rsid = annotations.pop('rsid', None)
    if rsid is not None:
        rsid = rsid[4]
    selected_literature = list(zip(pmids, text_passages))
    selected_criteria_table = []
    for criterium_id in selected_criteria:
        selected_criteria_table.append([selected_criteria[criterium_id]['criterium_name'], selected_criteria[criterium_id]['strength_description'], selected_criteria[criterium_id]['evidence']])

    generator.add_variant_info(v, classification, current_date, comment, rsid, selected_literature, scheme_description, selected_criteria_table)

    # extract & remove special annotations
    literature = annotations.pop('literature', None)
    user_classifications = annotations.pop('user_classifications', None)
    clinvar_submissions = annotations.pop('clinvar_submissions', None)
    heredicare_center_classifications = annotations.pop('heredicare_center_classifications', None)
    #consensus_scheme_classifications = annotations.pop('consensus_scheme_classifications', None)
    #user_scheme_classifications = annotations.pop('user_scheme_classifications', None)
    assays = annotations.pop('assays', None)
    # consequences
    variant_consequences = annotations.pop('variant_consequences', None)

    # basic information
    generator.add_subtitle("Scores & annotations:")
    for key in annotations:
        #print(key)
        generator.add_relevant_information(key.replace('_', ' '), str(annotations[key][4]))
    if variant_consequences is not None:
        generator.add_subtitle("Variant consequences:")
        generator.add_text("Flags column: first number = is_gencode_basic, second number: is_mane_select, third number: is_mane_plus_clinical, fourth number: is_ensembl_canonical")
        generator.add_table([[x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[11], str(x[13]) + str(x[14]) + str(x[15]) + str(x[16])] for x in variant_consequences], 
            ('Transcript Name', 'HGVSc', 'HGVSp', 'Consequence', 'Impact', 'Exon Nr.', 'Intron Nr.', 'Gene Symbol', 'Protein Domain', 'Flags'), [3, 2, 2, 3, 1.5, 1.2, 1.3, 1.5, 1.6, 1.5])
    if literature is not None:
        generator.add_subtitle("PubMed IDs:")
        generator.add_relevant_literature([str(x[2]) for x in literature])
    if any(x is not None for x in [user_classifications, clinvar_submissions, heredicare_center_classifications]):
        generator.add_subtitle("Classifications:")
    #if consensus_scheme_classifications is not None:
    #    generator.add_text("HerediVar consensus scheme classifications:")
    #    consensus_scheme_classifications = add_scheme_classes(consensus_scheme_classifications, 10)
    #    table_data = []
    #    for classification in consensus_scheme_classifications:
    #        scheme = classification[3]
    #        criteria_string = ' ## '.join([criterium[2] + ' Strength: ' + strength_to_text(criterium[3], scheme) + ' Evidence: ' + criterium[4] for criterium in classification[10]])
    #        new_dat = [classification[11], classification[7] + ' ' + classification[8], classification[9], classification[4], scheme, criteria_string]
    #        table_data.append(new_dat)
    #    generator.add_relevant_classifications(table_data, ('Class', 'Submitter', 'Affiliation', 'Date', 'Scheme', 'Selected criteria'), [1.2, 2, 2, 2, 2.2, 9.3])
    if user_classifications is not None:
        generator.add_text("HerediVar user classifications:")

        for user_classification in user_classifications:
            generator.add_text("Basic information")
            generator.add_relevant_information("Class", user_classification[1])
            generator.add_relevant_information("Full name", user_classification[8] + ' ' + user_classification[9])
            generator.add_relevant_information("Affiliation", user_classification[10])
            generator.add_relevant_information("Date", user_classification[5].strftime('%Y-%m-%d  %H:%M:%S'))
            generator.add_relevant_information("Comment", user_classification[4])

            # add scheme classification
            scheme = user_classification[11]
            generator.add_text("Selected scheme: " + scheme)
            selected_criteria = user_classification[13]
            if len(selected_criteria) > 0:
                generator.add_text("Selected criteria:")
                generator.add_table([[x[5], x[7], x[4]] for x in selected_criteria], ["Criterium", "Strength", "Evidence"], [2,3.5,13.5]) # criterium, strength, evidence
            
            # add text passages
            selected_literature_passages = user_classification[14]
            if len(selected_literature_passages) > 0:
                generator.add_text("Selected literature:")
                generator.add_table([[x[2], x[3]] for x in selected_literature_passages], ["PMID", "Text passage"], [2, 17]) # pmid, text_passage
            else:
                generator.add_text("No further literature evidence selected.")


        #generator.add_relevant_classifications([[x[1], x[8] + ' ' + x[9], x[10], x[5], x[4]] for x in user_classifications], ('Class', 'Submitter', 'Affiliation', 'Date', 'Comment'), [1.2, 2, 2, 2, 11.5])
    #if user_scheme_classifications is not None:
    #    generator.add_text("HerediVar user scheme classifications:")
    #    user_scheme_classifications = add_scheme_classes(user_scheme_classifications, 9)
    #    table_data = []
    #    for classification in user_scheme_classifications:
    #        scheme = classification[3]
    #        criteria_string = ' ## '.join([criterium[2] + ' Strength: ' + strength_to_text(criterium[3], scheme) + ' Evidence: ' + criterium[4] for criterium in classification[9]])
    #        new_dat = [classification[10], classification[6] + ' ' + classification[7], classification[8], classification[4], scheme, criteria_string]
    #        table_data.append(new_dat)
    #    generator.add_relevant_classifications(table_data, ('Class', 'Submitter', 'Affiliation', 'Date', 'Scheme', 'Selected criteria'), [1.2, 2, 2, 2, 2.2, 9.3])
    if heredicare_center_classifications is not None:
        generator.add_text("HerediCare center classifications:")
        generator.add_table([[x[1], x[3], x[5], x[4]] for x in heredicare_center_classifications], ('Class', 'Center', 'Date', 'Comment'),  [2, 2, 2, 12])
    if clinvar_submissions is not None:
        generator.add_text("ClinVar submissions:")
        generator.add_table([[x[2], x[3], x[4], ';'.join([condition[0] for condition in x[5]]), x[6], x[7]] for x in clinvar_submissions], ('Interpretation', 'Last evaluated', 'Review status', 'Condition', 'Submitter', 'Comment'), [1.5, 2, 2, 2, 2, 9])
    if assays is not None:
        generator.add_text("Assays:")
        generator.add_table([[x[1], x[2], x[3]] for x in assays], ("Assay type", "Score", "Date"), [3,3,3])


    generator.save_pdf()
    buffer.seek(io.SEEK_SET)
    evidence_b64 = functions.buffer_to_base64(buffer)
    return evidence_b64



def extract_criteria_from_request(request_obj, scheme_id, conn):
    # test if the scheme classification is valid
    criteria = {}
    non_criterium_form_fields = ['scheme', 'classification_type', 'final_class', 'comment', 'strength_select', 'pmid', 'text_passage']
    if request_obj['scheme'] != '1':
        for criterium_name in request_obj:
            if criterium_name not in non_criterium_form_fields and '_strength' not in criterium_name:
                evidence = request_obj[criterium_name]
                strength = request_obj[criterium_name + '_strength']
                criterium_id = conn.get_classification_criterium_id(scheme_id, criterium_name)
                criterium_strength_id = conn.get_classification_criterium_strength_id(criterium_id, strength)
                criteria[criterium_id] = {'evidence':evidence, 'strength':strength, 'criterium_name': criterium_name, 'criterium_strength_id': criterium_strength_id}
    return criteria



def get_scheme_classification(criteria, scheme_type):
    all_strengths = []
    for entry in criteria:
        all_strengths.append(entry[6])
    response = calculate_class(str(scheme_type), '+'.join(all_strengths))
    return response.get_json()['final_class']



def is_valid_scheme(selected_criteria, scheme):
    is_valid = True
    message = ''

    scheme_criteria = scheme['criteria']
    scheme_description = scheme['description']

    if scheme['scheme_type'] == 'none': # abort, always valid, never insert data
        return is_valid, message

    # ensure that at least one criterium is selected
    if len(selected_criteria) == 0:
        is_valid = False
        message = "You must select at least one of the classification scheme criteria to submit a classification scheme based classification. The classification was not submitted."

    all_selected_criteria_names = [selected_criteria[x]['criterium_name'] for x in selected_criteria]

    # ensure that only valid criteria were submitted
    for criterium_id in selected_criteria:
        current_criterium = selected_criteria[criterium_id]
        criterium_name = current_criterium['criterium_name']
        #ensure that each criterum has some evidence
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
        if any([x in current_mutually_exclusive_criteria for x in all_selected_criteria_names]):
            is_valid = False
            message = "A mutually exclusive criterium to " + str(criterium_name) + " was selected. Remember to not select " + str(criterium_name) + " together with any of " + str(current_mutually_exclusive_criteria) + ". The classification was not submitted."
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


def handle_selected_literature(previous_selected_literature, classification_id, pmids, text_passages, conn, is_user = True):
    received_update = False
    # insert and update
    for pmid, text_passage in zip(pmids, text_passages):
        conn.insert_update_selected_literature(is_user = is_user, classification_id = classification_id, pmid = pmid, text_passage = text_passage)
        received_update = True
    
    # delete if missing in pmids
    for entry in previous_selected_literature:
        previously_selected_pmid = str(entry[2])
        if previously_selected_pmid not in pmids:
            classification_id = entry[1]
            conn.delete_selected_literature(is_user = is_user, classification_id=classification_id, pmid=previously_selected_pmid)
            received_update = True
    
    return received_update


def get_clinvar_submission(variant_id, conn):
    clinvar_submission_id = conn.get_external_ids_from_variant_id(variant_id, id_source="clinvar_submission")
    print(clinvar_submission_id)
    clinvar_submission = {'status': None, 'date': None, 'message': None}
    if len(clinvar_submission_id) > 1: # this should not happen!
        clinvar_submission_id = clinvar_submission_id[len(clinvar_submission_id) - 1]
        flash("WARNING: There are multiple clinvar submission ids for this variant. There is probably an old clinvar submission somewhere in the system which should be deleted. Using " + str(clinvar_submission_id) + " now.", "alert-warning")
    if len(clinvar_submission_id) == 1: # variant was already submitted to clinvar
        clinvar_submission_id = clinvar_submission_id[0]
    if len(clinvar_submission_id) > 0:
        api_key = current_app.config['CLINVAR_API_KEY']
        headers = {'SP-API-KEY': api_key, 'Content-type': 'application/json'}
        resp = get_clinvar_submission_status(clinvar_submission_id, headers = headers)
        if resp.status_code not in [200]:
            raise RuntimeError("Status check failed:\n" + resp.content.decode("UTF-8"))
        response_content = resp.json()['actions'][0]
        clinvar_submission_status = response_content['status']
        clinvar_submission['status'] = clinvar_submission_status
        if clinvar_submission_status in ['submitted', 'processing']:
            clinvar_submission_date = response_content['updated']
            clinvar_submission['date'] = clinvar_submission_date.replace('T', '\n').replace('Z', '')
        else:
            clinvar_submission_file_url = response_content['responses'][0]['files'][0]['url']
            submission_file_response = requests.get(clinvar_submission_file_url, headers = headers)
            if submission_file_response.status_code != 200:
                raise RuntimeError("Status check failed:" + "\n" + clinvar_submission_file_url + "\n" + submission_file_response.content.decode("UTF-8"))
            submission_file_response = submission_file_response.json()
            clinvar_submission_date = submission_file_response['submissionDate']
            clinvar_submission['date'] = clinvar_submission_date
            if clinvar_submission_status == 'error':
                clinvar_submission_messages = submission_file_response['submissions'][0]['errors'][0]['output']['errors']
                clinvar_submission_messages = [x['userMessage'] for x in clinvar_submission_messages]
                clinvar_submission_message = ';'.join(clinvar_submission_messages)
                clinvar_submission['message'] = clinvar_submission_message
    
    return clinvar_submission


