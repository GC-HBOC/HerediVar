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
    #template_folder='templates',
    #static_folder='static',
    #static_url_path='/webapp/variant/static'
)




@variant_blueprint.route('/search', methods=['GET', 'POST'])
@require_login
def search():
    search_query=''
    if request.method == 'POST':
        search_query = request.form['quicksearch']
        search_type = request.form['chosen_search_type']
        if search_type != 'standard' and search_query != '' and '%' not in search_query:
            search_query = search_query + search_type
        if not is_valid_query(search_query):
            return redirect(url_for('variant.search'))
    query_type, search_query = preprocess_search_query(search_query)
    page = int(request.args.get('page', 1))
    per_page = 20
    conn = Connection()
    variants, total = conn.get_paginated_variants(page, per_page, query_type, search_query)
    conn.close()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('variant/search.html', variants=variants, page=page, per_page=per_page, pagination=pagination, search_query=search_query)



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
                        genome_build = genome_build = request.form['genome']
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
        if current_annotation_status is None or current_annotation_status[4] != 'pending':
            conn.insert_annotation_request(variant_id, session.get('user').get('preferred_username'))
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
    
    annotations = conn.get_all_variant_annotations(variant_id)

    conn.close()
    return render_template('variant/variant.html', 
                            variant=variant_oi, 
                            annotations = annotations,
                            current_annotation_status=current_annotation_status,
                            has_multiple_vids=has_multiple_vids)



@variant_blueprint.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
@require_login
def classify(variant_id):
    return render_template('variant/classify.html', variant_id=variant_id)


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
            rsid = annotations.pop('rsid', None)[4]
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

            conn.insert_consensus_classification_from_variant_id(session.get('user').get('preferred_username'), variant_id, classification, comment, date = current_date, evidence_document=evidence_b64)
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

@variant_blueprint.route('/classify/<int:variant_id>/user', methods=['GET', 'POST'])
@require_login
def user_classify(variant_id):
    if request.method == 'POST':
        classification = request.form['class']
        comment = request.form['comment']
        conn = Connection()
        conn.insert_user_classification(variant_id, classification, session.get('user').get('preferred_username'), comment) # UPDATE USER ID ONCE LOGIN IS READY!!!!!
        conn.close()
        flash(Markup("Successfully inserted new user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
        return redirect(url_for('variant.classify', variant_id = variant_id))

    return render_template('variant/user_classify.html')

