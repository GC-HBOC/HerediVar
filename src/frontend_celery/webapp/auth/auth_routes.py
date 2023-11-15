import json
import os
import sys
import certifi
import requests
from authlib.oauth2.rfc6749 import OAuth2Token
from flask import url_for, session, request, Blueprint, current_app
from flask import render_template, redirect
from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from flask_session import Session
from authlib.oauth2.rfc7636 import create_s256_code_challenge
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from .. import oauth
from ..utils import *
from ..tasks import notify_new_user
from requests.models import Response
import secrets
import string


auth_blueprint = Blueprint(
    'auth',
    __name__
)




def register_user(username, email, affiliation, first_name, last_name):
    #curl --location --request POST 'http://localhost:8080/auth/admin/realms/appsdeveloperblog/users' \
    #--header 'Content-Type: application/json' \
    #--header 'Authorization: Bearer ..G9----VZjeIpbmffN-YGrUVywziymBRwA7FFLAxcf6jS5548HVxxKeMPIvNEfDG7eWw' \
    #--data-raw '{"firstName":"Sergey","lastName":"Kargopolov", "email":"test@test.com", "enabled":"true", "username":"app-user"}'

    #{"attributes": {"id": ["688"]}}

    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {"enabled": 'true', "attributes": {"affiliation": [affiliation]}, "groups": [], "username": username, "emailVerified": "", "firstName": first_name, "lastName": last_name, "email": email}
    resp = requests.post(url = url, json = data, headers = header)
    print('User creation: ' + str(resp.status_code))
    return resp


def get_users(username = None):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    if username is not None:
        data = {'username': username, 'exact': 'true'}
        resp = requests.get(url = url, params = data, headers = header)
    else:
        resp = requests.get(url = url, headers = header)
    print('Get user: ' + str(resp.status_code))
    if resp.status_code == 200:
        users = resp.json()
        if len(users) == 1:
            return users[0]
        return users
    return None

#GET http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/account/
def get_profile():
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/realms/" + current_app.config['KEYCLOAK_REALM'] + "/account"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    resp = requests.get(url = url, headers = header)
    print('Get profile: ' + str(resp.status_code))
    if resp.status_code == 200:
        return resp.json()
    return None

def get_roles():
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/roles"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    resp = requests.get(url = url, headers = header)
    print('Get roles: ' + str(resp.status_code))
    if resp.status_code == 200:
        roles = resp.json()
        result = []
        i = 0
        for role in roles:
            if role['name'] in ['read_only', 'account_manager', 'super_user', 'user']:
                role['index'] = i
                result.append(role)
                i = i + 1
        return result
    return []

def get_role_to_id(avail_roles):
    res = {}
    for role in avail_roles:
        res[role['id']] = role['index']
    return res


#GET http://srv018.img.med.uni-tuebingen.de:5050/admin/realms/HerediVar/users/338acea6-73a3-49f5-a4d8-57095d33b428/role-mappings/realm
def get_roles_of_user(kc_user_id, avail_roles):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users/" + kc_user_id + "/role-mappings/realm"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    resp = requests.get(url = url, headers = header)
    print('Get roles of user: ' + str(resp.status_code))
    set_roles = resp.json()
    role2id = get_role_to_id(avail_roles)
    result = []
    for role in set_roles:
        #role['index'] = role2id[role['id']]
        if role['name'] not in ['default-roles-heredivar']:
            result.append(role2id[role['id']])
    return result

def grant_roles(kc_user_id, roles, avail_roles):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users/" + kc_user_id + "/role-mappings/realm"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = []
    for role in roles:
        role_to_add = avail_roles[int(role)]
        del role_to_add['index'] # delete the index field as keycloak doesnt like extra fields
        data.append(role_to_add)
    #data = [
    #    {"id":"788ca15c-6c7a-4ffe-9a63-da0fcfb1960e","name":"account_manager"},
    #    {"id":"882841ac-dc3b-493b-9f22-5a85e4ee5556","name":"super_user"}
    #]
    resp = requests.post(url = url, json = data, headers = header)
    print('Grant roles: ' + str(resp.status_code))
    return resp


#DELETE /admin/realms/HerediVar/users/338acea6-73a3-49f5-a4d8-57095d33b428/role-mappings/realm
def delete_roles(kc_user_id, roles, avail_roles):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users/" + kc_user_id + "/role-mappings/realm"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = []
    for role in roles:
        role_to_add = avail_roles[int(role)]
        del role_to_add['index'] # delete the index field as keycloak doesnt like extra fields
        data.append(role_to_add)
    resp = requests.delete(url = url, json = data, headers = header)
    print('Delete roles: ' + str(resp.status_code))
    return resp


#PUT http://srv018.img.med.uni-tuebingen.de:5050/admin/realms/HerediVar/users/9a5d58c0-4ab3-4c64-b918-2825f5c54701/reset-password
def reset_password(kc_user_id):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users/" + kc_user_id + "/reset-password"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(10))
    data = {"type":"password", "value":password, "temporary":True}

    resp = requests.put(url = url, headers = header, json = data)
    print('Reset password: ' + str(resp.status_code))
    return resp, password



