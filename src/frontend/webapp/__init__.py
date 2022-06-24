from flask import Flask
from authlib.integrations.flask_client import OAuth
from flask_session import Session # alternatives: flask-caching, flask-kvsesssion

oauth = OAuth()
sess = Session()

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


    from .main import create_module as main_create_module
    from .variant import create_module as variant_create_module
    from .doc import create_module as doc_create_module
    from .extended_information import create_module as extended_information_create_module
    from .io import create_module as io_create_module
    from .auth import create_module as auth_create_module
    from .user import create_module as user_create_module

    main_create_module(app)
    variant_create_module(app)
    io_create_module(app)
    doc_create_module(app)
    extended_information_create_module(app)
    auth_create_module(app)
    user_create_module(app)

    return app