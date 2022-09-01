
from flask import request, url_for, session, current_app
from urllib.parse import urlparse
import requests

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
    

    
    
    

        

