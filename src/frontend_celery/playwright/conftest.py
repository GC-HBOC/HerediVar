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

    
@pytest.fixture(autouse=True)
def _seed_db():
    import time
    time.sleep(10)
    utils.execute_sql_script("/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_structure/structure.sql")
    time.sleep(10)
    utils.execute_sql_script("/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_seeds/static.sql")

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
    

#---TRANSACTION 421342131045816, ACTIVE 1583 sec
#0 lock struct(s), heap size 1128, 0 row lock(s)
#MySQL thread id 477340, OS thread handle 139793800128256, query id 10062648333 SRV018.img.med.uni-tuebingen.de 10.203.68.22 ahdoebm1 
#Trx read view will not see trx with id >= 422169676, sees < 422169676
#---TRANSACTION 421342130999880, ACTIVE 1584 sec
#0 lock struct(s), heap size 1128, 0 row lock(s)
#MySQL thread id 477338, OS thread handle 139794766124800, query id 10062647631 SRV018.img.med.uni-tuebingen.de 10.203.68.22 ahdoebm1 
#Trx read view will not see trx with id >= 422169676, sees < 422169676
#---TRANSACTION 421342131083400, ACTIVE 1584 sec
#0 lock struct(s), heap size 1128, 0 row lock(s)
#MySQL thread id 477336, OS thread handle 139794767046400, query id 10062645909 SRV018.img.med.uni-tuebingen.de 10.203.68.22 ahdoebm1 
#Trx read view will not see trx with id >= 422169674, sees < 422169674
#---TRANSACTION 421342131016584, ACTIVE 1590 sec
#0 lock struct(s), heap size 1128, 0 row lock(s)
#MySQL thread id 477328, OS thread handle 139794744006400, query id 10062633565 SRV018.img.med.uni-tuebingen.de 10.203.68.22 ahdoebm1 
#Trx read view will not see trx with id >= 422169670, sees < 422169670