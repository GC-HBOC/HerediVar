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
from functools import partial
from playwright.sync_api import expect
import requests


#def test_screenshot(page):
#    response = page.goto(url_for("main.index", _external=True )) #    "http://localhost:4000" + 
#    print(response.request.all_headers())
#    page.screenshot(path="screenshots/index.png")



def test_variant_list_add(page):
    utils.login(page, utils.get_user())

    response = page.goto(url_for("user.my_lists", _external=True))
    assert response.status == 200

    # add new variant list
    list_name = "priv_l"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    #utils.screenshot(page)
    page.locator("#list_name").fill(list_name)
    #utils.screenshot(page)

    page.locator("#list-modal-submit").click()
    #utils.screenshot(page)

    utils.check_flash_id(page, "list_add_success")
    utils.click_link(page, "td:has-text('" + list_name + "')")

    #utils.screenshot(page)


    # add variant list public read
    list_name = "pub_l"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    page.locator("#list_name").fill(list_name)
    page.locator("#public_read").click()
    utils.screenshot(page)

    page.locator("#list-modal-submit").click()
    #utils.screenshot(page)

    utils.check_flash_id(page, "list_add_success")
    utils.click_link(page, "td:has-text('" + list_name + "')")


    # add variant list public edit
    list_name = "edit_l"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    page.locator("#list_name").fill(list_name)
    page.locator("#public_read").click()
    page.locator("#public_edit").click()
    utils.screenshot(page)

    page.locator("#list-modal-submit").click()
    #utils.screenshot(page)

    utils.check_flash_id(page, "list_add_success")
    utils.click_link(page, "td:has-text('" + list_name + "')")

    #
    #page.goto(url_for("user.my_lists", _external=True))
    #page.locator("#access_col_search").fill("private")
    #utils.screenshot(page)
    #page.locator("#access_col_search.search-input-selected").wait_for()
    #utils.screenshot(page)
    #expect(page.locator("tr[list_id]")).to_have_count(1)

def test_private_list_actions(page):
    # seed database
    conn = Test_Connection(roles = ["db_admin"])
    conn.insert_user(username = "transient_tester", first_name = "TRA", last_name = "TEST", affiliation = "AFF")
    user_id = conn.get_last_insert_id()

    list_name = "priv_l"
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = False, public_edit = False)
    list_id = conn.get_last_insert_id()

    variant_id_1 = conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T
    variant_id_2 = conn.insert_variant(chr = "chr22", pos = "28689217", ref = "T", alt = "C", orig_chr = "chr22", orig_pos = "28689217", orig_ref = "T", orig_alt = "C", user_id = user_id) # chr22-28689217-T-C

    conn.add_variant_to_list(list_id = list_id, variant_id = variant_id_1)


    # perform test
    utils.login(page, utils.get_user())

    # is the list visible?
    response = page.goto(url_for('user.my_lists', _external=True))
    assert response.status == 200
    expect(page.locator("tr[list_id='" + str(list_id) + "']")).to_have_count(0)

    # try accessing the private list
    response = page.goto(url_for('user.my_lists', view=list_id, _external=True))
    assert response.status == 403

    # is it possible to add variants?
    print(url_for("user.modify_list_content"))
    page.route("**/*" + url_for("user.modify_list_content") + "*", lambda route: continue_as_post(route, expected_stati = [200])) # utils.NO_ACCESS_STATI
    page.goto(url_for("user.modify_list_content", selected_list_id=list_id, variant_id = variant_id_2, action = 'add_to_list', next = url_for('variant.display', variant_id=variant_id_2), _external=True))
    utils.screenshot(page)
    print("YOOO")
    assert False

    #response = page.goto(url_for('variant.display', variant_id = variant_id_2, _external=True))
    #utils.screenshot(page)
    #assert response.status == 200
    #page.locator("#dropdownMenuButton1").click()
    #page.locator("#list_add_button").click()
    #page.locator("#list-add-modal-label").wait_for()
    #utils.screenshot(page)
    #expect(page.locator("div:has-text('" + list_name + "')")).to_have_count(0)
    #utils.screenshot(page)


def continue_as_post(route, expected_stati):
    response = route.fetch(method="POST")
    route.fulfill()
    if response.status not in expected_stati:
        raise AssertionError("Status code is not expected: " + str(response.status) + " should be in " + str(expected_stati))
    
    


def test_public_list_actions(page):
    # seed database
    conn = Test_Connection(roles = ["db_admin"])
    conn.insert_user(username = "transient_tester", first_name = "TRA", last_name = "TEST", affiliation = "AFF")
    user_id = conn.get_last_insert_id()

    list_name = "publ_l"
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = True, public_edit = False)
    list_id = conn.get_last_insert_id()

    variant_id_1 = conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T
    variant_id_2 = conn.insert_variant(chr = "chr22", pos = "28689217", ref = "T", alt = "C", orig_chr = "chr22", orig_pos = "28689217", orig_ref = "T", orig_alt = "C", user_id = user_id) # chr22-28689217-T-C

    conn.add_variant_to_list(list_id = list_id, variant_id = variant_id_1)


    # perform test
    utils.login(page, utils.get_user())

    # is the list visible?
    response = page.goto(url_for('user.my_lists', _external=True))
    assert response.status == 200
    expect(page.locator("tr[list_id=" + str(list_id) + "]")).to_have_count(1)

    # try accessing public list
    response = page.goto(url_for('user.my_lists', view=list_id, _external=True))
    assert response.status == 200



def test_public_edit_list_actions(page):
    # seed database
    conn = Test_Connection(roles = ["db_admin"])
    conn.insert_user(username = "transient_tester", first_name = "TRA", last_name = "TEST", affiliation = "AFF")
    user_id = conn.get_last_insert_id()

    list_name = "edit_l"
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = True, public_edit = True)
    list_id = conn.get_last_insert_id()

    variant_id_1 = conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T
    variant_id_2 = conn.insert_variant(chr = "chr22", pos = "28689217", ref = "T", alt = "C", orig_chr = "chr22", orig_pos = "28689217", orig_ref = "T", orig_alt = "C", user_id = user_id) # chr22-28689217-T-C

    conn.add_variant_to_list(list_id = list_id, variant_id = variant_id_1)


    # perform test
    utils.login(page, utils.get_user())

    # is the list visible?
    response = page.goto(url_for('user.my_lists', _external=True))
    assert response.status == 200
    expect(page.locator("tr[list_id=" + str(list_id) + "]")).to_have_count(1)

    # try accessing public editable list
    response = page.goto(url_for('user.my_lists', view=list_id, _external=True))
    assert response.status == 200



#test_variant_lists


#def test_get_started_link(page: Page):
#    page.goto("https://playwright.dev/")
#
#    # Click the get started link.
#    page.get_by_role("link", name="Get started").click()
#
#    # Expects page to have a heading with the name of Installation.
#    expect(page.get_by_role("heading", name="Installation")).to_be_visible()