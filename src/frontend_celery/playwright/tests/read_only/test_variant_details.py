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
import common.paths as paths
import time
from functools import partial
from playwright.sync_api import expect


def test_varaint_details_access(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr1", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T PALB2
    ]


    # start test
    utils.login(page, user)

    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.search", _external = True))
    utils.nav(page.click, utils.GOOD_STATI, ":nth-match(td[data-href='" + url_for("variant.display", variant_id = all_variant_ids[0], _external = False) + "'], 1)")
    expect(page.locator("#variant_page_title")).to_contain_text("chr2-214730440-G-A")

    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.display", chr="chr2", pos="214730440", ref = "G", alt = "A", _external = True))
    expect(page.locator("#variant_page_title")).to_contain_text("chr2-214730440-G-A")

    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.annotation_status", variant_id = all_variant_ids[0], _external = True))

    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.display", chr="2", pos="214730440", ref = "G", alt = "A", _external = True))
    expect(page.locator("#variant_page_title")).to_contain_text("chr2-214730440-G-A")






