from flask import Flask
from authlib.integrations.flask_client import OAuth
from flask_session import Session # alternatives: flask-caching, flask-kvsesssion
from urllib.parse import urlparse, urljoin
# for celery
from celery import Celery
from config import Config
# for logging
import logging
from flask.logging import default_handler
from logging.handlers import RotatingFileHandler
from pathlib import Path


oauth = OAuth()
sess = Session()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(object_name)
    sess.init_app(app=app)

    oauth.init_app(app=app)
    oauth.register(
        name='keycloak',
        client_id=app.config['CLIENTID'],
        client_secret=app.config['CLIENTSECRET'],
        server_metadata_url=app.config['DISCOVERYURL'],
        client_kwargs={
            'scope': 'openid email profile',
            'code_challenge_method': 'S256'  # enable PKCE
        }
    )

    celery.conf.update(app.config)


    from .main import create_module as main_create_module
    from .variant import create_module as variant_create_module
    from .doc import create_module as doc_create_module
    from .extended_information import create_module as extended_information_create_module
    from .io import create_module as io_create_module
    from .auth import create_module as auth_create_module
    from .user import create_module as user_create_module
    from .errorhandlers import create_module as errorhandlers_create_module

    main_create_module(app)
    variant_create_module(app)
    io_create_module(app)
    doc_create_module(app)
    extended_information_create_module(app)
    auth_create_module(app)
    user_create_module(app)
    errorhandlers_create_module(app)


    configure_logging(app)

    from .utils import request_has_connection, get_connection
    @app.teardown_request
    def close_db_connection(ex):
        if not app.config['TESTING']:
            if request_has_connection():
                conn = get_connection()
                conn.close()
                app.logger.debug("Closed db connection")

    return app



def configure_logging(app):
    app.logger.removeHandler(default_handler) # deactivate the default flask logging handler

    # set up new handler which writs to a file & add it to the app
    Path("logs/webapp/").mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler('logs/webapp/webapp.log', maxBytes=16384, backupCount=20)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(module)s>%(filename)s: %(lineno)d]') # format of the logged messages
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)