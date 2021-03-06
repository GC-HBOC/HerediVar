from flask import Flask, render_template, request, url_for, flash, redirect, session, Markup, send_from_directory
#from flask_mysqldb import MySQL
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
from flask_paginate import Pagination
from werkzeug.exceptions import abort
import common.functions as functions
import tempfile
import re
import annotation_service.fetch_heredicare_variants as heredicare
from datetime import datetime
from common.pdf_generator import pdf_gen
import io

app = Flask(__name__)

app.config['SECRET_KEY'] = '8pfucoisaugfqw94hoaiddrvhe6efc5b456vvfl09'
app.config['LOGS_FOLDER'] = 'downloads/logs/'
app.config['CONSENSUS_CLASSIFICATION_REPORT_FOLDER'] = 'downloads/consensus_classification_reports/'
#app.config["MYSQL_USER"] = "ahdoebm1"
#app.config["MYSQL_PASSWORD"] = "20220303"
#app.config["MYSQL_HOST"] = "SRV018.img.med.uni-tuebingen.de"
#app.config["MYSQL_DB"] = "bioinf_heredivar_ahdoebm1"
#app.config["MYSQL_PORT"] = 3306

##mysql = MySQL(app)




def get_variant(conn, variant_id):
    if variant_id is None:
        abort(404)
    variant = conn.get_one_variant(variant_id)
    if variant is None:
        abort(404)
    return variant

def get_variant_id(conn, chr, pos, ref, alt):
    if chr is None or pos is None or ref is None or alt is None:
        abort(404)
    variant_id = conn.get_variant_id(chr, pos, ref, alt)
    return variant_id

def is_valid_query(search_query):
    print(search_query)
    if re.search("%.*%\s*%.*%", search_query):
        flash("Search query ERROR: No multiple query types allowed in: " + search_query, 'alert-danger')
        return False
    if re.search('-', search_query):
        if not re.search("chr.+:\d+-\d+", search_query): # chr2:214767531-214780740
            flash("Search query malformed: Expecting chromosomal range search of the form: 'chr:start-end'. Query: " + search_query + " If you are looking for a gene which contains a '-' use the appropriate radio button or append '%gene%'.", 'alert-danger')
            return False # if the range query is not exactly of this form it is malformed
        else:
            res = re.search("chr.+:(\d+)-(\d+)", search_query)
            start = res.group(1)
            end = res.group(2)
            if start > end:
                flash("Search query WARNING: Range search start position is larger than the end position, in: " + search_query, 'alert-danger')
    if "%hgvs%" in search_query:
        if not re.search(".*:[c\.|p\.]", search_query):
            flash("Search query ERROR: malformed hgvs found in " + search_query + " expecting 'transcript:[c. OR p.]...'", 'alert-danger')
            return False
    return True

