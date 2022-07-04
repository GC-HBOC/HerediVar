from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from werkzeug.exceptions import abort
import common.functions as functions
import annotation_service.fetch_heredicare_variants as heredicare
from datetime import datetime
from ..utils import require_permission, require_login
import jsonschema
import os
import json
import requests

variant_io_blueprint = Blueprint(
    'variant_io',
    __name__
)

@variant_io_blueprint.route('/import-variants', methods=('GET', 'POST'))
@require_permission
def import_variants():
    conn = Connection()
    most_recent_import_request = conn.get_most_recent_import_request()
    if most_recent_import_request is None:
        status = 'finished'
    else:
        status = most_recent_import_request[3]

    if request.method == 'POST':
        request_type = request.args.get("type")
        if request_type == 'update_variants':


            if status == 'finished':
                import_queue_id = conn.insert_import_request(username = session['user']['user_id'])
                requested_at = conn.get_import_request(import_queue_id = import_queue_id)[2]
                requested_at = datetime.strptime(str(requested_at), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d-%H-%M-%S')

                logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
                log_file_path = logs_folder + 'heredicare_import:' + requested_at + '.log'
                heredicare.process_all(log_file_path)
                log_file_path = heredicare.get_log_file_path()
                date = log_file_path.strip('.log').split(':')[1].split('-')

                conn.close_import_request(import_queue_id)
                conn.close()
                return redirect(url_for('variant_io.import_summary', year=date[0], month=date[1], day=date[2], hour=date[3], minute=date[4], second=date[5]))

        elif request_type == 'reannotate':
            conn = Connection()
            variant_ids = conn.get_all_valid_variant_ids()
            for variant_id in variant_ids:
                conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])

            flash('Variant reannotation requested. It will be computed in the background.', 'alert-success')
        
    conn.close()
    return render_template('variant_io/import_variants.html', most_recent_import_request=most_recent_import_request)



@variant_io_blueprint.route('/import-variants/summary?date=<string:year>-<string:month>-<string:day>-<string:hour>-<string:minute>-<string:second>')
@require_login
def import_summary(year, month, day, hour, minute, second):
    logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
    requested_at = '-'.join([year, month, day, hour, minute, second])
    log_file = 'heredicare_import:' + requested_at + '.log'
    try:
        import_log_file = open(path.join(logs_folder, log_file), 'r')
    except:
        abort(404) # redirect to 404 page if the log file does not exist!
    num_new_variants = 0
    num_deleted_variants = 0
    num_error_new_variants = 0
    num_variants_new_annotations = 0
    num_rejected_to_delete_variants = 0
    num_duplicate_variants = 0

    num_heredivar_exclusive = 0
    num_heredicare_exclusive = 0
    num_heredivar_and_heredicare = 0
    for line in import_log_file:
        if '~~s0~~' in line:
            num_new_variants += 1 #functions.find_between(line, 'a total of ', ' vids were')
        if '~~s1~~' in line:
            num_deleted_variants += 1
        if '~~e2~~' in line:
            num_error_new_variants += 1
        if '~~i8~~' in line:
            num_variants_new_annotations += 1
        if '~~i2~~' in line:
            num_rejected_to_delete_variants += 1
        if '~~i1~~' in line:
            num_duplicate_variants += 1

        if '~~i5~~' in line:
            num_heredivar_exclusive = functions.find_between(line, 'a total of ', ' vids were')
        if '~~i6~~' in line:
            num_heredicare_exclusive = functions.find_between(line, 'a total of ', ' vids were')
        if '~~i7~~' in line:
            num_heredivar_and_heredicare = functions.find_between(line, 'a total of ', ' vids were')
    
    conn = Connection()
    finished_at = conn.get_import_request(date = requested_at)[4]
    print(finished_at)
    conn.close()
    requested_at = datetime.strptime(requested_at, '%Y-%m-%d-%H-%M-%S').strftime('%Y-%m-%d %H:%M:%S')
    print(requested_at)
    return render_template('variant_io/import_variants_summary.html', 
                            num_new_variants=num_new_variants,
                            num_deleted_variants=num_deleted_variants, 
                            num_error_new_variants=num_error_new_variants, 
                            num_variants_new_annotations=num_variants_new_annotations,
                            num_rejected_to_delete_variants=num_rejected_to_delete_variants,
                            num_heredivar_exclusive=num_heredivar_exclusive,
                            num_heredicare_exclusive=num_heredicare_exclusive,
                            num_heredivar_and_heredicare=num_heredivar_and_heredicare,
                            num_duplicate_variants=num_duplicate_variants,
                            requested_at=requested_at,
                            finished_at=finished_at,
                            log_file = log_file)




