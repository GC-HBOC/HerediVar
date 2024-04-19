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




def test_variant_list_add(page):
    utils.login(page, utils.get_user())

    utils.nav(page.goto, utils.GOOD_STATI, url_for("user.my_lists", _external=True))

    # add new variant list
    list_name = "priv_l"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    page.locator("#list_name").fill(list_name)
    #utils.screenshot(page)

    utils.nav(page.click, utils.GOOD_STATI, "#list-modal-submit")

    utils.check_flash_id(page, "list_add_success")
    utils.nav(page.click, utils.GOOD_STATI, "td:has-text('" + list_name + "')")

    utils.screenshot(page)


    # add variant list public read
    list_name = "pub_l"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    page.locator("#list_name").fill(list_name)
    page.locator("#public_read").click()
    #utils.screenshot(page)

    utils.nav(page.click, utils.GOOD_STATI, "#list-modal-submit")

    utils.check_flash_id(page, "list_add_success")
    utils.nav(page.click, utils.GOOD_STATI, "td:has-text('" + list_name + "')")

    utils.screenshot(page)


    # add variant list public edit
    list_name = "edit_l"
    page.locator("#create-list-button").click()
    page.wait_for_selector("#createModalLabel")
    page.locator("#list_name").fill(list_name)
    page.locator("#public_read").click()
    page.locator("#public_edit").click()
    #utils.screenshot(page)

    utils.nav(page.click, utils.GOOD_STATI, "#list-modal-submit")

    utils.check_flash_id(page, "list_add_success")
    utils.nav(page.click, utils.GOOD_STATI, "td:has-text('" + list_name + "')")




def test_private_list_actions(page, conn):
    # seed database
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

    # the list should not be visible
    utils.nav(page.goto, utils.GOOD_STATI, url_for('user.my_lists', _external=True))
    expect(page.locator("tr[list_id='" + str(list_id) + "']")).to_have_count(0)

    # try accessing the private list -> unauthorized
    utils.nav(page.goto, utils.UNAUTHORIZED_STATI, url_for('user.my_lists', view=list_id, _external=True))


    # try to add variants to the private list -> unauthorized
    get_data = {
        "selected_list_id": list_id,
        "variant_id": variant_id_2, 
        "action": 'add_to_list', 
        "next": url_for('variant.display', variant_id=variant_id_2)
    }
    post_data = {}
    url = url_for("user.modify_list_content", **get_data, _external=True)
    expected_stati = utils.UNAUTHORIZED_STATI
    utils.nav_post(page, url, expected_stati, form=post_data)

    # try to delete variants from the private list -> unauthorized
    get_data = {
        "selected_list_id": list_id,
        "variant_id": variant_id_1, 
        "action": 'remove_from_list', 
        "next": url_for('variant.display', variant_id=variant_id_1)
    }
    post_data = {}
    url = url_for("user.modify_list_content", **get_data, _external=True)
    expected_stati = utils.UNAUTHORIZED_STATI
    utils.nav_post(page, url, expected_stati, form=post_data)


    ################# PUT THIS IN SEPARATE TESTS ###################
    # try to delete the list
    get_data = {
        "type": 'delete_list'
    }
    post_data = {
        "list_id": list_id
    }
    url = url_for("user.my_lists", **get_data, _external=True)
    expected_stati = utils.UNAUTHORIZED_STATI
    utils.nav_post(page, url, expected_stati, form=post_data)

    # try to duplicate the list
    get_data = {
        "type": 'duplicate'
    }
    post_data = {
        "list_id": list_id,
        "list_name": "DUPLICATED LIST",
        "public_read": True,
        "public_edit": True
    }
    url = url_for("user.my_lists", **get_data, _external=True)
    expected_stati = utils.UNAUTHORIZED_STATI
    utils.nav_post(page, url, expected_stati, form=post_data)






