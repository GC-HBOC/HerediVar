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

def perform_browse_test(page, conn, worker, all_variant_ids, user_id):
    worker(page, conn, url_for('variant.search', _external=True), all_variant_ids)

    # do the same test on the variant list page
    list_name = "testlist"
    conn.insert_user_variant_list(user_id = user_id, list_name = list_name, public_read = False, public_edit = False)
    list_id = conn.get_last_insert_id()
    for variant_id in all_variant_ids:
        conn.add_variant_to_list(list_id, variant_id)
    worker(page, conn, url_for('user.my_lists', view = list_id, _external = True), all_variant_ids)

def test_cdna_range_search(page, conn):
    pass

def test_annotation_search(page, conn):
    pass




def test_hgvs_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert genes
    conn.insert_gene(hgnc_id = "45908", symbol = "GENE1", name = "GENE1 desc", type = "protein-coding gene", omim_id = "398476", orphanet_id = "324985")
    conn.insert_gene(hgnc_id = "45909", symbol = "GENE2", name = "GENE2 desc", type = "protein-coding gene", omim_id = "", orphanet_id = "")


    # insert transcripts
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST11111111111", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = True, is_mane_plus_clinical = True, is_ensembl_canonical = True, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST22222222222", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = False, is_mane_plus_clinical = True, is_ensembl_canonical = True, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST33333333333", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = False, is_mane_plus_clinical = False, is_ensembl_canonical = True, transcript_refseq = None)
    
    conn.insert_transcript(symbol = None, hgnc_id = "45909", transcript_ensembl = "ENST44444444444", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = False, is_mane_plus_clinical = False, is_ensembl_canonical = True, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45909", transcript_ensembl = "ENST55555555555", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = False, is_mane_select = False, is_mane_plus_clinical = True, is_ensembl_canonical = False, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45909", transcript_ensembl = "ENST66666666666", transcript_biotype = "protein coding", total_length = "100", chrom = "chr1", start = "100000", end = "100100", orientation = "+", exons = [(100000, 100100, True)], is_gencode_basic = False, is_mane_select = False, is_mane_plus_clinical = False, is_ensembl_canonical = False, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45909", transcript_ensembl = "ENST77777777777", transcript_biotype = "protein coding", total_length = "10", chrom = "chr1", start = "100000", end = "100010", orientation = "+", exons = [(100000, 100010, True)], is_gencode_basic = False, is_mane_select = False, is_mane_plus_clinical = False, is_ensembl_canonical = False, transcript_refseq = None)

    # insert variantsd
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr1", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T PALB2
    ]
    
    # insert consequences
    conn.insert_variant_consequence(variant_id = all_variant_ids[1], transcript_name = "ENST11111111111", hgvs_c = "c.100C>A", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE1", consequence_source = "ensembl")
    conn.insert_variant_consequence(variant_id = all_variant_ids[1], transcript_name = "ENST22222222222", hgvs_c = "c.101C>A", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE1", consequence_source = "ensembl")
    
    conn.insert_variant_consequence(variant_id = all_variant_ids[2], transcript_name = "ENST44444444444", hgvs_c = "c.200C>T", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE2", consequence_source = "ensembl")
    conn.insert_variant_consequence(variant_id = all_variant_ids[2], transcript_name = "ENST55555555555", hgvs_c = "c.201C>T", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE2", consequence_source = "ensembl")
    conn.insert_variant_consequence(variant_id = all_variant_ids[2], transcript_name = "ENST66666666666", hgvs_c = "c.202C>T", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE2", consequence_source = "ensembl")


    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, hgvs_search_worker, all_variant_ids, user_id)


def hgvs_search_worker(page, conn, url, all_variant_ids):
    # search for one hgvsc: mane select
    query = "ENST11111111111:c.100C>A"
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search for one hgvsc: not mane select
    query = "ENST22222222222:c.101C>A"
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search for one hgvsc with gene symbol
    query = "GENE1:c.100C>A"
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    query = "45908:c.100C>A" # use hgnc id instead of gene symbol
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    query = "UNKNOWNGENE:c.100C>A" # wrong gene
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(0)

    query = "GENE1:c.101C>A" # hgvsc is not the one from mane select
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(0)

    query = "GENE2:c.200C>T" # there is no mane select transcript -> gencode basic one is chosen
    variants_oi = [all_variant_ids[2]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search for one hgvsc without gene information
    query = "c.100C>A"
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    query = "c.101C>A" # hgvsc is not the one from mane select
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    expect(page.locator("tr[name='variant_row']")).to_have_count(0)

    # search for multiple hgvsc strings
    query = "c.100C>A;  ;GENE2:c.200C>T; \nENST11111111111:c.100C>A" # there is no mane select transcript -> gencode basic one is chosen
    variants_oi = [all_variant_ids[1], all_variant_ids[2]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#hgvs")
    page.locator("#hgvs").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

def test_id_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])
    recent_annotation_type_ids = conn.get_recent_annotation_type_ids()

    # insert variantsd
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr17", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id), # chr17-43045752-C-A BRCA1
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id), # chr16-23603525-C-T PALB2
        conn.insert_variant(chr = "chr16", pos = "23603526", ref = "A", alt = "T", orig_chr = "chr16", orig_pos = "23603526", orig_ref = "C", orig_alt = "T", user_id = user_id),
        conn.insert_variant(chr = "chr16", pos = "23603527", ref = "A", alt = "T", orig_chr = "chr16", orig_pos = "23603527", orig_ref = "C", orig_alt = "T", user_id = user_id)
    ]

    # insert variant id
    conn.insert_external_variant_id(all_variant_ids[0], "11111", recent_annotation_type_ids["rsid"])
    conn.insert_external_variant_id(all_variant_ids[0], "22222", recent_annotation_type_ids["cosmic"])
    conn.insert_external_variant_id(all_variant_ids[0], "33333", recent_annotation_type_ids["clinvar"])
    conn.insert_external_variant_id(all_variant_ids[1], "44444", recent_annotation_type_ids["rsid"])
    conn.insert_external_variant_id(all_variant_ids[1], "11111", recent_annotation_type_ids["cosmic"])
    conn.insert_external_variant_id(all_variant_ids[2], "55555", recent_annotation_type_ids["cosmic"])
    conn.insert_external_variant_id(all_variant_ids[3], "66666", recent_annotation_type_ids["heredicare_vid"])

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, id_search_worker, all_variant_ids, user_id)

def id_search_worker(page, conn, url, all_variant_ids):
    # search for the heredivar variant id
    query = str(all_variant_ids[0])
    variants_oi = [all_variant_ids[0]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#external_ids")
    page.locator("#external_ids").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # test all prefixes
    query = ";".join([str(all_variant_ids[0]) + ":heredivar", "44444:rsid", "55555:cosmic", "66666:heredicare"]) 
    variants_oi = [all_variant_ids[0], all_variant_ids[1], all_variant_ids[2], all_variant_ids[3]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#external_ids")
    page.locator("#external_ids").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search for one variant id which is equal in dbsnp and cosmic -> results in two variants
    query = "11111"
    variants_oi = [all_variant_ids[0], all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#external_ids")
    page.locator("#external_ids").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # filter this search down to the first variant
    query = "11111:rsid"
    variants_oi = [all_variant_ids[0]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#external_ids")
    page.locator("#external_ids").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)


def test_consensus_classification_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1 class 1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 2, heredicare consensus class 1
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3-
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3
        conn.insert_variant(chr = "chr2", pos = "214730444", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3+
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 4
        conn.insert_variant(chr = "chr2", pos = "214730446", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 4M
        conn.insert_variant(chr = "chr2", pos = "214730447", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 5
        conn.insert_variant(chr = "chr2", pos = "214730448", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # no classification

        conn.insert_variant(chr = "chr2", pos = "214730449", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # heredicare consensus class 1, no heredivar consensus class
        conn.insert_variant(chr = "chr2", pos = "214730450", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # heredicare consensus class 1, heredivar consensus class 1
    ]

    # insert consensus classifications
    classification_scheme_id = conn.get_classification_scheme_id_from_alias("ACMG standard + SVI", 'v1.0.0')
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[0], consensus_classification = "1", comment = "TEST1", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "1")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[1], consensus_classification = "2", comment = "TEST2", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "2")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[2], consensus_classification = "3-", comment = "TEST3", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "3")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[3], consensus_classification = "3", comment = "TEST4", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "3")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[4], consensus_classification = "3+", comment = "TEST5", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "3")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[5], consensus_classification = "4", comment = "TEST6", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "4")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[6], consensus_classification = "4M", comment = "TEST7", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "4")
    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[7], consensus_classification = "5", comment = "TEST8", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "5")

    conn.insert_consensus_classification(user_id = user_id, variant_id = all_variant_ids[10], consensus_classification = "1", comment = "TEST10", evidence_document = bytes("TESTEXAMPLE", 'utf-8'), date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "1")

    # insert heredicare consensus classification
    conn.insert_heredicare_annotation(variant_id = all_variant_ids[1], vid = "123456", n_fam = 0, n_pat = 0, consensus_class = "11", classification_date = functions.get_now(), comment = None, lr_cooc = None, lr_coseg = None, lr_family = None)
    conn.insert_heredicare_annotation(variant_id = all_variant_ids[9], vid = "123457", n_fam = 0, n_pat = 0, consensus_class = "11", classification_date = functions.get_now(), comment = None, lr_cooc = None, lr_coseg = None, lr_family = None)
    conn.insert_heredicare_annotation(variant_id = all_variant_ids[10], vid = "123458", n_fam = 0, n_pat = 0, consensus_class = "11", classification_date = functions.get_now(), comment = None, lr_cooc = None, lr_coseg = None, lr_family = None)

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, consensus_classification_search_worker, all_variant_ids, user_id)

