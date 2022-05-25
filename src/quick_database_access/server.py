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
import fetch_heredicare_variants as heredicare
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '8pfucoisaugfqw94hoaiddrvhe6efc5b456vvfl09'
app.config['LOGS_FOLDER'] = 'logs/'
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
    conn = Connection()
    most_recent_import_request = conn.get_most_recent_import_request()
    if most_recent_import_request is None:
        status = 'finished'
    else:
        status = most_recent_import_request[3]
    conn.close()

    if request.method == 'POST' and status == 'finished':
        conn = Connection()
        import_queue_id = conn.insert_import_request(user_id = 1) ##### change user_id once login is ready!!!
        requested_at = conn.get_import_request(import_queue_id = import_queue_id)[2]
        requested_at = datetime.strptime(str(requested_at), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d-%H-%M-%S')
        conn.close()

        heredicare.process_all(log_file_date = requested_at)
        log_file_path = heredicare.get_log_file_path()
        date = log_file_path.strip('.log').split(':')[1].split('-')

        conn = Connection()
        conn.close_import_request(import_queue_id)
        conn.close()
        return redirect(url_for('import_summary', year=date[0], month=date[1], day=date[2], hour=date[3], minute=date[4], second=date[5]))

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
            num_new_variants += 1 #functions.find_between(line, 'a total of ', ' seqids were')
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
            num_heredivar_exclusive = functions.find_between(line, 'a total of ', ' seqids were')
        if '~~i6~~' in line:
            num_heredicare_exclusive = functions.find_between(line, 'a total of ', ' seqids were')
        if '~~i7~~' in line:
            num_heredivar_and_heredicare = functions.find_between(line, 'a total of ', ' seqids were')
    
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


# überprüfe nochmal dass alles die summe aus dem oben ist
# idee: alle 1000 Varianten ein zwischen-report (der anzeigt wo das programm gerade ist) anzeigen und am ende ein redirect auf die summary page?



@app.route('/create', methods=('GET', 'POST'))
def create():
    chrs = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13',
            'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT']

    if request.method == 'POST':
        create_variant_from = request.args.get("type")
        if create_variant_from == 'vcf':
            chr = request.form['chr']
            pos = request.form['pos']
            ref = request.form['ref'].upper()
            alt = request.form['alt'].upper()

            if not chr or not pos or not ref or not alt:
                flash('All fields are required!', 'alert-danger')
            else:
                was_successful = validate_and_insert(chr, pos, ref, alt)
                if was_successful:
                    return redirect('create')

        if create_variant_from == 'hgvsc':
            hgvsc = request.form['hgvsc']
            if not hgvsc:
                flash('You need to provide a HGVS c-dot string!', 'alert-danger')
            else:
                print(hgvsc)
                chr, pos, ref, alt, possible_errors = functions.hgvsc_to_vcf(hgvsc)
                print(possible_errors)
                if possible_errors != '':
                    flash(possible_errors, "alert-danger")
                else:
                    was_successful = validate_and_insert(chr, pos, ref, alt)
                    if was_successful:
                        return redirect('create')

    return render_template('create.html', chrs=chrs)



def validate_and_insert(chr, pos, ref, alt):
    was_successful = False
    # validate request
    tmp_vcf_path = tempfile.gettempdir() + "/new_variant.vcf"
    functions.variant_to_vcf(chr, pos, ref, alt, tmp_vcf_path)
    execution_code_vcfcheck, err_msg_vcfcheck, vcf_errors = functions.check_vcf(tmp_vcf_path)
    if execution_code_vcfcheck != 0: # abort if there were errors in the variant or errors during the execution of the program
        flash(err_msg_vcfcheck, 'alert-danger')
    elif vcf_errors.startswith("ERROR:"):
        flash(vcf_errors, 'alert-danger')
    else:
        execution_code_vcfleftnormalize, err_msg_vcfleftnormalize, vcfleftnormalize_output = functions.left_align_vcf(tmp_vcf_path)
        if execution_code_vcfleftnormalize != 0: # abort if the left normalization was unsuccessful
            flash(err_msg_vcfleftnormalize, 'alert-danger')
        else: # insert variant
            conn = Connection()
            is_duplicate = conn.check_variant_duplicate(chr, pos, ref, alt) # check if variant is already contained
            if not is_duplicate:
                conn.insert_variant(chr, pos, ref, alt, chr, pos, ref, alt) # insert it -> original variant = actual variant because variant import is only allowed from grch38
                conn.insert_annotation_request(get_variant_id(conn, chr, pos, ref, alt), user_id=1) ########!!!! adjust user_id once login is working!
                flash(Markup("Successfully inserted variant: " + chr + ' ' + str(pos) + ' ' + ref + ' ' + alt + 
                            ' (view your variant <a href="display/chr=' + str(chr) + '&pos=' + str(pos) + '&ref=' + str(ref) + '&alt=' + str(alt) + '" class="alert-link">here</a>)'), "alert-success")
                was_successful = True
            else:
                flash("Variant not imported: already in database!!", "alert-danger")
            conn.close()
    return was_successful


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
# example: http://127.0.0.1:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http://127.0.0.1:5000/display/17
def variant(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = Connection()

    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    if request.method == 'POST':
        conn.insert_annotation_request(variant_id, user_id=1) ########!!!! adjust user_id once login is working!
        conn.close()
        return redirect(url_for('variant', variant_id=variant_id))

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

    conn.close()
    return render_template('variant.html', 
                            variant=variant_oi, 
                            variant_annotations=variant_annot_dict, 
                            clinvar_submissions=clinvar_submissions, 
                            variant_consequences=variant_consequences, 
                            literature=literature,
                            current_annotation_status=current_annotation_status)


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
    app.run(host='SRV023.img.med.uni-tuebingen.de', debug=True)


#@app.route('/browse', methods=['GET', 'POST'])
#def browse():
#    page = int(request.args.get('page', 1))
#    per_page = 20
#    variants, total = conn.get_paginated_variants(page, per_page)
#    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
#    return render_template('browse.html', variants=variants, page=page, per_page=per_page, pagination=pagination)