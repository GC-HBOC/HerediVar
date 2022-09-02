
from flask import request, url_for, session, current_app
from urllib.parse import urlparse
import requests

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
    data = response.data.decode('utf8')
    assert response.status_code == 200
    assert 'id="variantTable"' in data
    assert data.count('name="variant_row"') == 5
    assert 'variant_id="15"' in data
    assert 'variant_id="52"' in data
    assert 'variant_id="71"' in data
    assert 'variant_id="72"' in data
    assert 'variant_id="139"' in data

    response = test_client.get(url_for("variant.search", genes="BARD1"))
    data = response.data.decode('utf8')
    print(data)
    assert response.status_code == 200
    assert data.count('name="variant_row"') == 5
    assert 'variant_id="15"' in data

    
    
    
    

        

