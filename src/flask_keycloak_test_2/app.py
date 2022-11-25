import json
import os

import certifi
import requests
from authlib.oauth2.rfc6749 import OAuth2Token
from flask import Flask, url_for, session, request
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth, token_update
from authlib.integrations.flask_oauth2 import ResourceProtector
from functools import wraps
from flask_session import Session
from redis import Redis
from authlib.oauth2.rfc7636 import create_s256_code_challenge


# validate bearer token
from authlib.oauth2.rfc7662 import IntrospectTokenValidator

# decode jwt
from authlib.oidc.core import CodeIDToken
from authlib.jose import jwt

print("Using cacerts from " + certifi.where())
host = "SRV018.img.med.uni-tuebingen.de"

app = Flask(__name__)
app.secret_key = '!secret'

# configuration of server side session from flask-session module
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = Redis(host=host, port=6996, db=0)
app.config["SESSION_FILE_DIR"] = os.path.dirname(os.path.abspath(__file__)) + "/flask_sessions"
Session(app)


issuer = os.environ.get('ISSUER', "http://"+host+':5050/realms/HerediVar')
clientId = os.environ.get('CLIENT_ID', 'flask-webapp')
clientSecret = os.environ.get('CLIENT_SECRET', 'NRLzlQfotGy9W8hkuYFm3T48Bjnti15k')
os.environ['NO_PROXY'] = host
oidcDiscoveryUrl = f'{issuer}/.well-known/openid-configuration'


oauth = OAuth(app=app
              #, update_token=update_token
              )
oauth.register(
    name='keycloak',
    client_id=clientId,
    client_secret=clientSecret,
    server_metadata_url=oidcDiscoveryUrl,
    client_kwargs={
        'scope': 'openid email profile',
        'code_challenge_method': 'S256'  # enable PKCE
    }
)


# a session alternative to the above
#from authlib.integrations.requests_client import OAuth2Session
#client = OAuth2Session(clientId, clientSecret, scope='openid email profile', code_challenge_method='S256')
#authorization_endpoint = 'http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/protocol/openid-connect/auth'
#token_endpoint = "http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/protocol/openid-connect/token"
#user_info_endpoint = "http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/protocol/openid-connect/userinfo"


# a decorator which redirects to the login page if the user is not logged in. 
# Also sets the 'next' parameter to redirect to the page which called the require_login decorator
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # user is not logged in -> promt a login
        if session.get('user') is None:
            return redirect(url_for('login', next=request.url))
        
        # user is logged in -> check if access token is still valid using introspect endpoint --> introspect endpoint can be omitted if token is validated locally using some jwt lib
        
        token = session['tokenResponse']
        
        url = f'{issuer}/protocol/openid-connect/token/introspect'
        data = {'token': token.get("access_token"), 'token_type_hint': 'access_token', 'username': session['user']['preferred_username'], 'client_secret': clientSecret, 'client_id': clientId}
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
                print(request.url)
                return redirect(url_for('logout', next_logout=url_for('login', next_login=request.url))) # logout and return to login page! with next= page which you wanted to access in the first place
        
        return f(*args, **kwargs)
    return decorated_function

# how to add new permission policies: https://stackoverflow.com/questions/42186537/resources-scopes-permissions-and-policies-in-keycloak (i was using the resource based permissions)
#def require_permission(f, resources):
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        token = session['tokenResponse']
#        url = f'{issuer}/protocol/openid-connect/token'
#        #scopes = ["read_resources"] #["edit_resources"] 
#        data = {'grant_type':'urn:ietf:params:oauth:grant-type:uma-ticket', 'audience':clientId, "permission":resources}
#        header = {'Authorization': f'Bearer {token.get("access_token")}'}
#        resp = requests.post(url, data=data, headers=header)
#        if resp.status_code != 200:
#            return str(resp.status_code) + ' ' + resp.text # redirect to error page here
#        return f(*args, **kwargs)
#    return decorated_function
#


def require_permission(resources):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = session['tokenResponse']
            url = f'{issuer}/protocol/openid-connect/token'
            #scopes = ["read_resources"] #["edit_resources"] 
            data = {'grant_type':'urn:ietf:params:oauth:grant-type:uma-ticket', 'audience':clientId, "permission":resources, 'response_mode':'decision'}
            header = {'Authorization': f'Bearer {token.get("access_token")}'}
            resp = requests.post(url, data=data, headers=header)
            print(resp.json()['result'])
            if resp.status_code != 200:
                return str(resp.status_code) + ' ' + resp.text # redirect to error page here
            return f(*args, **kwargs)
        return wrapper
    return decorator





