import os
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions


functions.read_dotenv()

# register users at:
# http://srv018.img.med.uni-tuebingen.de:5050/admin/HerediVar/console/
# see for a tutorial: https://www.keycloak.org/docs/latest/server_admin/#_fine_grain_permissions

#set environment variables: export CLINVAR_API_KEY=12345

# example discovery url: http://srv018.img.med.uni-tuebingen.de:5050/realms/HerediVar/.well-known/openid-configuration

class Config(object):

    webapp_env = os.environ.get('WEBAPP_ENV', None)

    if webapp_env is None:
        raise ValueError("No WEBAPP_ENV environment variable set.")

    HOST = os.environ.get('HOST')
    print("HOSTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT:")
    print(HOST)

    ##### production config ####
    TESTING = False
    DEBUG = False
    TLS = True

    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') # should be at least 32 byte, used for signing the session objects

    # keycloak
    KEYCLOAK_PORT = '5050'
    ISSUER = os.environ.get('ISSUER', "http://"+HOST+':'+KEYCLOAK_PORT+'/realms/HerediVar')
    CLIENTID = os.environ.get('CLIENT_ID')
    CLIENTSECRET = os.environ.get('CLIENT_SECRET')
    DISCOVERYURL = f'{ISSUER}/.well-known/openid-configuration'


    CLINVAR_API_ENDPOINT = "https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions" # test endpoint



    # configuration of server side session from flask-session module
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    #SESSION_COOKIE_SECURE = True
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/flask_sessions"

    # other folders
    RESOURCES_FOLDER = 'resources/'
    LOGS_FOLDER = 'downloads/logs/'
    CONSENSUS_CLASSIFICATION_REPORT_FOLDER = 'downloads/consensus_classification_reports/'

    # Celery configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # clinvar
    CLINVAR_API_KEY = os.environ.get('CLINVAR_API_KEY')

    # orphanet
    ORPHANET_DISCOVERY_URL = "https://api.orphacode.org/EN/ClinicalEntity"
    ORPHANET_API_KEY = 'HerediVar'


class ProdConfig(Config):
    pass

    

class DevConfig(Config):
    
    DEBUG = True
    TLS = False

    os.environ['NO_PROXY'] = 'SRV018.img.med.uni-tuebingen.de'

    #HOST = "SRV018.img.med.uni-tuebingen.de"
    #SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b') # should be at least 32 byte, used for signing the session objects
    #CLIENTSECRET = os.environ.get('CLIENT_SECRET', 'NRLzlQfotGy9W8hkuYFm3T48Bjnti15k')


class GithubtestConfig(Config):
    #HOST = "127.0.0.1" # localhost
    TESTING = True
    DEBUG = True
    TLS = False



class LocaltestConfig(Config):
    #HOST = "SRV018.img.med.uni-tuebingen.de"
    TESTING = True
    DEBUG = True
    TLS = False
