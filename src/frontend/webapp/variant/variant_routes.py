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
                            return redirect('variant.create')
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
                        return redirect('variant.create')

    return render_template('variant/create.html', chrs=chrs)




@variant_blueprint.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@variant_blueprint.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http://srv023.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http://srv023.img.med.uni-tuebingen.de:5000/display/17
@require_login
def display(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = Connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    if request.method == 'POST':
        current_annotation_status = conn.get_current_annotation_status(variant_id)
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
    variant_annotations = conn.get_recent_annotations(variant_id)
    variant_annot_dict = {}
    for annot in variant_annotations:
        variant_annot_dict[annot[0]] = annot[1:len(annot)]

    clinvar_variant_annotation = conn.get_clinvar_variant_annotation(variant_id)
    clinvar_submissions = []
    if clinvar_variant_annotation is not None:
        variant_annot_dict["clinvar_variant_annotation"] = clinvar_variant_annotation # 0id,1variant_id,2variation_id,3interpretation,4review_status,5version_date
        clinvar_variant_annotation_id = clinvar_variant_annotation[0]
        clinvar_submissions = conn.get_clinvar_submissions(clinvar_variant_annotation_id)
    
    variant_consequences = conn.get_variant_consequences(variant_id) # 0transcript_name,1hgvs_c,2hgvs_p,3consequence,4impact,5exon_nr,6intron_nr,7symbol,8transcript.gene_id,9source,10pfam_accession,11pfam_description,12length,13is_gencode_basic,14is_mane_select,15is_mane_plus_clinical,16is_ensembl_canonical,17total_flag

    literature = conn.get_variant_literature(variant_id)

    current_annotation_status = conn.get_current_annotation_status(variant_id)

    vids = conn.get_external_ids_from_variant_id(variant_id, 'heredicare')
    if len(vids) > 1:
        has_multiple_vids = True
    else:
        has_multiple_vids = False

    consensus_classification = conn.get_consensus_classification(variant_id, most_recent=True)
    if len(consensus_classification) == 1:
        consensus_classification = consensus_classification[0]
    else:
        consensus_classification = None

    
    user_classifications = conn.get_user_classifications(variant_id) # 0user_classification_id,1classification,2variant_id,3user_id,4comment,5date,6user_id,7username,8first_name,9last_name,10affiliation

    heredicare_center_classifications = conn.get_heredicare_center_classifications(variant_id)


    conn.close()
    return render_template('variant/variant.html', 
                            variant=variant_oi, 
                            variant_annotations=variant_annot_dict, 
                            clinvar_submissions=clinvar_submissions, 
                            variant_consequences=variant_consequences, 
                            literature=literature,
                            current_annotation_status=current_annotation_status,
                            has_multiple_vids=has_multiple_vids,
                            consensus_classification=consensus_classification,
                            user_classifications=user_classifications,
                            heredicare_center_classifications=heredicare_center_classifications)



@variant_blueprint.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
@require_login
def classify(variant_id):
    return render_template('variant/classify.html', variant_id=variant_id)


@variant_blueprint.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
@require_permission
def consensus_classify(variant_id):
    conn = Connection()
    variant_annotations = conn.get_recent_annotations(variant_id)
    variant_annot_dict = {}
    for annot in variant_annotations:
        variant_annot_dict[annot[0]] = annot[1:len(annot)]
    
    literature = conn.get_variant_literature(variant_id)
    user_classifications = conn.get_user_classifications(variant_id)
    heredicare_center_classifications = conn.get_heredicare_center_classifications(variant_id)

    clinvar_variant_annotation = conn.get_clinvar_variant_annotation(variant_id)
    clinvar_submissions = []
    if clinvar_variant_annotation is not None:
        clinvar_variant_annotation_id = clinvar_variant_annotation[0]
        clinvar_submissions = conn.get_clinvar_submissions(clinvar_variant_annotation_id)


    if request.method == 'POST':
        classification = request.form['class']
        comment = request.form['comment']

        if not comment:
            flash('You must provide a comment!', 'alert-danger')
        else:
            variant_oi = get_variant(conn, variant_id)

            current_date = datetime.datetime.today().strftime('%Y-%m-%d')

            buffer = io.BytesIO()
            generator = pdf_gen(buffer)
            generator.add_title('Classification report')
            v = str(variant_oi[1]) + '-' + str(variant_oi[2]) + '-' + str(variant_oi[3]) + '-' + str(variant_oi[4])
            generator.add_variant_info(v, classification, current_date, comment)
            generator.add_subtitle("Relevant scores:")
            # basic information & scores:
            if 'include_cadd' in request.form:
                generator.add_relevant_information("CADD scaled: ", variant_annot_dict['cadd_scaled'][4])
            if 'include_revel' in request.form:
                generator.add_relevant_information("REVEL: ", variant_annot_dict['revel'][4])
            if 'include_phylop' in request.form:
                generator.add_relevant_information("PhyloP 100w: ", variant_annot_dict['phylop_100way'][4])
            if 'include_spliceai_max_delta' in request.form:
                generator.add_relevant_information("SpliceAI max delta: ", variant_annot_dict['spliceai_max_delta'][4])
            if 'include_spliceai_details' in request.form:
                generator.add_relevant_information("SpliceAI details: ", variant_annot_dict['spliceai_details'][4])
            if 'include_maxentscan_ref' in request.form:
                generator.add_relevant_information("MaxEntScan ref: ", variant_annot_dict['maxentscan_ref'][4])
            if 'include_maxentscan_alt' in request.form:
                generator.add_relevant_information("MaxEntScan alt: ", variant_annot_dict['maxentscan_alt'][4])
            
            if 'include_gnomad' in request.form:
                if 'include_gnomad_ac' in request.form:
                    generator.add_relevant_information("AC: ", variant_annot_dict['gnomad_ac'][4])
                if 'include_gnomad_af' in request.form:
                    generator.add_relevant_information("AF: ", variant_annot_dict['gnomad_af'][4])
                if 'include_gnomad_popmax' in request.form:
                    generator.add_relevant_information("Popmax: ", variant_annot_dict['gnomad_popmax'][4])
                if 'include_gnomad_hom' in request.form:
                    generator.add_relevant_information("Number homozygotes: ", variant_annot_dict['gnomad_hom'][4])
                if 'include_gnomad_het' in request.form:
                    generator.add_relevant_information("Number heterozygotes", variant_annot_dict['gnomad_het'][4])
                if 'include_gnomad_hemi' in request.form:
                    generator.add_relevant_information("Number hemizyogtes", variant_annot_dict['gnomad_hemi'][4])
            if 'include_flossies' in request.form:
                if 'include_flossies_num_afr' in request.form:
                    generator.add_relevant_information("Number african", variant_annot_dict['flossies_num_afr'][4])
                if 'include_flossies_num_eur' in request.form:
                    generator.add_relevant_information("Number european", variant_annot_dict['flossies_num_eur'][4])
            
            if 'include_tpdb' in request.form:
                if 'include_tp53db_class' in request.form:
                    generator.add_relevant_information("Class: ", variant_annot_dict['tp53db_class'][4])
                if 'include_tp53db_bayes_del' in request.form:
                    generator.add_relevant_information("Bayes del: ", variant_annot_dict['tp53db_bayes_del'][4])
                if 'include_tp53db_DNE_LOF_class' in request.form:
                    generator.add_relevant_information("DNE LOF class: ", variant_annot_dict['tp53db_DNE_LOF_class'][4])
                if 'include_tp53db_DNE_class' in request.form:
                    generator.add_relevant_information("DNE class: ", variant_annot_dict['tp53db_DNE_class'][4])
                if 'include_tp53db_domain_function' in request.form:
                    generator.add_relevant_information("Domain function", variant_annot_dict['tp53db_domain_function'][4])
                if 'include_tp53db_transactivation_class' in request.form:
                    generator.add_relevant_information("Transactivation class", variant_annot_dict['tp53db_transactivation_class'][4])
            if 'include_cancerhotspots_cancertypes' in request.form:
                generator.add_relevant_information("Cancerhotspots cancertypes: ", variant_annot_dict['cancerhotspots_cancertypes'][4])
            if 'include_cancerhotspots_ac' in request.form:
                generator.add_relevant_information("Cancerthotspots AC: ", variant_annot_dict['cancerhotspots_ac'][4])
            if 'include_cancerhotspots_af' in request.form:
                generator.add_relevant_information("Cancerhotspots AF: ", variant_annot_dict['cancerhotspots_af'][4])
            if 'include_heredicare_cases_count' in request.form:
                generator.add_relevant_information("HerediCare cases count: ", variant_annot_dict['heredicare_cases_count'][4])
            if 'include_heredicare_family_count' in request.form:
                generator.add_relevant_information("Heredicare family count: ", variant_annot_dict['heredicare_family_count'][4])
            
            # literature
            literature_ids = [x.replace('include_literature_', '') for x in request.form.keys() if x.startswith('include_literature')] # get selected literature ids
            if len(literature_ids) > 0:
                literature_oi = [str(x[2]) for x in literature if str(x[0]) in literature_ids] # collect relevant information for plotting to pdf
                generator.add_subtitle("Relevant PubMed IDs:")
                generator.add_relevant_literature(literature_oi)


            # user classifications
            user_classification_ids = [x.replace('include_user_classification_', '') for x in request.form.keys() if x.startswith('include_user_classification_')] # get selected user classification ids
            if len(user_classification_ids) > 0:
                include_user_classifications = True
                user_classifications_oi = [[x[1], x[3], x[5], x[4]] for x in user_classifications if str(x[0]) in user_classification_ids] # collect relevant information for plotting to pdf
            else:
                include_user_classifications = False
                

            # heredicare center classifications
            center_classification_ids = [x.replace('include_heredicare_center_classification_', '') for x in request.form.keys() if x.startswith('include_heredicare_center_classification_')] # get selected user classification ids
            if len(center_classification_ids) > 0:
                include_center_classifications = True
                center_classifications_oi = [[x[1], x[3], x[5], x[4]] for x in heredicare_center_classifications if str(x[0]) in center_classification_ids] # collect relevant information for plotting to pdf
            else:
                include_center_classifications = False

            # clinvar submissions 
            clinvar_submission_ids = [x.replace('include_clinvar_', '') for x in request.form.keys() if x.startswith('include_clinvar_')] # get selected user classification ids
            if len(clinvar_submission_ids) > 0:
                include_clinvar_submissions = True
                clinvar_submissions_oi = [[x[2], x[3], x[4], x[5][1], x[6]] for x in clinvar_submissions if str(x[0]) in clinvar_submission_ids] # collect relevant information for plotting to pdf
            else:
                include_clinvar_submissions = False
                
            
            if include_user_classifications or include_center_classifications or include_clinvar_submissions:
                generator.add_subtitle("Relevant classifications:")
            if include_user_classifications:
                generator.add_relevant_classifications(user_classifications_oi, ('Class', 'User', 'Date', 'Comment'), [6, 10, 11, 70])
            if include_center_classifications:
                generator.add_relevant_classifications(center_classifications_oi, ('Class', 'Center', 'Date', 'Comment'), [6, 10, 11, 70])
            if include_clinvar_submissions:
                generator.add_relevant_classifications(clinvar_submissions_oi, ('Interpretation', 'Last evaluated', 'Review status', 'Condition', 'Submitter'), [30, 30, 20, 20, 30])


            generator.save_pdf()

            buffer.seek(io.SEEK_SET)
            evidence_b64 = functions.buffer_to_base64(buffer)
            #functions.base64_to_file(evidence_b64, '/mnt/users/ahdoebm1/HerediVar/src/frontend/downloads/consensus_classification_reports/testreport.pdf')

            conn.insert_consensus_classification_from_variant_id(session.get('user').get('preferred_username'), variant_id, classification, comment, date = current_date, evidence_document=evidence_b64)
            flash(Markup("Successfully inserted new consensus classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
        conn.close()
        return redirect(url_for('variant.consensus_classify', variant_id=variant_id))

    conn.close()
    return render_template('variant/consensus_classify.html', variant_annotations = variant_annot_dict, literature=literature, user_classifications = user_classifications, heredicare_center_classifications=heredicare_center_classifications, clinvar_submissions=clinvar_submissions)

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