def consensus_classification_search_worker(page, conn, url, all_variant_ids):
    # search for each consensus classification once
    variant_id_by_consensus_class = {
        "cl1": [all_variant_ids[0], all_variant_ids[10]], 
        "cl2": [all_variant_ids[1]], 
        "cl3-": [all_variant_ids[2]], 
        "cl3": [all_variant_ids[3]], 
        "cl3p": [all_variant_ids[4]], 
        "cl4": [all_variant_ids[5]], 
        "cl4M": [all_variant_ids[6]], 
        "cl5": [all_variant_ids[7]], 
        "cl-": [all_variant_ids[8], all_variant_ids[9]]
    }
    all_check_selectors = ["cl1", "cl2", "cl3-", "cl3", "cl3p", "cl4", "cl4M", "cl5", "cl-"]
    for check_selector in all_check_selectors:
        variants_oi = variant_id_by_consensus_class[check_selector]
        utils.nav(page.goto, utils.GOOD_STATI, url)
        open_search_options(page)
        page.wait_for_selector("#cl1")
        uncheck_selectors = list(set(all_check_selectors) - {check_selector})
        uncheck_selectors.append("include_heredicare_consensus")
        check_group(page, check_selectors = [check_selector], uncheck_selectors = uncheck_selectors)
        utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
        check_variant_search(page, variants_oi)

    # search for all consensus classes simultaneously
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#cl1")
    check_group(page, check_selectors = all_check_selectors, uncheck_selectors = ["include_heredicare_consensus"])
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # include heredicare in search
    variants_oi = [all_variant_ids[0], all_variant_ids[9], all_variant_ids[10]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#cl1")
    check_selectors = ["cl1", "include_heredicare_consensus"]
    uncheck_selectors = list(set(all_check_selectors) - set(check_selectors))
    check_group(page, check_selectors = check_selectors, uncheck_selectors = uncheck_selectors)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

def check_group(page, check_selectors: list, uncheck_selectors: list):
    for check_selector in check_selectors:
        page.get_by_test_id(check_selector).check()
    for uncheck_selector in uncheck_selectors:
        page.get_by_test_id(uncheck_selector).uncheck()


def test_user_classification_search(page, conn):
# seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    conn.insert_user(username = "transient_tester", first_name = "TRA", last_name = "TEST", affiliation = "AFF")
    transient_test_user_id = conn.get_user_id("transient_tester")

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1 class 1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 2
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3-
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3
        conn.insert_variant(chr = "chr2", pos = "214730444", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3+
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 4
        conn.insert_variant(chr = "chr2", pos = "214730446", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 4M
        conn.insert_variant(chr = "chr2", pos = "214730447", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 5
        conn.insert_variant(chr = "chr2", pos = "214730448", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # no classification
    ]

    # insert consensus classifications
    classification_scheme_id = conn.get_classification_scheme_id_from_alias("ACMG standard + SVI", 'v1.0.0')
    conn.insert_user_classification(variant_id = all_variant_ids[0], classification = "1", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "1")
    conn.insert_user_classification(variant_id = all_variant_ids[1], classification = "2", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "2")
    conn.insert_user_classification(variant_id = all_variant_ids[2], classification = "3-", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "3")
    conn.insert_user_classification(variant_id = all_variant_ids[3], classification = "3", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "3")
    conn.insert_user_classification(variant_id = all_variant_ids[4], classification = "3+", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "3")
    conn.insert_user_classification(variant_id = all_variant_ids[5], classification = "4", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "4")
    conn.insert_user_classification(variant_id = all_variant_ids[6], classification = "4M", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "4")
    conn.insert_user_classification(variant_id = all_variant_ids[7], classification = "5", user_id = user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "5")

    conn.insert_user_classification(variant_id = all_variant_ids[1], classification = "1", user_id = transient_test_user_id, comment = "", date = functions.get_now(), scheme_id = classification_scheme_id, scheme_class = "1")


    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, user_classification_search_worker, all_variant_ids, user_id)

def user_classification_search_worker(page, conn, url, all_variant_ids):
    # search for each user classification once
    variant_id_by_class = {
        "ucl1": [all_variant_ids[0]], 
        "ucl2": [all_variant_ids[1]], 
        "ucl3-": [all_variant_ids[2]], 
        "ucl3": [all_variant_ids[3]], 
        "ucl3p": [all_variant_ids[4]], 
        "ucl4": [all_variant_ids[5]], 
        "ucl4M": [all_variant_ids[6]], 
        "ucl5": [all_variant_ids[7]], 
        "ucl-": [all_variant_ids[8]]
    }
    all_check_selectors = ["ucl1", "ucl2", "ucl3-", "ucl3", "ucl3p", "ucl4", "ucl4M", "ucl5", "ucl-"]
    for check_selector in all_check_selectors:
        variants_oi = variant_id_by_class[check_selector]
        utils.nav(page.goto, utils.GOOD_STATI, url)
        open_search_options(page)
        page.wait_for_selector("#ucl1")
        uncheck_selectors = list(set(all_check_selectors) - {check_selector})
        check_group(page, check_selectors = [check_selector], uncheck_selectors = uncheck_selectors)
        utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
        check_variant_search(page, variants_oi)

    # search for all classes simultaneously
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ucl1")
    check_group(page, check_selectors = all_check_selectors, uncheck_selectors = [])
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)




def test_automatic_classification_splicing_search(page, conn):
# seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1 class 1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 2
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 4
        conn.insert_variant(chr = "chr2", pos = "214730444", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 5
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # no classification
    ]

    # insert consensus classifications
    classification_scheme_id = conn.get_classification_scheme_id_from_alias("ACMG standard + SVI", 'v1.0.0')
    conn.insert_automatic_classification(variant_id = all_variant_ids[0], classification_scheme_id = classification_scheme_id, classification_splicing = "1", classification_protein = "2", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[1], classification_scheme_id = classification_scheme_id, classification_splicing = "2", classification_protein = "1", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[2], classification_scheme_id = classification_scheme_id, classification_splicing = "3", classification_protein = "1", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[3], classification_scheme_id = classification_scheme_id, classification_splicing = "4", classification_protein = "1", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[4], classification_scheme_id = classification_scheme_id, classification_splicing = "5", classification_protein = "1", tool_version = "1.0.0")


    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, automatic_classification_splicing_search_worker, all_variant_ids, user_id)

def automatic_classification_splicing_search_worker(page, conn, url, all_variant_ids):
    # search for each user classification once
    variant_id_by_class = {
        "acls1": [all_variant_ids[0]], 
        "acls2": [all_variant_ids[1]], 
        "acls3": [all_variant_ids[2]], 
        "acls4": [all_variant_ids[3]], 
        "acls5": [all_variant_ids[4]], 
        "acls-": [all_variant_ids[5]]
    }
    all_check_selectors = ["acls1", "acls2", "acls3", "acls4", "acls5", "acls-"]
    for check_selector in all_check_selectors:
        variants_oi = variant_id_by_class[check_selector]
        utils.nav(page.goto, utils.GOOD_STATI, url)
        open_search_options(page)
        page.wait_for_selector("#acls1")
        uncheck_selectors = list(set(all_check_selectors) - {check_selector})
        check_group(page, check_selectors = [check_selector], uncheck_selectors = uncheck_selectors)
        utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
        check_variant_search(page, variants_oi)

    # search for all classes simultaneously
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#acls1")
    check_group(page, check_selectors = all_check_selectors, uncheck_selectors = [])
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)