def test_modify_list_permissions(page, conn):
    # seed database
    user = utils.get_user()
    conn.insert_user(username = "transient_tester", first_name = "TRA", last_name = "TEST", affiliation = "AFF")
    other_user_id = conn.get_last_insert_id()

    list_name = "priv_l"
    conn.insert_user_variant_list(user_id = other_user_id, list_name = list_name, public_read = False, public_edit = False)
    private_list_id = conn.get_last_insert_id()

    list_name = "list1_allowed"
    user_id = conn.get_user_id(username = user["username"])
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = False, public_edit = False)
    allowed_list_id = conn.get_last_insert_id()

    # start test
    utils.login(page, user)

    # try to modify the list name -> allowed
    new_list_name = "ALLOWEDLISTNAME"
    utils.nav(page.goto, utils.GOOD_STATI, url_for('user.my_lists', _external=True))
    page.locator('#edit_list_' + str(allowed_list_id)).click()
    page.wait_for_selector("#createModalLabel")
    page.locator('#list_name').fill(new_list_name)
    page.locator('#list-modal-submit').click()
    utils.check_flash_id(page, "list_edit_permissions_success")
    expect(page.get_by_text(new_list_name)).to_be_visible()
    utils.screenshot(page)

    # try modify the list name -> unauthorized
    get_data = {
        "selected_list_id": private_list_id,
        "type": 'edit'
    }
    post_data = {
        "list_name": "THISISNOTALLOWED",
        "list_id": private_list_id
    }
    url = url_for("user.my_lists", **get_data, _external=True)
    expected_stati = utils.UNAUTHORIZED_STATI
    utils.nav_post(page, url, expected_stati, form=post_data)


    # try to select only public edit and not public read -> should not be possible
    utils.nav(page.goto, utils.GOOD_STATI, url_for('user.my_lists', _external=True))
    page.locator('#edit_list_' + str(allowed_list_id)).click()
    page.wait_for_selector("#createModalLabel")
    expect(page.locator('#public_edit')).to_be_disabled()
    page.locator('#public_read').click()
    page.locator('#public_edit').click()
    expect(page.locator('#public_read')).to_be_checked()
    expect(page.locator('#public_edit')).to_be_checked()
    page.locator('#public_read').click()
    expect(page.locator('#public_read')).not_to_be_checked()
    expect(page.locator('#public_edit')).to_be_disabled()
    expect(page.locator('#public_edit')).not_to_be_checked()

    # try to modify the list permissions -> allowed
    utils.nav(page.goto, utils.GOOD_STATI, url_for('user.my_lists', _external=True))
    page.locator('#edit_list_' + str(allowed_list_id)).click()
    page.wait_for_selector("#createModalLabel")
    page.locator('#public_read').click()
    page.locator('#public_edit').click()
    expect(page.locator('#public_read')).to_be_checked()
    expect(page.locator('#public_edit')).to_be_checked() # to be disabled
    page.locator('#list-modal-submit').click()
    utils.check_flash_id(page, "list_edit_permissions_success")
    expect(page.locator("span[title='Public list']")).to_have_count(1)
    utils.screenshot(page)

    # try modify the list permissions -> unauthorized
    get_data = {
        "type": 'edit'
    }
    post_data = {
        "list_name": list_name,
        "list_id": private_list_id,
        "public_read": True,
        "public_edit": True
    }
    url = url_for("user.my_lists", **get_data, _external=True)
    expected_stati = utils.UNAUTHORIZED_STATI
    utils.nav_post(page, url, expected_stati, form=post_data)












def test_public_list_actions(page, conn):
    # seed database
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
    utils.nav(page.goto, utils.GOOD_STATI, url_for('user.my_lists', _external=True))
    expect(page.locator("tr[list_id='" + str(list_id) + "']")).to_have_count(0)

    # try accessing the public list -> works
    utils.nav(page.goto, utils.GOOD_STATI, url_for('user.my_lists', view=list_id, _external=True))





