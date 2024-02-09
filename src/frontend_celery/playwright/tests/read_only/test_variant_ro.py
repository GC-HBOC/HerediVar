from os import path
import os
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
from utils import Test_Connection
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
import time


#def test_screenshot(page):
#    response = page.goto(url_for("main.index", _external=True )) #    "http://localhost:4000" + 
#    print(response.request.all_headers())
#    page.screenshot(path="screenshots/index.png")



def test_variant_lists(page):
    utils.login(page, utils.get_user())

    response = page.goto(url_for("user.my_lists", _external=True))
    assert response.status == 200

    # add new variant list
    list_one_name = "TESTTEST"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    utils.screenshot(page)
    page.locator("#list_name").fill(list_one_name)
    utils.screenshot(page)

    page.locator("#list-modal-submit").click()
    utils.screenshot(page)

    utils.check_flash_id(page, "list_add_success")

    page.locator("td:has-text('" + list_one_name + "')").click()
    utils.screenshot(page)

    #test_conn = Test_Connection(["db_admin"])
    #test_conn.execute_sql_script()
    #test_conn.revert_database()

def test_variant_lists_2(page):
    utils.login(page, utils.get_user())

    response = page.goto(url_for("user.my_lists", _external=True))
    assert response.status == 200

    # add new variant list
    list_one_name = "TESTTEST2"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    utils.screenshot(page)
    page.locator("#list_name").fill(list_one_name)
    utils.screenshot(page)

    page.locator("#list-modal-submit").click()
    utils.screenshot(page)

    utils.check_flash_id(page, "list_add_success")

    page.locator("td:has-text('" + list_one_name + "')").click()
    utils.screenshot(page)
    
def test_delet(page):
    print("YOOY")
    

#test_variant_lists


#def test_get_started_link(page: Page):
#    page.goto("https://playwright.dev/")
#
#    # Click the get started link.
#    page.get_by_role("link", name="Get started").click()
#
#    # Expects page to have a heading with the name of Installation.
#    expect(page.get_by_role("heading", name="Installation")).to_be_visible()