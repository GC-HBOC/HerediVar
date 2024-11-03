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

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection


def require_api_token_permission(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            authorization_header = parse_authorization_header(request.headers.get('Authorization'))

            conn = Connection()
            api_key_ok = conn.check_api_key(authorization_header['apikey'], authorization_header['username'])
            roles_ok, api_roles = conn.check_api_roles(authorization_header['username'], roles)
            user_id = conn.get_user_id(authorization_header['username'])
            conn.close()

            if not api_key_ok:
                abort(403, "Invalid credentials")
            if not roles_ok:
                abort(403, "Insufficient privileges")

            session['user'] = {'roles': api_roles, 'user_id': user_id,'preferred_username': authorization_header['username']}
            return f(*args, **kwargs)
        return wrapper
    return decorator

def parse_authorization_header(authorization_header: str):
    authorization_header = authorization_header.split(' ')

    result = {}
    next_keyword = True
    current_keyword = None
    for h in authorization_header:
        if h.strip() == '':
            continue
        if next_keyword:
            current_keyword = h
            next_keyword = False
            continue
        if not next_keyword:
            result[current_keyword] = h
            next_keyword = True

    keywords_oi = ['apikey', 'username']
    for kw in keywords_oi:
        if result.get(kw) is None:
            abort(403, "Incomplete authorization header. Missing keyword: " + kw)
        
    return result




# a decorator which redirects to the login page if the user is not logged in. 
# Also sets the 'next' parameter to redirect to the page which called the require_login decorator
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # user is not logged in -> promt a login
        if session.get('user') is None:
            return redirect(url_for('auth.login', next_login=request.url))
        
        if current_app.config["LOGIN_REQUIRED"]:
            # user is logged in -> check if access token is still valid using introspect endpoint --> introspect endpoint can be omitted if token is validated locally using some jwt lib
        
            token = session['tokenResponse']

            #print(session['user'])
            #print(token)

            # maybe also add: 
            # state=5AzjFWCkQzjmh4YozUfuE8pHytJj3i
            # nonce=fvdZHHR1mmAHBIbCQtgZ
            # code_challenge=hoiDWU7Vf4tOreIeYyIi7IKcw2BseRW7j5wwXROJtPA
            # code_challenge_method=S256
        
            issuer = current_app.config['ISSUER']
            url = f'{issuer}/protocol/openid-connect/token/introspect'
            data = {'token': token.get("access_token"), 'token_type_hint': 'access_token', 'username': session['user']['preferred_username'], 'client_secret': current_app.config['CLIENTSECRET'], 'client_id': current_app.config['CLIENTID']}
            header = {'Authorization': f'Bearer {token.get("access_token")}'}
            resp = requests.post(url, data=data, headers=header)
            resp.raise_for_status()
            resp = resp.json()

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
def require_permission(resources):
    def decorator(f):
        @require_login
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_app.config["LOGIN_REQUIRED"]:
                grant_access, status_code = request_uma_ticket(resources)
                if not grant_access:
                    abort(status_code)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def request_uma_ticket(resources):
    token = session['tokenResponse']
    issuer = current_app.config['ISSUER']
    url = f'{issuer}/protocol/openid-connect/token'
    client_id = current_app.config['CLIENTID']
    data = {'grant_type':'urn:ietf:params:oauth:grant-type:uma-ticket', 'audience':client_id, "permission":resources, 'response_mode':'decision'}
    header = {'Authorization': f'Bearer {token.get("access_token")}'}
    resp = requests.post(url, data=data, headers=header)
    #print(resp.json())
    decision = True
    if resp.status_code != 200:
        decision = False
        current_app.logger.error(session['user']['preferred_username'] + " tried to access a protected route, but had not the required permissions.")
    return decision, resp.status_code




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



