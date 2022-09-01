
from flask import request, url_for, session
from urllib.parse import urlparse
import requests

def test_login(test_client):
    """
    DOCSTRING
    """
    response = test_client.get("/create", follow_redirects=True)
    print(request.path)
    print(response.history)
    print(response.request.path)
    print(response.request.json())
    print(session['tokenResponse'])
    assert response.status_code == 2300
    #keycloak_auth_url = response.location
    #print(keycloak_auth_url)
    
    

        
    
