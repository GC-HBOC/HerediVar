from flask import Flask, render_template, request, url_for, flash, redirect, session
#from flask_mysqldb import MySQL
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
from flask_paginate import Pagination
from werkzeug.exceptions import abort
import common.functions as functions
import tempfile

app = Flask(__name__)

app.config['SECRET_KEY'] = '8pfucoisaugfqw94hoaiddrvhe6efc5b456vvfl09'

#app.config["MYSQL_USER"] = "ahdoebm1"
#app.config["MYSQL_PASSWORD"] = "20220303"
#app.config["MYSQL_HOST"] = "SRV018.img.med.uni-tuebingen.de"
#app.config["MYSQL_DB"] = "bioinf_heredivar_ahdoebm1"
#app.config["MYSQL_PORT"] = 3306

#mysql = MySQL(app)





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


@app.route('/')
def base():
    #conn.insert_variants_from_vcf("./data/NA12878_03_export_20220308_ahsturm1.vcf")
    return render_template('base.html')


@app.route('/create', methods=('GET', 'POST'))
def create():
    chrs = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13',
            'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT']
    if request.method == 'POST':
        chr = request.form['chr']
        pos = request.form['pos']
        ref = request.form['ref']
        alt = request.form['alt']

        if not chr or not pos or not ref or not alt:
            flash('All fields are required!')
        else:
            # VALIDATE REQUEST!!!!
            tmp_vcf_path = tempfile.gettempdir() + "/new_variant.vcf"
            functions.variant_to_vcf(chr, pos, ref, alt, tmp_vcf_path)
            execution_code_vcfcheck, err_msg_vcfcheck, vcf_errors = functions.check_vcf(tmp_vcf_path)
            if execution_code_vcfcheck != 0:
                flash(err_msg_vcfcheck)
            elif vcf_errors.startswith("ERROR:"):
                flash(vcf_errors)
            else:
                conn = Connection()
                conn.insert_variant(chr, pos, ref, alt)
                conn.close()
                return redirect(url_for('create'))

    return render_template('create.html', chrs=chrs)


@app.route('/browse', methods=['GET', 'POST'])
def browse():
    search_value = ''
    if request.method == 'POST':
        search_value = request.form['quicksearch']
    page = int(request.args.get('page', 1))
    per_page = 20
    conn = Connection()
    variants, total = conn.get_paginated_variants(page, per_page, search_value)
    conn.close()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('browse.html', variants=variants, page=page, per_page=per_page, pagination=pagination)


@app.route('/display/<int:variant_id>')
@app.route('/display/chr=<string:chr>&pos=<int:pos>&ref=<string:ref>&alt=<string:alt>') # alternative urls using vcf information
# example: http://127.0.0.1:5000/display/chr=chr2&pos=214767531&ref=C&alt=T is the same as: http://127.0.0.1:5000/display/17
def variant(variant_id=None, chr=None, pos=None, ref=None, alt=None):
    conn = Connection()
    if variant_id is None:
        variant_id = get_variant_id(conn, chr, pos, ref, alt)

    variant_oi = get_variant(conn, variant_id) # this redirects to 404 page if the variant was not found
    variant_annotations = conn.get_recent_annotations(variant_id)
    variant_annot_dict = {}
    for annot in variant_annotations:
        variant_annot_dict[annot[0]] = annot[1:len(annot)]

    clinvar_variant_annotation = conn.get_clinvar_variant_annotation(variant_id)
    clinvar_submissions = []
    if clinvar_variant_annotation is not None:
        variant_annot_dict["clinvar_variant_annotation"] = clinvar_variant_annotation
        clinvar_variant_annotation_id = clinvar_variant_annotation[0]
        clinvar_submissions = conn.get_clinvar_submissions(clinvar_variant_annotation_id)
    
    variant_consequences = conn.get_variant_consequences(variant_id)

    literature = conn.get_variant_literature(variant_id)

    conn.close()
    return render_template('variant.html', variant=variant_oi, variant_annotations=variant_annot_dict, clinvar_submissions=clinvar_submissions, variant_consequences=variant_consequences, literature=literature)


if __name__ == '__main__':
    app.run(debug=True)


#@app.route('/browse', methods=['GET', 'POST'])
#def browse():
#    page = int(request.args.get('page', 1))
#    per_page = 20
#    variants, total = conn.get_paginated_variants(page, per_page)
#    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
#    return render_template('browse.html', variants=variants, page=page, per_page=per_page, pagination=pagination)