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

def perform_browse_test(page, conn, worker, all_variant_ids, user_id):
    worker(page, conn, url_for('variant.search', _external=True), all_variant_ids)

    # do the same test on the variant list page
    list_name = "testlist"
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = False, public_edit = False)
    list_id = conn.get_last_insert_id()
    for variant_id in all_variant_ids:
        conn.add_variant_to_list(list_id, variant_id)
    worker(page, conn, url_for('user.my_lists', view = list_id, _external = True), all_variant_ids)

def test_range_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "T", alt = "A", orig_chr = "chr2", orig_pos = "214730441", orig_ref = "T", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730442", orig_ref = "G", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr2", pos = "214730451", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730451", orig_ref = "G", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr2", pos = "214730452", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730452", orig_ref = "G", orig_alt = "A", user_id = user_id),

        conn.insert_variant(chr = "chr17", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id), # chr17-43045752-C-A BRCA1
        conn.insert_variant(chr = "chr17", pos = "43045754", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045754", orig_ref = "C", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr17", pos = "43045760", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045760", orig_ref = "C", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr17", pos = "43045761", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045761", orig_ref = "C", orig_alt = "A", user_id = user_id),

        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T PALB2
    ]

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, variant_range_worker, all_variant_ids, user_id)


def variant_range_worker(page, conn, url, all_variant_ids):
    # search for one position
    query = "chr2:214730441-214730441"
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ranges")
    page.locator("#ranges").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(variants_oi))
    for variant_id in variants_oi:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()

    # search for longer range
    query = "chr2:214730441-214730451"
    variants_oi = [all_variant_ids[1], all_variant_ids[2], all_variant_ids[3]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ranges")
    page.locator("#ranges").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(variants_oi))
    for variant_id in variants_oi:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()

    # search for multiple ranges
    query = " ; chr2: 214730441-2147 30451;  ;;\n17:43045752-43045760; "
    variants_oi = [all_variant_ids[1], all_variant_ids[2], all_variant_ids[3], all_variant_ids[5], all_variant_ids[6], all_variant_ids[7]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ranges")
    page.locator("#ranges").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(variants_oi))
    for variant_id in variants_oi:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()


def test_gene_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert genes
    conn.insert_gene(hgnc_id = "45908", symbol = "GENE1", name = "GENE1 desc", type = "protein-coding gene", omim_id = "398476", orphanet_id = "324985")
    conn.insert_gene(hgnc_id = "5467675", symbol = "GENE2", name = "GENE2 desc", type = "protein-coding gene", omim_id = "676547", orphanet_id = "")
    conn.insert_gene(hgnc_id = "567856", symbol = "GENE3", name = "GENE3 desc", type = "protein-coding gene", omim_id = "", orphanet_id = "")

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730439", ref = "C", alt = "T", orig_chr = "chr2", orig_pos = "214730439", orig_ref = "C", orig_alt = "T", user_id = user_id), # chr2-214730439-C-T BARD1
        conn.insert_variant(chr = "chr17", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id), # chr17-43045752-C-A BRCA1
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T PALB2
    ]

    # insert consequences
    conn.insert_variant_consequence(variant_id = all_variant_ids[0], transcript_name = "ENST11111111111", hgvs_c = "c.1973G>A", hgvs_p = "p.Arg658His", consequence = "missense variant", impact = "moderate", exon_nr = "10", intron_nr  = "", hgnc_id = "", symbol = "GENE1", consequence_source = "ensembl", pfam_acc = "")
    conn.insert_variant_consequence(variant_id = all_variant_ids[1], transcript_name = "ENST22222222222", hgvs_c = "c.5518G>T", hgvs_p = "p.Asp1840Tyr", consequence = "missense variant", impact = "moderate", exon_nr = "10", intron_nr  = "", hgnc_id = "", symbol = "GENE2", consequence_source = "ensembl", pfam_acc = "")
    conn.insert_variant_consequence(variant_id = all_variant_ids[2], transcript_name = "ENST33333333333", hgvs_c = "", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE3", consequence_source = "ensembl", pfam_acc = "")
 	

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, variant_gene_worker, all_variant_ids, user_id)


def variant_gene_worker(page, conn, url, all_variant_ids):
    # search for one gene
    query = "GENE1"
    variants_oi = [all_variant_ids[0]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#genes")
    page.locator("#genes").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(variants_oi))
    for variant_id in variants_oi:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()

    # search for multiple genes
    query = "GENE1;; GENE2  ;\nGENE1"
    variants_oi = [all_variant_ids[0], all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#genes")
    page.locator("#genes").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(variants_oi))
    for variant_id in variants_oi:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()





def test_variant_type_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    all_variant_ids = [
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id), # chr16-23603525-C-T
        conn.insert_variant(chr = "chr22", pos = "28689217", ref = "T", alt = "C", orig_chr = "chr22", orig_pos = "28689217", orig_ref = "T", orig_alt = "C", user_id = user_id), # chr22-28689217-T-C
        conn.insert_sv_variant(chrom = "chr2", start = "9834578", end = "9834678", sv_type = "DEL", imprecise = False)[0] # take only variant_id, discard structural_variant_id
    ]

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, variant_type_search_worker, all_variant_ids, user_id)
    
    
def variant_type_search_worker(page, conn, url, all_variant_ids):
    small_variant_ids = [all_variant_ids[0], all_variant_ids[1]]
    sv_variant_ids = [all_variant_ids[2]]
    # search only small variants
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variant_type_small_variants")
    page.locator("#variant_type_small_variants").check()
    page.locator("#variant_type_structural_variant").uncheck()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(small_variant_ids))
    for variant_id in small_variant_ids:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()
    
    # search only structural variants
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variant_type_small_variants")
    page.locator("#variant_type_small_variants").uncheck()
    page.locator("#variant_type_structural_variant").check()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(sv_variant_ids))
    for variant_id in sv_variant_ids:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()

    # search both
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variant_type_small_variants")
    page.locator("#variant_type_small_variants").check()
    page.locator("#variant_type_structural_variant").check()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(all_variant_ids))
    for variant_id in all_variant_ids:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()


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