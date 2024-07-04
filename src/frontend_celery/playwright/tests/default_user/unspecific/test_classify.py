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

def test_user_classify(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    variant_id = conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # chr2-214730440-G-A BARD1

    # start the test
    utils.login(page, user)

    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.classify', variant_id = variant_id, _external = True))

    scheme_oi = "ACMG SVI adaptation"
    criteria = [
        {"name": "PVS1", "comment": "comment pvs1", "state": "selected"},
        {"name": "PS1", "comment": "comment ps1", "state": "selected"},
        {"name": "PM1", "comment": "comment pm1", "state": "unselected"},
    ]
    expected_scheme_class = "5"
    final_class = "5"
    final_comment = "THIS IS THE FINAL COMMENT!!"
    papers = [
        {"pmid": "123456", "passage": "passage for 123456"}
    ]

    page.select_option('select#scheme', label=scheme_oi)

    # select / unselect criteria and fill comment
    for criterium in criteria:
        criterium_name = criterium["name"]
        criterium_comment = criterium["comment"]
        criterium_state = criterium["state"]
        page.locator("#" + criterium_name + "_label").click()
        expect(page.locator("#select_criterium_check")).to_have_count(1)
        page.select_option('select#select_criterium_check', label=criterium_state)
        page.locator("#criteria_evidence").fill(criterium_comment)

    # select final classification
    expect(page.locator("#classification_preview")).to_have_text(expected_scheme_class)
    if expected_scheme_class != final_class:
        page.select_option('select#final_class', label=final_class)
    expect(page.locator("#final_class")).to_have_value(final_class)

    # fill comment
    page.locator("#comment").fill(final_comment)

    # select literature
    for paper in papers:
        page.locator('#blank_row_button').click()
        page.get_by_placeholder('pmid').last.fill(paper["pmid"])
        page.get_by_placeholder('Text citation').last.fill(paper["passage"])
    
    utils.nav(page.click, utils.GOOD_STATI, "#submit-acmg-form")
    utils.check_flash_id(page, "successful_user_classification")