def validate_and_insert_variant(chr, pos, ref, alt, genome_build):
    was_successful = True
    # validate request
    tmp_file_path = tempfile.gettempdir() + "/new_variant.vcf"
    tmp_vcfcheck_out_path = tempfile.gettempdir() + "/frontend_variant_import_vcf_errors.txt"
    functions.variant_to_vcf(chr, pos, ref, alt, tmp_file_path)
    

    command = ['/mnt/users/ahdoebm1/HerediVar/src/common/scripts/preprocess_variant.sh', '-i', tmp_file_path, '-o', tmp_vcfcheck_out_path]

    if genome_build == 'GRCh37':
        command.append('-l') # enable liftover
        
    returncode, err_msg, command_output = functions.execute_command(command, 'preprocess_variant')
    #print(err_msg)
    #print(command_output)
    
    if returncode != 0:
        flash(err_msg, 'alert-danger')
        was_successful = False
        return was_successful
    vcfcheck_errors = open(tmp_vcfcheck_out_path + '.pre', 'r').read()
    if 'ERROR:' in vcfcheck_errors:
        flash(vcfcheck_errors.replace('\n', ' '), 'alert-danger')
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
    vcfcheck_errors = open(tmp_vcfcheck_out_path + '.post', 'r').read()
    if 'ERROR:' in vcfcheck_errors:
        flash(vcfcheck_errors.replace('\n', ' '), 'alert-danger')
        was_successful = False
        return was_successful

    if was_successful:
        variant = functions.read_vcf_variant(tmp_file_path)[0] # accessing only the first element of the returned list is save because we process only one variant at a time
        new_chr = variant.CHROM
        new_pos = variant.POS
        new_ref = variant.REF
        new_alt = variant.ALT

        conn = Connection()
        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt) # check if variant is already contained
        if not is_duplicate:
            conn.insert_variant(new_chr, new_pos, new_ref, new_alt, chr, pos, ref, alt) # insert it -> original variant = actual variant because variant import is only allowed from grch38
            conn.insert_annotation_request(get_variant_id(conn, new_chr, new_pos, new_ref, new_alt), user_id=1) ########!!!! adjust user_id once login is working!
            flash(Markup("Successfully inserted variant: " + new_chr + ' ' + str(new_pos) + ' ' + new_ref + ' ' + new_alt + 
                        ' (view your variant <a href="display/chr=' + str(new_chr) + '&pos=' + str(new_pos) + '&ref=' + str(new_ref) + '&alt=' + str(new_alt) + '" class="alert-link">here</a>)'), "alert-success")
        else:
            flash("Variant not imported: already in database!!", "alert-danger")
            was_successful = False
        conn.close()

    #execution_code_vcfcheck, err_msg_vcfcheck, vcf_errors = functions.check_vcf(tmp_vcf_path, genome_build)
    #if execution_code_vcfcheck != 0: # abort if there were errors in the variant or errors during the execution of the program
    #    flash(err_msg_vcfcheck, 'alert-danger')
    #elif vcf_errors.startswith("ERROR:"):
    #    flash(vcf_errors, 'alert-danger')
    #else:
    #    execution_code_vcfleftnormalize, err_msg_vcfleftnormalize, vcfleftnormalize_output = functions.left_align_vcf(tmp_vcf_path, genome_build)
    #    if execution_code_vcfleftnormalize != 0: # abort if the left normalization was unsuccessful
    #        flash(err_msg_vcfleftnormalize, 'alert-danger')
    #    else: # insert variant
    #        conn = Connection()
    #        is_duplicate = conn.check_variant_duplicate(chr, pos, ref, alt) # check if variant is already contained
    #        if not is_duplicate:
    #            conn.insert_variant(chr, pos, ref, alt, chr, pos, ref, alt) # insert it -> original variant = actual variant because variant import is only allowed from grch38
    #            conn.insert_annotation_request(get_variant_id(conn, chr, pos, ref, alt), user_id=1) ########!!!! adjust user_id once login is working!
    #            flash(Markup("Successfully inserted variant: " + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + 
    #                        ' (view your variant <a href="display/chr=' + str(chr) + '&pos=' + str(pos) + '&ref=' + str(ref) + '&alt=' + str(alt) + '" class="alert-link">here</a>)'), "alert-success")
    #            was_successful = True
    #        else:
    #            flash("Variant not imported: already in database!!", "alert-danger")
    #        conn.close()
    return was_successful


def preprocess_search_query(query):
    res = re.search("(.*)(%.*%)", query)
    ext = ''
    if res is not None:
        query = res.group(1)
        ext = res.group(2)
    query = query.strip()
    if query.startswith(("HGNC:", "hgnc:")):
        return "gene", query[5:]
    if "%gene%" in ext:
        return "gene", query
    if "c." in query or "p." in query or "%hgvs%" in ext:
        return "hgvs", query
    if "-" in query or "%range%" in ext:
        return "range", query
    return "standard", query

@app.route('/')
def base():
    #conn.insert_variants_from_vcf("./data/NA12878_03_export_20220308_ahsturm1.vcf")
    return render_template('index.html')