def test_automatic_classification_protein_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1 class 1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 2
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 3
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 4
        conn.insert_variant(chr = "chr2", pos = "214730444", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # class 5
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # no classification
    ]

    # insert consensus classifications
    classification_scheme_id = conn.get_classification_scheme_id_from_alias("ACMG standard + SVI", 'v1.0.0')
    conn.insert_automatic_classification(variant_id = all_variant_ids[0], classification_scheme_id = classification_scheme_id, classification_splicing = "2", classification_protein = "1", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[1], classification_scheme_id = classification_scheme_id, classification_splicing = "1", classification_protein = "2", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[2], classification_scheme_id = classification_scheme_id, classification_splicing = "1", classification_protein = "3", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[3], classification_scheme_id = classification_scheme_id, classification_splicing = "1", classification_protein = "4", tool_version = "1.0.0")
    conn.insert_automatic_classification(variant_id = all_variant_ids[4], classification_scheme_id = classification_scheme_id, classification_splicing = "1", classification_protein = "5", tool_version = "1.0.0")


    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, automatic_classification_protein_search_worker, all_variant_ids, user_id)

def automatic_classification_protein_search_worker(page, conn, url, all_variant_ids):
    # search for each user classification once
    variant_id_by_class = {
        "aclp1": [all_variant_ids[0]], 
        "aclp2": [all_variant_ids[1]], 
        "aclp3": [all_variant_ids[2]], 
        "aclp4": [all_variant_ids[3]], 
        "aclp5": [all_variant_ids[4]], 
        "aclp-": [all_variant_ids[5]]
    }
    all_check_selectors = ["aclp1", "aclp2", "aclp3", "aclp4", "aclp5", "aclp-"]
    for check_selector in all_check_selectors:
        variants_oi = variant_id_by_class[check_selector]
        utils.nav(page.goto, utils.GOOD_STATI, url)
        open_search_options(page)
        page.wait_for_selector("#aclp1")
        uncheck_selectors = list(set(all_check_selectors) - {check_selector})
        check_group(page, check_selectors = [check_selector], uncheck_selectors = uncheck_selectors)
        utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
        check_variant_search(page, variants_oi)

    # search for all classes simultaneously
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#aclp1")
    check_group(page, check_selectors = all_check_selectors, uncheck_selectors = [])
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)


