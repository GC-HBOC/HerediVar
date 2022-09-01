
from flask import request, url_for, session
from urllib.parse import urlparse
import requests

def test_login(test_client):
    """
    DOCSTRING
    """
    response = test_client.get("/login", follow_redirects=True)
    print(request.path)
    print(response)
    print(session['tokenResponse'])
    assert response.status_code == 200
    #keycloak_auth_url = response.location
    #print(keycloak_auth_url)
    
    

        
    
