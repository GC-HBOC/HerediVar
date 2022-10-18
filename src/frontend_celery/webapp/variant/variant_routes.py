from calendar import c
from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort, jsonify
from flask_paginate import Pagination

from ..utils import *

import datetime
import sys
from os import path

#sys.path.append(path.dirname(path.abspath(__file__)))
from .variant_functions import *

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection






variant_blueprint = Blueprint(
    'variant',
    __name__
)



#http:#srv018.img.med.uni-tuebingen.de:5000/search?ranges=chr1%3A0-9999999999999%3Bchr2%3A0-99999999999999999999%3BchrMT%3A0-9999999999999999
@variant_blueprint.route('/search')  # CDH1  chr1:10295758-17027834; chr11:108229378-108229378
@require_login
def search():

    genes = request.args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")

    ranges = request.args.get('ranges', '')
    ranges = preprocess_query(ranges, pattern= r"chr.+:\d+-\d+")
    if ranges is None:
        flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    
    consensus = request.args.getlist('consensus')
    consensus = ';'.join(consensus)
    consensus = preprocess_query(consensus, r'[12345-]?')
    if consensus is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")

    user = request.args.getlist('user')
    user = ';'.join(user)
    user = preprocess_query(user, r'[12345-]?')
    if user is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")

    hgvs = request.args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = r".*:?c\..+")
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! c.HGVS should be prefixed by this pattern: 'transcript:c.' Results are not filtered by hgvs.", "alert-danger")
    if any(not(x.startswith('ENST') or x.startswith('NM') or x.startswith('NR') or x.startswith('XM') or x.startswith('XR')) for x in hgvs):
        flash("You are probably searching for a HGVS c-dot string without knowing its transcript. Be careful with the search results as they might not contain the variant you are looking for!", "alert-warning")

    variant_ids_oi = request.args.get('variant_ids_oi', '')
    variant_ids_oi = preprocess_query(variant_ids_oi, r'\d*')
    if variant_ids_oi is None:
        flash("You have an error in your variant id query(s). It must contain only numbers. Results are not filtered by variants.", "alert-danger")

    page = int(request.args.get('page', 1))
    per_page = 20
    conn = get_connection()
    variants, total = conn.get_variants_page_merged(page, per_page, user_id=session['user']['user_id'], ranges=ranges, genes = genes, consensus=consensus, user=user, hgvs=hgvs, variant_ids_oi=variant_ids_oi)

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('variant/search.html', variants=variants, page=page, per_page=per_page, pagination=pagination)


# chr1-17027834-G-A
@variant_blueprint.route('/create', methods=('GET', 'POST'))
@require_login
def create():
    chrs = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13',
            'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT']
    
    if request.method == 'POST':
        create_variant_from = request.args.get("type")
        
        if create_variant_from == 'vcf':
            chr = request.form.get('chr', '')
            pos = ''.join(request.form['pos'].split())
            ref = request.form.get('ref', '').upper().strip()
            alt = request.form.get('alt', '').upper().strip()

            if not chr or not pos or not ref or not alt or 'genome' not in request.form:
                flash('All fields are required!', 'alert-danger')
            else:
                #try:
                #    pos = int(pos)
                #except:
                #    flash('ERROR: Genomic position is not a valid integer.', 'alert-danger')
                    
                if int(pos) < 0:
                    flash('ERROR: Negative genomic position given, but must be positive.', 'alert-danger')
                else:
                    
                    genome_build = request.form['genome']
                    was_successful = validate_and_insert_variant(chr, pos, ref, alt, genome_build)
                    if was_successful:
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant: " + ' '.join([chr, pos, ref, alt, genome_build]) + ". This information is the unprocessed user input.") 
                        return redirect(url_for('variant.create'))

                    


        if create_variant_from == 'hgvsc':
            reference_transcript = request.form.get('transcript')
            hgvsc = request.form.get('hgvsc')
            if not hgvsc or not reference_transcript:
                flash('All fields are required!', 'alert-danger')
            else:
                chr, pos, ref, alt, possible_errors = functions.hgvsc_to_vcf(reference_transcript + ':' + hgvsc)
                if possible_errors != '':
                    flash(possible_errors, "alert-danger")
                else:
                    was_successful = validate_and_insert_variant(chr, pos, ref, alt, 'GRCh38')
                    if was_successful:
                        current_app.logger.info(session['user']['preferred_username'] + " successfully created a new variant from hgvs: " + hgvsc + "Which resulted in this vcf-style variant: " + ' '.join([chr, pos, ref, alt, "GRCh38"]))
                        return redirect(url_for('variant.create'))

    return render_template('variant/create.html', chrs=chrs)


@variant_blueprint.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http:#srv023.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http:#srv023.img.med.uni-tuebingen.de:5000/display/17
@require_login
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):

    conn = get_connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    current_annotation_status = conn.get_current_annotation_status(variant_id)
    if current_annotation_status is not None:
        if current_annotation_status[4] == 'pending' and current_annotation_status[7] is None:
            celery_task_id = start_annotation_service(variant_id = variant_id)
            current_annotation_status = current_annotation_status[0:7] + (celery_task_id, )


    if request.method == 'POST':
        user_action = request.args.get('action')
        if user_action == 'add_to_list':
            list_id = request.form['list_id']
            conn.add_variant_to_list(list_id, variant_id) # MAYBE add a check that this list belongs to you!
            return redirect(url_for('variant.display', variant_id=variant_id))
        if user_action == 'remove_from_list':
            list_id = request.form['list_id']
            user_id = session['user']['user_id']
            is_list_owner = conn.check_user_list_ownership(user_id, list_id)
            #print(is_list_owner)
            if not is_list_owner:
                current_app.logger.error(session['user']['preferred_username'] + " attempted view list with id " + str(list_id) + ", but this list was not created by him.")
                return abort(403)
            conn.delete_variant_from_list(list_id, variant_id)
        #if user_action == 'reannotate' and (current_annotation_status is None or current_annotation_status[4] != 'pending'):
        #    conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])
        #    conn.close()
        #    return redirect(url_for('variant.display', variant_id=variant_id, from_reannotate='True'))

    if request.args.get('from_reannotate', 'False') == 'True':
        variant_oi = conn.get_one_variant(variant_id)
        if variant_oi is None:
            return redirect(url_for('doc.deleted_variant'))
    else:
        variant_oi = get_variant(conn, variant_id) # this redirects to 404 page if the variant was not found  
    
    vids = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
    if len(vids) > 1:
        has_multiple_vids = True
    else:
        has_multiple_vids = False
    
    annotations = conn.get_all_variant_annotations(variant_id, group_output=True)
    if annotations.get('consensus_classification', None) is not None:
        annotations['consensus_classification'] = add_scheme_classes(annotations['consensus_classification'], 14)
        annotations['consensus_classification'] = prepare_scheme_criteria(annotations['consensus_classification'], 14)[0]

    if annotations.get('user_classifications', None) is not None:
        annotations['user_classifications'] = add_scheme_classes(annotations['user_classifications'], 13)
        annotations['user_classifications'] = prepare_scheme_criteria(annotations['user_classifications'], 13)

    lists = conn.get_lists_for_user(user_id = session['user']['user_id'], variant_id=variant_id)

    clinvar_submission = get_clinvar_submission(variant_id, conn)

    return render_template('variant/variant.html', 
                            variant=variant_oi, 
                            annotations = annotations,
                            current_annotation_status=current_annotation_status,
                            clinvar_submission = clinvar_submission,
                            has_multiple_vids=has_multiple_vids,
                            lists = lists)