# this function uses the refresh token to get a new access token and returns the status code from this call
def refresh_token():
    token = session['tokenResponse']

    url = f'{issuer}/protocol/openid-connect/token'
    data = {'client_id':clientId, 'client_secret': clientSecret, 'refresh_token': token['refresh_token'], 'grant_type': 'refresh_token'}
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



@app.route('/')
def index():
    user = session.get('user')
    prettyIdToken = None
    if user is not None:
        prettyIdToken = json.dumps(user, sort_keys=True, indent=4)
    return render_template('index.html', idToken=prettyIdToken)


@app.route('/login')
def login():
    # construct redirect uri: first redirect to keycloak login page
    # then redirect to auth with the next param which defaults to the '/' route
    # auth itself redirects to next ie. the page which required a login
    redirect_uri = url_for('auth', _external=True, next_login=request.args.get('next_login', '/'))

    return oauth.keycloak.authorize_redirect(redirect_uri)


@app.route('/auth')
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


    user_info = token_response['userinfo']

    
    if token_response:
        session['user'] = user_info
        session['tokenResponse'] = token_response

    return redirect(request.args.get('next_login', url_for('index')))


@app.route('/readonly')
@require_login
@require_permission(['read_resources'])
def readonly():
    # the following should be much easier...
    # see https://docs.authlib.org/en/latest/client/frameworks.html#auto-update-token
    token = session['tokenResponse']
    # get current access token
    # check if access token is still valid
    # if current access token is valid, use token for request
    # if current access token is invalid, use refresh token to obtain new access token
    # if sucessfull, update current access token, current refresh token
    # if current access token is valid, use token for request

    # call userinfo endpoint as an example
    #access_token = token['access_token']
    #userInfoEndpoint = f'{issuer}/protocol/openid-connect/userinfo'
    #userInfoResponse = requests.post(userInfoEndpoint,
    #                                 headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'})

    return "read route", 200


@app.route('/edit')
@require_login
@require_permission(['edit_resources'])
def edit():
    # the following should be much easier...
    # see https://docs.authlib.org/en/latest/client/frameworks.html#auto-update-token
    token = session['tokenResponse']
    # get current access token
    # check if access token is still valid
    # if current access token is valid, use token for request
    # if current access token is invalid, use refresh token to obtain new access token
    # if sucessfull, update current access token, current refresh token
    # if current access token is valid, use token for request

    # call userinfo endpoint as an example
    #access_token = token['access_token']
    #userInfoEndpoint = f'{issuer}/protocol/openid-connect/userinfo'
    #userInfoResponse = requests.post(userInfoEndpoint,
    #                                 headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'})

    return "edit route", 200


@app.route('/admin')
@require_login
@require_permission(['admin_resources'])
def admin():
    # the following should be much easier...
    # see https://docs.authlib.org/en/latest/client/frameworks.html#auto-update-token
    token = session['tokenResponse']
    # get current access token
    # check if access token is still valid
    # if current access token is valid, use token for request
    # if current access token is invalid, use refresh token to obtain new access token
    # if sucessfull, update current access token, current refresh token
    # if current access token is valid, use token for request

    # call userinfo endpoint as an example
    #access_token = token['access_token']
    #userInfoEndpoint = f'{issuer}/protocol/openid-connect/userinfo'
    #userInfoResponse = requests.post(userInfoEndpoint,
    #                                 headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'})

    return "admin_route", 200


@app.route('/testprotect')
@require_login
def testprotect():
    return 'you need to login to see this'
    

@app.route('/logout')
def logout():
    tokenResponse = session.get('tokenResponse')

    if tokenResponse is not None:
        # propagate logout to Keycloak
        refreshToken = tokenResponse['refresh_token']
        endSessionEndpoint = f'{issuer}/protocol/openid-connect/logout'

        requests.post(endSessionEndpoint, data={
            "client_id": clientId,
            "client_secret": clientSecret,
            "refresh_token": refreshToken,
        })

    session.pop('user', None)
    session.pop('tokenResponse', None)
    return redirect(request.args.get('next_logout', url_for('index')))


if __name__ == '__main__':
    app.run(host=host, port=5000, debug=True)