def test_list_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    conn.insert_user(username = "transient_tester", first_name = "TRA", last_name = "TEST", affiliation = "AFF")
    transient_test_user_id = conn.get_user_id("transient_tester")

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1 in list1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # in list 1
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # in list 2
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # in private list
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # in no list
    ]

    # insert lists
    conn.insert_user_variant_list(user_id = transient_test_user_id, list_name = "privl", public_read = False, public_edit = False)
    list_id_private = conn.get_last_insert_id()

    conn.insert_user_variant_list(user_id = user_id, list_name = "l1", public_read = False, public_edit = False)
    list_id_1 = conn.get_last_insert_id()

    conn.insert_user_variant_list(user_id = user_id, list_name = "l2", public_read = False, public_edit = False)
    list_id_2 = conn.get_last_insert_id()

    conn.insert_user_variant_list(user_id = user_id, list_name = "le", public_read = False, public_edit = False)
    list_id_private = conn.get_last_insert_id()

    # insert variants to list
    conn.add_variant_to_list(list_id = list_id_1, variant_id = all_variant_ids[0])
    conn.add_variant_to_list(list_id = list_id_1, variant_id = all_variant_ids[1])
    conn.add_variant_to_list(list_id = list_id_2, variant_id = all_variant_ids[2])
    conn.add_variant_to_list(list_id = list_id_private, variant_id = all_variant_ids[3])


    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, list_search_worker, all_variant_ids, user_id)


