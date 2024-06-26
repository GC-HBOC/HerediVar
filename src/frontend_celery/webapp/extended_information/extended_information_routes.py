from flask import Blueprint, render_template, abort, current_app, send_from_directory, request
from ..utils import require_login, require_permission, get_connection


extended_information_blueprint = Blueprint(
    'extended_information',
    __name__
)

@extended_information_blueprint.route('/gene/<int:gene_id>')
@require_permission(['read_resources'])
def gene(gene_id):
    conn = get_connection()
    gene_info = conn.get_gene(gene_id)
    transcripts = conn.get_transcripts(gene_id) # 0gene_id,1name,2biotype,3length,4is_gencode_basic,5is_mane_select,6is_mane_plus_clinical,7is_ensembl_canonical,8total_flags
    return render_template('extended_information/gene.html', gene_info=gene_info, transcripts=transcripts)


@extended_information_blueprint.route('/vid')
@require_permission(['admin_resources'])
def vid():
    vid = request.args.get('vid')
    if vid is None:
        abort(404)
    heredicare_variant = current_app.extensions['heredicare'].get_variant(vid)
    return heredicare_variant



