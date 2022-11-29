
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




def get_all_links(html_data):
    links = re.findall(r'href="(http.*?)"[ |>]', html_data)
    return links



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


