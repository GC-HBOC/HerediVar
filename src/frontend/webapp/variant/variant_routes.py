from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app, abort
from flask_paginate import Pagination
from ..utils import *
import datetime
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import io
from common.pdf_generator import pdf_gen



variant_blueprint = Blueprint(
    'variant',
    __name__
)



#http://srv018.img.med.uni-tuebingen.de:5000/search?ranges=chr1%3A0-9999999999999%3Bchr2%3A0-99999999999999999999%3BchrMT%3A0-9999999999999999
@variant_blueprint.route('/search')  # CDH1  chr1:10295758-17027834; chr11:108229378-108229378
@require_login
def search():

    genes = request.args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")

    ranges = request.args.get('ranges', '')
    ranges = preprocess_query(ranges, pattern= "chr.+:\d+-\d+")
    if ranges is None:
        flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    
    consensus = request.args.getlist('consensus')
    consensus = ';'.join(consensus)
    consensus = preprocess_query(consensus, '[12345]?')
    if consensus is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")

    hgvs = request.args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = ".+:c\.\d+[ACGTNacgtn]+>\d+[ACGTNacgtn]+")
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! Results are not filtered by hgvs.", "alert-danger")

    variant_ids_oi = request.args.get('variant_ids_oi', '')
    variant_ids_oi = preprocess_query(variant_ids_oi, '\d*')
    if variant_ids_oi is None:
        flash("You have an error in your variant id query(s). It must contain only numbers. Results are not filtered by variants.", "alert-danger")

    page = int(request.args.get('page', 1))
    per_page = 20
    conn = Connection()
    variants, total = conn.get_variants_page_merged(page, per_page, user_id=session['user']['user_id'], ranges=ranges, genes = genes, consensus=consensus, hgvs=hgvs, variant_ids_oi=variant_ids_oi)
    conn.close()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('variant/search.html', variants=variants, page=page, per_page=per_page, pagination=pagination)



@variant_blueprint.route('/create', methods=('GET', 'POST'))
@require_login
def create():
    chrs = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13',
            'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT']

    if request.method == 'POST':
        create_variant_from = request.args.get("type")
        if create_variant_from == 'vcf':
            chr = request.form['chr']
            pos = ''.join(request.form['pos'].split())
            ref = request.form['ref'].upper().strip()
            alt = request.form['alt'].upper().strip()

            if not chr or not pos or not ref or not alt or 'genome' not in request.form:
                flash('All fields are required!', 'alert-danger')
            else:
                try:
                    if int(pos) < 0:
                        flash('ERROR: Negative genomic position given, but must be positive.', 'alert-danger')
                    else:
                        genome_build = request.form['genome']
                        was_successful = validate_and_insert_variant(chr, pos, ref, alt, genome_build)
                        if was_successful:
                            return redirect(url_for('variant.create'))
                except:
                    flash('ERROR: Genomic position is not a valid integer.', 'alert-danger')


        if create_variant_from == 'hgvsc':
            reference_transcript = request.form['transcript']
            hgvsc = request.form['hgvsc']
            if not hgvsc or not reference_transcript:
                flash('All fields are required!', 'alert-danger')
            else:
                chr, pos, ref, alt, possible_errors = functions.hgvsc_to_vcf(reference_transcript + ':' + hgvsc)
                if possible_errors != '':
                    flash(possible_errors, "alert-danger")
                else:
                    was_successful = validate_and_insert_variant(chr, pos, ref, alt, 'GRCh38')
                    if was_successful:
                        return redirect(url_for('variant.create'))

    return render_template('variant/create.html', chrs=chrs)


