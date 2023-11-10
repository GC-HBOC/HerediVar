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
    total_num_variants = conn.get_number_of_variants()
    annotation_types = conn.get_annotation_types()
    total_num_classified_variants = conn.get_number_of_classified_variants()
    return render_template('index.html', total_num_variants = total_num_variants, annotation_types = annotation_types, total_num_classified_variants = total_num_classified_variants)



@main_blueprint.route('/downloads')
@require_permission(['read_resources'])
def downloads():    
    return render_template("main/downloads.html")