@app.route('/import-variants', methods=('GET', 'POST'))
def import_variants():
    if request.method == 'POST':
        request_type = request.args.get("type")
        if request_type == 'update_variants':
            conn = Connection()
            most_recent_import_request = conn.get_most_recent_import_request()
            if most_recent_import_request is None:
                status = 'finished'
            else:
                status = most_recent_import_request[3]

            if status == 'finished':
                import_queue_id = conn.insert_import_request(user_id = 1) ##### change user_id once login is ready!!!
                requested_at = conn.get_import_request(import_queue_id = import_queue_id)[2]
                requested_at = datetime.strptime(str(requested_at), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d-%H-%M-%S')

                logs_folder = path.join(app.root_path, app.config['LOGS_FOLDER'])
                log_file_path = logs_folder + 'heredicare_import:' + requested_at + '.log'
                heredicare.process_all(log_file_path)
                log_file_path = heredicare.get_log_file_path()
                date = log_file_path.strip('.log').split(':')[1].split('-')

                conn.close_import_request(import_queue_id)
                conn.close()
                return redirect(url_for('import_summary', year=date[0], month=date[1], day=date[2], hour=date[3], minute=date[4], second=date[5]))

        elif request_type == 'reannotate':
            conn = Connection()
            variant_ids = conn.get_all_valid_variant_ids()
            for variant_id in variant_ids:
                conn.insert_annotation_request(variant_id, user_id=1) ###### change user_id once login is ready!!!!!!!
            conn.close()

            flash('Variant reannotation requested. It will be computed in the background.', 'alert-success')
        

    return render_template('import_variants.html', most_recent_import_request=most_recent_import_request)



@app.route('/import-variants/summary?date=<string:year>-<string:month>-<string:day>-<string:hour>-<string:minute>-<string:second>')
def import_summary(year, month, day, hour, minute, second):
    logs_folder = path.join(app.root_path, app.config['LOGS_FOLDER'])
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
    return render_template('import_variants_summary.html', 
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


@app.route('/import-variants/summary/download?file=<string:log_file>')
def download_log_file(log_file):
    logs_folder = path.join(app.root_path, app.config['LOGS_FOLDER'])
    return send_from_directory(directory=logs_folder, path='', filename=log_file) 




@app.route('/create', methods=('GET', 'POST'))
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
                            return redirect('create')
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
                        return redirect('create')

    return render_template('create.html', chrs=chrs)




@app.route('/search', methods=['GET', 'POST'])
def browse():
    search_query=''
    if request.method == 'POST':
        search_query = request.form['quicksearch']
        search_type = request.form['chosen_search_type']
        if search_type != 'standard' and search_query != '' and '%' not in search_query:
            search_query = search_query + search_type
        if not is_valid_query(search_query):
            return redirect(url_for('browse'))
    query_type, search_query = preprocess_search_query(search_query)
    page = int(request.args.get('page', 1))
    per_page = 20
    conn = Connection()
    variants, total = conn.get_paginated_variants(page, per_page, query_type, search_query)
    conn.close()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('browse.html', variants=variants, page=page, per_page=per_page, pagination=pagination, search_query=search_query)


@app.route('/display/<int:variant_id>', methods=['GET', 'POST'])
@app.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>', methods=['GET', 'POST']) # alternative url using vcf information
# example: http://srv023.img.med.uni-tuebingen.de:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http://srv023.img.med.uni-tuebingen.de:5000/display/17
def variant(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = Connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    if request.method == 'POST':
        current_annotation_status = conn.get_current_annotation_status(variant_id)
        if current_annotation_status is None or current_annotation_status[4] != 'pending':
            conn.insert_annotation_request(variant_id, user_id=1) ########!!!! adjust user_id once login is working!
            conn.close()
            return redirect(url_for('variant', variant_id=variant_id, from_reannotate='True'))

    if request.args.get('from_reannotate', 'False') == 'True':
        variant_oi = conn.get_one_variant(variant_id)
        if variant_oi is None:
            return redirect(url_for('deleted_variant'))
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

    
    user_classifications = conn.get_user_classifications(variant_id)

    heredicare_center_classifications = conn.get_heredicare_center_classifications(variant_id)


    conn.close()
    return render_template('variant.html', 
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


@app.route('/download_evidence_document/<int:variant_id>')
def download_evidence_document(variant_id):
    conn = Connection()
    consensus_classification = conn.get_consensus_classification(variant_id, most_recent=True)
    conn.close()
    if consensus_classification is None:
        abort(404)
    consensus_classification = consensus_classification[0]
    b_64_report = consensus_classification[5]

    report_folder = path.join(app.root_path, app.config['CONSENSUS_CLASSIFICATION_REPORT_FOLDER'])
    report_filename = 'consensus_classification_report_' + str(variant_id) + '.pdf'
    report_path = path.join(report_folder, report_filename)
    if not path.isfile(report_path):
        functions.base64_to_file(base64_string = b_64_report, path = report_path)
    
    return send_from_directory(directory=report_folder, path='', filename=report_filename)

@app.route('/deleted_variant_info')
def deleted_variant():
    return render_template('deleted_variant.html')




@app.route('/classify/<int:variant_id>', methods=['GET', 'POST'])
def classify(variant_id):
    return render_template('classify.html', variant_id=variant_id)


@app.route('/classify/<int:variant_id>/consensus', methods=['GET', 'POST'])
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

            current_date = datetime.today().strftime('%Y-%m-%d')

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
            functions.base64_to_file(evidence_b64, '/mnt/users/ahdoebm1/HerediVar/src/quick_database_access/downloads/consensus_classification_reports/testreport.pdf')

            #conn.insert_consensus_classification_from_variant_id(variant_id, classification, comment, date = current_date, evidence_document=evidence_b64)
            flash(Markup("Successfully inserted new consensus classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
        conn.close()
        return redirect(url_for('consensus_classify', variant_id=variant_id))

    conn.close()
    return render_template('consensus_classify.html', variant_annotations = variant_annot_dict, literature=literature, user_classifications = user_classifications, heredicare_center_classifications=heredicare_center_classifications, clinvar_submissions=clinvar_submissions)

@app.route('/classify/<int:variant_id>/user', methods=['GET', 'POST'])
def user_classify(variant_id):
    if request.method == 'POST':
        classification = request.form['class']
        comment = request.form['comment']
        conn = Connection()
        conn.insert_user_classification(variant_id, classification, 1, comment) # UPDATE USER ID ONCE LOGIN IS READY!!!!!
        conn.close()
        flash(Markup("Successfully inserted new user classification return <a href=/display/" + str(variant_id) + " class='alert-link'>here</a> to view it!"), "alert-success")
        return redirect(url_for('classify', variant_id = variant_id))

    return render_template('user_classify.html')



'''
@app.route('/classification_report/<int:variant_id>')
def classification_report(variant_id):
    conn = Connection()

    variant_oi = get_variant(conn, variant_id)
    classification = '5'
    comment = "blabla some comment blablabla"
    today_date = datetime.today().strftime('%Y-%m-%d')
    classification_details = [classification, comment, today_date]

    variant_annotations = conn.get_recent_annotations(variant_id)
    variant_annot_dict = {}
    for annot in variant_annotations:
        variant_annot_dict[annot[0]] = annot[1:len(annot)]

    source_html = render_template('consensus_classification_report.html', variant=variant_oi, classification_details=classification_details, variant_annotations = variant_annot_dict)

    import common.test
    common.test.convert_html_to_pdf(source_html, '/mnt/users/ahdoebm1/HerediVar/src/quick_database_access/downloads/consensus_classification_reports/testreport.pdf')
    conn.close()
    return source_html
'''


@app.route('/gene/<int:gene_id>')
def gene(gene_id):
    conn = Connection()
    gene_info = conn.get_gene(gene_id)
    transcripts = conn.get_transcripts(gene_id) # 0gene_id,1name,2biotype,3length,4is_gencode_basic,5is_mane_select,6is_mane_plus_clinical,7is_ensembl_canonical,8total_flags
    conn.close()
    return render_template('gene.html', gene_info=gene_info, transcripts=transcripts)


@app.route('/help/search')
def search_help():
    return render_template('search_help.html')


if __name__ == '__main__':
    app.run(host='SRV018.img.med.uni-tuebingen.de', debug=True)


#@app.route('/browse', methods=['GET', 'POST'])
#def browse():
#    page = int(request.args.get('page', 1))
#    per_page = 20
#    variants, total = conn.get_paginated_variants(page, per_page)
#    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
#    return render_template('browse.html', variants=variants, page=page, per_page=per_page, pagination=pagination)