from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for
import requests





def test_index(page):
    utils.nav(page.goto, utils.GOOD_STATI, url_for("main.index", _external=True))

    base_url = utils.get_base_url(page)
    link_handles = page.locator("[href]")
    for handle in link_handles.element_handles():
        link = handle.get_attribute('href')
        if link == '#':
            continue
        if not link.startswith("http"):
            link = base_url.strip('/') + link

        resp = requests.get(link)
        if resp.status_code != 200:
            print("There was an error querying this url: " + link)
            print(resp.content)
        assert resp.status_code == 200









