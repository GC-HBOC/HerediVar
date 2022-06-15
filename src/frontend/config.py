import os

basedir = os.path.abspath(os.path.dirname(__file__))
host = 'SRV018.img.med.uni-tuebingen.de'

# register users at:
# http://srv018.img.med.uni-tuebingen.de:5050/admin/HerediVar/console/
# see for a tutorial: https://www.keycloak.org/docs/latest/server_admin/#_fine_grain_permissions

class Config(object):
    SECRET_KEY = '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b' # should be 32 byte
    LOGS_FOLDER = 'downloads/logs/'
    CONSENSUS_CLASSIFICATION_REPORT_FOLDER = 'downloads/consensus_classification_reports/'
    HOST = host

    KEYCLOAK_PORT = '5050'
    ISSUER = os.environ.get('ISSUER', "http://"+HOST+':'+KEYCLOAK_PORT+'/realms/HerediVar')
    CLIENTID = os.environ.get('CLIENT_ID', 'flask-webapp')
    CLIENTSECRET = os.environ.get('CLIENT_SECRET', 'NRLzlQfotGy9W8hkuYFm3T48Bjnti15k')
    DISCOVERYURL = f'{ISSUER}/.well-known/openid-configuration'

    # configuration of server side session from flask-session module
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    #app.config["SESSION_COOKIE_SECURE"] = True
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/flask_sessions"


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    TLS = False
    os.environ['NO_PROXY'] = host