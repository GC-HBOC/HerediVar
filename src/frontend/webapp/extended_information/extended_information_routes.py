from flask import Blueprint, render_template, abort, current_app, send_from_directory
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
from ..utils import require_login


extended_information_blueprint = Blueprint(
    'extended_information',
    __name__
)

@extended_information_blueprint.route('/gene/<int:gene_id>')
@require_login
def gene(gene_id):
    conn = Connection()
    gene_info = conn.get_gene(gene_id)
    transcripts = conn.get_transcripts(gene_id) # 0gene_id,1name,2biotype,3length,4is_gencode_basic,5is_mane_select,6is_mane_plus_clinical,7is_ensembl_canonical,8total_flags
    conn.close()
    return render_template('extended_information/gene.html', gene_info=gene_info, transcripts=transcripts)