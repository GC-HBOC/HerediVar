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
from subprocess import Popen, PIPE, STDOUT
import requests

GOOD_STATI=[200, 302, 304]
ERROR_STATI=[500, 302, 304]
UNAUTHORIZED_STATI=[403, 302, 304]
NOT_FOUND_STATI=[404, 302, 304]


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
    nav(page.goto, GOOD_STATI, url_for("main.index", _external=True))
    index_url = page.url
    username_handle = selector_exists(page, "#navbarDropdown_userdata")
    if username_handle is None:
        print("User not logged in: username not visible on page")
        return False
    if username_handle.inner_text().strip() != username.strip():
        print("User not logged in: wrong username visible on page")
        return False

    nav(page.goto, GOOD_STATI, url_for("auth.profile", _external=True))
    login_url = page.url
    if not login_url.startswith(index_url):
        print("User not logged in: keycloak does not have a session")
        return False

    return True

def logout(page: Page):
    nav(page.goto, GOOD_STATI, url_for('auth.logout', _external=True))
    nav(page.goto, GOOD_STATI, url_for('main.index', _external=True)) # refresh to be extra safe
    assert selector_exists(page, "#navbarDropdown_userdata") is None

def login(page: Page, user: dict):
    ili = is_logged_in(page, user["username"])
    #print("before: " + str(ili))
    if not ili:
        print("not logged in loggin in user now!")
        nav(page.goto, GOOD_STATI, url_for("auth.login", _external=True))
        page.locator("#username").fill(user["username"])
        page.locator("#password").fill(user["password"])

        nav(page.click, GOOD_STATI, "#kc-login")

        ili = is_logged_in(page, user["username"])
    #print("after: " + str(ili))
    assert ili


def nav(meth, expected_stati, *args, **kwargs):
    __tracebackhide__ = True
    with meth.__self__.expect_response("**") as response_info:
        meth(*args, **kwargs)
    response = response_info.value
    assert response.status in expected_stati, f"{response.request.method} {response.url} returned {response.status}"




def check_all_links(page):
    # check external links
    locator = page.locator(".external_link")
    nlinks = locator.count()
    for i in range(1, nlinks+1): # idk why it is not possible to iterate over the locator which matches multiple elements. Thus, we do this shiz
        url = page.locator(":nth-match(.external_link, " + str(i) + ")").get_attribute("uri")
        resp = requests.get(url)
        assert resp.status_code in GOOD_STATI, "The external link " + url + " returned status code " + resp.status_code

    # check standard href links
    base_url = get_base_url(page)
    link_handles = page.locator("[href]")
    for handle in link_handles.element_handles():
        link = handle.get_attribute('href')
        if link == '#':
            continue
        if not link.startswith("http"):
            link = base_url.strip('/') + link
        resp = requests.get(link)
        assert resp.status_code in GOOD_STATI, "The href powered link " + link + " returned status code " + resp.status_code

#import json
#def test(route, post_data):
#    post_data = json.dumps(post_data)
#    print(post_data)
#    route.continue_(method="POST", post_data=post_data)
#
#def nav_post(meth, url, post_data, expected_stati, *args, **kwargs):
#    routing_url = "**/*" + url + "*"
#    meth.__self__.route(routing_url, lambda route: test(route, post_data))
#    nav(meth, expected_stati, url, *args, **kwargs)
#    meth.__self__.unroute(routing_url)

def nav_post(page, url, expected_stati, *args, **kwargs):
    response = page.request.post(url, *args, **kwargs)
    assert response.status in expected_stati, f"{response.url} returned {response.status}"




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
    nav(page.goto, GOOD_STATI, url_for("main.index", _external=True))
    return page.url

def get_user():
    username = os.environ.get("TESTUSER")
    password = os.environ.get("TESTUSERPW")
    return {"username": username, "password": password}


def check_flash_id(page, flash_id):
    if flash_id.startswith('flash_id:'):
        flash_id = flash_id.split(':')[1]
    element_handle = page.locator(".alert_msg")
    try:
        expect(element_handle).to_have_class(re.compile(r"flash_id:" + flash_id))
    except AssertionError as e:
        print("Flash message on " + page.url + ": " + element_handle.text_content().strip())
        raise e
    

screenshot_name_dict={}
def screenshot(page, folder="screenshots"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    basename = page.url.split('?')[0].replace("/", '_')
    screenshot_num = screenshot_name_dict.get(basename, 0) + 1
    screenshot_name_dict[basename] = screenshot_num
    full_path = folder + "/" + basename + "_" + str(screenshot_num) + ".png"
    page.screenshot(path = full_path, full_page=True)


def execute_sql_script(scriptPath) :       
    scriptDirPath = os.path.dirname( os.path.realpath(scriptPath) )
    sourceCmd = "SOURCE %s" % (scriptPath,)
    command = [ "mysql",                
               "-h", os.environ.get("DB_HOST"), "-P", os.environ.get("DB_PORT"), "-u" + os.environ.get("DB_ADMIN"), "-p" + os.environ.get("DB_ADMIN_PW"),
               "--database", os.environ.get("DB_NAME"),
               "--unbuffered" ] #, "--execute", sourceCmd
    process = Popen( command 
                   , cwd=scriptDirPath
                   , stdout=PIPE
                   , stderr=PIPE
                   , stdin=PIPE)
    with open(scriptPath) as file:
        stdOut, stdErr = process.communicate(input=file.read().encode("utf-8"))
    if stdErr is not None and "[Error]" in stdErr.decode("utf-8"): 
        raise IOError(stdErr)
    return stdOut


#########################################
############ DEPRECATED CODE ############
#########################################

current_listeners = {"response": []}

def remove_response_listeners(page):
    for func in current_listeners["response"]:
        page.remove_listener("response", func)
    current_listeners["response"] = []

def subscribe_stati(page, expected_stati=[]):
    def __assert_stati(response):
        assert_stati(response, expected_stati)
    page.on("response", __assert_stati)
    current_listeners["response"].append(__assert_stati)

def assert_stati(response, expected_stati):
    #print(response.url + ": " + str(response.status))
    if response.status not in expected_stati:
        print("URL: " + response.url + " has status code: " + str(response.status))
        response_text = response.text()
        if "Werkzeug Debugger" in response_text:
            start_index = response_text.find("</html>")
            if start_index > -1:
                traceback = response_text[start_index+7::]
                print(traceback.strip())
    assert response.status in expected_stati # THIS ASSERT DOES NOT FAIL THE TEST! -> BUG IN PLAYWRIGHT?!

def click_link(page, locator, expected_stati = GOOD_STATI, link_attribute = "data-href"): # USE nav() with page.click instead
    link_handle = page.locator(locator)
    link_url = link_handle.get_attribute(link_attribute)
    subscribe_stati(page, expected_stati = expected_stati)
    link_handle.click()
    remove_response_listeners(page)
    page.wait_for_url("**" + link_url)

