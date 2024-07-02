from os import path
import os
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
import common.paths as paths
import time
from functools import partial
from playwright.sync_api import expect
import requests




def test_user_select_all_schemes(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    variant_id = conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # chr2-214730440-G-A BARD1

    # start the test
    utils.login(page, user)

    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.classify', variant_id = variant_id, _external = True))

    # test that all classification schemes are selectable
    classification_schemes = conn.get_classification_schemas()
    for classification_scheme_id in classification_schemes:
        classification_scheme_label = classification_schemes[classification_scheme_id]["description"]
        page.select_option('select#scheme', label=classification_scheme_label)

        # assert that all criteria are visible
        criteria = classification_schemes[classification_scheme_id]["criteria"]
        for criterium in criteria:
            expect(page.locator("#" + criterium)).to_have_count(1)