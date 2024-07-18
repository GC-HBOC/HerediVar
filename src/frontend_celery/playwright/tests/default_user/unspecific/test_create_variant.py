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






def test_create_simple_variant_vcf(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id)

    # start the test
    utils.login(page, user)

    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.create', _external = True))

    # variant already in database
    variant_from_vcf(variant_data = {
        "chrom": "chr2",
        "pos": "214730440",
        "ref": "G",
        "alt": "A",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_already_in_database")

    # incorrect position
    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "-1",
        "ref": "A",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "A",
        "ref": "A",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "439857298576283745283765823764867234",
        "ref": "A",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1-1",
        "ref": "A",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    # incorrect reference base
    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "A",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "V",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "N",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": ".",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "-",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234566",
        "ref": "CCGTGTGTGCACAGTTTGTTCTTGGACGAGGACTCGTGAGGATCGAGGGCTGGGGACCCCGGTGTGAGCAGGATGGGGCCCTGCCCTCCCGTGGGAGTTGTGGACTCGAGCCCAGGGGCTGCCCGTCACAGCGGTGTCCCAGGTCCCTGCCATCCGATTTTACCTGGGATGTCTTCTCTGGAGTTTGGAATTGCTTGAGGAACCCTGCGTGTGCTTGGAGAGGCCAGAGGGCTTGCTGAGAACCCCATGGACAGTGGAGAGCGGGATTCGAACCAAGGGCTGGACTCCCACACCTCTGGCCTGCGTCGCCCAGTTCTTTGTGGCTCTGAAGAATTGGCCGCTGTGGAAAAGAGCAAATGTCCGAGACCCCCAACAGGAAGAGTCTAAAAATCCAGTTTGCAACCACTTCTGACCTACAAAAAAATGGAAATTTAGTGTTTTTCAGCCTAAGACATTAAATTTCATATCAGAACAAAGCCTGCCCCAGGCTGACCCTCCCCAGCCGTACCGTGGTGAACGGGTTCAGAGGATACGTGGGCTGAAGGCTGGGCCTCGGGAGGGCTGGGGGCTTCCAGAGCCGGGGCAGCTGCAGCTCTCTCTGGTCTCACCTGGAACTTGCCCTGTAGATCCTCCCTGCCCTGCGGCTCCAATCGACCGTGCACGGGCCGTGGCATCCGTCCCCCAGGCGTCCTTCCCTGGTCTTAGCTTGTACAGCTCCCCACCCACCCAGGTACTCGGTTCCCGGAGACCAGGGCCAAACCAGGAGGCCCTCGGGAGATGGGGGGTCACCGAATTCATTTCCATGTGGGAACTTGGGATACAAAACAGCCAACTCTTCCTCAGCCACACGGATGTTTCTCCTCTAGTGGCCCCGAGAACCTACCATGGAGGGGACAGTGTCAGGGCTGGACGGGCACGGCGCAGCCACACGCACACAGCCCCCAGGAGGCACAGGGCCGGCAGGGAATGCAGGTCAAGCCAAGAGGATGGGCTCTGGTCCC",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    # incorrect alternative base
    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "N",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "IOL",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "-",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": ".",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "A"*1001,
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    # ref==alt
    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "C",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "variant_from_vcf_error")

    # missing data
    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "",
        "ref": "C",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "missing_data_vcf")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "",
        "alt": "G",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "missing_data_vcf")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "",
        "genome": "GRCh38"
    }, page = page)
    utils.check_flash_id(page, "missing_data_vcf")

    variant_from_vcf(variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "G",
        "genome": ""
    }, page = page)
    utils.check_flash_id(page, "missing_data_vcf")

    # correct variant
    variant_data = {
        "chrom": "chr1",
        "pos": "1234567",
        "ref": "C",
        "alt": "G",
        "genome": "GRCh38"
    }
    variant_from_vcf(variant_data, page = page)
    utils.check_flash_id(page, "successful_variant_from_vcf")
    utils.check_all_links(page)
    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.display', chr=variant_data["chrom"], pos=variant_data["pos"], ref=variant_data["ref"], alt=variant_data["alt"], _external = True))



