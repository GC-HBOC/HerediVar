import json
import os

import certifi
import requests
from authlib.oauth2.rfc6749 import OAuth2Token
from flask import url_for, session, request, current_app, abort, redirect
from authlib.integrations.flask_client import OAuth, token_update
from authlib.integrations.flask_oauth2 import ResourceProtector
from functools import wraps
from authlib.oauth2.rfc7636 import create_s256_code_challenge



# a decorator which redirects to the login page if the user is not logged in. 
# Also sets the 'next' parameter to redirect to the page which called the require_login decorator
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # user is not logged in -> promt a login
        if session.get('user') is None:
            return redirect(url_for('auth.login', next_login=request.url))
        
        # user is logged in -> check if access token is still valid using introspect endpoint --> introspect endpoint can be omitted if token is validated locally using some jwt lib
        
        token = session['tokenResponse']
        
        issuer = current_app.config['ISSUER']
        url = f'{issuer}/protocol/openid-connect/token/introspect'
        data = {'token': token.get("access_token"), 'token_type_hint': 'access_token', 'username': session['user']['preferred_username'], 'client_secret': current_app.config['CLIENTSECRET'], 'client_id': current_app.config['CLIENTID']}
        header = {'Authorization': f'Bearer {token.get("access_token")}'}
        resp = requests.post(url, data=data, headers=header)
        resp.raise_for_status()
        resp = resp.json()
        #print(resp['active'])

        #url = f'{issuer}/protocol/openid-connect/userinfo'
        #test_resp = requests.get(url, headers = {'Authorization': f'Bearer {token.get("access_token")}'})
        #print(token)
        #print(test_resp)
        #print(test_resp.text)

        # if access token is not valid request a new one using the refresh token
        if not resp['active']:
            print('access token invalid refreshing token')
            refresh_status_code = refresh_token()
            # if the refresh token is expired as well promt a new login by invalidating the client session
            if refresh_status_code != 200:
                return redirect(url_for('auth.logout', auto_logout='True', next_logout=url_for('auth.login', next_login=request.url))) # logout and return to login page! with next= page which you wanted to access in the first place
        
        return f(*args, **kwargs)
    return decorated_function

# how to add new permission policies: https://stackoverflow.com/questions/42186537/resources-scopes-permissions-and-policies-in-keycloak (i was using the resource based permissions)
def require_permission(f):
    @require_login
    @wraps(f)
    def decorated_function(*args, **kwargs):
        grant_access, status_code = request_uma_ticket()
        if not grant_access:
            abort(status_code)
        return f(*args, **kwargs)
    return decorated_function


def request_uma_ticket():
    token = session['tokenResponse']
    issuer = current_app.config['ISSUER']
    url = f'{issuer}/protocol/openid-connect/token'
    data = {'grant_type':'urn:ietf:params:oauth:grant-type:uma-ticket', 'audience':current_app.config['CLIENTID']}
    header = {'Authorization': f'Bearer {token.get("access_token")}'}
    resp = requests.post(url, data=data, headers=header)
    if resp.status_code != 200:
        current_app.logger.error(current_app['user']['preferred_username'] + " tried to access a protected route, but had not the required permissions.")
        return False, resp.status_code
    return True, 200

# not exactly a decorator, but a helper function for them
# this function uses the refresh token to get a new access token and returns the status code from this call
def refresh_token():
    token = session['tokenResponse']
    issuer = current_app.config['ISSUER']

    url = f'{issuer}/protocol/openid-connect/token'
    data = {'client_id':current_app.config['CLIENTID'], 'client_secret': current_app.config['CLIENTSECRET'], 'refresh_token': token['refresh_token'], 'grant_type': 'refresh_token'}
    resp = requests.post(url = url, data=data)
    new_token = resp.json()
    status_code = resp.status_code
    if status_code == 200:
        # another way to use the refresh token to update the access token...
        #token = oauth.keycloak.fetch_access_token(
        #    refresh_token=session['tokenResponse']['refresh_token'],
        #    grant_type='refresh_token')
        url = f'{issuer}/protocol/openid-connect/userinfo'
        session['tokenResponse'] = new_token

    return status_code



