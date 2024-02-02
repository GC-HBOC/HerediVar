from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for


def test_screenshot(page):
    response = page.goto(url_for("main.index", _external=True )) #    "http://localhost:4000" + 
    print(response.request.all_headers())
    page.screenshot(path="screenshots/index.png")

def test_login(page):
    response = page.goto(url_for("auth.login", _external=True))
    page.screenshot(path="screenshots/login.png")
    assert response.status == 200
    
    page.locator("#username").fill("superuser")
    page.locator("#password").fill("12345")
    page.screenshot(path="screenshots/login_filled.png")

    page.locator("#kc-login").click()
    page.screenshot(path="screenshots/login_done.png")
    



#def test_get_started_link(page: Page):
#    page.goto("https://playwright.dev/")
#
#    # Click the get started link.
#    page.get_by_role("link", name="Get started").click()
#
#    # Expects page to have a heading with the name of Installation.
#    expect(page.get_by_role("heading", name="Installation")).to_be_visible()