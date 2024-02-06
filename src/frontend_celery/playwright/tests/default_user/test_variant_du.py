from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for
from playwright.sync_api import ElementHandle, Frame, Page, Browser, TimeoutError as PlaywrightTimeoutError



#def test_screenshot(page):
#    response = page.goto(url_for("main.index", _external=True )) #    "http://localhost:4000" + 
#    print(response.request.all_headers())
#    page.screenshot(path="screenshots/index.png")




def TESTTEST(page):
    page.goto(url_for("main.index", _external=True))
    page.screenshot(path="screenshots/login1_before.png")
    utils.login(page, 'superuser', '12345')
    page.screenshot(path="screenshots/login1_after.png")
    assert False





#def test_get_started_link(page: Page):
#    page.goto("https://playwright.dev/")
#
#    # Click the get started link.
#    page.get_by_role("link", name="Get started").click()
#
#    # Expects page to have a heading with the name of Installation.
#    expect(page.get_by_role("heading", name="Installation")).to_be_visible()