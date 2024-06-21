import os
import sys
import requests
from flask import url_for, session, current_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from ..utils import *
from requests.models import Response
import secrets
import string


##############################################
######### ACCOUNT MANAGER FUNCTIONS ##########
##############################################

def register_user(username, email, affiliation, first_name, last_name):
    #curl --location --request POST 'http://localhost:8080/auth/admin/realms/appsdeveloperblog/users' \
    #--header 'Content-Type: application/json' \
    #--header 'Authorization: Bearer xxx' \
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


def grant_roles(kc_user_id, roles, avail_roles):
    url = current_app.config['KEYCLOAK_BASEPATH'] + "/admin/realms/" + current_app.config['KEYCLOAK_REALM'] + "/users/" + kc_user_id + "/role-mappings/realm"
    token = session['tokenResponse']['access_token']
    header = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = []
    for role in roles:
        role_to_add = avail_roles[int(role)]
        del role_to_add['index'] # delete the index field as keycloak doesnt like extra fields
        data.append(role_to_add)
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


# get roles of a user
# GET /admin/realms/HerediVar/users/13a14581-43e3-4d21-8d60-a7de7d9214cc/role-mappings/realm
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
        if role['name'] not in ['default-roles-heredivar']:
            result.append(role2id[role['id']])
    return result


def get_role_to_id(avail_roles):
    res = {}
    for role in avail_roles:
        res[role['id']] = role['index']
    return res


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

# get available role mappings
#GET /admin/realms/HerediVar/users/13a14581-43e3-4d21-8d60-a7de7d9214cc/role-mappings/realm/available





################################################
######### USER SELF-SERVICE FUNCTIONS ##########
################################################

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
    if current_app.config["TESTING"]:
        email_verified = True

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

