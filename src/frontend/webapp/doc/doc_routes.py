from flask import Blueprint, render_template, request
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection

doc_blueprint = Blueprint(
    'doc',
    __name__
)

# static info pages
@doc_blueprint.route('/help/search')
def search_help():
    return render_template('doc/search_help.html')


@doc_blueprint.route('/deleted_variant_info')
def deleted_variant():
    return render_template('doc/deleted_variant.html')


@doc_blueprint.route('/html_error')
def error():
    code = request.args.get('code', '0')
    text = request.args.get('text', 'missing description')
    return render_template('doc/html_error.html', code=code, text=text)