
from flask import request, url_for, session
from urllib.parse import urlparse
import requests

def test_login(test_client):
    """
    DOCSTRING
    """
    response = test_client.get("/login", follow_redirects=False)
    print(response.request.path)
    print(session['tokenResponse'])
    print(session['user'])
    assert session.get('user') is not None
    assert session.get('tokenResponse') is not None
    assert session.get('tokenResponse').get('access_token') is not None

    response = test_client.get("/create")
    print(response.data)
    print(response.status_code)


    assert response.status_code == 2300
    #keycloak_auth_url = response.location
    #print(keycloak_auth_url)
    
    

        
    
