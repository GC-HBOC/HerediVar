
from flask import request, url_for
from urllib.parse import urlparse
import requests

def test_login(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get(url_for('auth.login'), follow_redirects=True)
    print(request.path)
    print(response)
    #keycloak_auth_url = response.location
    #print(keycloak_auth_url)
    
    

        
    
