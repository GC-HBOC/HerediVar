import os
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions
from redis import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.client import Redis
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    TimeoutError
)

functions.read_dotenv()

# register users at:
# http://srv018.img.med.uni-tuebingen.de:5050/admin/HerediVar/console/
# see for a tutorial: https://www.keycloak.org/docs/latest/server_admin/#_fine_grain_permissions

#set environment variables: export CLINVAR_API_KEY=12345

# example discovery url: http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/.well-known/openid-configuration

class Config(object):

    weapp_env = functions.load_webapp_env()

    HOST = os.environ.get('HOST')
    PORT = os.environ.get('PORT')

    ##### production config ####
    TESTING = False
    DEBUG = False
    TLS = True

    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') # should be at least 32 byte, used for signing the session objects

    # keycloak
    KEYCLOAK_PORT = os.environ.get('KEYCLOAK_PORT', "5050")
    KEYCLOAK_HOST = os.environ.get('KEYCLOAK_HOST', 'localhost')
    KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'HerediVar')
    KEYCLOAK_BASEPATH = "http://"+KEYCLOAK_HOST + ":" + KEYCLOAK_PORT
    ISSUER = os.environ.get('ISSUER', "http://"+KEYCLOAK_HOST+':'+KEYCLOAK_PORT+'/realms/HerediVar')
    CLIENTID = os.environ.get('CLIENT_ID')
    CLIENTSECRET = os.environ.get('CLIENT_SECRET')
    DISCOVERYURL = f'{ISSUER}/.well-known/openid-configuration'

    # redis
    REDIS_PORT = os.environ.get('REDIS_PORT')
    REDIS_HOST = 'localhost'
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

    # configuration of server side session from flask-session module
    SESSION_PERMANENT = True
    
    SESSION_TYPE = 'redis'
    retry = Retry(ExponentialBackoff(), 3)
    SESSION_REDIS = Redis.from_url(REDIS_URL, retry=retry, retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError]) # use exponential backoff with 3 tries on specific redis errors
    
    #SESSION_USE_SIGNER = True # deprecated
    #SESSION_TYPE = "filesystem"
    #SESSION_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/flask_sessions"
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True

    # other folders
    #RESOURCES_FOLDER = 'resources/'
    #LOGS_FOLDER = 'downloads/logs/'
    #CONSENSUS_CLASSIFICATION_REPORT_FOLDER = 'downloads/consensus_classification_reports/'

    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    result_backend = REDIS_URL

    # orphanet
    ORPHANET_DISCOVERY_URL = "https://api.orphacode.org/EN/ClinicalEntity"
    ORPHANET_API_KEY = 'HerediVar'

    # mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEBUG = False

    # misc
    VCF_FILE_IMPORT_ACTIVE = False



class ProdConfig(Config):
    # keycloak
    KEYCLOAK_HOST = os.environ.get('KEYCLOAK_HOST', 'localhost')
    KEYCLOAK_PORT = '8080'
    KEYCLOAK_BASEPATH = "https://"+KEYCLOAK_HOST+"/kc"
    ISSUER = os.environ.get('ISSUER', KEYCLOAK_BASEPATH + "/realms/HerediVar")
    CLIENTID = os.environ.get('CLIENT_ID')
    CLIENTSECRET = os.environ.get('CLIENT_SECRET')
    DISCOVERYURL = f'{ISSUER}/.well-known/openid-configuration'

    # sesssion
    SESSION_COOKIE_SECURE = True
    #SESSION_COOKIE_NAME = "__Host-"
    

class DevConfig(Config):
    DEBUG = True
    TLS = False

    #HOST = "SRV018.img.med.uni-tuebingen.de"
    #SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b') # should be at least 32 byte, used for signing the session objects
    #CLIENTSECRET = os.environ.get('CLIENT_SECRET', 'NRLzlQfotGy9W8hkuYFm3T48Bjnti15k')


class LocaltestConfig(Config):
    #HOST = "SRV018.img.med.uni-tuebingen.de"
    TESTING = True
    DEBUG = True
    TLS = False

    HOST = os.environ.get('HOST')
    PORT = os.environ.get('PORT')
    SERVER_NAME = HOST + ':' + PORT # add port to url_for()