def variant_from_vcf(variant_data, page):
    page.locator('#vcf-tab').click()

    chrom = variant_data["chrom"]
    pos = variant_data["pos"]
    ref = variant_data["ref"]
    alt = variant_data["alt"]
    genome = variant_data["genome"]

    if chrom != "":
        page.select_option('select#Chromosome', label=chrom)
    page.locator('input#Position').fill(str(pos))
    page.locator('input#Reference').fill(ref)
    page.locator('input#Alternative').fill(alt)
    if genome != "":
        page.select_option('select#reference_genome', value=genome)

    utils.nav(page.click, utils.GOOD_STATI, "#submit_variant")


def test_create_simple_variant_hgvs(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # insert variants
    variant_id = conn.insert_variant(chr = "chr2", pos = "214730440", ref = "G", alt = "A", orig_chr = "chr2", orig_pos = "214730440", orig_ref = "G", orig_alt = "A", user_id = user_id)

    # insert genes
    conn.insert_gene(hgnc_id = "45908", symbol = "GENE1", name = "GENE1 desc", type = "protein-coding gene", omim_id = "398476", orphanet_id = "324985")

    # add some transcripts (for transcript annotations)    
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST00000260947", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = True, is_mane_plus_clinical = True, is_ensembl_canonical = True, transcript_refseq = None)

    # add some consequences
    consequences = [
        # ensembl
        {"transcript_name": "ENST00000260947", "hgvs_c": "c.1972C>T", "hgvs_p": "p.Arg658Cys", "consequence": "missense variant1", "impact": "high", "exon_nr": "exon1", "intron_nr": "intron2", "hgnc_id": "", "symbol": "GENE1", "consequence_source": "ensembl"},
    ]
    for consequence in consequences:
        conn.insert_variant_consequence(variant_id = variant_id, **consequence)


    # start the test
    utils.login(page, user)

    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.create', _external = True))

    # variant duplicate
    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": "c.1972C>T"
    }, page = page)
    utils.check_flash_id(page, "variant_already_in_database")

    variant_from_hgvs(variant_data = {
        "transcript": "NM_000465",
        "hgvs_c": "c.1972C>T"
    }, page = page)
    utils.check_flash_id(page, "variant_already_in_database")

    # wrong transcript
    variant_from_hgvs(variant_data = {
        "transcript": "ENST1234",
        "hgvs_c": "c.1972C>T"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    variant_from_hgvs(variant_data = {
        "transcript": "THISISNOTATRANSCRIPT",
        "hgvs_c": "c.1972C>T"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    # wrong hgvs
    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": "p.Arg658Cys"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": "1972C>T"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": "c.2C>T"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": "c.1972A>T"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": "c.1972C>N"
    }, page = page)
    utils.check_flash_id(page, "variant_from_hgvs_error")

    # missing data
    variant_from_hgvs(variant_data = {
        "transcript": "",
        "hgvs_c": "c.1972C>T"
    }, page = page)
    utils.check_flash_id(page, "missing_data_hgvs")

    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000260947",
        "hgvs_c": ""
    }, page = page)
    utils.check_flash_id(page, "missing_data_hgvs")


    # insert works
    variant_from_hgvs(variant_data = {
        "transcript": "ENST00000676179",
        "hgvs_c": "c.85C>G"
    }, page = page)
    utils.check_flash_id(page, "successful_variant_from_hgvs")



def variant_from_hgvs(variant_data, page):
    page.locator('#hgvs-tab').click()

    transcript = variant_data["transcript"]
    hgvs_c = variant_data["hgvs_c"]

    page.locator("#reference_transcript").fill(transcript)
    page.locator("#hgvsc").fill(hgvs_c)

    utils.nav(page.click, utils.GOOD_STATI, "#submit_variant_hgvs")

#def test_create_sv(page, conn):
#    # seed database
#    user = utils.get_user()
#    user_id = conn.get_user_id(user["username"])
#
#    # start the test
#    utils.login(page, user)
#
#    utils.nav(page.goto, utils.GOOD_STATI, url_for('variant.create', _external = True))