@auth_blueprint.route('/register', methods=['GET', 'POST'])
@require_permission(['account_manager_resources'])
def register():

    roles = get_roles()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        affiliation = request.form.get('affiliation')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        selected_roles = request.form.getlist('role') # a list of role indexes -> this id resembles the number in the array returned from get_roles()

        #admin_token = get_admin_token()
        resp = register_user(username, email, affiliation, first_name, last_name)
        if resp.status_code == 201: # user creation was successful
            new_user = get_users(username)
            if new_user is not None: # get user id was successful
                kc_user_id = new_user['id']
                resp, password = reset_password(kc_user_id)
                if resp.status_code == 204: # set password was successful
                    resp = grant_roles(kc_user_id, selected_roles, roles)
                    if resp.status_code == 204: # grant roles was successful
                        flash("New user created successfully!", 'alert-success')
                        task = notify_new_user.apply_async(args=[first_name + ' ' + last_name, email, username, password])
                        return redirect(url_for('auth.register'))

        flash(resp.json(), 'alert-danger')

    return render_template('auth/register.html', roles = roles)


# get available role mappings
#GET http://srv018.img.med.uni-tuebingen.de:5050/admin/realms/HerediVar/users/13a14581-43e3-4d21-8d60-a7de7d9214cc/role-mappings/realm/available

# get roles of a user
# GET /admin/realms/HerediVar/users/13a14581-43e3-4d21-8d60-a7de7d9214cc/role-mappings/realm


@auth_blueprint.route('/show_users')
@require_permission(['account_manager_resources'])
def show_users():
    
    users = get_users()

    return render_template('auth/show_users.html', users = users)


#PUT http://srv018.img.med.uni-tuebingen.de:5050/admin/realms/HerediVar/users/338acea6-73a3-49f5-a4d8-57095d33b428
def update_user_information(kc_user_id, username, first_name, last_name, e_mail, affiliation, enabled):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users/" + kc_user_id
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    #
    user = get_users(username)

    if e_mail != user['email']:
        email_verified = False
    else:
        email_verified = user['emailVerified']

    data = {
        "id":user['id'],
        "username":user['username'],
        "enabled":enabled,
        "emailVerified":email_verified,
        "firstName":first_name,
        "lastName":last_name,
        "email":e_mail,
        "attributes":{"affiliation":[affiliation]},
        }

    resp = requests.put(url = url, headers = header, json = data)
    print("Update user information: " + str(resp.status_code))
    return resp


def get_added_and_deleted_roles(set_roles, new_roles):
    added_roles = []
    deleted_roles = []

    for role_index in set_roles:
        if role_index not in new_roles:
            deleted_roles.append(role_index)
    
    for new_role_index in new_roles:
        if new_role_index not in set_roles:
            added_roles.append(new_role_index)

    return added_roles, deleted_roles
        



@auth_blueprint.route('/edit_user/<string:username>', methods = ['GET', 'POST'])
@require_permission(['account_manager_resources'])
def edit_user(username):
    
    user = get_users(username)
    kc_user_id = user['id']
    avail_roles = get_roles()
    set_roles = get_roles_of_user(kc_user_id, avail_roles)

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
        
        if enabled == 'on':
            enabled = True
        else:
            enabled = False

        resp = update_user_information(kc_user_id, user['username'], first_name, last_name, e_mail, affiliation, enabled)


        added_roles, deleted_roles = get_added_and_deleted_roles(set_roles, new_roles)
        resp = grant_roles(kc_user_id, added_roles, avail_roles)
        resp = delete_roles(kc_user_id, deleted_roles, avail_roles)


        if resp.status_code == 204:
            flash('Successfully changed user information!', 'alert-success')
            return redirect(url_for('auth.edit_user', username = username))
        flash(resp.json(), 'alert-danger')


    return render_template('auth/edit_user.html', user = user, avail_roles = avail_roles, set_roles = set_roles)





# Edit general info
# POST http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/account/
def edit_general_info(username, e_mail, first_name, last_name, affiliation):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/realms/" + current_app.config['KEYCLOAK_REALM'] + "/account/"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    #{"id":"3fab0e7f-0a56-4982-83e4-de6145b0238f",
    # "username":"superuser",
    # "firstName":"Lydiaa",
    # "lastName":"Todd",
    # "email":"superuser@testmail.com",
    # "emailVerified":true,
    # "userProfileMetadata":{"attributes":[{"name":"username","displayName":"${username}","required":true,"readOnly":true,"validators":{}},{"name":"email","displayName":"${email}","required":true,"readOnly":false,"validators":{"email":{"ignore.empty.value":true}}},{"name":"firstName","displayName":"${firstName}","required":true,"readOnly":false,"validators":{}},{"name":"lastName","displayName":"${lastName}","required":true,"readOnly":false,"validators":{}}]},
    # "attributes":{"affiliation":["affiliation3"],"locale":["en"]}}
    user = get_profile()

    #print(user)

    if len(user) == 0:
        resp = Response()
        resp.code = "not found"
        resp.error_type = "notfound"
        resp.status_code = 404
        resp._content = b'{ "errorMessage" : "No such user" }'
        return resp


    email_verified = user['emailVerified']
    if e_mail != user['email']:
        email_verified = False
        

    data = {
        "id":user['id'],
        "username":user['username'],
        "emailVerified":email_verified,
        "firstName":first_name,
        "lastName":last_name,
        "email":e_mail,
        "attributes":{"affiliation":[affiliation]},
        }
    
    resp = requests.post(url = url, headers = header, json = data)
    return resp



