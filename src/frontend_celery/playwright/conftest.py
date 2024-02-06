import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from webapp import create_app
import pytest
import os
sys.path.append(path.dirname(path.abspath(__file__)))
import utils


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

#@pytest.fixture()
#def client():
#    return app.test_client()

@pytest.fixture(autouse=True)
def _push_request_context(request, app):
    ctx = app.test_request_context()  # create context
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)


@pytest.fixture
def page(browser):
    context = utils.get_context(browser)
    page = utils.get_page(context)
    yield page
    utils.save_browser_state(context)

#@pytest.fixture()
#def page2(playwright):
#    browser = playwright.firefox.launch(args=['--no-proxy-server'])
#    context = browser.new_context(
#            #user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
#            color_scheme=r"light"
#        )
#    page = context.new_page()
#    return page