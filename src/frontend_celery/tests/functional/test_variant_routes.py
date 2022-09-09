
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
from io import StringIO, BytesIO
import common.functions as functions

basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data_dir = basepath + "/data"


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
    #print(data)
    assert response.status_code == 200
    assert 'id="variantTable"' in data
    assert data.count('name="variant_row"') == 8 # always +1 because there are duplicated rows which are merged with js
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
    response = test_client.get(url_for("variant.search", consensus=3))
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="139"' in data

    response = test_client.get(url_for("variant.search", consensus=[3,4]))
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

    ##### test that all data is there #####
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
    #print(all_anntation_ids_raw)
    all_annotation_ids = []
    for ids in all_anntation_ids_raw:
        ids = ids[0].strip(' ').strip(';').split(';')
        all_annotation_ids.extend(ids)
    #print(all_annotation_ids)

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
                assert 'consensus_scheme_classification_id="' + str(classification[0]) in data
                for scheme_criterium in classification[9]:
                    assert 'consensus_scheme_classification_id="' + str(scheme_criterium[0]) in data

        if key == 'user_scheme_classifications':
            for classification in annotations['user_scheme_classifications']:
                assert 'user_scheme_classification_id="' + str(classification[0]) in data
                for scheme_criterium in classification[9]:
                    assert 'selected_scheme_criterium_id="' + str(scheme_criterium[0]) in data

            
        if key == 'heredicare_center_classifications':
            for classification in annotations['heredicare_center_classifications']:
                assert 'heredicare_center_classification_id="' + str(classification[0]) + '"' in data

    ##### test that links are built properly #####
    assert url_for('variant_io.submit_assay', variant_id=variant_id) in data
    assert url_for('variant.classify', variant_id=variant_id) in data
    assert url_for('download.variant', variant_id=variant_id) in data
    assert url_for('variant_io.submit_clinvar', variant_id=variant_id) in data

    links = get_all_links(data)
    for link in links:
        print(link)
        if 'cosmic' not in link:
            response = requests.get(link)
            assert response.status_code == 200
    #check cosmic:
    link = 'https://cancer.sanger.ac.uk/cosmic/search?q=BARD1+c.1972C>T'
    response = requests.get(link)
    assert response.status_code == 200



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

    ##### Incorrect orphanet #####
    response = test_client.post(
        url_for("variant_io.submit_clinvar", variant_id=variant_id),
        data={
            "condition": "This is not an orphanet code",
            "gene": "BARD1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "The selected condition contains errors. It MUST be one of the provided autocomplete values." in data
    
    ##### successul upload to clinvar #####
    response = test_client.post(
        url_for("variant_io.submit_clinvar", variant_id=variant_id),
        data={
            "condition": "Hereditary breast and ovarian cancer syndrome: 145",
            "gene": "BARD1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert request.endpoint == 'variant.display'
    assert "ERROR" not in data
    assert "WARNING" not in data


    ##### too quickly submitted again #####
    response = test_client.post(
        url_for("variant_io.submit_clinvar", variant_id=variant_id),
        data={
            "condition": "Hereditary breast and ovarian cancer syndrome: 145",
            "gene": "BARD1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert request.endpoint == 'variant.display'
    assert "Please wait until it is finished before making updates to the previous one." in data

    
    ##### Variant does not have a consensus classification
    variant_id = 71
    response = test_client.get(url_for("variant_io.submit_clinvar", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert request.endpoint == 'variant.display'
    assert "There is no consensus classification for this variant! Please create one before submitting to ClinVar!" in data




def test_variant_history(test_client):
    """
    This tests the completeness of the variant history page
    """
    ##### check completeness #####
    variant_id = 15

    response = test_client.get(url_for("variant.classification_history", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    conn = Connection()
    consensus_classifications = conn.get_consensus_classification(variant_id, sql_modifier=conn.add_userinfo)
    user_classifications = conn.get_user_classifications(variant_id)
    user_scheme_classifications = conn.get_user_scheme_classification(variant_id, sql_modifier=conn.add_userinfo)
    consensus_scheme_classifications = conn.get_consensus_scheme_classification(variant_id, scheme = 'all', most_recent = False, sql_modifier=conn.add_userinfo)
    conn.close()

    # this could be improved by making custom html attributes saving the type & id of the classification 
    if consensus_classifications is not None:
        assert data.count('consensus classification') == len(consensus_classifications) + 2 # add two because this string is also in the caption and the legend
    
    if user_classifications is not None:
        assert data.count('user_classifications') == len(user_classifications) + 1 # also contained i nthe legend
    
    if user_scheme_classifications is not None:
        assert data.count('user scheme classification') == len(user_scheme_classifications) + 1 
    
    if consensus_scheme_classifications is not None:
        assert data.count('consensus scheme classification') == len(consensus_scheme_classifications) + 1
    




def test_classify(test_client):
    """
    This classifies a variant using different schema & checks the consensus classification evidence document
    """
    ##### test access to the classify page #####
    variant_id = 15
    response = test_client.get(url_for("variant.classify", variant_id=variant_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    ##### post a new user classification #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "1",
            'comment': "This is a test comment.",
            'ps1': "Evidence for ps1 given in this field",
            'ps2': "Evidence for ps2 given in this field",
            'ps1_strength': "ps",
            'ps2_strength': "ps",
            'scheme': "acmg_standard"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted/updated classification based on classification scheme" in data
    assert "Successfully inserted new user classification" in data

    ##### test posting invalid data #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "1",
            'comment': "This is a test comment.",
            'pp1': "Evidence for pp1 given in this field",
            'bs4': "Evidence for bs4 given in this field", # mutually exclusive to pp1
            'pp1_strength': "ps",
            'bs4_strength': "bs",
            'scheme': "acmg_standard"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "There are criteria which are mutually exclusive" in data

    assert "It appears that you already have a classification for this variant. You can edit it here." in data


    ##### test posting none as classification scheme #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update.",
            'pp1': "Evidence for pp1 given in this field", # this should be ignored
            'pp1_strength': "ps", # this should be ignored
            'scheme': "none"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted/updated classification based on classification scheme" not in data
    assert "It appears that you already have a classification for this variant. You can edit it here." in data
    assert "Successfully updated user classification" in data

    ##### test posting invalid strength #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update 2.",
            'pp1': "Evidence for pp1 given in this field", 
            'pp1_strength': "ba", 
            'scheme': "acmg_standard"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted/updated classification based on classification scheme" not in data
    assert "It appears that you already have a classification for this variant. You can edit it here." in data
    assert "Successfully updated user classification" not in data
    assert "There are criteria with strengths that can not be selected" not in data


    ##### test posting criteria which can not be selected #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update 2.",
            'pm3': "Evidence for pm3 given in this field", # forbidden for amg tp53
            'pm3_strength': "pm", 
            'scheme': "acmg_TP53"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted/updated classification based on classification scheme" not in data
    assert "It appears that you already have a classification for this variant. You can edit it here." in data
    assert "Successfully updated user classification" not in data
    assert "There are criteria which can not be activated with the provided scheme (TP_53)" not in data

    ##### test inserting a new task force classification #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update 2.",
            '4.4': "Evidence for 4.4 given in this field",
            '4.4_strength': "ps", 
            'scheme': "task-force"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted/updated classification based on classification scheme" in data
    assert "It appears that you already have a classification for this variant. You can edit it here." in data


    # test that data was saved correctly to db
    conn = Connection()
    user_scheme_classifications = conn.get_user_scheme_classification(15, 3)
    conn.close()
    assert len(user_scheme_classifications) == 5
    


def test_acmg_classification_calculation(test_client):
    """
    This tests that the class returned by the acmg endpoint is correct
    """

    scheme = 'acmg_standard'

    assert issue_acmg_endpoint(test_client, scheme, 'pvs1+ps1') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'pvs1+pm1+pm4') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'pvs1+pm1+pp5') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'pvs1+pp1+pp3+pp5') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'ps1+ps3+ps4') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'ps1+pm1+pm2+pm3') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'ps2+pm2+pm4+pp1+pp3') == 5
    assert issue_acmg_endpoint(test_client, scheme, 'ps3+pm6+pp1+pp2+pp3+pp4') == 5

    assert issue_acmg_endpoint(test_client, scheme, 'pvs1+pm2') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'ps4+pm1') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'ps4+pm1+pm2') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'ps4+pp1+pp3+pp4') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'pm1+pm2+pm4+pm6') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'pm1+pm2+pp1+pp2') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'pm6+pp1+pp2+pp3+pp4+pp5') == 4
    assert issue_acmg_endpoint(test_client, scheme, 'pm1+pp1+pp2+pp4+pp3') == 4
    
    assert issue_acmg_endpoint(test_client, scheme, 'ba1') == 1
    assert issue_acmg_endpoint(test_client, scheme, 'bs1+bs3') == 1
    assert issue_acmg_endpoint(test_client, scheme, 'bs1+bs2+bp1') == 1
    assert issue_acmg_endpoint(test_client, scheme, 'bs1+bs2+bp1+bp2') == 1

    assert issue_acmg_endpoint(test_client, scheme, 'bs1+bp1') == 2
    assert issue_acmg_endpoint(test_client, scheme, 'bp1+bp4') == 2

    assert issue_acmg_endpoint(test_client, scheme, 'bp1+bp4+pvs1+pm2') == 3


