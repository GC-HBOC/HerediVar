from flask import Flask, render_template, request, url_for, flash, redirect
from flask_mysqldb import MySQL
import VCFIO

app = Flask(__name__)

app.config['SECRET_KEY'] = '8pfucoisaugfqw94hoaiddrvhe6efc5b456vvfl09'

app.config["MYSQL_USER"] = "ahdoebm1"
app.config["MYSQL_PASSWORD"] = "20220303"
app.config["MYSQL_HOST"] = "SRV018.img.med.uni-tuebingen.de"
app.config["MYSQL_DB"] = "bioinf_heredivar_ahdoebm1"
app.config["MYSQL_PORT"] = 3306

mysql = MySQL(app)


def get_db_connection():
    conn = mysql.connection
    return conn


def store_variants_from_vcf(path):
    variants = VCFIO.read_variants(path)

    conn = get_db_connection()
    for variant in variants:
        chr = variant.CHROM
        pos = variant.POS
        ref = variant.REF
        alt = variant.ALT
        conn.cursor().execute("INSERT INTO variant (chr, pos, ref, alt) VALUES (%s, %s, %s, %s)",
                              (chr, pos, ref, alt))
    conn.commit()


@app.route('/')
def base():
    #store_variants_from_vcf("./data/NA12878_03_export_20220308_ahsturm1.vcf")
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
            conn = get_db_connection()
            conn.cursor().execute("INSERT INTO variant (chr, pos, ref, alt) VALUES (%s, %s, %s, %s)",
                         (chr, pos, ref, alt))
            conn.commit()
            return redirect(url_for('create'))

    return render_template('create.html', chrs=chrs)


if __name__ == '__main__':
    app.run(debug=True)
