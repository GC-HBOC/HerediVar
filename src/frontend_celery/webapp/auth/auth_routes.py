import json
import os
import sys
import certifi
import requests
from authlib.oauth2.rfc6749 import OAuth2Token
from flask import url_for, session, request, Blueprint, current_app
from flask import render_template, redirect
from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from functools import wraps
from flask_session import Session
from redis import Redis
from authlib.oauth2.rfc7636 import create_s256_code_challenge
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from .. import oauth
from ..utils import *


auth_blueprint = Blueprint(
    'auth',
    __name__
)



@auth_blueprint.route('/login')
def login():

    if current_app.config.get('TESTING', False):
        issuer = current_app.config['ISSUER']
        url = f'{issuer}/protocol/openid-connect/token'
        data = {'client_id':current_app.config['CLIENTID'], 'client_secret': current_app.config['CLIENTSECRET'], 'grant_type': 'password', 'username': 'testuser', 'password': '12345'}
        token_response = requests.post(url = url, data=data)
        session['tokenResponse'] = token_response.json()

        url = f'{issuer}/protocol/openid-connect/userinfo'
        data = {'authorization': session['tokenResponse']['access_token']}
        user_response = requests.post(url = url, data=data)
        print(user_response.status_code)
        print(user_response.json)

        if token_response.status_code != 200:
            return redirect(url_for('main.index'))
        return save_redirect(request.args.get('next_login', url_for('main.index')))

    # construct redirect uri: first redirect to keycloak login page
    # then redirect to auth with the next param which defaults to the '/' route
    # auth itself redirects to next ie. the page which required a login
    redirect_uri = url_for('auth.auth', _external=True, next_login=request.args.get('next_login', url_for('main.index')))

    return oauth.keycloak.authorize_redirect(redirect_uri)


@auth_blueprint.route('/auth')
def auth():
    token_response = oauth.keycloak.authorize_access_token()

    #userinfo = oauth.keycloak.userinfo(request)
    #idToken = oauth.keycloak.parse_id_token(tokenResponse)


    # get user_info using jwt token in tokenResponse
    #keys = requests.get(f'{issuer}/protocol/openid-connect/certs')
    #keys = keys.text
    #claims = jwt.decode(token_response['id_token'], keys, claims_cls=CodeIDToken)
    #claims.validate()

    #print(token_response)


    if token_response:
        user_info = token_response['userinfo']
        

        # save user to database - this is only to record which user made which actions in the database and has nothing to do with authenitication
        username = user_info['preferred_username']
        first_name = user_info['given_name']
        last_name = user_info['family_name']
        affiliation = user_info.get('affiliation')
        if affiliation is None or affiliation.strip() == '':
            flash('LOGIN ERROR: You are missing the affiliation tag ask a HerediVar administrator to add it!', 'alert-danger')
            current_app.logger.error("Could not login user " + username + ", because the user was missing affiliation tag in keycloak.")
            return redirect(url_for('auth.logout', auto_logout='True'))
        conn = Connection()
        conn.insert_user(username, first_name, last_name, affiliation) # this inserts only if the user is not already in the database and updates the information if the information changed (except for username this one has to stay)
        user_info['user_id'] = conn.get_user_id(username)
        conn.close()

        # init the session
        session['user'] = user_info
        session['tokenResponse'] = token_response

        current_app.logger.info("User " + username + ' (' + affiliation + ") successfully logged in.")

        return save_redirect(request.args.get('next_login', url_for('main.index')))
    
    flash('ERROR: could not fetch user information from authentication server!', 'alert-danger')
    current_app.logger.error("Could not fetch user information from authentication server.")
    return redirect(url_for('main.index'))


@auth_blueprint.route('/logout')
def logout():
    tokenResponse = session.get('tokenResponse')
    auto_logout = request.args.get('auto_logout', False)

    if tokenResponse is not None:
        # propagate logout to Keycloak
        refreshToken = tokenResponse['refresh_token']
        issuer = current_app.config['ISSUER']
        endSessionEndpoint = f'{issuer}/protocol/openid-connect/logout'

        requests.post(endSessionEndpoint, data={
            "client_id": current_app.config['CLIENTID'],
            "client_secret": current_app.config['CLIENTSECRET'],
            "refresh_token": refreshToken,
        })
    
    logout_reason = "manual logout"
    if auto_logout:
        logout_reason = "automatic logout"
    current_app.logger.info("Successfully logged " + session['user']['preferred_username'] + " out. Reason: " + logout_reason)

    session.pop('user', None)
    session.pop('tokenResponse', None)

    if not auto_logout:
        flash("Successfully logged out!", "alert-success")

    return save_redirect(request.args.get('next_logout', url_for('main.index')))


@auth_blueprint.route('/register')
@require_permission
def register():
    if current_app.config['TLS']:
        prefix = 'https://'
    else:
        prefix = 'http://'
    return redirect(prefix + current_app.config['HOST'] + ':' + current_app.config['KEYCLOAK_PORT'] + '/admin/HerediVar/console/')