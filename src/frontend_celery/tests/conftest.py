from webapp import create_app
import pytest
import os



#@pytest.fixture(scope='module')
#def test_client():
#    env = "test"
#    app = create_app('config.%sConfig' % env.capitalize())
#
#    
#    with app.test_client() as test_client:
#        with app.app_context(): # Establish an application context
#            yield test_client 

# Instead of pushing an app context using the with statement
# one can use this code to set one up manually This enables using url_for

@pytest.fixture
def app():
    app = create_app()
    return app

@pytest.fixture
def test_client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def config(app):
    return app.config

@pytest.fixture(autouse=True)
def _push_request_context(request, app):
    ctx = app.test_request_context()  # create context
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
