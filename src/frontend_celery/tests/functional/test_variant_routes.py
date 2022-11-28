
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
import time

basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data_dir = basepath + "/data"


def test_login(test_client):
    response = test_client.get(url_for('auth.login'))


    assert 'tokenResponse' in session
    assert 'user' in session
    assert 'user_id' in session['user']
    


def test_browse(test_client):
    """
    This tests if the browse variant table works properly
    """
    response = test_client.get(url_for("variant.search"), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    #print(data)
    assert response.status_code == 200
    assert 'id="variantTable"' in data
    assert data.count('name="variant_row"') == 12 # always +1 because there are duplicated rows which are merged with js
    assert 'data-href="' + url_for('variant.display', variant_id="15") + '"' in data # make sure link was built correctly
    assert 'c.1972C>T' in data # make sure mane select hgvs is displayed
    assert 'p.Arg658Cys' in data
    assert 'variant_id="15"' in data # ensure that all variant ids are present, this can not handle more than 20 entries as this would result in a pagination -> extra tests??
    assert 'variant_id="52"' in data
    assert 'variant_id="71"' in data
    assert 'variant_id="72"' in data
    assert 'variant_id="130"' in data
    assert 'variant_id="146"' in data
    assert 'variant_id="32"' in data
    assert 'variant_id="139"' in data
    assert 'variant_id="164"' in data
    assert 'variant_id="168"' in data
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

    response = test_client.get(url_for("variant.search", lookup_list_id=8, lookup_list_name="public read"))
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    response = test_client.get(url_for("variant.search", lookup_list_id=10, lookup_list_name="private inaccessible"))
    data = response.data.decode('utf8')
    assert response.status_code == 403


        

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
    conn = Connection(["super_user"])
    annotations = conn.get_all_variant_annotations(variant_id, group_output=True)
    if annotations.get('consensus_classification', None) is not None:
        annotations['consensus_classification'] = add_scheme_classes(annotations['consensus_classification'], 14)
        annotations['consensus_classification'] = prepare_scheme_criteria(annotations['consensus_classification'], 14)[0]

    if annotations.get('user_classifications', None) is not None:
        annotations['user_classifications'] = add_scheme_classes(annotations['user_classifications'], 13)
        annotations['user_classifications'] = prepare_scheme_criteria(annotations['user_classifications'], 13)
    conn.close()
    
    #print('\n'.join([line for line in data.split('\n') if line.strip() != '']))

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
            most_recent_consensus_classification = annotations['consensus_classification']
            assert 'consensus_classification_id="' + str(most_recent_consensus_classification[0]) + '"' in data
            current_criteria = most_recent_consensus_classification[14]
            for criterium in current_criteria:
                assert 'consensus_criterium_applied_id="' + str(criterium[0]) + '"' in data
        
        if key == 'user_classifications':
            for user_classification in annotations['user_classifications']:
                assert 'user_classification_id="' + str(user_classification[0]) + '"' in data
                current_criteria = user_classification[13]
                for criterium in current_criteria:
                    assert 'user_criterium_applied_id="' + str(criterium[0]) + '"' in data
            
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
            assert response.status_code == 200 or response.status_code == 429
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
            "orpha_code": "1234567890",
            "orpha_name": "missing_orpha_name",
            "gene": "BARD1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    print(data)
    assert response.status_code == 200
    assert "The selected orphanet id (1234567890) is not valid." in data
    
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

    print(data)

    conn = Connection(['super_user'])
    consensus_classifications = conn.get_consensus_classifications_extended(variant_id, most_recent=False)
    user_classifications = conn.get_user_classifications_extended(variant_id)
    conn.close()

    # this could be improved by making custom html attributes saving the type & id of the classification 
    if consensus_classifications is not None:
        assert data.count('consensus classification') == len(consensus_classifications) + 2 # add two because this string is also in the caption and the legend
    
    if user_classifications is not None:
        assert data.count('user classification') == len(user_classifications) + 1 # also contained in the legend

    



def test_classify(test_client):
    """
    This classifies a variant using different schema & checks the consensus classification evidence document
    """
    ##### test access to the classify page #####
    variant_id = 130
    user_id = 3
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
            'scheme': "2"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    print(data)
    assert response.status_code == 200
    assert "Successfully inserted new user classification" in data

    time.sleep(2) # this is nececssary to not have multiple classifications at the same time

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
            'scheme': "2"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "A mutually exclusive criterium to pp1 was selected." in data


    ##### test posting none as classification scheme #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update.",
            'pp1': "Evidence for pp1 given in this field", # this should be ignored
            'pp1_strength': "ps", # this should be ignored
            'scheme': "1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted new user classification" in data


    ##### test posting invalid strength #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update 2.",
            'pp1': "Evidence for pp1 given in this field", 
            'pp1_strength': "ba", 
            'scheme': "2"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
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
            'scheme': "3"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully updated user classification" not in data
    assert "There are criteria which can not be activated with the provided scheme (TP_53)" not in data

    time.sleep(2) # this is nececssary to not have multiple classifications at the same time

    ##### test inserting a new task force classification #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update 2.",
            '4.4': "Evidence for 4.4 given in this field",
            '4.4_strength': "ps", 
            'scheme': "5"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted new user classification" in data

    

    # test that data was saved correctly to db
    conn = Connection(['super_user'])
    user_scheme_classifications = conn.get_user_classifications(variant_id, 3)
    conn.close()
    assert len(user_scheme_classifications) == 3


    ##### test inserting literature passages & uddating the classification #####

    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "1",
            'comment': "This is a test comment update0",
            'ps1': "Evidence for ps1 given in this field update1",
            'ps2': "Evidence for ps2 given in this field update2",
            'ps3': "Evidence for ps3 given in this field",
            'ps1_strength': "ps",
            'ps2_strength': "ps",
            'ps3_strength': "ps",
            'scheme': "2",
            'pmid': [35205822, 33099839],
            'text_passage': ["This is a text passage...", "This is another text passage..."]
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully updated user classification" in data

    conn = Connection(['super_user'])
    classification = conn.get_user_classifications_extended(variant_id, user_id, scheme_id=2)[0]
    selected_literature = conn.get_selected_literature(is_user=True, classification_id=classification[0])
    assert len(selected_literature) == 2
    all_pmids = [str(x[2]) for x in selected_literature]
    all_text_passages = [x[3] for x in selected_literature]
    assert "35205822" in all_pmids
    assert "This is a text passage..." in all_text_passages
    assert "33099839" in all_pmids
    assert "This is another text passage..." in all_text_passages

    assert len(classification[13]) == 3
    all_criteria_evidence = [x[4] for x in classification[13]]
    assert "Evidence for ps1 given in this field update1" in all_criteria_evidence
    assert "Evidence for ps2 given in this field update2" in all_criteria_evidence
    assert "Evidence for ps3 given in this field" in all_criteria_evidence
    assert "This is a test comment update0" == classification[4]

    conn.close()
    
    






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




def test_acmg_classification_calculation(test_client):
    """
    This tests that the class returned by the acmg endpoint is correct
    """

    scheme_type = 'acmg'

    assert issue_acmg_endpoint(test_client, scheme_type, 'pvs1+ps1') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'pvs1+pm1+pm4') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'pvs1+pm1+pp5') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'pvs1+pp1+pp3+pp5') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps1+ps3+ps4') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps1+pm1+pm2+pm3') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps2+pm2+pm4+pp1+pp3') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps3+pm6+pp1+pp2+pp3+pp4') == 5

    assert issue_acmg_endpoint(test_client, scheme_type, 'pvs1+pm2') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps4+pm1') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps4+pm1+pm2') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'ps4+pp1+pp3+pp4') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'pm1+pm2+pm4+pm6') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'pm1+pm2+pp1+pp2') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'pm6+pp1+pp2+pp3+pp4+pp5') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, 'pm1+pp1+pp2+pp4+pp3') == 4
    
    assert issue_acmg_endpoint(test_client, scheme_type, 'ba1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, 'bs1+bs3') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, 'bs1+bs2+bp1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, 'bs1+bs2+bp1+bp2') == 1

    assert issue_acmg_endpoint(test_client, scheme_type, 'bs1+bp1') == 2
    assert issue_acmg_endpoint(test_client, scheme_type, 'bp1+bp4') == 2

    assert issue_acmg_endpoint(test_client, scheme_type, 'bp1+bp4+pvs1+pm2') == 3




