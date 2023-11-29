from flask import render_template, request, url_for, flash, redirect, Blueprint, current_app, session
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from werkzeug.exceptions import abort
import common.functions as functions
import common.paths as paths
import annotation_service.fetch_heredicare_variants as heredicare
from datetime import datetime
from ..utils import require_permission, get_clinvar_submission_status, get_connection, check_clinvar_status, check_update_clinvar_status
import jsonschema
import json
import requests
from werkzeug.utils import secure_filename
import io

variant_io_blueprint = Blueprint(
    'variant_io',
    __name__
)



"""
#http://srv018.img.med.uni-tuebingen.de:5000/import-variants/summary%3Fdate%3D2022-06-15-11-44-25
@variant_io_blueprint.route('/import-variants/summary?date=<string:year>-<string:month>-<string:day>-<string:hour>-<string:minute>-<string:second>')
@require_permission(['read_resources'])
def import_summary(year, month, day, hour, minute, second):
    logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
    requested_at = '-'.join([year, month, day, hour, minute, second])
    log_file = secure_filename('heredicare_import:' + requested_at + '.log')
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
    
    conn = get_connection()
    finished_at = conn.get_import_request(date = requested_at)[4]
    requested_at = datetime.strptime(requested_at, '%Y-%m-%d-%H-%M-%S').strftime('%Y-%m-%d %H:%M:%S')
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

"""

@variant_io_blueprint.route('/submit_clinvar/<int:variant_id>', methods=['GET', 'POST'])
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

    # get orphanet codes -- this is hardcoded now
    #orphanet_codes = get_orphanet_codes()

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
        data = get_clinvar_submission_json(variant, selected_gene, clinvar_accession)
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

    return render_template('variant_io/submit_clinvar.html', 
                            variant = variant,
                            genes = genes)


#def get_orphanet_codes():
#    # fetch orphanet entities for the autocomplete search bar
#    orphanet_json = requests.get(current_app.config['ORPHANET_DISCOVERY_URL'], headers={'apiKey': current_app.config['ORPHANET_API_KEY']})
#    orphanet_json = json.loads(orphanet_json.text)
#    orphanet_codes = []
#    for entry in orphanet_json:
#        if entry['Status'] == 'Active':
#            orpha_code = entry['ORPHAcode']
#            preferred_term = entry['Preferred term']
#            #orpha_definition = entry['Definition']
#            orphanet_codes.append([orpha_code, preferred_term + ': ' + str(orpha_code)])
#    return orphanet_codes






def get_clinvar_submission_json(variant, selected_gene, clinvar_accession = None):
    # required fields: 
    # clinvarSubmission > clinicalSignificance > clinicalSignificanceDescription (one of: "Pathogenic", "Likely pathogenic", "Uncertain significance", "Likely benign", "Benign", "Pathogenic, low penetrance", "Uncertain risk allele", "Likely pathogenic, low penetrance", "Established risk allele", "Likely risk allele", "affects", "association", "drug response", "confers sensitivity", "protective", "other", "not provided")
    # clinvarSubmission > clinicalSignificance > comment
    # clinvarSubmission > clinicalSignificance > customAssertionScore (ACMG) !!! requires assertion method as well
    # clinvarSubmission > clinicalSignificance > dateLastEvaluated

    # clinvarSubmission > conditionSet > condition > id (hereditary breast cancer)
    # clinvarSubmission > conditionSet > condition > db (OMIM)

    # clinvarSubmission > localID (HerediVar variant_id)

    # clinvarSubmission > observedIn > affectedStatus (not provided??)
    # clinvarSubmission > observedIn > alleleOrigin (germline)
    # clinvarSubmission > observedIn > collectionMethod (curation: For variants that were not directly observed by the submitter, but were interpreted by curation of multiple sources, including clinical testing laboratory reports, publications, private case data, and public databases.)
    
    # clinvarSubmission > variantSet > variant > chromosomeCoordinates > alternateAllele (vcf alt field if up to 50nt long variant!)
    # clinvarSubmission > variantSet > variant > assembly (GRCh38)
    # clinvarSubmission > variantSet > variant > chromosome (Values are 1-22, X, Y, and MT)
    # clinvarSubmission > variantSet > variant > referenceAllele (vcf ref field)
    # clinvarSubmission > variantSet > variant > start (vcf pos field: 1-based coordinates)
    # clinvarSubmission > variantSet > variant > stop (vcf pos field + length of variant)
    mrcc = variant.get_recent_consensus_classification()

    data = {}
    clinvar_submission = []
    clinvar_submission_properties = {}

    assertion_criteria = get_assertion_criteria(mrcc.scheme.type, mrcc.scheme.reference)
    data['assertionCriteria'] = assertion_criteria
    
    clinical_significance = {}
    clinical_significance['clinicalSignificanceDescription'] = mrcc.class_to_text()
    clinical_significance['comment'] = get_extended_comment(mrcc)
    clinical_significance['dateLastEvaluated'] = mrcc.date.split(' ')[0] # only grab the date and trim the time
    clinvar_submission_properties['clinicalSignificance'] =  clinical_significance

    if clinvar_accession is not None:
        clinvar_submission_properties['clinvarAccession'] = str(clinvar_accession)


    condition_set = {}
    condition = []
    condition.append({'id': "145", 'db': 'Orphanet'}) #(https://www.omim.org/entry/114480)
    condition_set['condition'] = condition
    clinvar_submission_properties['conditionSet'] =  condition_set

    clinvar_submission_properties['localID'] =  str(variant.id)

    observed_in = []

    observed_in_properties = {}
    observed_in_properties['affectedStatus'] = 'not provided'
    observed_in_properties['alleleOrigin'] = 'germline'
    observed_in_properties['collectionMethod'] = 'curation'
    observed_in.append(observed_in_properties)
    clinvar_submission_properties['observedIn'] =  observed_in

    if clinvar_accession is None:
        clinvar_submission_properties['recordStatus'] = 'novel'
    else:
        clinvar_submission_properties['recordStatus'] = 'update'
    data['clinvarSubmissionReleaseStatus'] = 'public'

    variant_set = {}
    variant_json = []
    variant_properties = {}

    # id,chr,pos,ref,alt
    variant_properties['chromosomeCoordinates'] = {'alternateAllele': variant.alt, 
                                                   'assembly': 'GRCh38', 
                                                   'chromosome': variant.chrom.strip('chr'), 
                                                   'referenceAllele': variant.ref, 
                                                   'start': variant.pos,
                                                   'stop': int(variant.pos) + len(variant.ref)-1}

    if selected_gene is not None:
        gene = []
        gene_properties = {'symbol': selected_gene}
        gene.append(gene_properties)
        variant_properties['gene'] = gene
    
    variant_json.append(variant_properties)
    variant_set['variant'] = variant_json
    clinvar_submission_properties['variantSet'] =  variant_set

    clinvar_submission.append(clinvar_submission_properties)

    data['clinvarSubmission'] = clinvar_submission
    #print(data)
    return data


