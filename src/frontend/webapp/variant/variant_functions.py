from ..utils import *
import datetime
import io
from common.pdf_generator import pdf_gen
from ..io.download_routes import calculate_class
from functools import cmp_to_key

def add_scheme_classes(classifications, index): # the index is the index where the classification criteria are located
    annotated_classifications = []
    for classification in classifications:
        current_class = get_scheme_classification(classification[index], classification[3])
        annotated_classifications.append(classification + (current_class,))
    return annotated_classifications



# sort & append strength to text
def prepare_scheme_criteria(classifications, index):
    new_classifications = []
    for classification in classifications:
        classification = list(classification) # needed because of append
        current_criteria = classification[index]
        current_criteria = sorted(current_criteria, key=cmp_to_key(compare))
        current_scheme = classification[3]
        for i in range(len(current_criteria)):
            current_criteria[i] = list(current_criteria[i])
            current_criteria[i].append(strength_to_text(current_criteria[i][3], current_scheme))
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
    user_classification = conn.get_user_classification(user_id, variant_id)
    if user_classification is not None:
        previous_classification=user_classification[1]
        previous_comment=user_classification[4]
        previous_classification_id=user_classification[0]
        return {'has_classification': True, 'class': previous_classification, 'comment':previous_comment, 'id':previous_classification_id}
    else:
        return get_default_previous_classification()



def get_schemes_with_info(variant_id, user_id, conn):
    # fetch previous scheme classifications (could be multiple because of different schemes)
    # 0id, 1variant_id, 2user_id, 3scheme, 4date
    previous_scheme_classifications = conn.get_user_scheme_classification(variant_id, user_id)
    # extract scheme and convert to scheme->scheme_classification_id dict
    schemes_with_info = {}
    if previous_scheme_classifications is not None:
        for entry in previous_scheme_classifications:
            scheme_key = entry[3]
            if scheme_key in schemes_with_info:
                raise RuntimeError("ERROR: There are multiple user scheme classifications for variant_id: " + str(variant_id) + ", scheme: " + scheme_key + ", user_id: " + str(user_id))
            schemes_with_info[scheme_key] = {'classification_id':entry[0], 'date':entry[4].strftime('%Y-%m-%d'), 'selected_criteria':conn.get_scheme_criteria(entry[0])}
    return schemes_with_info
    


def get_default_previous_classification():
    return {'has_classification': False, 'class': 3, 'comment':'', 'id':None}



def convert_scheme_criteria_to_dict(criteria):
    criteria_dict = {} # convert to dict criterium->criterium_id,strength,evidence
    for entry in criteria:
        criterium_key = entry[2]
        criteria_dict[criterium_key] = {'id':entry[0], 'strength':entry[3], 'evidence':entry[4]}
    return criteria_dict



def handle_scheme_classification(scheme_classification_id, criteria, conn):
    previous_criteria = conn.get_scheme_criteria(scheme_classification_id)
    previous_criteria_dict = convert_scheme_criteria_to_dict(previous_criteria)
    
    scheme_classification_got_update = False
    for criterium in criteria:
        evidence = criteria[criterium]['evidence']
        strength = criteria[criterium]['strength']
        # insert new criteria
        if criterium not in previous_criteria_dict:
            conn.insert_scheme_criterium(scheme_classification_id, criterium, strength, evidence)
            scheme_classification_got_update = True
        # update records if they were present before
        elif evidence != previous_criteria_dict[criterium]['evidence'] or strength != previous_criteria_dict[criterium]['strength']:
            conn.update_scheme_criterium(previous_criteria_dict[criterium]['id'], strength, evidence)
            scheme_classification_got_update = True
    
    
    # delete unselected criterium tags
    criteria_to_delete = [x for x in previous_criteria_dict if x not in criteria]
    for criterium in criteria_to_delete:
        conn.delete_scheme_criterium(previous_criteria_dict[criterium]['id'])
        scheme_classification_got_update = True
    
    # make sure that the date corresponds to the date last edited!
    if scheme_classification_got_update:
        conn.update_scheme_classification_date(scheme_classification_id)
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
    annotations = conn.get_all_variant_annotations(variant_id, most_recent_scheme_consensus=False)
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
    consensus_scheme_classifications = annotations.pop('consensus_scheme_classifications', None)
    user_scheme_classifications = annotations.pop('user_scheme_classifications', None)

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
    
    if any(x is not None for x in [user_classifications, clinvar_submissions, heredicare_center_classifications, consensus_scheme_classifications, user_scheme_classifications]):
        generator.add_subtitle("Classifications:")
    if consensus_scheme_classifications is not None:
        generator.add_text("HerediVar consensus scheme classifications:")
        consensus_scheme_classifications = add_scheme_classes(consensus_scheme_classifications, 10)
        table_data = []
        for classification in consensus_scheme_classifications:
            scheme = classification[3]
            criteria_string = ' ## '.join([criterium[2] + ' Strength: ' + strength_to_text(criterium[3], scheme) + ' Evidence: ' + criterium[4] for criterium in classification[10]])
            new_dat = [classification[11], classification[7] + ' ' + classification[8], classification[9], classification[4], scheme, criteria_string]
            table_data.append(new_dat)
        generator.add_relevant_classifications(table_data, ('Class', 'Submitter', 'Affiliation', 'Date', 'Scheme', 'Selected criteria'), [1.2, 2, 2, 2, 2.2, 9.3])
    if user_classifications is not None:
        generator.add_text("HerediVar user classifications:")
        generator.add_relevant_classifications([[x[1], x[8] + ' ' + x[9], x[10], x[5], x[4]] for x in user_classifications], ('Class', 'Submitter', 'Affiliation', 'Date', 'Comment'), [1.2, 2, 2, 2, 11.5])
    if user_scheme_classifications is not None:
        generator.add_text("HerediVar user scheme classifications:")
        user_scheme_classifications = add_scheme_classes(user_scheme_classifications, 9)
        #print(user_scheme_classifications)
        table_data = []
        for classification in user_scheme_classifications:
            scheme = classification[3]
            criteria_string = ' ## '.join([criterium[2] + ' Strength: ' + strength_to_text(criterium[3], scheme) + ' Evidence: ' + criterium[4] for criterium in classification[9]])
            new_dat = [classification[10], classification[6] + ' ' + classification[7], classification[8], classification[4], scheme, criteria_string]
            table_data.append(new_dat)
        generator.add_relevant_classifications(table_data, ('Class', 'Submitter', 'Affiliation', 'Date', 'Scheme', 'Selected criteria'), [1.2, 2, 2, 2, 2.2, 9.3])
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
    # test if the scheme classification is valid
    criteria = {}
    non_criterium_form_fields = ['scheme', 'classification_type', 'final_class', 'comment', 'strength_select']
    for criterium in request_obj:
        if criterium not in non_criterium_form_fields and '_strength' not in criterium:
            evidence = request_obj[criterium]
            strength = request_obj[criterium + '_strength']
            criteria[criterium] = {'evidence':evidence, 'strength':strength}
    return criteria