@variant_blueprint.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
@require_login
def classify(variant_id):
    conn = get_connection()

    user_id = session['user']['user_id']
    schemes_with_info = {user_id: get_schemes_with_info(variant_id, user_id, conn)}
    #print(schemes_with_info)
    previous_classification = get_previous_user_classification(variant_id, user_id, conn)

    variant_oi = conn.get_variant_more_info(variant_id)


    classification_schemas = conn.get_classification_schemas()


    do_redirect = False

    #is_admin, status_code = request_uma_ticket() # checks if the user has rights to access the consensus classification, only for display purposes

    if request.method == 'POST':
        ####### classification based on classification scheme submit 
        scheme_id = int(request.form['scheme'])
        #scheme_id = conn.get_scheme_id_from_scheme_name(scheme)

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        possible_classifications = ["1","2","3","4","5"]

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form, scheme_id, conn)
        #scheme_classification_is_valid, message = is_valid_scheme(criteria, scheme)
        scheme_classification_is_valid = True
        without_scheme = scheme_id == 1
        message = ""
        user_classification_is_valid = (str(classification) in possible_classifications) and comment
        
        # actually submit the data to the database
        if (not scheme_classification_is_valid) and (not without_scheme): # error in scheme
            flash(message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a user classification!", "alert-danger")

        if user_classification_is_valid and scheme_classification_is_valid:
            # always insert a user classification
            user_classification_id = handle_user_classification(variant_id, user_id, previous_classification, classification, comment, scheme_id, conn)

            if not without_scheme:
                if user_classification_id is None: # we are processing an update -> pull the classification id from the schemes with info
                    user_classification_id = schemes_with_info[user_id][scheme_id]['classification_id']
                handle_scheme_classification(user_classification_id, criteria, conn)

            do_redirect = True
            

        #if user_classification_is_valid and ((scheme_classification_is_valid and not without_scheme) or (without_scheme)): # we want to submit the user classification if scheme is none
        #    user_classification_id = handle_user_classification(variant_id, user_id, previous_classification, classification, comment, scheme_id, conn)
        #    do_redirect = True
        #
        #if scheme_classification_is_valid and (not without_scheme) and user_classification_is_valid: # only if both are valid submit the scheme classification
        #    # test if the current user already has a scheme classification for this scheme
        #    #if scheme not in schemes_with_info[user_id]:
        #    #    conn.insert_user_scheme_classification(variant_id, user_id, scheme)
        #    #    scheme_classification_id = conn.get_user_scheme_classification(variant_id, user_id, scheme=scheme)[0][0]
        #    #else:
        #
        #    if user_classification_id is None: # we are processing an update -> pull the classification id from the schemes with info
        #        user_classification_id = schemes_with_info[user_id][scheme_id]['classification_id']
        #    
        #    handle_scheme_classification(user_classification_id, criteria, conn)

    # either redirect or show the webpage depending on success of submission / page reload
    if do_redirect: # do redirect if one of the submissions was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully user-classified variant " + str(variant_id) + " with class " + str(classification))
        return redirect(url_for('variant.classify', variant_id = variant_id))
    else:
        return render_template('variant/classify.html',
                                classification_type='user',
                                variant_oi=variant_oi, 
                                classification_schemas=json.dumps(classification_schemas),
                                schemes_with_info=json.dumps(schemes_with_info), 
                                previous_classification=json.dumps(previous_classification)
                            )


@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission
def consensus_classify(variant_id):
    conn = get_connection()

    classification_schemas = conn.get_classification_schemas()

    variant_oi = conn.get_variant_more_info(variant_id)
    previous_classification = {} # keep empty because we always submit a new consensus classification 
    schemes_with_info = {} # this is used to preselect from previous classify submissions

    # get dict of all previous user classifications
    user_classifications = conn.get_user_classifications(variant_id = variant_id, user_id='all', scheme_id='all')
    #[(11, '4', 15, 3, 'r', datetime.date(2022, 10, 17), 2), (20, '1', 15, 3, 'reha2', datetime.date(2022, 10, 14), 3), (28, '3', 15, 3, 'dsvsagbruj', datetime.date(2022, 10, 17), 1)]
    if user_classifications is not None:
        for classification in user_classifications:
            current_user_id = classification[3]
            current_schemes_with_info = get_schemes_with_info(variant_id, current_user_id, conn)
            current_schemes_with_info['user'] = conn.get_user(current_user_id)
            schemes_with_info[current_user_id] = current_schemes_with_info

    #print(schemes_with_info)

    do_redirect=False
    if request.method == 'POST':

        ####### classification based on classification scheme submit 
        scheme_id = request.form['scheme']

        classification = request.form['final_class']
        comment = request.form['comment'].strip()
        possible_classifications = ["1","2","3","4","5"]

        # test if the input is valid
        criteria = extract_criteria_from_request(request.form, scheme_id, conn)
        #scheme_classification_is_valid, message = is_valid_scheme(criteria, scheme)
        scheme_classification_is_valid = True
        message = ""
        without_scheme = scheme_id == 1
        user_classification_is_valid = (str(classification) in possible_classifications) and comment
        
        
        # actually submit the data to the database
        if (not scheme_classification_is_valid) and (not without_scheme): # error in scheme
            flash(message, "alert-danger")
        if not user_classification_is_valid: # error in user classification
            flash("Please provide comment & class to submit a consensus classification", "alert-danger")

        if user_classification_is_valid and scheme_classification_is_valid:
            classification_id = handle_consensus_classification(variant_id, classification, comment, scheme_id, conn)
            
            if not without_scheme:
                handle_scheme_classification(classification_id, criteria, conn, where = "consensus")
            
            do_redirect = True

        #if user_classification_is_valid and ((scheme_classification_is_valid and scheme != 'none') or (scheme == 'none')):
        #    handle_consensus_classification(variant_id, classification, comment, conn)
        #    
        #    do_redirect = True
        #
        #if scheme_classification_is_valid and (scheme != 'none') and user_classification_is_valid: # only if both are valid submit the scheme classification
        #    scheme_classification_id = conn.insert_consensus_scheme_classification(session['user']['user_id'], variant_id, scheme)
        #    #scheme_classification_id = conn.get_consensus_scheme_classification(variant_id, scheme=scheme, most_recent=True)[0][0]
        #    handle_scheme_classification(scheme_classification_id, criteria, conn)



    if do_redirect: # do redirect if one of the submissions was successful
        current_app.logger.info(session['user']['preferred_username'] + " successfully consensus-classified variant " + str(variant_id) + " with class " + str(classification) + " from scheme_id " + str(scheme_id))
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))
    else:
        return render_template('variant/classify.html', 
                                classification_type='consensus',
                                variant_oi=variant_oi, 
                                classification_schemas=json.dumps(classification_schemas),
                                schemes_with_info=json.dumps(schemes_with_info), 
                                previous_classification=json.dumps(previous_classification)
                                )





@variant_blueprint.route('/display/<int:variant_id>/classification_history')
@require_login
def classification_history(variant_id):
    conn = get_connection()
    variant_oi = conn.get_variant_more_info(variant_id)
    if variant_oi is None:
        abort(404)
    consensus_classifications = conn.get_consensus_classifications_extended(variant_id, most_recent=False)
    user_classifications = conn.get_user_classifications_extended(variant_id)

    #print(consensus_classifications)
    #print(user_classifications)
    
    recorded_classifications = []
    most_recent_consensus_classification = None
    if consensus_classifications is not None:
        most_recent_consensus_classification = [x for x in consensus_classifications if x[6] == 1][0]
        consensus_classifications = add_scheme_classes(consensus_classifications, 14)
        consensus_classifications = prepare_scheme_criteria(consensus_classifications, 14)
        print(consensus_classifications)
        recorded_classifications.extend([{'type':'consensus classification', 
                                     'submitter': x[9] + ' ' + x[10],
                                     'affiliation':x[11],
                                     'class':x[3], 
                                     'date':x[5], 
                                     # additional information
                                     'comment':x[4], 
                                     'evidence_document_url':url_for('download.evidence_document', consensus_classification_id=x[0]),
                                     'scheme':x[12].replace('_', ' '),
                                     'selected_criteria':x[14],
                                     'class_by_scheme': x[15]
                                    } for x in consensus_classifications])
    if user_classifications is not None:
        user_classifications = add_scheme_classes(user_classifications, 13)
        user_classifications = prepare_scheme_criteria(user_classifications, 13)
        print(user_classifications)
        recorded_classifications.extend([{'type':'user classification',
                                          'submitter':x[8] + ' ' + x[9],
                                          'affiliation':x[10],
                                          'class':x[1],
                                          'date':x[5], 
                                          # additional information
                                          'comment':x[4],
                                          'scheme':x[11].replace('_', ' '),
                                          'selected_criteria':x[13],
                                          'class_by_scheme': x[14]
                                        } for x in user_classifications])

    print(recorded_classifications)

    return render_template('variant/classification_history.html', 
                            variant_oi = variant_oi,
                            most_recent_consensus_classification=most_recent_consensus_classification, 
                            recorded_classifications=recorded_classifications)


