from webapp import create_app
from flask import request
import os

def test_home_page(test_client):
    """
    when the '/' page is requested (GET) check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200

        
    
def test_config(config):
    """
    This test ensures that sensitive data was read from a
    secure location & was set properly in the client
    """
    environment_secret_key = os.environ.get('FLASK_SECRET_KEY')
    flask_secret_key = config['SECRET_KEY']
    assert environment_secret_key == flask_secret_key

    environment_client_id = os.environ.get('CLIENT_ID')
    flask_client_id = config['CLIENTID']
    assert environment_client_id == flask_client_id

    environment_client_secret = os.environ.get('CLIENT_SECRET')
    flask_client_secret = config['CLIENTSECRET']
    assert environment_client_secret == flask_client_secret