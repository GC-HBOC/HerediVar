from flask import Blueprint, render_template

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/webapp/main/static'
)


@main_blueprint.route('/')
def index():
    return render_template('index.html')