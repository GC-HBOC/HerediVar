from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
import re
from playwright.sync_api import Page, expect
from flask import url_for


def test_login(page: Page):
    utils.login(page, utils.get_user())
    utils.screenshot(page)

def test_login2(page: Page):
    utils.login(page, utils.get_user())
    utils.screenshot(page)

def test_edit_profile(page: Page):
    utils.login(page, utils.get_user())

    # successful edit of user information
    utils.nav(page.goto, utils.GOOD_STATI, url_for("auth.profile", _external=True))
    page.locator("input[name='first_name']").fill("Testuser Firstname")
    page.locator("input[name='last_name']").fill("Testuser Lastname")
    page.locator("input[name='e_mail']").fill("izg.vgi@4woegnu.com")
    page.locator("input[name='affiliation']").fill("Testuser Affiliation")
    utils.nav(page.click, utils.GOOD_STATI, "button:has-text('Submit')")

    utils.check_flash_id(page, "success_userinfo")

    utils.screenshot(page)

    # unsuccessful edit of email because it already exists
    utils.nav(page.goto, utils.GOOD_STATI, url_for("auth.profile", _external=True))
    page.locator("input[name='e_mail']").fill("stduser@testmail.com")
    utils.nav(page.click, utils.GOOD_STATI, "button:has-text('Submit')")

    utils.check_flash_id(page, "emailExistsMessage")