@variant_io_blueprint.route('/submit_clinvar/<int:variant_id>', methods=['GET', 'POST'])
@require_permission
def submit_clinvar(variant_id):
    # get relevant information
    conn = Connection()
    consensus_classification = conn.get_consensus_classification(variant_id, most_recent=True)
    if consensus_classification is None:
        flash("There is no consensus classification for this variant! Please create one before submitting to ClinVar!", "alert-danger")
        return redirect(url_for('variant.display', variant_id  =variant_id))
    else:
        consensus_classification = consensus_classification[0]
    variant_oi = conn.get_variant_more_info(variant_id)
    genes = variant_oi[6]
    if genes is None:
        genes = []
    else:
        genes = genes.split(';')
    conn.close

    orphanet_json = requests.get("https://api.orphacode.org/EN/ClinicalEntity", headers={'apiKey': 'HerediVar'})
    orphanet_json = json.loads(orphanet_json.text)
    orphanet_codes = {}
    for entry in orphanet_json:
        if entry['Status'] == 'Active':
            orpha_code = entry['ORPHAcode']
            preferred_term = entry['Preferred term']
            #orpha_definition = entry['Definition']
            orphanet_codes[orpha_code] = preferred_term

    #from collections import OrderedDict
    #orphanet_codes = OrderedDict(sorted(orphanet_codes.items(), key=lambda t: t[1]))
    
    orphanet_codes = list(orphanet_codes.items())
    orphanet_codes = [str(x[1]) + ': ' + str(x[0]) for x in orphanet_codes]
    #print(orphanet_codes)

    if request.method == 'POST':
        selected_condition = request.form['condition']
        selected_gene = request.form.get('gene', None)
        if not selected_condition:
            flash("All fields are required!", "alert-danger")
        elif selected_condition not in orphanet_codes:
            flash("The selected condition contains errors. It MUST be one of the provided autocomplete values.", 'alert-danger')
        else:
            # submit to clinvar api
            base_url = 'https://submit.ncbi.nlm.nih.gov/api/v1/submissions/?dry-run=true'
            api_key = os.environ.get('CLINVAR_API_KEY')
            headers = {'SP-API-KEY': api_key, 'Content-type': 'application/json'}

            schema = json.loads(open("/mnt/users/ahdoebm1/HerediVar/clinvar_submission_schema.json").read())

            selected_condition_orphanet_id = str(selected_condition.split(': ')[1])
            data = get_clinvar_submission_json(variant_oi, consensus_classification, selected_gene, selected_condition_orphanet_id)

    
            try:
                jsonschema.validate(instance = data, schema = schema)
            except jsonschema.exceptions.ValidationError as ex:
                abort(500, 'There is an error in the JSON for ClinVar api submission!' + str(ex))


            postable_data = {
                "actions": [{
                    "type": "AddData",
                    "targetDb": "clinvar",
                    "data": {"content": data}
                }]
            }

            resp = requests.post(base_url, headers = headers, data=json.dumps(postable_data))
            if resp.status_code == 200:
                flash("Successfully uploaded consensus classification to ClinVar.", "alert-success")
                return redirect(url_for('variant.display', variant_id=variant_id))
            flash("There was an error during submission to clinvar. It ended with status code: " + str(resp.status_code), "alert-danger")
    

    # the orphanet codes have to be in a dictionary so that they are parsable as a list by JSON.parse!
    data = {
        'orphanet_codes': orphanet_codes
    }
    return render_template('variant_io/submit_clinvar.html', data = data, genes=genes)


def class_to_text(classification):
    classification = str(classification)
    if classification == '1':
        return 'Benign'
    if classification == '2':
        return 'Likely Benign'
    if classification == '3':
        return 'Uncertain significance'
    if classification == '4':
        return 'Likely pathogenic'
    if classification == '5':
        return 'Pathogenic'


