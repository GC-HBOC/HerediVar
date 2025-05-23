
import sys
import os
from flask import Flask
from authlib.integrations.flask_client import OAuth
from flask_session import Session # alternatives: flask-caching, flask-kvsesssion
from urllib.parse import urlparse, urljoin
# for celery
from celery import Celery
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common import paths, functions
#from annotation_service.heredicare_interface import Heredicare_Flask
# for logging
import logging
from flask.logging import default_handler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask_mail import Mail


oauth = OAuth()
sess = Session()
celery = Celery(__name__, backend="redis", 
    broker=Config.CELERY_BROKER_URL,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    result_backend=Config.result_backend
)
mail = Mail()
#heredicare = Heredicare_Flask()


def create_app():
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """

    env = functions.load_webapp_env()
    object_name = 'config.%sConfig' % env.capitalize()
    print(object_name)

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

    mail.init_app(app=app)

    #heredicare.init_app(app=app)


    from .main import create_module as main_create_module
    from .variant import create_module as variant_create_module
    from .extended_information import create_module as extended_information_create_module
    from .download import create_module as download_create_module
    from .auth import create_module as auth_create_module
    from .user import create_module as user_create_module
    from .errorhandlers import create_module as errorhandlers_create_module
    from .upload import create_module as upload_create_module
    from .api import create_module as api_create_module

    main_create_module(app)
    variant_create_module(app)
    download_create_module(app)
    extended_information_create_module(app)
    auth_create_module(app)
    user_create_module(app)
    errorhandlers_create_module(app)
    upload_create_module(app)
    api_create_module(app)


    configure_logging(app)

    from .utils import request_has_connection, get_connection
    @app.teardown_request
    def close_db_connection(ex):
        if request_has_connection():
            conn = get_connection()
            conn.close()
            app.logger.debug("Closed db connection")

    #@app.after_request
    #def add_header(response):
    #    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    #    response.headers['Content-Security-Policy'] = "default-src 'self' 'report-sample'; img-src 'self' data:; " #script-src 'self' 'wasm-unsafe-eval'
    #    return response

    return app








def configure_logging(app):
    app.logger.removeHandler(default_handler) # deactivate the default flask logging handler

    # set up new handler which writs to a file & add it to the app
    Path(paths.webapp_log_dir).mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(paths.webapp_log, maxBytes=16384, backupCount=20)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(module)s>%(filename)s: %(lineno)d]') # format of the logged messages
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)