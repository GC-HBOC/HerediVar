
from flask import request, url_for, session, current_app
from urllib.parse import urlparse
import requests

def test_login(test_client):
    """
    DOCSTRING
    """
    #response = test_client.get("/login", follow_redirects=False)
    #print(response.request.path)
    #print(session['tokenResponse'])
    #print(session['user'])

    login_admin()

    print(session['tokenResponse'])
    print(session['user'])

    response = test_client.get("/create", follow_redirects=True)
    print(response)
    print(response())
    print(response.text)
    print(response.status_code)


    assert response.status_code == 2300
    #keycloak_auth_url = response.location
    #print(keycloak_auth_url)
    
    

        
def login_admin():
    issuer = current_app.config['ISSUER']
    url = f'{issuer}/protocol/openid-connect/token'
    data = {'client_id':current_app.config['CLIENTID'], 'client_secret': current_app.config['CLIENTSECRET'], 'grant_type': 'password', 'username': 'testuser', 'password': '12345'}
    token_response = requests.post(url = url, data=data)
    assert token_response.status_code == 200
    session['tokenResponse'] = token_response.json()

    url = f'{issuer}/protocol/openid-connect/userinfo'
    data = {'token': session["tokenResponse"]["access_token"], 'token_type_hint': 'access_token', 'client_secret': current_app.config['CLIENTSECRET'], 'client_id': current_app.config['CLIENTID']}
    header = {'Authorization': f'Bearer {session["tokenResponse"]["access_token"]}'}
    user_response = requests.post(url = url, data=data, headers=header)
    assert user_response.status_code == 200
    session['user'] = user_response.json()

    assert session.get('user') is not None
    assert session.get('tokenResponse') is not None
    assert session.get('tokenResponse').get('access_token') is not None
