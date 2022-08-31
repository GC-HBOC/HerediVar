
from flask import request, url_for
from urllib.parse import urlparse
import requests

def test_login(test_client):
    """
    DOCSTRING
    """
    response = test_client.get(url_for('auth.login'), follow_redirects=True)
    print(request.path)
    print(response)
    #keycloak_auth_url = response.location
    #print(keycloak_auth_url)
    
    

        
    