def list_search_worker(page, conn, url, all_variant_ids):
    # search for each user classification once
    variant_id_by_list = {
        "l1": [all_variant_ids[0], all_variant_ids[1]], 
        "l2": [all_variant_ids[2]],
        "le": []
    }
    
    # search for one list
    for list_name in variant_id_by_list:
        variants_oi = variant_id_by_list[list_name]
        utils.nav(page.goto, utils.GOOD_STATI, url)
        open_search_options(page)
        page.wait_for_selector("#add_list_select")
        page.get_by_placeholder("Select a list... start search by typing").nth(0).fill(list_name)
        page.locator("div[data-element-name='" + list_name + "']").click()
        utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
        check_variant_search(page, variants_oi)

    # search for multiple lists
    variants_oi = variant_id_by_list["l1"]
    variants_oi.extend(variant_id_by_list["l2"])
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#add_list_select")
    page.get_by_placeholder("Select a list... start search by typing").nth(0).fill("l1")
    page.locator("div[data-element-name='l1']").click()
    page.locator("#add_list_select").click()
    page.get_by_placeholder("Select a list... start search by typing").nth(1).fill("l2")
    page.locator("div[data-element-name='l2']").click()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search for unknown list
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#add_list_select")
    page.get_by_placeholder("Select a list... start search by typing").nth(0).fill("this list does not exist")
    page.locator("#aclp-").click()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)
    utils.check_flash_id(page, "unknown_list_search")

    # search for forbidden list
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#add_list_select")
    page.get_by_placeholder("Select a list... start search by typing").nth(0).fill("privl")
    page.locator("#aclp-").click()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)
    utils.check_flash_id(page, "unknown_list_search")

    # also fill the list_id hidden input to truely test forbidden lists
    lookup_list_id = conn.get_list_id_by_name("privl")[0]
    utils.nav(page.goto, utils.UNAUTHORIZED_STATI, url_for("variant.search", lookup_list_id=lookup_list_id, lookup_list_name="privl", _external=True))


