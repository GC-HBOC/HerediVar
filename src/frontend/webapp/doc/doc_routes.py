from flask import Blueprint, render_template, request
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from ..utils import require_login

doc_blueprint = Blueprint(
    'doc',
    __name__
)

# static info pages
@doc_blueprint.route('/help/search')
@require_login
def search_help():
    return render_template('doc/search_help.html')


@doc_blueprint.route('/deleted_variant_info')
@require_login
def deleted_variant():
    return render_template('doc/deleted_variant.html')

