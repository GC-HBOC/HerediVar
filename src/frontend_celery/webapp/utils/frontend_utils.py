from flask import flash, Markup, g, request, current_app, redirect, url_for, session
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions

from urllib.parse import urlparse, urljoin


# this prevents open redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    allowed_schemes = ('http')
    if current_app.config.get('TLS', True):
        allowed_schemes = ('https')
    is_same_scheme = test_url.scheme in allowed_schemes
    is_same_netloc = ref_url.netloc == test_url.netloc
    return is_same_scheme and is_same_netloc
           

def save_redirect(target):
    if not target or not is_safe_url(target):
        current_app.logger.error("Unsafe redirect url detected: " + str(target))
        return redirect(url_for('main.index')) # maybe use abort() here??
    return redirect(target) # url is save to redirect to!




def is_user_logged_in():
    resp = session.get('tokenResponse', None)
    if resp is None:
        return False
    return True

def get_preferred_username():
    user_obj = session.get('user', None)
    if user_obj is not None:
        return user_obj['preferred_username']
    return "Anonymous user"

def request_has_connection():
    return hasattr(g, 'dbconn')


def get_connection():
    user = session.get('user')
    if user is None:
        roles = ['read_only']
    else:
        roles = user.get('roles', ['read_only'])
    if not request_has_connection():
        #print(roles)
        g.dbconn = Connection(roles)        
        current_app.logger.debug("established db connection")
    return g.dbconn




def strength_to_text(strength, scheme):
    if 'acmg' in scheme:
        if strength == 'pvs':
            return 'very strong pathogenic'
        if strength == 'ps':
            return 'strong pathogenic'
        if strength == 'pm':
            return 'moderate pathogenic'
        if strength == 'pp':
            return 'supporting pathogenic'
        if strength == 'bp':
            return 'supporting benign'
        if strength == 'bs':
            return 'strong benign'
        if strength == 'ba':
            return 'stand-alone benign'
    
    if 'task-force' in scheme:
        if strength == 'pvs':
            return 'pathogenic'
        if strength == 'ps':
            return 'likely pathogenic'
        if strength == 'pm':
            return 'likely benign'
        if strength == 'pp':
            return 'benign'
        if strength == 'bp':
            return 'uncertain'