def get_extended_comment(mrcc):
    selected_criteria = mrcc.scheme.criteria
    criterium_strings = []
    for criterium in selected_criteria:
        criterium_strings.append(criterium.name + " (" + criterium.strength + ")" + ": " + criterium.evidence)

    result = ""
    if len(criterium_strings) == 1:
        result = "According to the " + mrcc.scheme.display_name + " criteria we chose this criterium: " + criterium_strings[0]
    elif len(criterium_strings) > 1:
        result = "According to the " + mrcc.scheme.display_name + " criteria we chose these criteria: " + ', '.join(criterium_strings)
    
    return mrcc.comment.strip('.') + ". " + result


def get_assertion_criteria(scheme_type, assertion_criteria_source):
    assertion_criteria = {}
    if scheme_type in ['acmg', 'enigma-brca1', 'enigma-brca2']:
        assertion_criteria_source = assertion_criteria_source.replace('https://pubmed.ncbi.nlm.nih.gov/', '').strip('/')
        assertion_criteria['db'] = "PubMed"
        assertion_criteria['id'] = assertion_criteria_source
    elif scheme_type in ['enigma-brca1', 'enigma-brca2']:
        assertion_criteria['url'] = assertion_criteria_source
    else:
        assertion_criteria['url'] = assertion_criteria_source
    return assertion_criteria



@variant_io_blueprint.route('/submit_assay/<int:variant_id>', methods=['GET', 'POST'])
@require_permission(['edit_resources'])
def submit_assay(variant_id):

    do_redirect = False
    if request.method == 'POST':
        assay_type = request.form.get('assay_type')
        assay_report = request.files.get('report')
        assay_score = request.form.get('score')

        #print(assay_type)
        #print(assay_report)
        #print(assay_score)


        if not assay_type or not assay_report or not assay_score or not assay_report.filename:
            flash('All fields are required!', 'alert-danger')
        else:

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

            conn = get_connection()
            conn.insert_assay(variant_id, assay_type, b_64_assay_report, assay_report.filename, assay_score, functions.get_today())

            flash("Successfully uploaded a new assay for variant " + str(variant_id), "alert-success")

            current_app.logger.info(session['user']['preferred_username'] + " successfully uploaded a new assay for variant " + str(variant_id))

            do_redirect = True


            #functions.base64_to_file(b_64_assay_report, '/mnt/users/ahdoebm1/HerediVar/src/frontend/webapp/io/test.pdf')


    if do_redirect :
        return redirect(url_for('variant_io.submit_assay', variant_id = variant_id))
    return render_template('variant_io/submit_assay.html')
