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
from webapp import tasks
from webapp.variant import variant_functions

api_blueprint = Blueprint(
    'api',
    __name__
)


@api_blueprint.route('/api/v1.0/get/consensus_classification', methods=['GET'])
@require_api_token_permission(["read_only"])
def consensus_classification():
    
    conn = get_connection() #Connection(roles = ["read_only"])

    variant_id = request.args.get('variant_id')
    if variant_id is None:
        chrom = request.args.get('chrom')
        pos = request.args.get('pos')
        ref = request.args.get('ref')
        alt = request.args.get('alt')

        variant_id = conn.get_variant_id(chrom, pos, ref, alt)

    if variant_id is None:
        abort(404, "Requested variant does not exist or missing variant information")

    variant = conn.get_variant(variant_id, include_annotations = False, include_consensus = True, include_user_classifications = False, include_heredicare_classifications=False, include_automatic_classification=False, include_clinvar=False, include_consequences=False, include_assays=False, include_literature=False, include_external_ids=False)

    v_res = api_functions.prepare_variant(variant)
    mrcc = variant.get_recent_consensus_classification()
    mrcc_res = api_functions.prepare_classification(mrcc)

    result = {
        "variant": v_res,
        "classification": mrcc_res
    }

    return jsonify(result)



@api_blueprint.route('/api/v1.0/check_variant', methods = ['GET'])
@require_api_token_permission(["read_only"])
def check():
    variant = {
            'VID': None,
            'CHROM': None,
            'POS_HG19': None,
            'REF_HG19': None,
            'ALT_HG19': None,
            'POS_HG38': None,
            'REF_HG38': None,
            'ALT_HG38': None,
            'REFSEQ': request.args.get('transcript'),
            'CHGVS': request.args.get('hgvsc'),
            'CGCHBOC': None,
            'VISIBLE': 1,
            'GEN': request.args.get("gene"),
            'canon_chrom': '',
            'canon_pos': '',
            'canon_ref': '',
            'canon_alt': '',
            'comment': ''
    }

    genome_build = request.args.get('genome')
    if genome_build == "GRCh38":
        variant["CHROM"] = request.args.get('chrom')
        variant["POS_HG38"] = request.args.get('pos')
        variant["REF_HG38"] = request.args.get('ref')
        variant["ALT_HG38"] = request.args.get('alt')
    elif genome_build == "GRCh37":
        variant["CHROM"] = request.args.get('chrom')
        variant["POS_HG19"] = request.args.get('pos')
        variant["REF_HG19"] = request.args.get('ref')
        variant["ALT_HG19"] = request.args.get('alt')

    conn = get_connection() #  Connection(roles = ["read_only"])
    status, message = tasks.map_hg38(variant, -1, conn, insert_variant = False, perform_annotation = False, external_ids = None)

    result = {
        "status": status,
        "message": message
    }
    return jsonify(result)




@api_blueprint.route('/api/v1.0/post/variant', methods = ['POST'])
@require_api_token_permission(["user"])
def insert_variant():
    conn = get_connection()

    user = conn.parse_raw_user(conn.get_user(session["user"]["user_id"]))
    create_result, do_redirect = variant_functions.create_variant_from_request(request, user, conn)

    return jsonify(create_result)



