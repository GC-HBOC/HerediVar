from flask import request, url_for, session, current_app
from urllib.parse import urlparse
import requests
import html
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from common.db_IO import Connection
import re
from io import StringIO, BytesIO
import common.functions as functions
import time

basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data_dir = basepath + "/data"



def issue_acmg_endpoint(test_client, scheme_type, version, classes):
    response = test_client.get(url_for("download.calculate_class", scheme_type=scheme_type, version=version, selected_classes=classes))
    data = response.get_json()
    assert response.status_code == 200
    return data['final_class']



def test_acmg_classification_calculation(test_client):
    """
    This tests that the class returned by the acmg endpoint is correct
    """

    scheme_type = 'acmg'
    version = 'v1.0.0'

    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pvs1+ps1') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pvs1+pm1+pm4') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pvs1+pm1+pp5') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pvs1+pp1+pp3+pp5') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps1+ps3+ps4') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps1+pm1+pm2+pm3') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps2+pm2+pm4+pp1+pp3') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps3+pm6+pp1+pp2+pp3+pp4') == 5

    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pvs1+pm2') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps4+pm1') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps4+pm1+pm2') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ps4+pp1+pp3+pp4') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pm1+pm2+pm4+pm6') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pm1+pm2+pp1+pp2') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pm6+pp1+pp2+pp3+pp4+pp5') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'pm1+pp1+pp2+pp4+pp3') == 4
    
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'ba1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'bs1+bs3') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'bs1+bs2+bp1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'bs1+bs2+bp1+bp2') == 1

    assert issue_acmg_endpoint(test_client, scheme_type, version, 'bs1+bp1') == 2
    assert issue_acmg_endpoint(test_client, scheme_type, version, 'bp1+bp4') == 2

    assert issue_acmg_endpoint(test_client, scheme_type, version, 'bp1+bp4+pvs1+pm2') == 3




def test_task_force_classification_calculation(test_client):
    """
    This tests that the class returned by the task-force class calculation endpoint is correct
    """

    scheme_type = 'task-force'
    version = 'v1.0.0'

    assert issue_acmg_endpoint(test_client, scheme_type, version, '1.1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, version, '1.1+2.1') == 1

    assert issue_acmg_endpoint(test_client, scheme_type, version, '2.1') == 2
    assert issue_acmg_endpoint(test_client, scheme_type, version, '2.1+5.1') == 2


    assert issue_acmg_endpoint(test_client, scheme_type, version, '5.1') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, '5.2+5.6') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, version, '5.2+5.6+4.3') == 5

    assert issue_acmg_endpoint(test_client, scheme_type, version, '1.2') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, version, '1.2+1.1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, version, '1.2+1.1+2.2') == 1

    assert issue_acmg_endpoint(test_client, scheme_type, version, '2.5') == 2
    assert issue_acmg_endpoint(test_client, scheme_type, version, '2.5+2.2') == 2

    assert issue_acmg_endpoint(test_client, scheme_type, version, '4.1') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, version, '4.2+3.3') == 4

    assert issue_acmg_endpoint(test_client, scheme_type, version, '3.4') == 3