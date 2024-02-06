from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
import re
from playwright.sync_api import Page, expect
from flask import url_for




def test_login(page: Page):
    utils.login(page, utils.get_user())
    page.screenshot(path="screenshots/login1.png")

def test_login2(page: Page):
    utils.login(page, utils.get_user())
    page.screenshot(path="screenshots/login2.png")


def test_edit_profile(page: Page):

    utils.login(page, utils.get_user())

    page.on("response", utils.assert_good_stati)

    response = page.goto(url_for("auth.profile", _external=True))
    assert response.status == 200

    page.locator("input[name='first_name']").fill("Testuser Firstname")
    page.locator("input[name='last_name']").fill("Testuser Lastname")
    page.locator("input[name='e_mail']").fill("izg.vgi@4woegnu.com")
    page.locator("input[name='affiliation']").fill("Testuser Affiliation")
    page.get_by_text("Submit").click()

    page.remove_listener("response", utils.assert_good_stati)
    #page.screenshot(path="screenshots/userinfo3.png")

    utils.check_flash_id(page, "success_userinfo")

    response = page.goto(url_for("auth.profile", _external=True))
    assert response.status == 200

    page.locator("input[name='e_mail']").fill("stduser@testmail.com")
    page.on("response", utils.assert_good_stati)
    page.get_by_text("Submit").click()
    page.remove_listener("response", utils.assert_good_stati)

    utils.check_flash_id(page, "emailExistsMessage")