def test_task_force_classification_calculation(test_client):
    """
    This tests that the class returned by the task-force class calculation endpoint is correct
    """

    scheme_type = 'task-force'

    assert issue_acmg_endpoint(test_client, scheme_type, '1.1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, '1.1+2.1') == 1

    assert issue_acmg_endpoint(test_client, scheme_type, '2.1') == 2
    assert issue_acmg_endpoint(test_client, scheme_type, '2.1+5.1') == 2


    assert issue_acmg_endpoint(test_client, scheme_type, '5.1') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, '5.2+5.6') == 5
    assert issue_acmg_endpoint(test_client, scheme_type, '5.2+5.6+4.3') == 5

    assert issue_acmg_endpoint(test_client, scheme_type, '1.2') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, '1.2+1.1') == 1
    assert issue_acmg_endpoint(test_client, scheme_type, '1.2+1.1+2.2') == 1

    assert issue_acmg_endpoint(test_client, scheme_type, '2.5') == 2
    assert issue_acmg_endpoint(test_client, scheme_type, '2.5+2.2') == 2

    assert issue_acmg_endpoint(test_client, scheme_type, '4.1') == 4
    assert issue_acmg_endpoint(test_client, scheme_type, '4.2+3.3') == 4

    assert issue_acmg_endpoint(test_client, scheme_type, '3.4') == 3




