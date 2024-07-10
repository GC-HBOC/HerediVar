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

    test_classification(page, classification)




def test_classification(page, classification):
    variant_id = classification["variant_id"]
    scheme_oi = classification["scheme_oi"]
    criteria = classification["criteria"]
    expected_scheme_class = classification["expected_scheme_class"]
    final_class = classification["final_class"]
    final_comment = classification["final_comment"]
    papers = classification["papers"]
    user_from_db = classification["user"]

    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.classify', variant_id = variant_id, _external = True))

    page.select_option('select#scheme', label=scheme_oi)

    # select / unselect criteria and fill comment
    for criterium in criteria:
        criterium_name = criterium["name"]
        criterium_comment = criterium["comment"]
        criterium_state = criterium["state"]
        criterium_strength = criterium["strength"]
        page.locator("#" + criterium_name + "_label").click()
        expect(page.locator("#select_criterium_check")).to_have_count(1)
        page.select_option('select#select_criterium_check', label=criterium_state)
        page.locator("#criteria_evidence").fill(criterium_comment)
        page.locator("#additional_content").get_by_label(criterium_strength, exact=True).check()

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

    utils.check_all_links(page)

    # go back to the variant display page and assert that the classification is visible and correct
    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.display', variant_id = variant_id, _external=True))

    expect(page.locator("table#userClassificationsTable > tbody > tr")).to_have_count(1)
    table_data = page.locator("table#userClassificationsTable > tbody > tr > td")
    
    expect(table_data.nth(0)).to_have_text(final_class)
    expect(table_data.nth(1)).to_have_text(scheme_oi)
    #expect(table_data[2]) # criteria
    for criterium in criteria:
        criterium_locator = table_data.nth(2).locator("button").get_by_text(criterium["name"])
        expect(criterium_locator).to_have_count(1) # criterium is there
        criterium_locator.click() # open popover to view details

        parent = criterium_locator.locator("..")
        expect(parent.get_by_text(criterium["state"])).to_be_visible()
        expect(parent.get_by_text(criterium["state"])).to_have_count(1)
        expect(parent.get_by_text(criterium["comment"])).to_be_visible()
        expect(parent.get_by_text(criterium["comment"])).to_have_count(1)
        expect(parent.get_by_text(criterium["strength"])).to_be_visible()
        expect(parent.get_by_text(criterium["strength"])).to_have_count(1)
    expect(table_data.nth(3)).to_have_text(final_comment)
    expect(table_data.nth(4)).to_have_text(expected_scheme_class)
    for paper in papers:
        expect(table_data.nth(5).get_by_text(paper["pmid"])).to_have_count(1)
    expect(table_data.nth(6)).to_have_text(user_from_db[2] + " " + user_from_db[3])
    expect(table_data.nth(7)).to_have_text(user_from_db[4])
