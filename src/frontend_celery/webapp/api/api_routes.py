import json
import os
import sys
import requests
from flask import url_for, session, request, Blueprint, current_app
from flask import render_template, redirect, jsonify
from flask_session import Session
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from ..utils import *
from . import api_functions

api_blueprint = Blueprint(
    'api',
    __name__
)


@api_blueprint.route('/api/v1.0/get/consensus_classification', methods=['GET'])
@accept_token
def consensus_classification():
    
    conn = Connection(roles = ["read_only"])

    variant_id = request.args.get('variant_id')
    if variant_id is None:
        chrom = request.args.get('chrom')
        pos = request.args.get('pos')
        ref = request.args.get('ref')
        alt = request.args.get('alt')

        variant_id = conn.get_variant_id(chrom, pos, ref, alt)

    if variant_id is None:
        conn.close()
        abort(404, "Requested variant does not exist or missing variant information")

    variant = conn.get_variant(variant_id, include_annotations = False, include_consensus = True, include_user_classifications = False, include_heredicare_classifications=False, include_automatic_classification=False, include_clinvar=False, include_consequences=False, include_assays=False, include_literature=False, include_external_ids=False)
    conn.close()

    v_res = api_functions.prepare_variant(variant)
    mrcc = variant.get_recent_consensus_classification()
    mrcc_res = api_functions.prepare_classification(mrcc)

    result = {
        "variant": v_res,
        "classification": mrcc_res
    }

    return jsonify(result)







