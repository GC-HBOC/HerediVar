from webapp import create_app
import pytest
import os



@pytest.fixture(scope='module')
def test_client():
    env = "test"
    app = create_app('config.%sConfig' % env.capitalize())

    
    with app.test_client() as test_client:
        with app.app_context(): # Establish an application context
            yield test_client 