@variant_blueprint.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http://srv023.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http://srv023.img.med.uni-tuebingen.de:5000/display/17
@require_login
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = Connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    current_annotation_status = conn.get_current_annotation_status(variant_id)
    if request.method == 'POST':
        user_action = request.args.get('action')
        if user_action == 'add_to_list':
            list_id = request.form['add-to-list']
            conn.add_variant_to_list(list_id, variant_id) # MAYBE add a check that this list belongs to you!
            return redirect(url_for('variant.display', variant_id=variant_id))
        if user_action == 'reannotate' and (current_annotation_status is None or current_annotation_status[4] != 'pending'):
            conn.insert_annotation_request(variant_id, user_id = session['user']['user_id'])
            conn.close()
            return redirect(url_for('variant.display', variant_id=variant_id, from_reannotate='True'))

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

    lists = conn.get_lists_for_user(user_id = session['user']['user_id'], variant_id=variant_id)


    clinvar_submission_id = conn.get_external_ids_from_variant_id(variant_id, id_source="clinvar_submission")
    clinvar_submission = {'status': None, 'date': None, 'message': None}
    if len(clinvar_submission_id) > 1: # this should not happen!
        clinvar_submission_id = clinvar_submission_id[len(clinvar_submission_id) - 1]
        flash("WARNING: There are multiple clinvar submission ids for this variant. There is probably an old clinvar submission somewhere in the system which should be deleted. Using " + str(clinvar_submission_id) + " now.", "alert-warning")
    if len(clinvar_submission_id) == 1: # variant was already submitted to clinvar
        clinvar_submission_id = clinvar_submission_id[0]
        api_key = os.environ.get('CLINVAR_API_KEY')
        headers = {'SP-API-KEY': api_key, 'Content-type': 'application/json'}
        resp = get_clinvar_submission_status(clinvar_submission_id, headers = headers)
        if resp.status_code not in [200]:
            conn.close()
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

    conn.close()
    return render_template('variant/variant.html', 
                            variant=variant_oi, 
                            annotations = annotations,
                            current_annotation_status=current_annotation_status,
                            clinvar_submission = clinvar_submission,
                            has_multiple_vids=has_multiple_vids,
                            lists = lists)


@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission
def consensus_classify(variant_id):

    if request.method == 'POST':
        classification = request.form['class']
        comment = request.form['comment']

        if not comment:
            flash('You must provide a comment!', 'alert-danger')
        else:
            conn = Connection()
            annotations = conn.get_all_variant_annotations(variant_id)
            annotations.pop('consensus_classification', None)
            variant_oi = get_variant(conn, variant_id)

            current_date = datetime.datetime.today().strftime('%Y-%m-%d')

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
            #functions.base64_to_file(evidence_b64, '/mnt/users/ahdoebm1/HerediVar/src/frontend/downloads/consensus_classification_reports/testreport.pdf')

            conn.insert_consensus_classification_from_variant_id(session['user']['user_id'], variant_id, classification, comment, evidence_document=evidence_b64, date = current_date)
            flash(Markup("Successfully inserted new consensus classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
            conn.close()
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))
    
    conn = Connection()
    if conn.get_consensus_classification(variant_id, most_recent=True) is not None:
        has_consensus = True
    else:
        has_consensus = False
    conn.close()
    return render_template('variant/consensus_classify.html', has_consensus=has_consensus)


@variant_blueprint.route('/display/<int:variant_id>/consensus_classification_history')
@require_login
def consensus_classification_history(variant_id):
    conn = Connection()
    consensus_classifications = conn.get_consensus_classification(variant_id)
    conn.close()
    most_recent_consensus_classification = [x for x in consensus_classifications if x[6] == 1][0]
    other_consensus_classifications = [x for x in consensus_classifications if x[6] == 0]
    if consensus_classifications is None:
        abort(404) # redirect to error page
    return render_template('variant/classification_history.html', most_recent_consensus_classification=most_recent_consensus_classification, other_consensus_classifications=other_consensus_classifications)


@variant_blueprint.route('/classify/<int:variant_id>/user', methods=['GET', 'POST'])
@require_login
def user_classify(variant_id):
    conn = Connection()
    user_classification = conn.get_user_classification_by_username(session['user']['preferred_username'], variant_id)
    # default values
    previous_classification = 1
    previous_comment = ''
    has_classification = False
    if user_classification is not None:
        previous_classification=user_classification[1]
        previous_comment=user_classification[4]
        has_classification = True

    if request.method == 'POST':
        classification = request.form['class']
        comment = request.form['comment'].strip()
        if classification:
            previous_classification = classification
        if comment:
            previous_comment = comment
        if not comment or not classification:
            flash("All fields are required!", "alert-danger")
        else:
            current_date = datetime.datetime.today().strftime('%Y-%m-%d')
            if user_classification is not None: # user already has a classification for this variant -> he requests an update
                conn.update_user_classification(user_classification[0], classification, comment, date = current_date)
                flash(Markup("Successfully updated user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
            else: # user does not yet have a classification for this variant -> he wants to create a new one
                conn.insert_user_classification(variant_id, classification, session['user']['user_id'], comment, date = current_date)
                conn.close()
                flash(Markup("Successfully inserted new user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
            return redirect(url_for('variant.user_classify', variant_id = variant_id))
    conn.close()

    return render_template('variant/user_classify.html', previous_classification=int(previous_classification), previous_comment=previous_comment, has_classification=has_classification)

@variant_blueprint.route('/classify/<int:variant_id>/acmg', methods=['GET', 'POST'])
@require_login
def acmg_classify(variant_id):
    if request.method == 'POST':
        print(request.form['pvs1'])
    return render_template('variant/acmg.html')