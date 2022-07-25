from ..utils import *
import datetime
import io
from common.pdf_generator import pdf_gen
from ..io.download_routes import calculate_acmg_class
from functools import cmp_to_key

def add_scheme_classes(classifications, index):
    annotated_classifications = []
    for classification in classifications:
        current_class = get_acmg_classification(classification[index])
        annotated_classifications.append(classification + (current_class,))
    return annotated_classifications



# sort & append strength to text
def prepare_scheme_criteria(classifications, index):
    new_classifications = []
    for classification in classifications:
        classification = list(classification)
        current_criteria = classification[index]
        current_criteria = sorted(current_criteria, key=cmp_to_key(compare))
        for i in range(len(current_criteria)):
            current_criteria[i] = list(current_criteria[i])
            current_criteria[i].append(strength_to_text(current_criteria[i][3]))
        classification[index] = current_criteria
        new_classifications.append(classification)
    return new_classifications

def compare(a, b):
    a = criterium_to_num(a[2])
    b = criterium_to_num(b[2])
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



def get_previous_user_classification(variant_id, user_id, conn):
    user_classification = conn.get_user_classification(user_id, variant_id)
    if user_classification is not None:
        previous_classification=user_classification[1]
        previous_comment=user_classification[4]
        previous_classification_id=user_classification[0]
        return {'has_classification': True, 'class': previous_classification, 'comment':previous_comment, 'id':previous_classification_id}
    else:
        return get_default_previous_classification()



def get_schemes_with_info(variant_id, user_id, conn):
    # fetch previous acmg classifications (could be multiple because of different schemes)
    # 0id, 1variant_id, 2user_id, 3scheme, 4date
    previous_acmg_classifications = conn.get_user_acmg_classification(variant_id, user_id)
    # extract scheme and convert to scheme->acmg_classification_id dict
    schemes_with_info = {}
    if previous_acmg_classifications is not None:
        for entry in previous_acmg_classifications:
            scheme_key = entry[3]
            if scheme_key in schemes_with_info:
                raise RuntimeError("ERROR: There are multiple user acmg classifications for variant_id: " + str(variant_id) + ", scheme: " + scheme_key + ", user_id: " + str(user_id))
            schemes_with_info[scheme_key] = {'classification_id':entry[0], 'date':entry[4].strftime('%Y-%m-%d'), 'selected_criteria':conn.get_acmg_criteria(entry[0])}
    return schemes_with_info
    


def get_default_previous_classification():
    return {'has_classification': False, 'class': 3, 'comment':'', 'id':None}



def convert_acmg_criteria_to_dict(criteria):
    criteria_dict = {} # convert to dict criterium->criterium_id,strength,evidence
    for entry in criteria:
        criterium_key = entry[2]
        criteria_dict[criterium_key] = {'id':entry[0], 'strength':entry[3], 'evidence':entry[4]}
    return criteria_dict



def handle_acmg_classification(acmg_classification_id, criteria, conn):
    previous_criteria = conn.get_acmg_criteria(acmg_classification_id)
    previous_criteria_dict = convert_acmg_criteria_to_dict(previous_criteria)
    
    acmg_classification_got_update = False
    for criterium in criteria:
        evidence = criteria[criterium]['evidence']
        strength = criteria[criterium]['strength']
        # insert new criteria
        if criterium not in previous_criteria_dict:
            conn.insert_acmg_criterium(acmg_classification_id, criterium, strength, evidence)
            acmg_classification_got_update = True
        # update records if they were present before
        elif evidence != previous_criteria_dict[criterium]['evidence'] or strength != previous_criteria_dict[criterium]['strength']:
            conn.update_acmg_criterium(previous_criteria_dict[criterium]['id'], strength, evidence)
            acmg_classification_got_update = True
    
    
    # delete unselected criterium tags
    criteria_to_delete = [x for x in previous_criteria_dict if x not in criteria]
    for criterium in criteria_to_delete:
        conn.delete_acmg_criterium(previous_criteria_dict[criterium]['id'])
        acmg_classification_got_update = True
    
    # make sure that the date corresponds to the date last edited!
    if acmg_classification_got_update:
        conn.update_acmg_classification_date(acmg_classification_id)
        flash("Successfully inserted/updated classification based on classification scheme", 'alert-success')
            


