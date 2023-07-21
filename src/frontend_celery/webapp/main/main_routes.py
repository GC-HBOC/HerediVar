from flask import Blueprint, render_template
from ..utils import *

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/webapp/main/static'
)


@main_blueprint.route('/')
def index():
    conn = get_connection()
    annotation_stati, errors, warnings, total_num_variants = conn.get_annotation_statistics()
    database_info = conn.get_database_info()
    total_num_classified_variants = conn.get_number_of_classified_variants()
    return render_template('index.html', total_num_variants = total_num_variants, database_info = database_info, total_num_classified_variants = total_num_classified_variants)