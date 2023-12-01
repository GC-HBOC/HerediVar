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

def get_all_links(html_data):
    links = re.findall(r'href="(http.*?)"[ |>]', html_data)
    return links


def test_clinvar_submission(test_client):
    """
    This submitts a variant to the clinvar test api
    """
    variant_id = 15

    ##### standard get #####
    response = test_client.get(url_for("variant_io.submit_clinvar", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    links = get_all_links(data)
    for link in links:
        response = requests.get(link)
        assert response.status_code == 200
    
    ##### successul upload to clinvar #####
    response = test_client.post(
        url_for("variant_io.submit_clinvar", variant_id=variant_id),
        data={
            "orpha_code": "145",
            "orpha_name": "Hereditary breast and ovarian cancer syndrome",
            "gene": "BARD1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "ERROR" not in data
    assert "WARNING" not in data


    ##### too quickly submitted again #####
    response = test_client.post(
        url_for("variant_io.submit_clinvar", variant_id=variant_id),
        data={
            "orpha_code": "145",
            "orpha_name": "Hereditary breast and ovarian cancer syndrome",
            "gene": "BARD1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200


    #print(functions.find_between(data, '<!-- messages -->', '<!-- messages end -->'))
    assert "Please wait for ClinVar to finish processing it before submitting making changes to it." in data

    
    ##### Variant does not have a consensus classification
    variant_id = 71
    response = test_client.get(url_for("variant_io.submit_clinvar", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "There is no consensus classification for this variant! Please create one before submitting to ClinVar!" in data






def test_export_variant_to_vcf(test_client):
    """
    This does a variant to vcf export and checks if the output is equal to a vcf file which was generated before
    """
    variant_id = 15
    response = test_client.get(url_for("download.variant", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Error during VCF Check" not in data


    variant_id = 52
    response = test_client.get(url_for("download.variant", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Error during VCF Check" not in data

    with open(test_data_dir + '/variant_52.vcf', 'r') as f1:
        vcf_variant_52 = StringIO(f1.read())
    vcf_variant_52.seek(0)
    
    compare_vcf(vcf_variant_52, data)



def compare_vcf(reference_file, vcf_string):
    for line in reference_file:
        line = line.strip()
        if line == '':
            continue
        if line.startswith('#'): 
            if not line.startswith('##fileDate'): # skip the filedate header line because this one changes daily, but the test data is not updated daily
                assert line in vcf_string # test that header line is there
            continue

        parts = line.split('\t')
        info = parts[7]

        assert info[0:7].join('\t') in vcf_string # test that variant is there

        for info_entry in info.split(';'):
            if 'consequences' in info_entry:
                for consequence in info_entry.strip('consequences=').split('&'):
                    assert consequence in vcf_string
            else:
                if (info_entry not in vcf_string):
                    print(info_entry)
                    print(vcf_string)
                assert info_entry.strip() in vcf_string # test that info is there


def test_submit_assay(test_client):
    """
    This tests if the submission of assays works properly
    """
    variant_id = 168

    response = test_client.get(url_for("variant_io.submit_assay", variant_id=variant_id),follow_redirects=True)

    assert response.status_code == 200

    reference_assay = BytesIO(open(test_data_dir + "/test_assay.pdf", "rb").read())
    response = test_client.post(
        url_for("variant_io.submit_assay", variant_id=variant_id),
        data={
            "assay_type": "functional",
            "report": (reference_assay, 'test_assay.pdf'),
            "score": "1234"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))


    assert 'All fields are required!' not in data
    assert response.status_code == 200
    assert "Successfully uploaded a new assay" in data


    conn = Connection(['super_user'])
    all_assays = conn.get_assays(variant_id)
    assert len(all_assays) == 1

    b_64_assay = conn.get_assay_report(all_assays[0][0])[0]
    #functions.base64_to_file(assay[0], path = test_data_dir + '/test_assay_downloaded.pdf')
    b_64_assay_test = functions.get_base64_encoding(test_data_dir + "/test_assay.pdf")
    #assert open(test_data_dir + "/test_assay_downloaded.pdf", "rb").read() == open(test_data_dir + "/test_assay.pdf", "rb").read()
    b_64_assay == b_64_assay_test
    conn.close()