def issue_acmg_endpoint(test_client, scheme, classes):
    response = test_client.get(url_for("download.calculate_class", scheme=scheme, selected_classes=classes))
    data = response.get_json()
    assert response.status_code == 200
    return data['final_class']

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

    
    with open(test_data_dir + '/variant_52.vcf', 'r') as img1:
        vcf_variant_52 = StringIO(img1.read())
    vcf_variant_52.seek(0)
    print(data)
    
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
            #print(info_entry)
            if 'consequences' in info_entry:
                for consequence in info_entry.strip('consequences=').split('&'):
                    assert consequence in vcf_string
            else:
                assert info_entry.strip() in vcf_string # test that info is there


def test_user_lists(test_client):
    """
    This first creates a new user list for the testuser and subsequentially adds variants, deletes, renames and searches them
    """
    
    ##### test that endpoint is reachable & no lists contained #####
    response = test_client.get(url_for("user.my_lists"), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'name="user_list_row"' not in data
    assert 'Please select a list to view its content!' in data


    ##### create a new list #####
    response = test_client.post(
        url_for("user.my_lists", type='create'), 
        data={
            "list_name": "first list"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully created new list' in data


    conn = Connection()

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 1
    list_id = user_lists[0][0]

    conn.close()


    ##### add variants to the list #####
    variant_id = 52
    response = test_client.post(
        url_for("variant.display", variant_id=variant_id, action='add_to_list'),
        data={
            "add-to-list": list_id
        }, 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    variant_id = 130
    response = test_client.post(
        url_for("variant.display", variant_id=variant_id, action='add_to_list'),
        data={
            "add-to-list": list_id
        }, 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    ##### test that the variants are in the list #####
    conn = Connection()

    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 2
    assert '52' in variants_in_list
    assert '130' in variants_in_list

    conn.close()

    ##### test showing the list #####
    response = test_client.get(url_for("user.my_lists", view=list_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 200
    assert data.count('variant_id="') == 4
    # these variants occur twice as they have two mane select transcripts -> these rows are merged by javascript which can not be tested here
    assert data.count('variant_id="52"') == 2 
    assert data.count('variant_id="130"') == 2

    ##### test searching the list #####
    response = test_client.get(url_for("user.my_lists", view=list_id, genes='BRCA2'), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 200
    assert data.count('variant_id="') == 2
    assert data.count('variant_id="52"') == 2

    ##### test renaming the list #####
    response = test_client.post(
        url_for("user.my_lists", type='edit'), 
        data={
            "list_name": "first list update",
            "list_id": list_id
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully changed list name' in data
    
    conn = Connection()

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 1
    assert user_lists[0][2] == "first list update"

    conn.close()


    ##### test deleting variants from the list #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=18, variant_id=130), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed variant from list!' in data

    conn = Connection()

    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 1
    assert '52' in variants_in_list

    conn.close()
    
    ##### test deleting the list #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_list'), 
        data={
            "list_id": list_id
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed list' in data

    conn = Connection()

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 0

    conn.close()


    ##### test accessing the list from another user #####
    response = test_client.get(url_for("user.my_lists", view=8), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 403






def test_submit_assay(test_client):
    """
    This tests if the submission of assays works properly
    """
    variant_id = 15

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


    conn = Connection()
    all_assays = conn.get_assays(variant_id)
    assert len(all_assays) == 1

    assay = conn.get_assay_report(all_assays[0][0])
    functions.base64_to_file(assay[0], path = test_data_dir + '/test_assay_downloaded.pdf')
    assert open(test_data_dir + "/test_assay_downloaded.pdf", "rb").read() == open(test_data_dir + "/test_assay.pdf", "rb").read()
    conn.close()

    



def get_all_links(html_data):
    links = re.findall(r'href="(http.*?)"[ |>]', html_data)
    return links