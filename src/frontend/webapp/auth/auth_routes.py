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
    # construct redirect uri: first redirect to keycloak login page
    # then redirect to auth with the next param which defaults to the '/' route
    # auth itself redirects to next ie. the page which required a login
    redirect_uri = url_for('auth.auth', _external=True, next_login=request.args.get('next_login', '/'))

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

    print(token_response)


    if token_response:
        user_info = token_response['userinfo']

        # init the session
        session['user'] = user_info
        session['tokenResponse'] = token_response

        # save user to database - this is only to record which user made which actions in the database and has nothing to do with authenitication
        username = user_info['preferred_username']
        first_name = user_info['given_name']
        last_name = user_info['family_name']
        affiliation = user_info.get('affiliation')
        if affiliation is None or affiliation.strip() == '':
            flash('LOGIN ERROR: user was missing affiliation ask a HerediVar administrator to add it!', 'alert-danger')
            return redirect(url_for('auth.logout', auto_logout='True'))
        conn = Connection()
        conn.insert_user(username, first_name, last_name, affiliation) # this inserts only if the user is not already in the database and updates the information if the information changed (except for username this one has to stay)
        conn.close()


        return redirect(request.args.get('next_login', url_for('main.index')))
    
    flash('ERROR: could not fetch user information from authentication server!', 'alert-danger')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/logout')
def logout():
    tokenResponse = session.get('tokenResponse')

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

    session.pop('user', None)
    session.pop('tokenResponse', None)

    auto_logout = request.args.get('auto_logout', False)
    if not auto_logout:
        flash("Successfully logged out!", "alert-success")

    return redirect(request.args.get('next_logout', url_for('main.index')))


@auth_blueprint.route('/register')
@require_permission
def register():
    if current_app.config['TLS']:
        prefix = 'https://'
    else:
        prefix = 'http://'
    return redirect(prefix + current_app.config['HOST'] + ':' + current_app.config['KEYCLOAK_PORT'] + '/admin/HerediVar/console/')