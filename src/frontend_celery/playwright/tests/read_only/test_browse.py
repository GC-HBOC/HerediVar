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
import time
from functools import partial
from playwright.sync_api import expect
import requests


def test_variant_type_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    all_variant_ids = [
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id), # chr16-23603525-C-T
        conn.insert_variant(chr = "chr22", pos = "28689217", ref = "T", alt = "C", orig_chr = "chr22", orig_pos = "28689217", orig_ref = "T", orig_alt = "C", user_id = user_id), # chr22-28689217-T-C
        conn.insert_sv_variant(chrom = "chr2", start = "9834578", end = "9834678", sv_type = "DEL", imprecise = False)
    ]

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, variant_type_search_worker, all_variant_ids, user_id)
    

def perform_browse_test(page, conn, worker, all_variant_ids, user_id):
    worker(page, conn, url_for('variant.search', _external=True), all_variant_ids)

    # do the same test on the variant list page
    list_name = "testlist"
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = False, public_edit = False)
    list_id = conn.get_last_insert_id()
    for variant_id in all_variant_ids:
        conn.add_variant_to_list(list_id, variant_id)
    worker(page, conn, url_for('user.my_lists', view = list_id, _external = True), all_variant_ids)

def variant_type_search_worker(page, conn, url, all_variant_ids):
    pass # TODO



def test_variant_string_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    all_variant_ids = [
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id), # chr16-23603525-C-T
        conn.insert_variant(chr = "chr22", pos = "28689217", ref = "T", alt = "C", orig_chr = "chr22", orig_pos = "28689217", orig_ref = "T", orig_alt = "C", user_id = user_id), # chr22-28689217-T-C
        conn.insert_variant(chr = "chr2", pos = "214730460", ref = "T", alt = "C", orig_chr = "chr2", orig_pos = "214730460", orig_ref = "T", orig_alt = "C", user_id = user_id) # chr2-214730460-T-C
    ]

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, variant_string_search_worker, all_variant_ids, user_id)


def variant_string_search_worker(page, conn, url, all_variant_ids):
    # successful search
    variant_id_1 = all_variant_ids[0]
    query_1 = get_exact_variant_str_repr(variant_id_1, conn)
    variant_id_2 = all_variant_ids[1]
    query_2 = get_exact_variant_str_repr(variant_id_2, conn)

    expected_variant_ids = [variant_id_1, variant_id_2]
    query = query_1 + "; ;\n" + query_2 + "," + query_1 + "  \t"

    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variants")
    page.locator("#variants").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(expected_variant_ids))
    for variant_id in expected_variant_ids:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()

    # unknown variant
    query = "chr1-1234-N-N"
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variants")
    page.locator("#variants").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(0)

    # erroneous searches
    queries = ["chr1-1234-C", query_1.replace('-', ' '), "chr1-A-1234-C", ".*-.*-.*-.*", "---", "chr1-1234-A-G-T"]
    for query in queries:
        utils.nav(page.goto, utils.GOOD_STATI, url)
        open_search_options(page)
        page.wait_for_selector("#variants")
        page.locator("#variants").fill(query)
        utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
        utils.check_flash_id(page, "search_error_variants")



def open_search_options(page):
    if not page.locator("#variants").is_visible(): # only click the magnifying glass if the search options are not visible
        page.locator('#searchOptionsToggle').click()

def get_exact_variant_str_repr(variant_id, conn):
    variant = conn.get_variant(variant_id)
    str_repr = '-'.join([variant.chrom, str(variant.pos), variant.ref, variant.alt])
    return str_repr