import os
import sys
import requests
from flask import url_for, session, request, Blueprint, current_app, render_template, redirect
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from .. import oauth, tasks
from ..utils import *
import secrets
from . import auth_functions

#from authlib.oauth2.rfc6749 import OAuth2Token
#from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
#from authlib.oauth2.rfc7636 import create_s256_code_challenge

auth_blueprint = Blueprint(
    'auth',
    __name__
)


####################################
########### LOGIN ROUTES ###########
####################################

@auth_blueprint.route('/login')
def login():
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

    if token_response:
        user_info = token_response['userinfo']
        
        # this is only to record which user made which actions in the database and has nothing to do with authenitication
        username = user_info['preferred_username']
        first_name = user_info['given_name']
        last_name = user_info['family_name']
        affiliation = user_info.get('affiliation')
        roles = user_info['roles']
        

        # init the session
        session['user'] = user_info
        session['tokenResponse'] = token_response

        if affiliation is None or affiliation.strip() == '':
            flash('LOGIN ERROR: You are missing the affiliation tag ask a HerediVar administrator to add it!', 'alert-danger')
            current_app.logger.error("Could not login user " + username + ", because the user was missing affiliation tag in keycloak.")
            return redirect(url_for('auth.logout', auto_logout='True'))
        conn = Connection(session['user']['roles'])
        # this inserts only if the user is not already in the database and updates the information if the information changed (except for username this one has to stay)
        conn.insert_user(username, first_name, last_name, affiliation, ';'.join(roles)) 
        user_id = conn.get_user_id(username)
        user_info['user_id'] = user_id
        conn.close()

        current_app.logger.info("User " + user_info['preferred_username'] + ' (' + user_info.get('affiliation') + ") successfully logged in.")

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



##############################################
########### ACCOUNT MANAGER ROUTES ###########
##############################################

@auth_blueprint.route('/show_users')
@require_permission(['account_manager_resources'])
def show_users():
    users = auth_functions.get_users()
    return render_template('auth/show_users.html', users = users)


@auth_blueprint.route('/register', methods=['GET', 'POST'])
@require_permission(['account_manager_resources'])
def register():
    roles = auth_functions.get_roles()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        affiliation = request.form.get('affiliation')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        selected_roles = request.form.getlist('role') # a list of role indexes -> this id resembles the number in the array returned from get_roles()

        #admin_token = get_admin_token()
        resp = auth_functions.register_user(username, email, affiliation, first_name, last_name)
        if resp.status_code == 201: # user creation was successful
            new_user = auth_functions.get_users(username)
            if new_user is not None: # get user id was successful
                kc_user_id = new_user['id']
                resp, password = auth_functions.reset_password(kc_user_id)
                if resp.status_code == 204: # set password was successful
                    resp = auth_functions.grant_roles(kc_user_id, selected_roles, roles)
                    if resp.status_code == 204: # grant roles was successful
                        flash("New user created successfully!", 'alert-success')
                        task = tasks.notify_new_user.apply_async(args=[first_name + ' ' + last_name, email, username, password])
                        return redirect(url_for('auth.register'))

        flash(resp.json(), 'alert-danger')

    return render_template('auth/register.html', roles = roles)


@auth_blueprint.route('/edit_user/<string:username>', methods = ['GET', 'POST'])
@require_permission(['account_manager_resources'])
def edit_user(username):
    user = auth_functions.get_users(username)
    kc_user_id = user['id']
    avail_roles = auth_functions.get_roles()
    set_roles = auth_functions.get_roles_of_user(kc_user_id, avail_roles)

    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        e_mail = request.form.get('e_mail', '')
        affiliation = request.form.get('affiliation', '')
        enabled = request.form.get('enabled', 'off')
        new_roles = [int(x) for x in request.form.getlist('role')] # a list of role index numbers in avail_roles list
        if any([x.strip() == '' for x in [first_name, last_name, e_mail, affiliation, enabled]]):
            flash('All information is required!', 'alert-danger')
            return render_template('auth/edit_user.html', user = user, avail_roles = avail_roles, set_roles = set_roles)
        if len(new_roles) == 0:
            flash('Please provide at least one role!', 'alert-danger')
            return render_template('auth/edit_user.html', user = user, avail_roles = avail_roles, set_roles = set_roles)
        
        enabled = enabled == 'on'

        resp = auth_functions.update_user_information(kc_user_id, user['username'], first_name, last_name, e_mail, affiliation, enabled)

        added_roles, deleted_roles = auth_functions.get_added_and_deleted_roles(set_roles, new_roles)
        resp = auth_functions.grant_roles(kc_user_id, added_roles, avail_roles)
        resp = auth_functions.delete_roles(kc_user_id, deleted_roles, avail_roles)

        avail_roles = auth_functions.get_roles()
        new_roles = auth_functions.get_roles_of_user(kc_user_id, avail_roles)
        final_new_roles = []
        if enabled:
            for new_role_index in new_roles:
                final_new_roles.append(avail_roles[new_role_index]['name'])
        conn = get_connection()
        conn.set_api_roles(username, ";".join(final_new_roles))

        if resp.status_code == 204:
            flash('Successfully changed user information!', 'alert-success')
            return redirect(url_for('auth.edit_user', username = username))
        flash(resp.json(), 'alert-danger')

    return render_template('auth/edit_user.html', user = user, avail_roles = avail_roles, set_roles = set_roles)



#############################################
######### USER SELF-SERVICE ROUTES ##########
#############################################

@auth_blueprint.route('/change_password')
@require_login
def change_password():
    # handled by keycloak directly -> simply redirect
    return redirect(current_app.config['KEYCLOAK_BASEPATH'] + "/realms/" + current_app.config['KEYCLOAK_REALM'] + "/account/#/security/signingin")


@auth_blueprint.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():
    # every user can view and edit basic user information
    # ofc excluding roles etc
    username = session['user']['preferred_username']

    user = auth_functions.get_profile()
        
    if request.method == 'POST':
        e_mail = request.form.get('e_mail')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        affiliation = request.form.get('affiliation')
        if any([x is None for x in [e_mail, first_name, last_name, affiliation]]):
            flash('All fields are required!', 'alert-danger')
            return render_template('auth/profile', user = user)
        
        resp = auth_functions.edit_general_info(username, e_mail, first_name, last_name, affiliation)
        if resp.status_code == 204:
            flash("Successfully changed information", 'alert-success flash_id:success_userinfo')
            return redirect(url_for('auth.profile'))
        error_message = ''.join(resp.json()["errorMessage"].split())
        flash_id = "flash_id:" + error_message
        flash("Error: " + error_message, "alert-danger " + flash_id)

    return render_template('auth/profile.html', user = user)


@auth_blueprint.route('/generate_api_key', methods=['GET', 'POST'])
@require_permission(["read_resources"])
def generate_api_key():
    username = session['user']['preferred_username']
    new_key = secrets.token_hex(32)

    conn = get_connection()
    conn.set_api_key(username, new_key)

    flash("Successfully updated API key.", "alert-success")

    return render_template('auth/generate_api_key.html', api_key = new_key)