''''remove later: '''
@variant_blueprint.route("/insert_data")
def insert():
    conn = get_connection()
    for classification_scheme_id in criteria_descriptions:
        current_classification_scheme = criteria_descriptions[classification_scheme_id]
        for classification_criterium_name in current_classification_scheme:
            current_description = current_classification_scheme[classification_criterium_name]
            current_description = re.sub(' +', ' ', current_description)
            current_description = re.sub('\n', '', current_description)
            current_description = re.sub('\r', '\n', current_description)
            is_selectable = 1
            if current_description.startswith('Excluded'):
                is_selectable = 0
            conn.insert_classification_criterium(classification_scheme_id, classification_criterium_name, current_description, is_selectable)
            classification_criterium_id = conn.get_last_insert_id()
            if classification_scheme_id in ['2','3','4']:
                classification_criterium_strength_name = re.sub('\d', '', classification_criterium_name)
            else:
                classification_criterium_strength_name = taskforce_mapping_dict[classification_criterium_name]
            conn.insert_classification_criterium_strength(classification_criterium_id, classification_criterium_strength_name, description_mapping_dict[classification_criterium_strength_name], 1)

            has_strength_select = classification_criterium_name in criteria_with_strength_select.get(classification_scheme_id, [])
            if has_strength_select:
                if classification_criterium_name.startswith('p'):
                    for classification_strength_name in ['pvs', 'ps', 'pm', 'pp']:
                        if not classification_criterium_name.startswith(classification_strength_name):
                            conn.insert_classification_criterium_strength(classification_criterium_id, classification_strength_name, description_mapping_dict[classification_strength_name], 0)
                
                if classification_criterium_name.startswith('b'):
                    for classification_strength_name in ['ba', 'bs', 'bp']:
                        if not classification_criterium_name.startswith(classification_strength_name):
                            conn.insert_classification_criterium_strength(classification_criterium_id, classification_strength_name, description_mapping_dict[classification_strength_name], 0)


criteria_with_strength_select = {
    '2': [
        'pp1', 'ps1', 'bp1', 'bs1'
    ],
    '3': [
        'pp1', 'ps1', 'bp1', 'bs1'
    ],
    '4': [
        'pp1', 'ps1', 'bp1', 'bs1'
    ],
    '5': [
    ],
    '6': [
    ]
}

description_mapping_dict = {
    "pvs": "very strong pathogenic",
    "ps": "strong pathogenic",
    "pm": "medium pathogenic",
    "pp": "supporting pathogenic",
    "bp": "supporting benign",
    "bs": "strong benign",
    "ba": "stand-alone benign"
}

taskforce_mapping_dict =  {
    '1.1': 'pp', '1.2': 'pp', '1.3': 'pp', 
    '2.1': 'pm', '2.2': 'pm', '2.3': 'pm', '2.4': 'pm', '2.5': 'pm', '2.6': 'pm', '2.7': 'pm', '2.8': 'pm', '2.9': 'pm', '2.10': 'pm', 
    '3.1': 'bp', '3.2': 'bp', '3.3': 'bp', '3.4': 'bp', '3.5': 'bp', 
    '4.1': 'ps', '4.2': 'ps', '4.3': 'ps', '4.4': 'ps', '4.5': 'ps', '4.6': 'ps', '4.7': 'ps', '4.8': 'ps', '4.9': 'ps', 
    '5.1': 'pvs', '5.2': 'pvs', '5.3': 'pvs', '5.4': 'pvs', '5.5': 'pvs', '5.6': 'pvs'
}

