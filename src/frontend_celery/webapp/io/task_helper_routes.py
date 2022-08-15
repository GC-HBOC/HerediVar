from turtle import down
from flask import Blueprint, abort, current_app, send_from_directory, send_file, request, flash, redirect, url_for, session, jsonify, Markup
from os import path
import sys

from ..utils import require_login, start_annotation_service
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import io
import datetime
import tempfile
from shutil import copyfileobj
import re



task_helper_blueprint = Blueprint(
    'task_helper',
    __name__
)



import celery_module


# this route listens on the GET parameter: annotation_queue_id or variant_id
@task_helper_blueprint.route('/task/run_annotation_service', methods=['POST'])
@require_login
def run_annotation_service():
    annotation_queue_id = request.args.get('annotation_queue_id')
    variant_id = request.args.get('variant_id')
    if (annotation_queue_id is None and variant_id is None) or (annotation_queue_id is not None and variant_id is not None):
        abort(404)
    celery_task_id = start_annotation_service(variant_id=variant_id, annotation_queue_id=annotation_queue_id)
    return jsonify({}), 202, {'annotation_status_url': url_for('task_helper.annotation_status', task_id=celery_task_id)}





@task_helper_blueprint.route('/task/annotation_status/<task_id>')
@require_login
def annotation_status(task_id):
    task = celery_module.annotate_variant.AsyncResult(task_id)

    if task.state != 'FAILURE':
        response = {
            'state': task.state,
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)