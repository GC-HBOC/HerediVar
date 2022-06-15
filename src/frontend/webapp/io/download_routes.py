from flask import Blueprint, render_template, abort, current_app, send_from_directory
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection

download_blueprint = Blueprint(
    'download',
    __name__
)

# downloads
@download_blueprint.route('/download_evidence_document/<int:variant_id>')
def evidence_document(variant_id):
    conn = Connection()
    consensus_classification = conn.get_consensus_classification(variant_id, most_recent=True)
    conn.close()
    if consensus_classification is None:
        abort(404)
    consensus_classification = consensus_classification[0]
    b_64_report = consensus_classification[5]

    report_folder = path.join(path.dirname(current_app.root_path), current_app.config['CONSENSUS_CLASSIFICATION_REPORT_FOLDER'])
    report_filename = 'consensus_classification_report_' + str(variant_id) + '.pdf'
    report_path = path.join(report_folder, report_filename)
    if not path.isfile(report_path):
        functions.base64_to_file(base64_string = b_64_report, path = report_path)
    
    return send_from_directory(directory=report_folder, path='', filename=report_filename)


@download_blueprint.route('/import-variants/summary/download?file=<string:log_file>')
def log_file(log_file):
    logs_folder = path.join(path.dirname(current_app.root_path), current_app.config['LOGS_FOLDER'])
    return send_from_directory(directory=logs_folder, path='', filename=log_file) 