@auth_blueprint.route('/change_password')
@require_login
def change_password():
    return redirect(current_app.config['KEYCLOAK_BASEPATH'] + "/realms/" + current_app.config['KEYCLOAK_REALM'] + "/account/#/security/signingin")
    #return redirect(current_app.config['KEYCLOAK_BASEPATH'] + "/realms/HerediVar/protocol/openid-connect/auth?redirect_uri=http%3A%2F%2Fsrv018.img.med.uni-tuebingen.de%3A5050%2Frealms%2FHerediVar%2Faccount%2F%23%2Fsecurity%2Fsigningin")
    #/realms/myrealm/protocol/openid-connect/auth
    #?response_type=code
    #&client_id=myclient
    #&redirect_uri=https://myclient.com
    #&kc_action=update_profile


@auth_blueprint.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():

    username = session['user']['preferred_username']
    print(username)

    user = get_profile()
        
    if request.method == 'POST':
        e_mail = request.form.get('e_mail')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        affiliation = request.form.get('affiliation')
        if any([x is None for x in [e_mail, first_name, last_name, affiliation]]):
            flash('All fields are required!', 'alert-danger')
            return render_template('auth/profile', user = user)
        
        resp = edit_general_info(username, e_mail, first_name, last_name, affiliation)
        if resp.status_code == 204:
            flash("Successfully changed information", 'alert-success')
            return redirect(url_for('auth.profile'))
        return resp.json()

    return render_template('auth/profile.html', user = user)













@auth_blueprint.route('/login')
def login():

    # you can not use the regular login route during testing because this redirects to the keycloak form which can not
    # be filled computationally
    if current_app.config.get('TESTING', False):
        issuer = current_app.config['ISSUER']
        url = f'{issuer}/protocol/openid-connect/token'
        data = {'client_id':current_app.config['CLIENTID'], 'client_secret': current_app.config['CLIENTSECRET'], 'grant_type': 'password', 'username': 'superuser', 'password': '12345'}
        token_response = requests.post(url = url, data=data)
        assert token_response.status_code == 200
        session['tokenResponse'] = token_response.json()

        url = f'{issuer}/protocol/openid-connect/userinfo'
        data = {'token': session["tokenResponse"]["access_token"], 'token_type_hint': 'access_token', 'client_secret': current_app.config['CLIENTSECRET'], 'client_id': current_app.config['CLIENTID']}
        header = {'Authorization': f'Bearer {session["tokenResponse"]["access_token"]}'}
        user_response = requests.post(url = url, data=data, headers=header)
        assert user_response.status_code == 200
        user_info = user_response.json()
        
        # this is only to record which user made which actions in the database and has nothing to do with authenitication
        username = user_info['preferred_username']
        first_name = user_info['given_name']
        last_name = user_info['family_name']
        affiliation = user_info.get('affiliation')

        # init the session
        session['user'] = user_info

        if affiliation is None or affiliation.strip() == '':
            flash('LOGIN ERROR: You are missing the affiliation tag ask a HerediVar administrator to add it!', 'alert-danger')
            current_app.logger.error("Could not login user " + username + ", because the user was missing affiliation tag in keycloak.")
            return redirect(url_for('auth.logout', auto_logout='True'))
        conn = Connection(session['user']['roles'])
        conn.insert_user(username, first_name, last_name, affiliation) # this inserts only if the user is not already in the database and updates the information if the information changed (except for username this one has to stay)
        user_info['user_id'] = conn.get_user_id(username)
        conn.close()

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
        

        # this is only to record which user made which actions in the database and has nothing to do with authenitication
        username = user_info['preferred_username']
        first_name = user_info['given_name']
        last_name = user_info['family_name']
        affiliation = user_info.get('affiliation')

        # init the session
        session['user'] = user_info
        session['tokenResponse'] = token_response

        print(session['user'])

        if affiliation is None or affiliation.strip() == '':
            flash('LOGIN ERROR: You are missing the affiliation tag ask a HerediVar administrator to add it!', 'alert-danger')
            current_app.logger.error("Could not login user " + username + ", because the user was missing affiliation tag in keycloak.")
            return redirect(url_for('auth.logout', auto_logout='True'))
        conn = Connection(session['user']['roles'])
        conn.insert_user(username, first_name, last_name, affiliation) # this inserts only if the user is not already in the database and updates the information if the information changed (except for username this one has to stay)
        user_info['user_id'] = conn.get_user_id(username)
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