criteria_descriptions = {
    '2': {
        "pvs1":
            '''Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation 
            codon, single or multi-exon deletion) in a gene where loss of function (LOF) 
            is a known mechanism of disease \r\n\r\n
                Caveats: \r\n
                - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7) \r\n
                - Use caution interpreting LOF variants at the extreme 3' end of a gene \r\n
                - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact \r\n
                - Use caution in the presence of multiple transcripts''',
        
        # strong pathogenic
        "ps1":
            '''Same amino acid change as a previously established pathogenic variant 
            regardless of nucleotide change. \r\n\r\n
                Example: Val->Leu caused by either G>C or G>T in the same codon \r\n
                Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level''',
        "ps2":
            '''De novo (both maternity and paternity confirmed) in a patient with the 
            disease and no family history. \r\n \r\n
            Note: Confirmation of paternity only is insufficient. Egg donation, surrogate 
            motherhood, errors in embryo transfer, etc. can contribute to non-maternity.''',
        "ps3":
            '''Well-established in vitro or in vivo functional studies supportive of a 
            damaging effect on the gene or gene product. \r\n\r\n
            Note: Functional studies that have been validated and shown to be 
            reproducible and robust in a clinical diagnostic laboratory setting are 
            considered the most well-established.''',
        "ps4":
            '''The prevalence of the variant in affected individuals is significantly 
            increased compared to the prevalence in controls. \r\n\r\n
                Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control 
            studies, is >5.0 and the confidence interval around the estimate of RR or OR 
            does not include 1.0. See manuscript for detailed guidance. \r\n\r\n
                Note 2: In instances of very rare variants where case-control studies may 
            not reach statistical significance, the prior observation of the variant in 
            multiple unrelated patients with the same phenotype, and its absence in 
            controls, may be used as moderate level of evidence.''',
        
        # moderate pathogenic
        "pm1":
            '''Located in a mutational hot spot and/or critical and well-established 
            functional domain (e.g. active site of an enzyme) without benign variation.''',
        "pm2":
			'''Absent from controls (or at extremely low frequency if recessive)
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n
            Caveat: Population data for indels may be poorly called by next generation 
            sequencing.''',
        "pm3":
			'''For recessive disorders, detected in trans with a pathogenic variant. \r\n\r\n 
            Note: This requires testing of parents (or offspring) to determine phase.''',
        "pm4":
			'''Protein length changes due to in-frame deletions/insertions in a non-repeat 
            region or stop-loss variants.''',
        "pm5":
			'''Novel missense change at an amino acid residue where a different 
            missense change determined to be pathogenic has been seen before. \r\n\r\n 
            Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n
            Caveat: Beware of changes that impact splicing rather than at the amino 
            acid/protein level.''',
        "pm6":
			'''Assumed de novo, but without confirmation of paternity and maternity.''',
        
        # supporting pathogenic
        'pp1':
			'''Co-segregation with disease in multiple affected family members in a gene 
            definitively known to cause the disease. \r\n\r\n
            Note: May be used as stronger evidence with increasing segregation data.''',
        "pp2":
			'''Missense variant in a gene that has a low rate of benign missense variation 
            and where missense variants are a common mechanism of disease.''',
        "pp3":
			'''Multiple lines of computational evidence support a deleterious effect on 
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n
            Caveat: As many in silico algorithms use the same or very similar input for 
            their predictions, each algorithm should not be counted as an independent 
            criterion. PP3 can be used only once in any evaluation of a variant.''',
        "pp4":
			'''Patient's phenotype or family history is highly specific for a disease with a 
            single genetic etiology.''',
        "pp5":
			'''Reputable source recently reports variant as pathogenic but the evidence is 
            not available to the laboratory to perform an independent evaluation.''',
        
        # stand alone benign
        "ba1":
			'''Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, 
            or ExAC.''',
        
        # strong benign
        "bs1":
			'''Allele frequency is greater than expected for disorder.''',
        "bs2":
			'''Observed in a healthy adult individual for a recessive (homozygous), 
            dominant (heterozygous), or X-linked (hemizygous) disorder with full 
            penetrance expected at an early age.''',
        "bs3":
			'''Well-established in vitro or in vivo functional studies shows no damaging 
            effect on protein function or splicing.''',
        "bs4":
			'''Lack of segregation in affected members of a family. \r\n\r\n
            Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, 
                epilepsy) can mimic lack of segregation among affected individuals. Also, 
                families may have more than one pathogenic variant contributing to an 
                autosomal dominant disorder, further confounding an apparent lack of 
                segregation.''',
        
        # supporting benign
        "bp1":
			'''Missense variant in a gene for which primarily truncating variants are 
            known to cause disease''',
        "bp2":
			'''Observed in trans with a pathogenic variant for a fully penetrant dominant 
            gene/disorder; or observed in cis with a pathogenic variant in any 
            inheritance pattern.''',
        "bp3":
			'''In-frame deletions/insertions in a repetitive region without a known 
            function''',
        "bp4":
			'''Multiple lines of computational evidence suggest no impact on gene or 
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n
            Caveat: As many in silico algorithms use the same or very similar input for 
            their predictions, each algorithm cannot be counted as an independent 
            criterion. BP4 can be used only once in any evaluation of a variant.''',
        "bp5":
			'''Variant found in a case with an alternate molecular basis for disease.''',
        "bp6":
			'''Reputable source recently reports variant as benign but the evidence is not 
            available to the laboratory to perform an independent evaluation.''',
        "bp7":
			'''A synonymous (silent) variant for which splicing prediction algorithms 
            predict no impact to the splice consensus sequence nor the creation of a 
            new splice site AND the nucleotide is not highly conserved.'''
    },
    '3': {
        # very strong pathogenic
        "pvs1":
			'''Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon,
            single or multiexon deletion) in a gene where LOF is a known mechanism of disease \r\n\r\n
            Use SVI-approved decision tree to determine the strength of this criterion
            (refer to Abou Tayoun et al. for more details).''',
        
        # strong pathogenic
        "ps1":
			'''Same amino acid change as a previously established pathogenic variant 
            regardless of nucleotide change. \r\n\r\n
            Use original description with the following additions: \r\n
                PS1: \r\n
                    - Must confirm there is no difference in splicing using RNA data. \r\n
                    - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the 
                      TP53 VCEP (see ClinVar for VCEP classifications). \r\n\r\n
                PS1_Moderate: \r\n
                    - Must confirm there is no difference in splicing using a metapredictor. \r\n
                    - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the TP53 VCEP (see ClinVar).''',
        "ps2":
			'''De novo (both maternity and paternity confirmed) in a patient with the 
            disease and no family history. \r\n\r\n
            Use SVI-approved scoring system to determine the strength of this criterion 
            (refer to Table 2 from original publication: PMC8374922 (linked above) for more details)''',
        "ps3":
			'''Well-established in vitro or in vivo functional studies supportive of a 
            damaging effect on the gene or gene product. \r\n\r\n
            The following additions have been made by the TP53 ACMG specification: \r\n
                - PS3: transactivation assays in yeast demonstrate a low functioning allele 
                  (≤20% activity) AND there is evidence of dominant negative effect and loss-of-function 
                  OR there is a second assay showing low function (colony formation assays, apoptosis assays, 
                  tetramer assays, knock-in mouse models and growth suppression assays).\r\n\r\n
                - PS3_Moderate: transactivation assays in yeast demonstrate a partially 
                  functioning allele (>20% and ≤75% activity) AND there is evidence of dominant 
                  negative effect and loss-of-function OR there is a second assay showing low function 
                  (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse models and 
                  growth suppression assays).\r\n\r\n
                - PS3_Moderate: there is no data available from transactivation assays in yeast BUT 
                  there is evidence of dominant negative effect and loss-of-function AND there is a second 
                  assay showing low function (colony formation assays, apoptosis assays, tetramer assays, 
                  knock-in mouse models and growth suppression assays).\r\n\r\n
                ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.''',
        "ps4":
			'''The prevalence of the variant in affected individuals is significantly 
            increased compared to the prevalence in controls. \r\n\r\n
            Use SVI-approved scoring system to determine the strength of this criterion 
            (refer to Table 3 from original publication: PMC8374922 (linked above) for more details). 
            This criterion cannot be applied when a variant also meets BA1 or BS1. Refrain from considering 
            probands who have another pathogenic variant(s) in a highly penetrant cancer gene(s) that is a 
            logical cause for presentation. \r\n\r\n
            Caveat: \r\n
                Please be mindful of the risk of clonal hematopoieses of indeterminate potential with TP53 variants 
                (Coffee et al., 2017; Weitzel et al., 2017). One should take care to ensure that probands have 
                germline and not mosaic somatic TP53 variants.''',
        
        # moderate pathogenic
        "pm1":
			'''Located in a mutational hot spot and/or critical and well-established 
            functional domain (e.g. active site of an enzyme) without benign variation. \r\n\r\n
            Located in a mutational hotspot defined as: \r\n
                - Variants within the following codons on protein NP_000537.3: 175, 273, 245, 248, 282, 249. \r\n
                - Variants seen in cancerhotspots.org (v2) with >10 somatic occurrences (recommendation from the ClinGen 
                  Germline/Somatic Variant Curation Subcommittee).''',
        "pm2":
			'''Absent from controls (or at extremely low frequency if recessive)
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n
            Caveat: Population data for indels may be poorly called by next generation 
            sequencing. \r\n\r\n
            PM2_Supporting: absent from population databases (gnomAD (most up-to-date non-cancer dataset) is the 
            preferred population database at this time http:#gnomad.broadinstitute.org).''',
        "pm3":
			'''Excluded.''',
        "pm4":
			'''Excluded.''',
        "pm5":
			'''Novel missense change at an amino acid residue where a different 
            missense change determined to be pathogenic has been seen before. \r\n\r\n 
            Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n\r\n
            PM5: novel missense change at an amino acid residue where at least two other different missense changes 
                determined to be pathogenic by the TP53 VCEP have been seen before. 
                PM5_Supporting: novel missense change at an amino acid residue where a different missense 
                change determined to be pathogenic by the TP53 VCEP has been seen before. \r\n\r\n
            Both criteria require the following additions: \r\n
                - Grantham should be used to compare the variants, and the variant being evaluated must have 
                  equal to or higher score than the observed pathogenic variants. \r\n
                - Splicing should be ruled out using a metapredictor. \r\n
                - This criterion cannot be applied when a variant also meets PM1.''',
        "pm6":
			'''Assumed de novo, but without confirmation of paternity and maternity. \r\n\r\n
            Use SVI-approved scoring system to determine the strength of this criterion (refer to Table 2 from original 
            publication: PMC8374922 (linked above) for more details).''',
        
        # supporting pathogenic
        'pp1':
			'''Co-segregation with disease in multiple affected family members in a gene 
            definitively known to cause the disease. \r\n\r\n
            PP1: co-segregation with disease is observed in 3–4 meioses in one family. \r\n
            PP1_Moderate: co-segregation with disease is observed in 5–6 meioses in one family. \r\n
            PP1_Strong: co-segregation with disease is observed >7 meioses in >1 family.''',
        "pp2":
			'''Excluded.''',
        "pp3":
			'''Multiple lines of computational evidence support a deleterious effect on 
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n
            Caveat: As many in silico algorithms use the same or very similar input for 
            their predictions, each algorithm should not be counted as an independent 
            criterion. PP3 can be used only once in any evaluation of a variant. \r\n\r\n
            PP3: Use original description with the following additions: \r\n
                - For missense variants, use a combination of BayesDel (≥0.16) and optimised Align-GVGD (C55-C25). \r\n
                - For splicing variants, use a metapredictor. \r\n\r\n
            PP3_Moderate: for missense variants, use a combination of BayesDel (≥0.16) and optimized Align-GVGD (C65).''',
        "pp4":
			'''Excluded.''',
        "pp5":
			'''Excluded.''',
        
        # stand alone benign
        "ba1":
			'''Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, 
            or ExAC.\r\n\r\n
            Allele frequency is ≥0.1% in a non-founder population with a minimum of five alleles 
            (gnomAD (most up-to-date non-cancer dataset)) is the preferred population database 
            at this time http:#gnomad.broadinstitute.org).''',
        
        # strong benign
        "bs1":
			'''Allele frequency is greater than expected for disorder. \r\n\r\n
            Allele frequency is ≥0.03% and <0.1% in a non-founder population with a minimum of five alleles 
            (gnomAD (most up-to-date non-cancer dataset) is the preferred population database at this time 
            http:#gnomad.broadinstitute.org).''',
        "bs2":
			'''Observed in a healthy adult individual for a recessive (homozygous), 
            dominant (heterozygous), or X-linked (hemizygous) disorder with full 
            penetrance expected at an early age.\r\n\r\n
            BS2: observed in a single dataset in ≥8 females, who have reached at least 60 years of age without cancer 
                (i.e. cancer diagnoses after age 60 are ignored). \r\n\r\n
            BS2_Supporting: observed in a single dataset in 2–7 females, who have reached at least 60 years of age without cancer. \r\n\r\n
            Caveat: Be mindful of the risk of clonal hematopoiesis of indeterminate potential with TP53 variants (Coffee et al., 2017; Weitzel et al., 2017). 
                Individuals with mosaic somatic TP53 variants should not be included as evidence for BS2.''',
        "bs3":
			'''Well-established in vitro or in vivo functional studies shows no damaging 
            effect on protein function or splicing. \r\n\r\n
            - BS3: transactivation assays in yeast demonstrate a functional allele or super-transactivation 
                (>75% activity) AND there is no evidence of dominant negative effect and loss-of-function OR 
                there is a second assay showing retained function (colony formation assays, apoptosis assays, 
                tetramer assays, knock-in mouse models and growth suppression assays). \r\n\r\n
            - BS3_Supporting: transactivation assays in yeast demonstrate a partially functioning allele 
                (>20% and ≤75% activity) AND there is no evidence of dominant negative effect and loss-of-function 
                OR there is a second assay showing retained function (colony formation assays, apoptosis assays, 
                tetramer assays, knock-in mouse models and growth suppression assays). \r\n\r\n
            - BS3_Supporting: there is no data available from transactivation assays in yeast BUT there is no 
                evidence of dominant negative effect and loss-of-function AND there is a second assay showing 
                retained function (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse 
                models and growth suppression assays). \r\n\r\n
            ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.''',
        "bs4":
			'''Lack of segregation in affected members of a family. \r\n\r\n
            The variant segregates to opposite side of the family meeting LFS criteria, or the variant is 
            present in >3 living unaffected individuals (at least two of three should be female) above 55 years of age.''',
            
        # supporting benign
        "bp1":
			'''Excluded''',
        "bp2":
			'''Observed in trans with a pathogenic variant for a fully penetrant dominant 
            gene/disorder; or observed in cis with a pathogenic variant in any 
            inheritance pattern. \r\n\r\n
            Variant is observed in trans with a TP53 pathogenic variant (phase confirmed), 
            or there are three or more observations with a TP53 pathogenic variant when phase is unknown (at least two different 
            TP53 pathogenic variants). The other observed pathogenic variants must have been classified using 
            the TP53-specific guidelines.''',
        "bp3":
			'''Excluded''',
        "bp4":
			'''Multiple lines of computational evidence suggest no impact on gene or 
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n
            Caveat: As many in silico algorithms use the same or very similar input for 
            their predictions, each algorithm cannot be counted as an independent 
            criterion. BP4 can be used only once in any evaluation of a variant. \r\n\r\n
            Same rule description with the following additions: \r\n
                - For missense variants, use a combination of BayesDel (<0.16) and optimized Align-GVGD (C15-C0). \r\n
                - For splicing variants, use a metapredictor.''',
        "bp5":
			'''Excluded''',
        "bp6":
			'''Excluded''',
        "bp7":
			'''A synonymous (silent) variant for which splicing prediction algorithms 
            predict no impact to the splice consensus sequence nor the creation of a 
            new splice site AND the nucleotide is not highly conserved. \r\n\r\n
            Same description with the following additions: \r\n
                - Splicing should be ruled out using a metapredictor. \r\n
                - If a new alternate site is predicted, compare strength to native site in interpretation.'''
    },

    '4': {
        # very strong pathogenic
        "pvs1":
			'''Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon,
            single or multiexon deletion) in a gene where LOF is a known mechanism of disease \r\n\r\n
                - Very strong: Per ClinGen SVI guidelines with the exception of canonical splice sites \r\n
                - Strong: Per ClinGen SVI guidelines. Use the strong strength of evidence for canonical splice sites. \r\n
                caveat: \r\n
                 CDH1 exonic deletions or tandem duplications of in-frame exon truncations in NMD-resistant 
                 zone located upstream the most 3' well characterized pathogenic variant c.2506G>T (p.Glu836Ter). 
                 Use moderate strength if premature stop is downstream of this variant \r\n 
                - Moderate: Per ClinGen SVI guidelines. \r\n
                caveats: \r\n 
                1. G to non-G variants disrupting the last nucleotide of an exon \r\n
                2. Canonical splice sites located in exons demonstrated experimentally to result in in-frame partial skipping/insertion (e.g., Exon 3 donor site) 
                - Supporting: Per ClinGen SVI guidelines. \r\n\r\n
            Additional comment: \r\n 
                RNA analysis is recommended for splicing alterations, and if the RNA evidence does not support the prediction, the strength should be updated 
                PP3 cannot be applied for canonical splice sites''',
        
        # strong pathogenic
        "ps1":
			'''Same amino acid change as a previously established pathogenic variant 
            regardless of nucleotide change. \r\n\r\n
                Example:	Val->Leu caused by either G>C or G>T in the same codon \r\n
                Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level \r\n\r\n
            Additional comment: \r\n
                Variant must not impact splicing.''',
        "ps2":
			'''De novo (both maternity and paternity confirmed) in a patient with the 
            disease and no family history. \r\n \r\n
            Strength specifications: \r\n
                - Very strong: ≥2 patients with DGC and/or LBC w/parental confirmation 
                - Strong: 1 patient with DGC and/or LBC w/parental confirmation \r\n
                Additional comment: \r\n
                    Use ClinGen's de novo point system for a highly specific phenotype (see Table S2 from 
                    original publication linked at the top of the page)''',
        "ps3":
			'''Well-established in vitro or in vivo functional studies supportive of a 
            damaging effect on the gene or gene product. \r\n\r\n
            Strength specifications: \r\n
                - Strong: RNA assay demonstrating abnormal out-of-frame transcripts \r\n
                - Supporting: RNA assay demonstrating abnormal in-frame transcripts \r\n
            Additional comment: \r\n
                This rule can only be applied to demonstrate splicing defects.''',
        "ps4":
			'''The prevalence of the variant in affected individuals is significantly 
            increased compared to the prevalence in controls. \r\n\r\n
            Strength specifications: \r\n
                - Very strong: 16 families meet HDGC criteria \r\n
                - Strong: 4 families meet HDGC criteria \r\n
                - Moderate: 2 families meet HDGC criteria \r\n
                - Supporting: 1 family meets HDGC criteria \r\n\r\n
            Additional comment: \r\n
                This rule assumes 30% penetrance in individuals with pathogenic variants. For example, 
                if the variant in observed in 3 families, at least one of those families need to meet 
                criteria for HDGC in order to apply this rule. PS4 cannot be applied to variants that meet BS1 or BA1''',
        
        # moderate pathogenic
        "pm1":
			'''Excluded.''',
        "pm2":
			'''Absent from controls (or at extremely low frequency if recessive)
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n
            <1/100,000 alleles in gnomAD cohort; if present in ≥2 individuals, must be present in 
            <1/50,000 alleles within a sub-population \r\n\r\n
            Additional comment: \r\n
                Use gnomAD to determine allele frequency. Beware of technical limitations that 
                can inaccurately represent allele frequency in this population database''',
        "pm3":
			'''Excluded''',
        "pm4":
			'''Protein length changes due to in-frame deletions/insertions in a non-repeat 
            region or stop-loss variants. \r\n\r\n
            Additional comment: \r\n
                No rule specification proposed. Variant example - CDH1 c.2647T>C (p.Ter883Glnext*29)''',
        "pm5":
			'''Excluded''',
        "pm6":
			'''Assumed de novo, but without confirmation of paternity and maternity. \r\n\r\n
            Strength specification: \r\n
                - Very strong: ≥4 patients with DGC and/or LBC w/o parental confirmation \r\n
                - Strong: ≥2 patients with DGC and/or LBC w/o parental confirmation \r\n
                - Moderate: 1 patient with DGC and/or LBC w/o parental confirmation \r\n\r\n
            Additional comment: \r\n
                Use ClinGen's de novo point system for a highly specific phenotype (See Table S2 
                of original publication linked at the top of this page)''',
        
        # supporting pathogenic
        'pp1':
			'''Co-segregation with disease in multiple affected family members in a gene 
            definitively known to cause the disease. \r\n\r\n
            Strength specification: \r\n
                - Strong: ≥7 meioses across ≥2 families \r\n
                - Moderate: 5-6 meioses across ≥1 families \r\n
                - Supporting: 3-4 meioses across ≥1 families \r\n\r\n
            Additional comment: \r\n
                Based strength of rule code on number of meioses across one or more families.''',
        "pp2":
			'''Excluded''',
        "pp3":
			'''Multiple lines of computational evidence support a deleterious effect on 
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n
            Strength specification: \r\n
                - Moderate: Variants affecting the same splice site as a well-characterized variant with 
                similar or worse in silico/RNA predictions \r\n
                - Supporting: At least 3 in silico splicing predictors in agreement (.Human Splicing 
                Finder (HSF), Maximum Entropy (MaxEnt), Berkeley Drosophilia Genome Project (BDGP), or ESEfinder) \r\n\r\n
            Additional comment: \r\n
                Rule code is only for non-canonical splicing variants. Code also does not apply to last 
                nucleotide of exon 3 (c.387G). Do not use protein-based computational prediction models for missense variants''',
        "pp4":
			'''Use PS4 in place of PP4.''',
        "pp5":
			'''Excluded''',
        
        # stand alone benign
        "ba1":
			'''Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, 
            or ExAC. \r\n\r\n
            MAF cutoff of 0.2% \r\n\r\n
            Additional comment: \r\n
                99.99% CI; subpopulation must have a minimum of 5 alleles present.''',
        
        # strong benign
        "bs1":
			'''Allele frequency is greater than expected for disorder. \r\n\r\n
            Stand alone: MAF cutoff of 0.1% \r\n\r\n
            Additional comment: \r\n
                99.99% CI; subpopulation must have a minimum of 5 alleles present''',
        "bs2":
			'''Observed in a healthy adult individual for a recessive (homozygous), 
            dominant (heterozygous), or X-linked (hemizygous) disorder with full 
            penetrance expected at an early age. \r\n\r\n
            Strength specification: \r\n
                - Strong: Variant seen in ≥10 individuals w/o DCG, SRC tumors, or LBC & whose families do not suggest HDGC \r\n
                - Supporting: Variant seen in ≥3 individuals w/o DCG, SRC tumors, or LBC & whose families do not suggest HDGC	''',
        "bs3":
			'''Well-established in vitro or in vivo functional studies shows no damaging 
            effect on protein function or splicing. \r\n
            Functional RNA studies demonstrating no impact on transcript composition. \r\n\r\n
            Additional comment: \r\n
                This rule can only be used to demonstrate lack of splicing and can be downgraded based on quality of data.''',
        "bs4":
			'''Lack of segregation in affected members of a family. \r\n\r\n
            Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, 
                epilepsy) can mimic lack of segregation among affected individuals. Also, 
                families may have more than one pathogenic variant contributing to an 
                autosomal dominant disorder, further confounding an apparent lack of 
                segregation. \r\n\r\n
            Additional comment: \r\n
                Beware of the presence of phenocopies (e.g., breast cancer) that can 
                mimic lack of segregation. Also, families may have more than one pathogenic 
                variant contributing to another AD disorder''',
        
        # supporting benign
        "bp1":
			'''Excluded''',
        "bp2":
			'''Observed in trans with a pathogenic variant for a fully penetrant dominant 
            gene/disorder; or observed in cis with a pathogenic variant in any 
            inheritance pattern. \r\n\r\n
            Strength specifications: \r\n
                - Strong: Variant observed in trans w/known pathogenic variant (phase confirmed) 
                OR observed in the homozygous state in individual w/o personal &/or family 
                history of DGC, LBC, or SRC tumors \r\n
                - Supporting: Variant is observed in cis (or phase is unknown) w/ a pathogenic variant \r\n\r\n
            Additional comment: \r\n
                Evidence code is dependent on strength of data. Take consideration of quality of 
                sequencing data when applying code. Note that code requires knowledge of individuals'
                phenotype. Therefore, data from population databases should only be used when phenotypic 
                info is available.''',
        "bp3":
			'''Excluded''',
        "bp4":
			'''Multiple lines of computational evidence suggest no impact on gene or 
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n
            Splicing predictions only. At least 3 in silico splicing predictors in agreement 
            (Human Splicing Finder (HSF), Maximum Entropy (MaxEnt), Berkeley Drosophilia 
            Genome Project (BDGP), or ESEfinder) \r\n\r\n
            Additional comment: \r\n
                This rule can only be used when splicing predictions models suggest no 
                impact on protein. Do not use protein based computational prediction models 
                for missense. variants''',
        "bp5":
			'''Variant found in a case with an alternate molecular basis for disease. \r\n\r\n
            Additional comment: \r\n
                This applies if a P/LP variant is identified in an alternate gene known to cause HDGC (e.g., CTNNA1)''',
        "bp6":
			'''Excluded''',
        "bp7":
			'''A synonymous (silent) variant for which splicing prediction algorithms 
            predict no impact to the splice consensus sequence nor the creation of a 
            new splice site AND the nucleotide is not highly conserved. \r\n\r\n
            Synonymous variants where nucleotide is not highly conserved; variant is 
            the reference nucleotide in 1 primate and/or >3 mammal species \r\n\r\n
            Additional comment: \r\n
                Note the CDH1 rule specification does not require a benign in silico splice prediction. 
                This allows use with BP4, as appropriate, to classify variants meeting both criteria as likely benign '''
    },
    '5': {
        '1.1' :
			'''Allele frequency ≥ 1 % (MAF ≥ 0.01) in large populations like Caucasians, Africans or Asians. \r\n\r\n
            CAVE: Allele freuqency ≥ 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations) 
            does NOT suffice this criterium.''',
        '1.2' :
			'''Variants with a multifactorial calculated pobability of < 0,001 (< 0,1 %) to be pathogenic. \r\n\r\n
            CAVE: Currently only applicable to BRCA1/2.''', 
        '1.3' :
			'''Variants in high risk genes which occur in at least 10 individuals within suitable groups of non-diseased individuals (e. g. FLOSSIES).''', 
        '2.1' :
			'''Allele frequency between 0.5 and 1 % (MAF 0.005–0,01) in large populations like Caucasians, Africans or Asians. \r\n\r\n
            CAVE: Allele freuqency between 0.5 and 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations) 
            does NOT suffice this criterium.''', 
        '2.2' :
			'''Either exonic variants (A), which lead to the substitution of an amino acid 
            (missense variants), or small in-frame insertions/ 
            deletions, which lead to insertions/deletions of one or 
            amino acid(s) and whose a priori probability for pathogenicity is 
            for pathogenicity is ≤ 2% (A-GVGD analysis, 
            http:#priors.hci.utah.edu/PRIORS/), and (B) synonymous 
            variants, if these variants (A, B) are likely to be pathogenic according to bioinformatic 
            prediction programs the splicing result with a high probability and (A) are outside the relevant
            and (A) are located outside of the relevant functional
            domains defined by the VUS task-force (see tables A5.1–5.9 from the original proposal linked at the top of this page).
            For the non-BRCA1/2 genes, the above variants must be
            In large populations with an allele frequency of.
            0.001 ≤ MAF < 0.01 (0.1-1%).''', 
        '2.3' :
			'''Synonymous substitutions or intronic variants, which 
            do not contain mRNA aberrations in the form of exon deletions/ 
            duplications or monoallelic expression of the wild-type 
            transcript in RNA analyses. This applies even if they are likely to alter the splice-result 
            according to bioinformatic prediction programs (for programs and thresholds, see Appendix A1 
            of the original proposal liked at the top of this page).''', 
        '2.4' :
			'''Variants that occur in the same gene with a clearly pathogenic 
            variant in trans (co-occurrence). It must be confirmed that a homozygous 
            or compound heterozygous genotype is associated with a known clinically distinct 
            phenotype.''',
        '2.5' :
			'''Variants with a multifactorial calculated probability to be pathogenic of 0.001-0.049. \r\n\r\n
            CAVE: Does only apply to BRCA1/2.''', 
        '2.6' :
			'''Exonic variants which cause an amino acid change equal to a known class 1 variant, but 
            encode a different nucleotide change. Additionally, the variant must not show a conspicious splice prediction.''', 
        '2.7' :
			'''Missense variants which have information from functional analyses (or similar). These, however, do not suffice for 
            a multifactorial classification. Additionally, the variant was previously classified by expert panels like 
            ENIGMA or the ClinGen-expert-group as class 2''', 
        '2.8' :
			'''Suitable functional analyses do not show a loss of function or functional relevance. Additionally there must not 
            be contradictory data. \r\n\r\n
            Comment: The suitable functional analyses are dependent on the gene of the variant.''', 
        '2.9' :
			'''Paired LOH-analyses in blood or tumor samples show a loss of the allele which contains the variant under consideration. 
            This was proven among tumor tissue (BC or OC).''', 
        '2.10' :
			'''Variants within genes of intermediate risk without hints to potential function loss. These variants must also occour 
            in at least 20 individuals of suitable non-diseased cohorts (e. g. FLOSSIES) \r\n\r\n
            CAVE: Exceptions are possible in case of frequent foundermutations (e. g. CHEK2, c.1100del).''', 
        '3.1' :
			'''A special case in which the criteria clearly state a certain classification. However, the variant is listed among 
            the special cases of the genes or other exceptions occur (see table 5 of the original proposal linked at the top of the page)''', 
        '3.2' :
			'''Variants with controversial data with regards to its classification.''', 
        '3.3' :
			'''Variants which can be found within -20 to +3 bp and  -3 to +8 bp from an exon/intron border. This applies only if 
            there is no in-vitro mRNA analysis and criteria 4.3, 4.4 or 2.6 do not apply.''', 
        '3.4' :
			'''Exon duplications without additional analyses (e. g. cDNA analyses, break-point analyses, ...)''', 
        '3.5' :
			'''Variants with a multifaktorial calculated pathogenicity probability between 0.05 and 0.949. \r\n\r\n
            CAVE: This criterium only applies to BRCA1/2 variants.''', 
        '4.1' :
			'''Variants with a multifaktorial calculated pathogenicity probability between 0.95 and 0.99. \r\n\r\n
            CAVE: This criterium only applies to BRCA1/2 variants.''', 
        '4.2' :
			'''Variants which encode an early stop of the protein synthesis (nonsense- or frameshift variants). In addition, 
            variants must not cause damage to known clinical relevant functional protein domains as long as the induced stop 
            codon is found approximately 50 bp upstream from the last exon-exon-junction. \r\n\r\n
            Comment: If there is at least one exon-exon-junction complex downstream of the new, early stop codon, the early one 
            would be able to recruit the Upf1 and, thus, induce nonsense-mediated decay (NMD))''', 
        '4.3' :
			'''Intronic variants at position ± 1,2 or a G to A/T or C change at the last position of the exon. Apply this criterium if there is 
            a positive splice prediction and there is no mRNA analysis. \r\n\r\n
            CAVE: Applies to BRCA1/2 variants at the last position of the exon only if the first 6 bases within the intron are not equal to "GTRRGT". \r\n\r\n
            Exceptions: \r\n
            - A cryptic spice site (AG/GT) is activated by the variant and the (predicted) new exon yields in-frame splicing --> class 3 \r\n
            - A transcript with (predicted) skipped exon(s) exists as a relevant alternatively spliced transcipt --> class 3 \r\n
            - The (predicted) skipped exon(s) is spliced in-frame and does not contain known functional domains --> class 3''', 
        '4.4' :
			'''Variants which cause the same amino acid change as a known class 5 pathogenic missence variant, but is characterized by another nucleotide change. 
            Also, it is required that there is no prediction of abberant splicing.''', 
        '4.5' :
			'''In-frame deletions which cause the loss of a class 5 missence variant and which disrupt or cause the loss of funcionally important protein domains.''', 
        '4.6' :
			'''In-frame insertions which were verified via in-vitro mRNA analyses, that disrupt functionally important protein domains.''', 
        '4.7' :
			'''Variants which cause a change in the tranlation initiation codon (AUG, Methionin). Additionally, there must not be evidence 
            (e. g. close alternative start-codon) for an alternative classification.''', 
        '4.8' :
			'''Variants which do have information from functional analyses, clinical data, or other evidence that do, however, not suffice for a multifactorial classification
            and which were classified as class 4 by expert panels like ENIGMA or ClinGen.''', 
        '4.9' :
			'''Variants which have functional analyses that depict loss of function or another functional relevance and which do not have contradictory information.''', 
        '5.1' :
			'''Nonsense- or frameshift variants which induce an early stop codon. This stop codon prevents the expression of known relevant functional protein domains.''', 
        '5.2' :
			'''Variants with a multifactorial calculated probability to be pathogenic of more than 0.99. \r\n\r\n
            CAVE: Only applies to BRCA1/2.''', 
        '5.3' :
			'''Splice variants which were shown to induce a frame shift that causes an early stop of the proteinbiosynthesis and, thus, prevents the expression of known relevant functional protein domains.
            This was proven via in-vitro mRNA analyses. It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).''', 
        '5.4' :
			'''Splice variants in which an invitro mRNA analysis has detected an in-frame deletion/insertion that leads to the 
            interruption or loss of a known clinically relevant domain or to a change in the protein structure which functionally inactivates the protein.
            It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).''', 
        '5.5' :
			'''Copy number deletions which cause the disruption or loss of (an) exon(s) which contain clinically relevant functional domain(s) 
            or which cause a predicted inactivation of known clinically relevant functional domains due to a frame shift.''', 
        '5.6' :
			'''Copy number duplications of any size which were proven (with lab-analyses) to duplicate one or multiple 
            exons that cause a frame shift and, thus, inactivate known clinically relevant functional protein domains.'''
    },
    '6': {
        '1.1' :
			'''Allele frequency ≥ 1 % (MAF ≥ 0.01) in large populations like Caucasians, Africans or Asians. \r\n\r\n
            CAVE: Allele freuqency ≥ 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations) 
            does NOT suffice this criterium.''',
        '1.2' :
			'''Variants with a multifactorial calculated pobability of < 0,001 (< 0,1 %) to be pathogenic. \r\n\r\n
            CAVE: Currently only applicable to BRCA1/2.''', 
        '1.3' :
			'''Variants in high risk genes which occur in at least 10 individuals within suitable groups of non-diseased individuals (e. g. FLOSSIES).''', 
        '2.1' :
			'''Allele frequency between 0.5 and 1 % (MAF 0.005–0,01) in large populations like Caucasians, Africans or Asians. \r\n\r\n
            CAVE: Allele freuqency between 0.5 and 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations) 
            does NOT suffice this criterium.''', 
        '2.2' :
			'''Either exonic variants (A), which lead to the substitution of an amino acid 
            (missense variants), or small in-frame insertions/ 
            deletions, which lead to insertions/deletions of one or 
            amino acid(s) and whose a priori probability for pathogenicity is 
            for pathogenicity is ≤ 2% (A-GVGD analysis, 
            http:#priors.hci.utah.edu/PRIORS/), and (B) synonymous 
            variants, if these variants (A, B) are likely to be pathogenic according to bioinformatic 
            prediction programs the splicing result with a high probability and (A) are outside the relevant
            and (A) are located outside of the relevant functional
            domains defined by the VUS task-force (see tables A5.1–5.9 from the original proposal linked at the top of this page).
            For the non-BRCA1/2 genes, the above variants must be
            In large populations with an allele frequency of.
            0.001 ≤ MAF < 0.01 (0.1-1%).''', 
        '2.3' :
			'''Synonymous substitutions or intronic variants, which 
            do not contain mRNA aberrations in the form of exon deletions/ 
            duplications or monoallelic expression of the wild-type 
            transcript in RNA analyses. This applies even if they are likely to alter the splice-result 
            according to bioinformatic prediction programs (for programs and thresholds, see Appendix A1 
            of the original proposal liked at the top of this page).''', 
        '2.4' :
			'''Variants that occur in the same gene with a clearly pathogenic 
            variant in trans (co-occurrence). It must be confirmed that a homozygous 
            or compound heterozygous genotype is associated with a known clinically distinct 
            phenotype.''',
        '2.5' :
			'''Variants with a multifactorial calculated probability to be pathogenic of 0.001-0.049. \r\n\r\n
            CAVE: Does only apply to BRCA1/2.''', 
        '2.6' :
			'''Exonic variants which cause an amino acid change equal to a known class 1 variant, but 
            encode a different nucleotide change. Additionally, the variant must not show a conspicious splice prediction.''', 
        '2.7' :
			'''Missense variants which have information from functional analyses (or similar). These, however, do not suffice for 
            a multifactorial classification. Additionally, the variant was previously classified by expert panels like 
            ENIGMA or the ClinGen-expert-group as class 2''', 
        '2.8' :
			'''Suitable functional analyses do not show a loss of function or functional relevance. Additionally there must not 
            be contradictory data. \r\n\r\n
            Comment: The suitable functional analyses are dependent on the gene of the variant.''', 
        '2.9' :
			'''Paired LOH-analyses in blood or tumor samples show a loss of the allele which contains the variant under consideration. 
            This was proven among tumor tissue (BC or OC).''', 
        '2.10' :
			'''Variants within genes of intermediate risk without hints to potential function loss. These variants must also occour 
            in at least 20 individuals of suitable non-diseased cohorts (e. g. FLOSSIES) \r\n\r\n
            CAVE: Exceptions are possible in case of frequent foundermutations (e. g. CHEK2, c.1100del).''', 
        '3.1' :
			'''A special case in which the criteria clearly state a certain classification. However, the variant is listed among 
            the special cases of the genes or other exceptions occur (see table 5 of the original proposal linked at the top of the page)''', 
        '3.2' :
			'''Variants with controversial data with regards to its classification.''', 
        '3.3' :
			'''Variants which can be found within -20 to +3 bp and  -3 to +8 bp from an exon/intron border. This applies only if 
            there is no in-vitro mRNA analysis and criteria 4.3, 4.4 or 2.6 do not apply.''', 
        '3.4' :
			'''Exon duplications without additional analyses (e. g. cDNA analyses, break-point analyses, ...)''', 
        '3.5' :
			'''Variants with a multifaktorial calculated pathogenicity probability between 0.05 and 0.949. \r\n\r\n
            CAVE: This criterium only applies to BRCA1/2 variants.''', 
        '4.1' :
			'''Variants with a multifaktorial calculated pathogenicity probability between 0.95 and 0.99. \r\n\r\n
            CAVE: This criterium only applies to BRCA1/2 variants.''', 
        '4.2' :
			'''Variants which encode an early stop of the protein synthesis (nonsense- or frameshift variants). In addition, 
            variants must not cause damage to known clinical relevant functional protein domains as long as the induced stop 
            codon is found approximately 50 bp upstream from the last exon-exon-junction. \r\n\r\n
            Comment: If there is at least one exon-exon-junction complex downstream of the new, early stop codon, the early one 
            would be able to recruit the Upf1 and, thus, induce nonsense-mediated decay (NMD))''', 
        '4.3' :
			'''Intronic variants at position ± 1,2 or a G to A/T or C change at the last position of the exon. Apply this criterium if there is 
            a positive splice prediction and there is no mRNA analysis. \r\n\r\n
            CAVE: Applies to BRCA1/2 variants at the last position of the exon only if the first 6 bases within the intron are not equal to "GTRRGT". \r\n\r\n
            Exceptions: \r\n
            - A cryptic spice site (AG/GT) is activated by the variant and the (predicted) new exon yields in-frame splicing --> class 3 \r\n
            - A transcript with (predicted) skipped exon(s) exists as a relevant alternatively spliced transcipt --> class 3 \r\n
            - The (predicted) skipped exon(s) is spliced in-frame and does not contain known functional domains --> class 3''', 
        '4.4' :
			'''Variants which cause the same amino acid change as a known class 5 pathogenic missence variant, but is characterized by another nucleotide change. 
            Also, it is required that there is no prediction of abberant splicing.''', 
        '4.5' :
			'''In-frame deletions which cause the loss of a class 5 missence variant and which disrupt or cause the loss of funcionally important protein domains.''', 
        '4.6' :
			'''In-frame insertions which were verified via in-vitro mRNA analyses, that disrupt functionally important protein domains.''', 
        '4.7' :
			'''Variants which cause a change in the tranlation initiation codon (AUG, Methionin). Additionally, there must not be evidence 
            (e. g. close alternative start-codon) for an alternative classification.''', 
        '4.8' :
			'''Variants which do have information from functional analyses, clinical data, or other evidence that do, however, not suffice for a multifactorial classification
            and which were classified as class 4 by expert panels like ENIGMA or ClinGen.''', 
        '4.9' :
			'''Variants which have functional analyses that depict loss of function or another functional relevance and which do not have contradictory information.''', 
        '5.1' :
			'''Nonsense- or frameshift variants which induce an early stop codon. This stop codon prevents the expression of known relevant functional protein domains.''', 
        '5.2' :
			'''Variants with a multifactorial calculated probability to be pathogenic of more than 0.99. \r\n\r\n
            CAVE: Only applies to BRCA1/2.''', 
        '5.3' :
			'''Splice variants which were shown to induce a frame shift that causes an early stop of the proteinbiosynthesis and, thus, prevents the expression of known relevant functional protein domains.
            This was proven via in-vitro mRNA analyses. It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).''', 
        '5.4' :
			'''Splice variants in which an invitro mRNA analysis has detected an in-frame deletion/insertion that leads to the 
            interruption or loss of a known clinically relevant domain or to a change in the protein structure which functionally inactivates the protein.
            It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).''', 
        '5.5' :
			'''Copy number deletions which cause the disruption or loss of (an) exon(s) which contain clinically relevant functional domain(s) 
            or which cause a predicted inactivation of known clinically relevant functional domains due to a frame shift.''', 
        '5.6' :
			'''Copy number duplications of any size which were proven (with lab-analyses) to duplicate one or multiple 
            exons that cause a frame shift and, thus, inactivate known clinically relevant functional protein domains.'''
    }
}







@variant_blueprint.route('/test', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('test_index.html', email=session.get('email', ''))