def issue_acmg_endpoint(test_client, scheme_type, classes):
    response = test_client.get(url_for("download.calculate_class", scheme_type=scheme_type, selected_classes=classes))
    data = response.get_json()
    assert response.status_code == 200
    return data['final_class']



def test_user_lists(test_client):
    """
    This first creates a new user list for the testuser and subsequentially adds variants, deletes, renames and searches them
    """
    
    ##### test that endpoint is reachable & no lists contained #####
    response = test_client.get(url_for("user.my_lists"), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert data.count('name="user_list_row"') == 2
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


    conn = Connection(['super_user'])

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 3
    list_id = conn.get_latest_list_id()

    conn.close()


    ##### add variants to the list #####
    variant_id = 71
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    variant_id = 72
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    ##### test that the variants are in the list #####
    conn = Connection(['super_user'])

    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 2
    assert '71' in variants_in_list
    assert '72' in variants_in_list

    conn.close()

    ##### test showing the list #####
    response = test_client.get(url_for("user.my_lists", view=list_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    print(data)
    
    assert response.status_code == 200
    assert data.count('variant_id="') == 2
    assert data.count('variant_id="71"') == 1
    assert data.count('variant_id="72"') == 1

    ##### test searching the list #####
    response = test_client.get(url_for("user.my_lists", view=list_id, genes='BRCA1'), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 200
    assert data.count('variant_id="') == 1
    assert data.count('variant_id="71"') == 1

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
    assert 'Successfully changed list settings' in data
    
    conn = Connection(['super_user'])

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 3
    assert conn.get_user_variant_list(list_id)[2] == "first list update"

    conn.close()


    ##### test deleting variants from the list #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=list_id, variant_id=71), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed variant from list!' in data

    conn = Connection(['super_user'])

    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 1
    assert '72' in variants_in_list

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

    conn = Connection(['super_user'])

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 2

    conn.close()


    ##### test accessing the private list from another user #####
    response = test_client.get(url_for("user.my_lists", view=10), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403


    ##### test accessing the public list from another user #####
    response = test_client.get(url_for("user.my_lists", view=8), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200


    ##### test accessing the public&editable list from another user #####
    response = test_client.get(url_for("user.my_lists", view=9), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 200


    ##### test deleting the public list from another user #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_list'), 
        data={
            "list_id": 9
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403

    ##### test adding variants to the public list from another user #####
    list_id = 9 # public read & edit -> should work
    variant_id = 71
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    conn = Connection(['super_user'])
    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 1
    assert '71' in variants_in_list
    conn.close()

    list_id = 8 # only public read -> should not work
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 403

    ##### test renaming & changing the permission bits a public list from another user #####
    list_id = 9
    response = test_client.post(
        url_for("user.my_lists", type='edit'), 
        data={
            "list_name": "first list update",
            "list_id": list_id
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403

    ##### test deleting variants from the public list #####
    list_id = 9 # should work
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=list_id, variant_id=71), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed variant from list!' in data

    conn = Connection(['super_user'])
    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 0
    conn.close()

    list_id = 8 # should not work
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=list_id, variant_id=52), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403


    ##### test creating a public list #####
    response = test_client.post(
        url_for("user.my_lists", type='create'), 
        data={
            "list_name": "new public list",
            "public_read": "true",
            "public_edit": "true"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully created new list' in data

    # check that the public and private bits are set correctly
    conn = Connection(['super_user'])
    public_list_id = conn.get_latest_list_id()
    list_oi = conn.get_user_variant_list(public_list_id)
    assert list_oi[3] == 1
    assert list_oi[4] == 1
    conn.close()






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


    conn = Connection(['super_user'])
    all_assays = conn.get_assays(variant_id)
    assert len(all_assays) == 1

    b_64_assay = conn.get_assay_report(all_assays[0][0])[0]
    #functions.base64_to_file(assay[0], path = test_data_dir + '/test_assay_downloaded.pdf')
    b_64_assay_test = functions.get_base64_encoding(test_data_dir + "/test_assay.pdf")
    #assert open(test_data_dir + "/test_assay_downloaded.pdf", "rb").read() == open(test_data_dir + "/test_assay.pdf", "rb").read()
    b_64_assay == b_64_assay_test
    conn.close()

    

def test_create_variant(test_client):
    """
    This creates a new variant 
    """

    response = test_client.get(url_for("variant.create"), follow_redirects=True)
    assert response.status_code == 200

    ##### create new variant successfully #####
    response = test_client.post(
        url_for("variant.create", type = "vcf"), 
        data={
            "chr": "chr1",
            "pos": "10295758",
            "ref": "G",
            "alt": "A",
            "genome": "GRCh38"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))

    print(data)

    assert response.status_code == 200
    assert "Successfully inserted variant" in data
    assert "alert-danger" not in data
    assert "ERROR" not in data

    links = get_all_links(data)
    for link in links:
        response = requests.get(link)
        assert response.status_code == 200
    

    ##### post the same one again - should be rejected #####
    response = test_client.post(
        url_for("variant.create", type = "vcf"), 
        data={
            "chr": "chr1",
            "pos": "10295758",
            "ref": "G",
            "alt": "A",
            "genome": "GRCh38"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Variant not imported: already in database!" in data



    ##### post invalid data #####
    response = test_client.post(
        url_for("variant.create", type = "vcf"), 
        data={
            "chr": "chr1",
            "pos": "10295", # wrong position
            "ref": "G",
            "alt": "A",
            "genome": "GRCh38"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))
    
    print(data)
    
    assert response.status_code == 200
    assert "ERROR: Reference base(s) not correct." in data


    ##### post missing data #####
    response = test_client.post(
        url_for("variant.create", type = "vcf"), 
        data={
            "chr": "chr1",
            "pos": "10303165",
            "ref": "C",
            # missing alternative allele information
            "genome": "GRCh38"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))

    print(data)

    assert response.status_code == 200
    assert "All fields are required!" in data



def test_create_variant_from_grch37(test_client):
    response = test_client.get(url_for("variant.create"), follow_redirects=True)
    assert response.status_code == 200

    ##### create new variant from grch37 successfully #####
    #chr1	10363223	C	T
    response = test_client.post(
        url_for("variant.create", type = "vcf"), 
        data={
            "chr": "chr1",
            "pos": "10363223",
            "ref": "C",
            "alt": "T",
            "genome": "GRCh37"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))

    print(data)

    assert response.status_code == 200
    assert "Successfully inserted variant" in data
    assert "alert-danger" not in data
    assert "ERROR" not in data
    assert "10303165" in data

    links = get_all_links(data)
    for link in links:
        response = requests.get(link)
        assert response.status_code == 200


def test_create_variant_from_hgvs(test_client):
    response = test_client.get(url_for("variant.create"), follow_redirects=True)
    assert response.status_code == 200

    ##### create new variant from HGVS #####
    response = test_client.post(
        url_for("variant.create", type = "hgvsc"), 
        data={
            "hgvsc": "c.1519G>A",
            "transcript": "ENST00000260947"
        },
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    data = html.unescape(response.data.decode('utf8'))

    print(data)

    assert response.status_code == 200
    assert "Successfully inserted variant" in data
    assert "alert-danger" not in data
    assert "ERROR" not in data
    assert "214767531" in data







def get_all_links(html_data):
    links = re.findall(r'href="(http.*?)"[ |>]', html_data)
    return links





