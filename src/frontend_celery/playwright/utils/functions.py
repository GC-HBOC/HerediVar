from os import path
import os
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for
from playwright.sync_api import ElementHandle, Frame, Page, Browser, TimeoutError as PlaywrightTimeoutError, expect
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions



def subscribe_request_response(page):
    page.on("request", lambda request: print(">>", request.method, request.url))
    page.on("response", lambda response: print("<<", response.status, response.url))



def check_inner_text(page: Page, selector: str, expected: str, timeout: int = 500):
    actual = None
    try:
        element = page.wait_for_selector(selector, timeout=timeout, state='attached')
        actual = element.inner_text()
    except PlaywrightTimeoutError:
        pass
    assert expected == actual

def selector_exists(page: Page, selector: str, timeout: int = 500):
    try:
        return page.wait_for_selector(selector, timeout=timeout, state='attached')
    except PlaywrightTimeoutError:
        return None

def is_logged_in(page: Page, username: str):
    page.goto(url_for("main.index", _external=True))
    index_url = page.url
    username_handle = selector_exists(page, "#navbarDropdown_userdata")
    if username_handle is None:
        print("User not logged in: username not visible on page")
        return False
    if username_handle.inner_text().strip() != username.strip():
        print("User not logged in: wrong username visible on page")
        return False

    page.goto(url_for("auth.profile", _external=True))
    login_url = page.url
    if not login_url.startswith(index_url):
        print("User not logged in: keycloak does not have a session")
        return False

    return True

def logout(page: Page):
    resp = page.goto(url_for('auth.logout', _external=True))
    resp.status == 200
    resp = page.goto(url_for('main.index', _external=True)) # refresh to be extra safe
    resp.status == 200
    assert selector_exists(page, "#navbarDropdown_userdata") is None

def login(page: Page, user: dict):
    ili = is_logged_in(page, user["username"])
    #print("before: " + str(ili))
    page.screenshot(path="screenshots/login_before.png")
    if not ili:
        logout(page)
        print("not logged in loggin in user now!")
        page.on("response", assert_good_stati)
        response = page.goto(url_for("auth.login", _external=True))
        assert response.status == 200

        page.locator("#username").fill(user["username"])
        page.locator("#password").fill(user["password"])

        page.locator("#kc-login").click()
        page.remove_listener("response", assert_good_stati)

        ili = is_logged_in(page, user["username"])
    #print("after: " + str(ili))
    page.screenshot(path="screenshots/login_after.png")
    assert ili


def assert_good_stati(response, good_stati=[200, 302, 304]):
    if response.status not in good_stati:
        print("URL: " + response.url + " has status code: " + str(response.status))
    assert response.status in good_stati

def save_browser_state(context, filename = ".auth/state.json"):
    storage = context.storage_state(path=filename)
    #print(storage)

def get_context(browser, filename = ".auth/state.json"):
    if path.isfile(filename):
        context = browser.new_context(storage_state=filename)
    else:
        context = browser.new_context()
    return context

def get_page(context):
    page = context.new_page()
    return page

def get_base_url(page):
    page.goto(url_for("main.index", _external=True))
    return page.url

def get_user():
    username = os.environ.get("TESTUSER")
    password = os.environ.get("TESTUSERPW")
    return {"username": username, "password": password}


def check_flash_id(page, flash_id):
    if flash_id.startswith('flash_id:'):
        flash_id = flash_id.split(':')[1]
    element_handle = page.locator(".alert")
    try:
        expect(element_handle).to_have_class(re.compile(r"flash_id:" + flash_id))
    except AssertionError as e:
        print("Flash message on " + page.url + ": " + element_handle.text_content().strip())
        raise e
    

screenshot_name_dict={}

def screenshot(page, folder="screenshots"):
    if not os.path.exists(folder):
        os.makedirs(path)
    basename = page.url.replace("/", '_')
    screenshot_num = screenshot_name_dict.get(basename, 0) + 1
    screenshot_name_dict[basename] = screenshot_num
    full_path = folder + "/" + basename + "_" + str(screenshot_num) + ".png"
    page.screenshot(path = full_path)


def revert_database():
    command = ["./revert_db.sh"]
    functions.execute_command(command, "mysql")
    #paths = ["/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_structure/structure.sql",
    #         "/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_seeds/static.sql"]
    #for path in paths:
    #    command = ["/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/revert_db.sh"]
    #    #command = ["mysql", "-h", os.environ.get("DB_HOST"), "-P", os.environ.get("DB_PORT"), "-u" + os.environ.get("DB_ADMIN"), "-p" + os.environ.get("DB_ADMIN_PW"), os.environ.get("DB_NAME"), path]
    #    functions.execute_command(command, "mysql")
    #    print(command)