def test_page_size_adjust(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730446", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # 
    ]

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, page_size_adjust_worker, all_variant_ids, user_id)


def page_size_adjust_worker(page, conn, url, all_variant_ids):
    # adjust page size to 5
    variants_oi = all_variant_ids[0:5]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#page_size")
    page.locator("#page_size").select_option("5")
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)



def test_search_order_adjust(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730442", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730443", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730445", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # 
        conn.insert_variant(chr = "chr2", pos = "214730446", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # 
    ]

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, search_order_adjust_worker, all_variant_ids, user_id)


def search_order_adjust_worker(page, conn, url, all_variant_ids):
    # adjust page size to 5
    variants_oi = all_variant_ids[-6:]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#sort_by")
    page.locator("#sort_by").select_option("recent")
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)


def test_variant_status_adjust(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr2", pos = "214730441", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id) # 
    ]

    conn.hide_variant(variant_id = all_variant_ids[0], is_hidden = False)

    # start the test
    utils.login(page, user)

    perform_browse_test(page, conn, variant_status_adjust_worker, all_variant_ids, user_id)


def variant_status_adjust_worker(page, conn, url, all_variant_ids):
    # search without hidden variants
    variants_oi = [all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search with hidden variants
    variants_oi = all_variant_ids
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.locator("#include_hidden").check()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)



