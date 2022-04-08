from flask import Flask, render_template, request, url_for, flash, redirect
#from flask_mysqldb import MySQL
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)

#app.config['SECRET_KEY'] = '8pfucoisaugfqw94hoaiddrvhe6efc5b456vvfl09'

#app.config["MYSQL_USER"] = "ahdoebm1"
#app.config["MYSQL_PASSWORD"] = "20220303"
#app.config["MYSQL_HOST"] = "SRV018.img.med.uni-tuebingen.de"
#app.config["MYSQL_DB"] = "bioinf_heredivar_ahdoebm1"
#app.config["MYSQL_PORT"] = 3306

#mysql = MySQL(app)

conn = Connection()



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
            conn.insert_variant(chr, pos, ref, alt)
            return redirect(url_for('create'))

    return render_template('create.html', chrs=chrs)


@app.route('/browse', methods=['GET'])
def browse():
    #page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    page = int(request.args.get('page', 1))
    per_page = 20
    variants = conn.get_paginated_variants(page, per_page)
    total = 100
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    return render_template('browse.html', variants=variants, page=page, per_page=per_page, pagination=pagination)


if __name__ == '__main__':
    app.run(debug=True)
