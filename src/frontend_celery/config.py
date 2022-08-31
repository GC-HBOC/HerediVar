import os

basedir = os.path.abspath(os.path.dirname(__file__))

# register users at:
# http://srv018.img.med.uni-tuebingen.de:5050/admin/HerediVar/console/
# see for a tutorial: https://www.keycloak.org/docs/latest/server_admin/#_fine_grain_permissions

#set environment variables: export CLINVAR_API_KEY=12345

class Config(object):
    # basic config
    SECRET_KEY = '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b' # should be at least 32 byte, used for signing the session objects
    HOST = 'SRV018.img.med.uni-tuebingen.de'

    # keycloak config
    KEYCLOAK_PORT = '5050'
    ISSUER = os.environ.get('ISSUER', "http://"+HOST+':'+KEYCLOAK_PORT+'/realms/HerediVar')
    CLIENTID = os.environ.get('CLIENT_ID', 'flask-webapp')
    CLIENTSECRET = os.environ.get('CLIENT_SECRET', 'NRLzlQfotGy9W8hkuYFm3T48Bjnti15k')
    DISCOVERYURL = f'{ISSUER}/.well-known/openid-configuration'

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


class ProdConfig(Config):
    TLS = True
    DEBUG = False
    TESTING = False
    HOST = "host not specified"


class DevConfig(Config):
    DEBUG = True
    TLS = False
    os.environ['NO_PROXY'] = 'SRV018.img.med.uni-tuebingen.de'
    TESTING = False
    HOST = "SRV018.img.med.uni-tuebingen.de"

class TestConfig(Config):
    TESTING = True
    HOST = "127.0.0.1"
    DEBUG = True
    TLS = False

    KEYCLOAK_PORT = '5050'
    ISSUER = os.environ.get('ISSUER', "http://"+HOST+':'+KEYCLOAK_PORT+'/realms/HerediVar')
    CLIENTID = os.environ.get('CLIENT_ID', 'flask-webapp')
    CLIENTSECRET = os.environ.get('CLIENT_SECRET', 'NRLzlQfotGy9W8hkuYFm3T48Bjnti15k')
    DISCOVERYURL = f'{ISSUER}/.well-known/openid-configuration'