def get_clinvar_submission_json(variant_oi, consensus_classification, selected_gene, selected_condition_orphanet_id):
    # required fields: 
    # clinvarSubmission > clinicalSignificance > clinicalSignificanceDescription (one of: "Pathogenic", "Likely pathogenic", "Uncertain significance", "Likely benign", "Benign", "Pathogenic, low penetrance", "Uncertain risk allele", "Likely pathogenic, low penetrance", "Established risk allele", "Likely risk allele", "affects", "association", "drug response", "confers sensitivity", "protective", "other", "not provided")
    # clinvarSubmission > clinicalSignificance > comment
    # clinvarSubmission > clinicalSignificance > customAssertionScore (ACMG) !!! requires assertion method as well
    # clinvarSubmission > clinicalSignificance > dateLastEvaluated

    # clinvarSubmission > conditionSet > condition > id (hereditary breast cancer)
    # clinvarSubmission > conditionSet > condition > db (OMIM)

    # clinvarSubmission > localID (HerediVar variant_id)

    # clinvarSubmission > observedIn > affectedStatus (not provided??)
    # clinvarSubmission > observedIn > alleleOrigin (not applicable??)
    # clinvarSubmission > observedIn > collectionMethod (curation: For variants that were not directly observed by the submitter, but were interpreted by curation of multiple sources, including clinical testing laboratory reports, publications, private case data, and public databases.)
    
    # clinvarSubmission > variantSet > variant > chromosomeCoordinates > alternateAllele (vcf alt field if up to 50nt long variant!)
    # clinvarSubmission > variantSet > variant > assembly (GRCh38)
    # clinvarSubmission > variantSet > variant > chromosome (Values are 1-22, X, Y, and MT)
    # clinvarSubmission > variantSet > variant > referenceAllele (vcf ref field)
    # clinvarSubmission > variantSet > variant > start (vcf pos field: 1-based coordinates)
    # clinvarSubmission > variantSet > variant > stop (vcf pos field + length of variant)

    data = {}
    clinvar_submission = []
    clinvar_submission_properties = {}

    assertion_criteria = {}
    citation = {'db':'PubMed', 'id': '25741868'}
    assertion_criteria['citation'] = citation
    assertion_criteria['method'] = 'ACMG Guidelines, 2015'
    clinvar_submission_properties['assertionCriteria'] = assertion_criteria
    
    clinical_significance = {}
    clinical_significance['clinicalSignificanceDescription'] = class_to_text(consensus_classification[3])
    clinical_significance['comment'] = consensus_classification[4]
    clinical_significance['customAssertionScore'] = 0
    clinical_significance['dateLastEvaluated'] = consensus_classification[5].strftime('%Y-%m-%d')
    clinvar_submission_properties['clinicalSignificance'] =  clinical_significance

    condition_set = {}
    condition = []
    condition.append({'id': selected_condition_orphanet_id, 'db': 'Orphanet'}) #(https://www.omim.org/entry/114480)
    condition_set['condition'] = condition
    clinvar_submission_properties['conditionSet'] =  condition_set

    clinvar_submission_properties['localID'] =  str(variant_oi[0])

    observed_in = []

    observed_in_properties = {}
    observed_in_properties['affectedStatus'] = 'not provided'
    observed_in_properties['alleleOrigin'] = 'germline'
    observed_in_properties['collectionMethod'] = 'curation'
    observed_in.append(observed_in_properties)
    clinvar_submission_properties['observedIn'] =  observed_in

    clinvar_submission_properties['recordStatus'] =  'novel'
    clinvar_submission_properties['releaseStatus'] =  'public'

    variant_set = {}
    variant = []
    variant_properties = {}



    # id,chr,pos,ref,alt
    variant_properties['chromosomeCoordinates'] = {'alternateAllele': variant_oi[4], 
                                                   'assembly': 'GRCh38', 
                                                   'chromosome': variant_oi[1].strip('chr'), 
                                                   'referenceAllele': variant_oi[3], 
                                                   'start': variant_oi[2],
                                                   'stop': int(variant_oi[2]) + len(variant_oi[3])-1}

    if selected_gene is not None:
        gene = []
        gene_properties = {'symbol': selected_gene}
        gene.append(gene_properties)
        variant_properties['gene'] = gene
    
    variant.append(variant_properties)
    variant_set['variant'] = variant
    clinvar_submission_properties['variantSet'] =  variant_set

    clinvar_submission.append(clinvar_submission_properties)

    data['clinvarSubmission'] = clinvar_submission
    print(data)
    return data