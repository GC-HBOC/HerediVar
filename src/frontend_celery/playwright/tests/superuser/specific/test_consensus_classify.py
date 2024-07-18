
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


def test_consensus_classify(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    variant_id = conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # chr2-214730440-G-A BARD1

    # start the test
    utils.login(page, user)

    classification = {
        "variant_id": variant_id,
        "scheme_oi": "ACMG SVI adaptation",
        "criteria": [
            {"name": "PVS1", "comment": "comment pvs1", "state": "selected", "strength": "very strong"},
            {"name": "PS1", "comment": "comment ps1", "state": "selected", "strength": "strong"},
            {"name": "PM4", "comment": "comment pm4", "state": "selected", "strength": "very strong"},
            {"name": "PM1", "comment": "comment pm1", "state": "unselected", "strength": "medium"}
        ],
        "expected_scheme_class": "5",
        "final_class": "5",
        "final_comment": "THIS IS THE FINAL COMMENT!!",
        "papers": [
            {"pmid": "123456", "passage": "passage for 123456"}
        ],
        "user": conn.get_user(user_id) # id,username,first_name,last_name,affiliation
    }

    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.consensus_classify", variant_id = variant_id, _external = True))
    utils.select_classify(classification, page)
    assert_consensus_classification(classification, page)

def assert_consensus_classification(classification, page):
    variant_id = classification["variant_id"]
    scheme_oi = classification["scheme_oi"]
    criteria = classification["criteria"]
    expected_scheme_class = classification["expected_scheme_class"]
    final_class = classification["final_class"]
    final_comment = classification["final_comment"]
    papers = classification["papers"]

    # go back to the variant display page and assert that the classification is visible and correct
    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.display', variant_id = variant_id, _external = True))

    expect(page.locator("#mrcc_final_class")).to_have_text("Class: " + final_class)
    #expect(page.locator("#mrcc_final_class")).to_have_text(re.compile(r"Date: " + functions.get_today()))

