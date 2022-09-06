
from flask import request, url_for, session, current_app
from urllib.parse import urlparse
import requests
import html
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from common.db_IO import Connection
import re
from webapp.variant.variant_routes import add_scheme_classes, prepare_scheme_criteria

def test_login(test_client):
    response = test_client.get(url_for('auth.login'))


    assert 'tokenResponse' in session
    assert 'user' in session
    assert 'user_id' in session['user']


def test_create(test_client):
    """
    DOCSTRING
    """
    #response = test_client.get("/login", follow_redirects=False)
    #print(response.request.path)
    #print(session['tokenResponse'])
    #print(session['user'])

    # check access
    response = test_client.get(url_for("variant.create"), follow_redirects=True)
    #print(response)
    #print(session['tokenResponse'])
    #print(response.data)
    #print(response.status_code)

    assert response.status_code == 200
    

def test_browse(test_client):
    """
    This tests if the browse variant table works properly
    """
    response = test_client.get(url_for("variant.search"), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    print(data)
    assert response.status_code == 200
    assert 'id="variantTable"' in data
    assert data.count('name="variant_row"') == 7 # always +1 because there are duplicated rows which are merged with js
    assert 'data-href="' + url_for('variant.display', variant_id="15") + '"' in data # make sure link was built correctly
    assert 'c.1972C>T' in data # make sure mane select hgvs is displayed
    assert 'p.Arg658Cys' in data
    assert 'variant_id="15"' in data # ensure that all variant ids are present, this can not handle more than 20 entries as this would result in a pagination -> extra tests??
    assert 'variant_id="52"' in data
    assert 'variant_id="71"' in data
    assert 'variant_id="72"' in data
    assert 'variant_id="139"' in data
    assert 'variant_id="130"' in data
    assert 'c.1008C>T' in data
    assert 'c.9866C>T' in data
    assert 'MUTYH' in data
    assert 'HPDL' in data
    

    # search for genes
    response = test_client.get(url_for("variant.search", genes="BARD1"))
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    # search for ranges
    response = test_client.get(url_for("variant.search", ranges="chr17:43124030-43124035"))
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="71"' in data
    
    # search for hgvs
    response = test_client.get(url_for("variant.search", hgvs="c.1972C>T"))
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    response = test_client.get(url_for("variant.search", hgvs="ENST00000613192:c.*35C>T"))
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    response = test_client.get(url_for("variant.search", hgvs="BARD1:c.*35C>T")) # not the mane select transcript
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 0

    response = test_client.get(url_for("variant.search", hgvs="BARD1:c.1972C>T")) # gene + mane select transcript works
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    response = test_client.get(url_for("variant.search", hgvs="ENST00000613192:c.*35C>T;c.1972C>T ,   ENST00000420246:c.*131C>T ")) # gene + mane select transcript works
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 2
    assert 'variant_id="15"' in data
    assert 'variant_id="72"' in data

    response = test_client.get(url_for("variant.search", hgvs="c.1972C>T ,   ENST00000420246:c.*131C>T ", genes="TP53")) # gene + mane select transcript works
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="72"' in data

    # search for consensus classifications
    response = test_client.get(url_for("variant.search", consensus=3)) # gene + mane select transcript works
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="139"' in data

    response = test_client.get(url_for("variant.search", consensus=[3,4])) # gene + mane select transcript works
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 2
    assert 'variant_id="15"' in data
    assert 'variant_id="139"' in data

        

def test_variant_display(test_client):
    """
    This checks the completeness of the variant display page. All information must be shown somewhere
    """
    variant_id = 15
    response = test_client.get(url_for("variant.display", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    #print(data)
    assert response.status_code == 200
    assert "chr2-214730440-G-A (GRCh38)" in data


    conn = Connection()
    annotations = conn.get_all_variant_annotations(variant_id, group_output=True)
    if annotations.get('consensus_scheme_classifications', None) is not None:
        annotations['consensus_scheme_classifications'] = add_scheme_classes(annotations['consensus_scheme_classifications'], 10)
        annotations['consensus_scheme_classifications'] = prepare_scheme_criteria(annotations['consensus_scheme_classifications'], 10)

    if annotations.get('user_scheme_classifications', None) is not None:
        annotations['user_scheme_classifications'] = add_scheme_classes(annotations['user_scheme_classifications'], 9)
        annotations['user_scheme_classifications'] = prepare_scheme_criteria(annotations['user_scheme_classifications'], 9)
    conn.close()

    all_anntation_ids_raw = re.findall(r'annotation_id="((\d*;?)*)"', data)
    print(all_anntation_ids_raw)
    all_annotation_ids = []
    for ids in all_anntation_ids_raw:
        ids = ids[0].strip(' ').strip(';').split(';')
        all_annotation_ids.extend(ids)
    print(all_annotation_ids)

    for key in annotations:
        if key == 'standard_annotations':
            for group in annotations['standard_annotations']:
                for annotation in annotations['standard_annotations'][group]:
                    value = str(annotations['standard_annotations'][group][annotation][-1])
                    assert value in all_annotation_ids

        if key == 'clinvar_submissions':
            for submission in annotations['clinvar_submissions']:
                assert 'clinvar_id="' + str(submission[0]) + '"' in data
        
        if key == 'variant_consequences':
            for consequence in annotations['variant_consequences']:
                assert consequence[0] in data
            
        if key == 'literature':
            for paper in annotations['literature']:
                assert "PMID:" + str(paper[2]) in data

        if key == 'assays':
            for assay in annotations['assays']:
                assert 'assay_id="' + str(assay[0]) in data

        if key == 'consensus_classification':
            assert 'consensus_classification_id="' + str(annotations['consensus_classification'][0]) + '"' in data
        
        if key == 'user_classifications':
            for user_classification in annotations['user_classifications']:
                assert 'user_classification_id="' + str(user_classification[0]) + '"' in data
            
        if key == 'consensus_scheme_classifications':
            for classification in annotations['consensus_scheme_classifications']:
                print(classification)
                assert 'consensus_scheme_classification_id="' + str(classification[0]) in data
                for scheme_criterium in classification[9]:
                    assert 'consensus_scheme_classification_id="' + str(scheme_criterium[0]) in data

        if key == 'user_scheme_classifications':
            for classification in annotations['user_scheme_classifications']:
                assert 'user_scheme_classification_id="' + str(classification[0]) in data
                print(classification)
                for scheme_criterium in classification[9]:
                    assert 'selected_scheme_criterium_id="' + str(scheme_criterium[0]) in data

            
        if key == 'heredicare_center_classifications':
            for classification in annotations['heredicare_center_classifications']:
                assert 'heredicare_center_classification_id="' + str(classification[0]) + '"' in data

    assert response.status_code == 30285


def test_variant_history(test_client):
    """
    This tests the completeness of the variant history page
    """
    pass


def test_classify(test_client):
    """
    This classifies a variant using different schema & checks the consensus classification evidence document
    """
    pass

def test_acmg_classification_calculation(test_client):
    """
    This tests if the class returned by the acmg endpoint is correct
    """
    pass

def test_export_variant_to_vcf(test_client):
    """
    This does a variant to vcf export and checks if the output is equal to a vcf file which was generated before
    """
    pass

def test_user_lists(test_client):
    """
    This first creates a new user list for the testuser and subsequentially adds variants, deletes, renames and searches them
    """
    pass

def test_submit_assay(test_client):
    """
    This testsif the submission of assays works properly
    """
    pass