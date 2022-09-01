from webapp import create_app
from flask import request
import os

def test_home_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
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
    print(flask_secret_key)
    assert environment_secret_key == flask_secret_key