def test_range_search(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variantsd
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
    check_variant_search(page, variants_oi)

    # search for longer range
    query = "chr2:214730441-214730451"
    variants_oi = [all_variant_ids[1], all_variant_ids[2], all_variant_ids[3]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ranges")
    page.locator("#ranges").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # search for multiple ranges
    query = " ; chr2-214730441-214730451;  ;;\n17\t43045752  \t43045760; "
    variants_oi = [all_variant_ids[1], all_variant_ids[2], all_variant_ids[3], all_variant_ids[5], all_variant_ids[6], all_variant_ids[7]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ranges")
    page.locator("#ranges").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)

    # upload bam file and search for it
    variants_oi = [all_variant_ids[1], all_variant_ids[2], all_variant_ids[3], all_variant_ids[5], all_variant_ids[6], all_variant_ids[7]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#ranges")
    with page.expect_file_chooser() as fc_info:
        page.locator("#loadbed").click()
    file_chooser = fc_info.value
    file_chooser.set_files(paths.range_search_bed)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)




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
    conn.insert_variant_consequence(variant_id = all_variant_ids[0], transcript_name = "ENST11111111111", hgvs_c = "c.1973G>A", hgvs_p = "p.Arg658His", consequence = "missense variant", impact = "moderate", exon_nr = "10", intron_nr  = "", hgnc_id = "", symbol = "GENE1", consequence_source = "ensembl")
    conn.insert_variant_consequence(variant_id = all_variant_ids[1], transcript_name = "ENST22222222222", hgvs_c = "c.5518G>T", hgvs_p = "p.Asp1840Tyr", consequence = "missense variant", impact = "moderate", exon_nr = "10", intron_nr  = "", hgnc_id = "", symbol = "GENE2", consequence_source = "ensembl")
    conn.insert_variant_consequence(variant_id = all_variant_ids[2], transcript_name = "ENST33333333333", hgvs_c = "", hgvs_p = "", consequence = "missense variant", impact = "moderate", exon_nr = "", intron_nr  = "", hgnc_id = "", symbol = "GENE3", consequence_source = "ensembl")

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
    check_variant_search(page, variants_oi)

    # search for multiple genes
    query = "GENE1;; GENE2  ;\nGENE1"
    variants_oi = [all_variant_ids[0], all_variant_ids[1]]
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#genes")
    page.locator("#genes").fill(query)
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, variants_oi)





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
    check_variant_search(page, small_variant_ids)
    
    # search only structural variants
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variant_type_small_variants")
    page.locator("#variant_type_small_variants").uncheck()
    page.locator("#variant_type_structural_variant").check()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, sv_variant_ids)

    # search both
    utils.nav(page.goto, utils.GOOD_STATI, url)
    open_search_options(page)
    page.wait_for_selector("#variant_type_small_variants")
    page.locator("#variant_type_small_variants").check()
    page.locator("#variant_type_structural_variant").check()
    utils.nav(page.click, utils.GOOD_STATI, "#submit_search")
    check_variant_search(page, all_variant_ids)


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
    check_variant_search(page, expected_variant_ids)

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

# this function checks if the number of shown variants is correct and that the correct rows are shwon
def check_variant_search(page, variants_oi):
    expect(page.locator("tr[name='variant_row']")).to_have_count(len(variants_oi))
    for variant_id in variants_oi:
        expect(page.locator("tr[name='variant_row'][variant_id='" + str(variant_id) + "']")).to_be_visible()