def get_scheme_classification(criteria, scheme):
    all_strengths = []
    for entry in criteria:
        all_strengths.append(entry[3])
    response = calculate_class(scheme, '+'.join(all_strengths))
    return response.get_json()['final_class']



def is_valid_scheme(criteria, scheme):
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
        
    criteria_with_strength_select = get_criteria_with_strength_select()
    not_activateable_buttons = get_not_activatable_buttons()
    disable_groups = get_disable_groups()

    if 'task-force' in scheme:
        pass
    elif 'acmg' in scheme:
        if any(criterium[0] != criteria[criterium]['strength'][0] for criterium in criteria):
            is_valid = False
            message = "There are criteria with invalid strengths."
        if any((criterium not in criteria_with_strength_select[scheme]) and (criterium[0:2] != criteria[criterium]['strength'][0:2]) for criterium in criteria):
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


##### these functions return data which is needed to
# (1) display buttons correctly in frontend
# (2) verify that the inserted data is valid
def get_criteria_with_strength_select():
    criteria_with_strength_select = {
        'acmg_standard': [
            'pp1', 'ps1', 'bp1', 'bs1'
        ],
        'acmg_TP53': [
            'pp1', 'ps1', 'bp1', 'bs1'
        ],
        'acmg_CDH1': [
            'pp1', 'ps1', 'bp1', 'bs1'
        ],
        'task-force': [

        ],
        'task-force-brca': [

        ]
    }
    return criteria_with_strength_select

def get_not_activatable_buttons():
    not_activateable_buttons = {
        'acmg_standard': [],
        'acmg_TP53': ['pm3', 'pm4', 'pp2', 'pp4', 'pp5', 'bp1', 'bp3', 'bp5', 'bp6'],
        'acmg_CDH1': ['pm1', 'pm3', 'pm5', 'pp2', 'pp4', 'pp5', 'bp1', 'bp3', 'bp6'],
        'task-force': ['1.2', '2.5', '3.5', '4.1', '5.2'],
        'task-force-brca': []
    }
    return not_activateable_buttons

def get_disable_groups():
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
        },
        'task-force': {
            '1.1': [], '1.2': [], '1.3': [], 
            '2.1': [], '2.2': [], '2.3': [], '2.4': [], '2.5': [], '2.6': ['3.3'], '2.7': [], '2.8': [], '2.9': [], '2.10': [], 
            '3.1': [], '3.2': [], '3.3': [], '3.4': [], '3.5': [], 
            '4.1': [], '4.2': [], '4.3': ['3.3'], '4.4': ['3.3'], '4.5': [], '4.6': [], '4.7': [], '4.8': [], '4.9': [], 
            '5.1': [], '5.2': [], '5.3': [], '5.4': [], '5.5': [], '5.6': []
        },
        'task-force-brca': {
            '1.1': [], '1.2': [], '1.3': [], 
            '2.1': [], '2.2': [], '2.3': [], '2.4': [], '2.5': [], '2.6': ['3.3'], '2.7': [], '2.8': [], '2.9': [], '2.10': [], 
            '3.1': [], '3.2': [], '3.3': [], '3.4': [], '3.5': [], 
            '4.1': [], '4.2': [], '4.3': ['3.3'], '4.4': ['3.3'], '4.5': [], '4.6': [], '4.7': [], '4.8': [], '4.9': [], 
            '5.1': [], '5.2': [], '5.3': [], '5.4': [], '5.5': [], '5.6': []
        } 
    }
    return disable_groups
