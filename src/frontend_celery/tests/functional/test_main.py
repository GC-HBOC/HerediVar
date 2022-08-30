from webapp import create_app
from flask import request

def test_home_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('/')
    assert response.status_code == 200

        
    
