
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


def test_browse(test_client):
    """
    This tests if the browse variant table works properly
    """
    response = test_client.get(url_for("variant.search"), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    #print(data)
    assert response.status_code == 200
    assert 'id="variantTable"' in data
    assert data.count('name="variant_row"') == 10
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

    # test page size
    response = test_client.get(url_for("variant.search", page_size = 5), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 5
    assert data.count('class="page-link"') == 8 # 2 pages + 2 buttons right, left * 2 because the navbar is on top and on bottom

    response = test_client.get(url_for("variant.search", page_size = 31), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "This page size is not supported. Defaulting to 20" in data
    assert data.count('name="variant_row"') == 10

    # test sort by option
    response = test_client.get(url_for("variant.search", page_size = 5, sort_by = 'recent'), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 5
    variant_ids = [168,164,146,139,130]
    last_pos = -2
    for variant_id in variant_ids:
        cur_pos = data.find('variant_id="' + str(variant_id) + '"')
        assert cur_pos != -1
        assert last_pos < cur_pos
        last_pos = cur_pos

    response = test_client.get(url_for("variant.search", page_size = 5, sort_by = 'gnomic_position'), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    with open("/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/tests/test_dat/browse_01.html", "w") as file:
        file.write(data)
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 5
    variant_ids = [139, 130, 15, 146, 52]
    last_pos = -2
    for variant_id in variant_ids:
        cur_pos = data.find('variant_id="' + str(variant_id) + '"')
        assert cur_pos != -1
        assert last_pos < cur_pos
        last_pos = cur_pos

def test_browse_cDNA_ranges(test_client):
    """
    This tests if the search for cDNA ranges works properly
    """
    response = test_client.get(url_for("variant.search", cdna_ranges="ENST00000357654 1 10"), follow_redirects=True)
    data = response.data.decode('utf8')
    #71,168
    #ENST00000357654
    #c.52_64del
    #c.670+1G>C
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 0

    response = test_client.get(url_for("variant.search", cdna_ranges="ENST00000357654 670 670+1"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="168"' in data

    response = test_client.get(url_for("variant.search", cdna_ranges="BRCA1 670 670+1"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="168"' in data


def test_browse_consensus_classification(test_client):
    """
    This tests if the search for consensus classifications works properly
    """
    # one class
    response = test_client.get(url_for("variant.search", consensus=3), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="139"' in data

    # multiple classes
    response = test_client.get(url_for("variant.search", consensus=[3,4]), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 2
    assert 'variant_id="15"' in data
    assert 'variant_id="139"' in data

    response = test_client.get(url_for("variant.search", consensus=["1","2","3-","3","3+","4M","4","5","-"]), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 10
    assert 'variant_id="15"' in data
    assert 'variant_id="52"' in data
    assert 'variant_id="71"' in data
    assert 'variant_id="72"' in data
    assert 'variant_id="130"' in data
    assert 'variant_id="146"' in data
    assert 'variant_id="32"' in data
    assert 'variant_id="139"' in data
    assert 'variant_id="164"' in data
    assert 'variant_id="168"' in data

    response = test_client.get(url_for("variant.search", consensus=["5"], include_heredicare_consensus="on"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

def test_browse_external_ids(test_client):
    """
    Test if the external id search works properly
    """
    #serach for heredicare id
    response = test_client.get(url_for("variant.search", external_ids="11740058"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

    response = test_client.get(url_for("variant.search", external_ids="11740058:heredicare"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

    #search for clinvar id
    response = test_client.get(url_for("variant.search", external_ids="blimblam2:clinvar"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

    # search multiple
    response = test_client.get(url_for("variant.search", external_ids="11334923;11740058"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 2
    assert 'variant_id="52"' in data
    assert 'variant_id="139"' in data


def test_browse_automatic_classification(test_client):
    """
    Test that automatic classification search is working properly
    """
    response = test_client.get(url_for("variant.search", automatic_splicing=["2"]), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

    response = test_client.get(url_for("variant.search", automatic_splicing=["2"], automatic_protein=["3"]), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

    response = test_client.get(url_for("variant.search", automatic_splicing=["-"]), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 9
    assert 'variant_id="15"' in data
    assert 'variant_id="71"' in data
    assert 'variant_id="72"' in data
    assert 'variant_id="130"' in data
    assert 'variant_id="146"' in data
    assert 'variant_id="32"' in data
    assert 'variant_id="139"' in data
    assert 'variant_id="164"' in data
    assert 'variant_id="168"' in data



def test_browse_genes(test_client):
    """
    This tests if the search for genes works properly
    """
    response = test_client.get(url_for("variant.search", genes="BARD1"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

def test_browse_ranges(test_client):
    """
    This tests if the search for genomic ranges works properly
    """
    response = test_client.get(url_for("variant.search", ranges="chr17:43124030-43124035"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="71"' in data

def test_browse_hgvs(test_client):
    """
    This tests if the search for hgvs strings works properly
    """
    # with ensembl transcript name
    response = test_client.get(url_for("variant.search", hgvs="ENST00000613192:c.*35C>T"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    # with gene name, hgvs is not the mane select transcript -> this does not return the variant of interest
    response = test_client.get(url_for("variant.search", hgvs="BARD1:c.*35C>T"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 0

    # gene + mane select transcript
    response = test_client.get(url_for("variant.search", hgvs="BARD1:c.1972C>T"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    # without transcript/gene
    response = test_client.get(url_for("variant.search", hgvs="c.1972C>T"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    # multiple hgvs
    response = test_client.get(url_for("variant.search", hgvs="ENST00000613192:c.*35C>T;c.1972C>T ,   ENST00000420246:c.*131C>T "), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 2
    assert 'variant_id="15"' in data
    assert 'variant_id="72"' in data

    response = test_client.get(url_for("variant.search", hgvs="c.1972C>T ,   ENST00000420246:c.*131C>T ", genes="TP53"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="72"' in data


def test_browse_annotations(test_client):
    """
    Test that annotation search is working properly
    """
    #annotation_type_id=21&annotation_operation=&annotation_value=
    response = test_client.get(url_for("variant.search", annotation_type_id="4", annotation_operation=">", annotation_value="5"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    response = test_client.get(url_for("variant.search", annotation_type_id=["4", "4"], annotation_operation=[">", "<"], annotation_value=["5", "1"]), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 0

    response = test_client.get(url_for("variant.search", annotation_type_id="4", annotation_operation="=", annotation_value="5"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 0

    response = test_client.get(url_for("variant.search", annotation_type_id="4", annotation_operation="<", annotation_value="2"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="52"' in data

    response = test_client.get(url_for("variant.search", annotation_type_id="16", annotation_operation="<", annotation_value="eas"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert 'The operation &lt; is not allowed for popmax.' in data

    response = test_client.get(url_for("variant.search", annotation_type_id="16", annotation_operation="=", annotation_value="eas"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    response = test_client.get(url_for("variant.search", annotation_type_id="16", annotation_operation="~", annotation_value="AS"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data


def test_browse_list(test_client):
    """
    This tests if the search for variant lists works properly
    """
    # allowed list
    response = test_client.get(url_for("variant.search", lookup_list_id=8, lookup_list_name="public read"), follow_redirects=True)
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 1
    assert 'variant_id="15"' in data

    # unallowed/non existing list
    response = test_client.get(url_for("variant.search", lookup_list_id=11, lookup_list_name="private inaccessible"), follow_redirects=True)
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
    v = conn.get_variant(variant_id)
    conn.close()
    
    #print('\n'.join([line for line in data.split('\n') if line.strip() != '']))

    all_anntation_ids_raw = re.findall(r'annotation_id="((\d*;?)*)"', data)
    #print(all_anntation_ids_raw)
    all_annotation_ids = []
    for ids in all_anntation_ids_raw:
        ids = ids[0].strip(' ').strip(';').split(';')
        all_annotation_ids.extend(ids)
    #print(all_annotation_ids)

    annotations = v.annotations
    for key in annotations.get_all_annotation_names():
        current_annotation = getattr(annotations, key)
        if current_annotation is not None:
            assert str(current_annotation.id) in all_annotation_ids

    clinvar_submissions = v.clinvar.submissions
    if clinvar_submissions is not None:
        for submission in clinvar_submissions:
            assert 'clinvar_id="' + str(submission.id) + '"' in data

    consequences = v.consequences
    if consequences is not None:
        for consequence in consequences:
            assert consequence.transcript.name in data
        
    literature = v.literature
    if literature is not None:
        for paper in literature:
            assert "PMID:" + str(paper.pmid) in data

    assays = v.assays
    if assays is not None:
        for assay in assays:
            assert 'assay_id="' + str(assay.id) in data

    consensus_classification = v.get_recent_consensus_classification()
    if consensus_classification is not None:
        assert 'consensus_classification_id="' + str(consensus_classification.id) + '"' in data
        current_criteria = consensus_classification.scheme.criteria
        for criterium in current_criteria:
            assert 'consensus_criterium_applied_id="' + str(criterium.id) + '"' in data

    user_classifications = v.user_classifications
    if user_classifications is not None:
        for classification in user_classifications:
            assert 'user_classification_id="' + str(classification.id) + '"' in data
            current_criteria = classification.scheme.criteria
            for criterium in current_criteria:
                assert 'user_criterium_applied_id="' + str(criterium.id) + '"' in data    
        
    heredicare_classifications = v.heredicare_classifications
    if heredicare_classifications is not None:
        for classification in heredicare_classifications:
            assert 'heredicare_center_classification_id="' + str(classification.id) + '"' in data


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
            'ps3': "Evidence for ps3 given in this field",
            'ps1_strength': "ps",
            'ps2_strength': "ps",
            'ps3_strength': "ps",
            'ps1_state': "selected",
            'ps2_state': "selected",
            'ps3_state': "unselected",
            'scheme': "2"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    #with open("/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/tests/functional/test.html", 'w') as file:
    #    file.write(data)
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
            'pp1_state': "selected",
            'bs4_state': "selected",
            'scheme': "2"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "A mutually exclusive criterium to PP1 was selected." in data

    ##### test posting none as classification scheme #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update.",
            'scheme': "1"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted new user classification" in data

    ##### test invalid criteria (they do not exist) #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update.",
            'non_exist': "Evidence", 
            'non_exist_strength': "ba",
            'non_exist_state': "selected",
            'scheme': "2"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 500


    ##### test posting invalid strength #####
    response = test_client.post(
        url_for("variant.classify", variant_id=variant_id),
        data = {
            'final_class': "2",
            'comment': "This is a test comment update 2.",
            'pp1': "Evidence for pp1 given in this field", 
            'pp1_strength': "ba", 
            'pp1_state': "selected",
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
            'pm3_state': "selected",
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
            '4.4_state': "selected",
            'scheme': "5"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully inserted new user classification" in data

    
    ##### test inserting literature passages & updating the classification #####

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
            'ps1_state': "selected",
            'ps2_state': "selected",
            'ps3_state': "selected",
            'scheme': "2",
            'pmid': [35205822, 33099839],
            'text_passage': ["This is a text passage...", "This is another text passage..."]
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200
    assert "Successfully updated user classification" in data

    # test that data was saved correctly to db
    conn = Connection(['super_user'])
    variant = conn.get_variant(variant_id, include_annotations = False, include_heredicare_classifications=False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
    assert len(variant.user_classifications) == 3

    classification = variant.user_classifications[0]
    selected_literature = classification.literature
    assert len(selected_literature) == 2
    all_pmids = [str(x.pmid) for x in selected_literature]
    all_text_passages = [x.text_passage for x in selected_literature]
    assert "35205822" in all_pmids
    assert "This is a text passage..." in all_text_passages
    assert "33099839" in all_pmids
    assert "This is another text passage..." in all_text_passages

    selected_criteria = classification.scheme.criteria
    assert len(selected_criteria) == 3
    all_criteria_evidence = [x.evidence for x in selected_criteria]
    assert "Evidence for ps1 given in this field update1" in all_criteria_evidence
    assert "Evidence for ps2 given in this field update2" in all_criteria_evidence
    assert "Evidence for ps3 given in this field" in all_criteria_evidence
    assert "This is a test comment update0" == classification.comment

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

    #print(data)

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
    print(data)
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