def handle_user_classification(variant_id, user_id, previous_classification, new_classification, new_comment, conn):
    current_date = datetime.datetime.today().strftime('%Y-%m-%d')
    if previous_classification['has_classification']: # user already has a classification -> he requests an update
        if previous_classification['comment'] != new_comment or previous_classification['class'] != new_classification:
            conn.update_user_classification(previous_classification['id'], new_classification, new_comment, date = current_date)
            flash(Markup("Successfully updated user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
    else: # user does not yet have a classification for this variant -> he wants to create a new one
        conn.insert_user_classification(variant_id, new_classification, user_id, new_comment, date = current_date)
        flash(Markup("Successfully inserted new user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
    


def handle_consensus_classification(variant_id, classification, comment, conn):
    ## get relevant information
    annotations = conn.get_all_variant_annotations(variant_id)
    annotations.pop('consensus_classification', None)
    variant_oi = get_variant(conn, variant_id)
    current_date = datetime.datetime.today().strftime('%Y-%m-%d')

    ## compute pdf containing all annotations
    evidence_b64 = get_evidence_pdf(variant_oi, annotations, classification, comment, current_date)

    #functions.base64_to_file(evidence_b64, '/mnt/users/ahdoebm1/HerediVar/src/frontend/downloads/consensus_classification_reports/testreport.pdf')
    conn.insert_consensus_classification_from_variant_id(session['user']['user_id'], variant_id, classification, comment, evidence_document=evidence_b64, date = current_date)
    


def get_evidence_pdf(variant_oi, annotations, classification, comment, current_date):
    buffer = io.BytesIO()
    generator = pdf_gen(buffer)
    generator.add_title('Classification report')
    v = str(variant_oi[1]) + '-' + str(variant_oi[2]) + '-' + str(variant_oi[3]) + '-' + str(variant_oi[4])
    rsid = annotations.pop('rsid', None)
    if rsid is not None:
        rsid = rsid[4]
    generator.add_variant_info(v, classification, current_date, comment, rsid)

    #literature
    literature = annotations.pop('literature', None)
    # classifications
    user_classifications = annotations.pop('user_classifications', None)
    clinvar_submissions = annotations.pop('clinvar_submissions', None)
    heredicare_center_classifications = annotations.pop('heredicare_center_classifications', None)

    # consequences
    variant_consequences = annotations.pop('variant_consequences', None)
    # basic information
    generator.add_subtitle("Scores & annotations:")
    for key in annotations:
        generator.add_relevant_information(key, str(annotations[key][4]))
    if variant_consequences is not None:
        generator.add_subtitle("Variant consequences:")
        generator.add_text("Flags column: first number = is_gencode_basic, second number: is_mane_select, third number: is_mane_plus_clinical, fourth number: is_ensembl_canonical")
        generator.add_relevant_classifications([[x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[11], str(x[13]) + str(x[14]) + str(x[15]) + str(x[16])] for x in variant_consequences], 
            ('Transcript Name', 'HGVSc', 'HGVSp', 'Consequence', 'Impact', 'Exon Nr.', 'Intron Nr.', 'Gene Symbol', 'Protein Domain', 'Flags'), [3, 2, 2, 3, 1.5, 1.2, 1.3, 1.5, 1.6, 1.5])
    
    if literature is not None:
        generator.add_subtitle("PubMed IDs:")
        generator.add_relevant_literature([str(x[2]) for x in literature])
    
    if user_classifications is not None or clinvar_submissions is not None or heredicare_center_classifications is not None:
        generator.add_subtitle("Previous classifications:")
    if user_classifications is not None:
        generator.add_text("HerediVar user classifications:")
        generator.add_relevant_classifications([[x[1], x[8] + ' ' + x[9], x[10], x[5], x[4]] for x in user_classifications], ('Class', 'User', 'Affiliation', 'Date', 'Comment'), [1.2, 2, 2, 2, 11.5])
    if heredicare_center_classifications is not None:
        generator.add_text("HerediCare center classifications:")
        generator.add_relevant_classifications([[x[1], x[3], x[5], x[4]] for x in heredicare_center_classifications], ('Class', 'Center', 'Date', 'Comment'),  [2, 2, 2, 12])
    if clinvar_submissions is not None:
        generator.add_text("ClinVar submissions:")
        generator.add_relevant_classifications([[x[2], x[3], x[4], x[5][1], x[6], x[7]] for x in clinvar_submissions], ('Interpretation', 'Last evaluated', 'Review status', 'Condition', 'Submitter', 'Comment'), [1.5, 2, 2, 2, 2, 9])
    
    generator.save_pdf()
    buffer.seek(io.SEEK_SET)
    evidence_b64 = functions.buffer_to_base64(buffer)
    return evidence_b64



def extract_criteria_from_request(request_obj):
    # test if the acmg classification is valid
    criteria = {}
    non_criterium_form_fields = ['scheme', 'classification_type', 'final_class', 'comment', 'strength_select']
    for criterium in request_obj:
        if criterium not in non_criterium_form_fields and '_strength' not in criterium:
            evidence = request_obj[criterium]
            strength = request_obj[criterium + '_strength']
            criteria[criterium] = {'evidence':evidence, 'strength':strength}
    return criteria



def get_acmg_classification(criteria):
    all_strengths = []
    for entry in criteria:
        all_strengths.append(entry[3])
    response = calculate_acmg_class('+'.join(all_strengths))
    return response.get_json()['final_class']



def is_valid_acmg(criteria, scheme):
    is_valid = True
    message = ''
    # ensure that at least one criterium is selected
    if len(criteria) == 0:
        is_valid = False
        message = "You must select at least one of the classification scheme criteria to submit a classification scheme based classification. The classification scheme based classification was not submitted."

    # ensure that only valid criteria were submitted -> handled by database
    # ensure that the strength properties are valid -> 
    # ensure that no criteria are selected that can't be selected following the scheme
    # ensure that no mutually exclusive criteria are selected
        
    criteria_with_strength_select = ['pp1', 'ps1', 'bp1', 'bs1']

    not_activateable_buttons = {
        'acmg_standard': [],
        'acmg_TP53': ['pm3', 'pm4', 'pp2', 'pp4', 'pp5', 'bp1', 'bp3', 'bp5', 'bp6'],
        'acmg_CDH1': ['pm1', 'pm3', 'pm5', 'pp2', 'pp4', 'pp5', 'bp1', 'bp3', 'bp6'],
        'task-force': []
    }

    disable_groups = {
        'acmg_standard': {
            # very strong pathogenic
            'pvs1': [],
            # strong pathogenic
            'ps1': [], 'ps2': [],'ps3': [],'ps4': [],
            # moderate pathogenic
            'pm1': [],'pm2': [],'pm3': [],'pm4': [],'pm5': [],'pm6': [],
            # supporting pathogenic
            'pp1': ['bs4'],'pp2': [],'pp3': [],'pp4': [],'pp5': [],
            # supporting benign
            'bp1': [],'bp2': [],'bp3': [],'bp4': [],'bp5': [],'bp6': [],'bp7': [],
            # strong benign
            'bs1': ['ps4'],'bs2': [],'bs3': [],'bs4': ['pp1'],
            # stand alone benign
            'ba1': ['ps4']
        },
        'acmg_TP53': {
            # very strong pathogenic
            'pvs1': [],
            # strong pathogenic
            'ps1': [], 'ps2': [],'ps3': [],'ps4': [],
            # moderate pathogenic
            'pm1': [],'pm2': [],'pm3': [],'pm4': [],'pm5': [],'pm6': [],
            # supporting pathogenic
            'pp1': ['bs4'],'pp2': [],'pp3': [],'pp4': [],'pp5': [],
            # supporting benign
            'bp1': [],'bp2': [],'bp3': [],'bp4': [],'bp5': [],'bp6': [],'bp7': [],
            # strong benign
            'bs1': ['ps4'],'bs2': [],'bs3': [],'bs4': ['pp1'],
            # stand alone benign
            'ba1': ['ps4']
        },
        'acmg_CDH1': {
            # very strong pathogenic
            'pvs1': [],
            # strong pathogenic
            'ps1': [], 'ps2': [],'ps3': [],'ps4': [],
            # moderate pathogenic
            'pm1': [],'pm2': [],'pm3': [],'pm4': [],'pm5': [],'pm6': [],
            # supporting pathogenic
            'pp1': ['bs4'],'pp2': [],'pp3': [],'pp4': [],'pp5': [],
            # supporting benign
            'bp1': [],'bp2': [],'bp3': [],'bp4': [],'bp5': [],'bp6': [],'bp7': [],
            # strong benign
            'bs1': ['ps4'],'bs2': [],'bs3': [],'bs4': ['pp1'],
            # stand alone benign
            'ba1': ['ps4']
        }
    }

    if 'task-force' in scheme:
        pass
    elif 'acmg' in scheme:
        if any(criterium[0] != criteria[criterium]['strength'][0] for criterium in criteria):
            is_valid = False
            message = "There are criteria with invalid strengths."
        if any((criterium not in criteria_with_strength_select) and (criterium[0:2] != criteria[criterium]['strength'][0:2]) for criterium in criteria):
            is_valid = False
            message = "There are criteria with strengths that can not be selected"

    if any(criterium in not_activateable_buttons[scheme] for criterium in criteria):
        is_valid = False
        message = "There are criteria which can not be activated with the provided scheme (" + scheme + ")"

    for criterium in criteria:
        current_disable_group = disable_groups[scheme][criterium]
        if (any(criterium in current_disable_group for criterium in criteria)):
            is_valid = False
            message = "There are criteria which are mutually exclusive to " + str(criterium)

    
    return is_valid, message
