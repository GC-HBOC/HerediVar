from flask import Blueprint, render_template, abort, current_app, request
from ..utils import *
from common.heredicare_interface import Heredicare


extended_information_blueprint = Blueprint(
    'extended_information',
    __name__
)

@extended_information_blueprint.route('/gene/<int:gene_id>')
@require_permission(['read_resources'])
def gene(gene_id):
    conn = get_connection()
    require_valid(gene_id, "gene", conn)
    gene_info = conn.get_gene(gene_id)
    transcripts = conn.get_transcripts(gene_id) # 0gene_id,1name,2biotype,3length,4is_gencode_basic,5is_mane_select,6is_mane_plus_clinical,7is_ensembl_canonical,8total_flags
    return render_template('extended_information/gene.html', gene_info=gene_info, transcripts=transcripts)


# return variant information from heredicare
# this is more a utility and should only be used to debug
@extended_information_blueprint.route('/vid')
@require_permission(['admin_resources'])
def vid():
    vid = request.args.get('vid')
    require_set(vid)
    heredicare_interface = Heredicare()
    heredicare_variant = heredicare_interface.get_variant(vid)
    return heredicare_variant



