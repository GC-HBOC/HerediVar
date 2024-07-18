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


def get_default_annotation_values():
    # simple annotations
    simple_annotation_values = {
        'phylop_100way': "3.54", # 4
        'cadd_scaled': "13.5", # 5
        'spliceai_details': "GENE1|0.00|0.00|0.00|0.00|-38|14|-1|-44,GENE2|0.00|0.00|0.00|0.00|-38|14|-1|-44", # 7
        'spliceai_max_delta': "0.0,0.0", # 8
        'gnomad_ac': "100", # 11
        'gnomad_af': "0.2", # 12
        'gnomad_hom': "53", # 13
        'gnomad_hemi': "52", # 14
        'gnomad_het': "51", # 15
        'gnomad_popmax': "AFR", # 16
        'gnomadm_ac_hom': "13", # 17
        'flossies_num_afr': "4", # 19
        'flossies_num_eur': "5", # 20
        'cancerhotspots_ac': "127", # 23
        'cancerhotspots_af': "0.005", # 24
        'tp53db_class': "LFS&LFL&noFH&FH&TP53_Chompret&Other", # 27
        'tp53db_DNE_LOF_class': "notDNE_notLOF", # 29
        'tp53db_DNE_class': "Yes", # 31
        'tp53db_domain_function': "Tetramerisation", # 32
        'tp53db_transactivation_class': "partially_functional", # 33
        'task_force_protein_domain': "ATPase/Helicase domain", # 36
        'task_force_protein_domain_source': "BWRL/ENIGMA", # 37
        'hexplorer': "-1.72", # 39
        'hexplorer_mut': "-1.58", # 40
        'hexplorer_wt': "-1.34", # 41
        'hexplorer_rev': "2.3", # 42
        'hexplorer_rev_mut': "1.45", # 43
        'hexplorer_rev_wt': "1.58", # 44
        'max_hbond': "9.80", # 45
        'max_hbond_mut': "6.60", # 46
        'max_hbond_wt': "4.79", # 47
        'max_hbond_rev': "5.78", # 48
        'max_hbond_rev_mut': "5.78", # 49
        'max_hbond_rev_wt': "6.89", # 50
        'gnomad_popmax_AF': "0.89", # 51
        'hci_prior': "0.02", # 52
        'bayesdel': "0.61701", # 55
        'gnomad_popmax_AC': "512", # 59
        'coldspot': "True", # 61
        'gnomad_ac_nc': "111429", # 64
        'gnomad_af_nc': "0.0212989", # 65
        'gnomad_hom_nc': "71126", # 66
        'gnomad_hemi_nc': "117", # 67
        'gnomad_het_nc': "8", # 68
        'faf95_popmax': "0.0174378", # 69
        'brca_exchange_clinical_significance': "Not Yet Reviewed" # 18
    }




    # transcript specific annotations
    transcript_specific_annotation_values = {
        "revel": [{"transcript": "ENST11111111111", "value": "0.198"}, {"transcript": "ENST22222222222", "value": "0.199"}], # 6
        "maxentscan": [{"transcript": "ENST11111111111", "value": "9.42|10.56"}, {"transcript": "ENST22222222222", "value": "7.86|7.47"}], # 53
        "maxentscan_swa": [{"transcript": "ENST11111111111", "value": "-4.50|-4.13|-4.50|-5.03|-5.72|-5.03"}, {"transcript": "ENST22222222222", "value": "-2.66|-1.95|-2.66|3.62|4.78|-3.82"}], # 54
        "pfam_domains": [{"transcript": "ENST11111111111", "value": "PF07728"}, {"transcript": "ENST22222222222", "value": "PF12774"}] # 70
    }

    # ID annotations
    id_annotation_values = {
        "rsid": "328", # 3
        "heredicare_vid": "8829570", # 56
        "cosmic": "COSV58787045", # 60
        "clinvar": "41818" # 62
    }

    # other annotations
    other_annotation_values = {
        "cancerhotspots": [{"oncotree_symbol": "soc", "cancertype": "Serous Ovarian Cancer", "tissue": "ovaryfallopiantube", "occurances": "3"},
                           {"oncotree_symbol": "gbm", "cancertype": "Glioblastoma Multiforme", "tissue": "cnsbrain", "occurances": "2"}
                        ], # 63
        "heredicare": [{"vid": "8829570", "n_fam": "1", "n_pat": "1", "consensus_class": "13", "classification_date": functions.get_today(), "comment": "CONSENSUS CLASSIFICATION EXAMPLE IMPORT", "lr_cooc": "0.169", "lr_coseg": "0.196", "lr_family": "0.6969"}]
    }

    annotation_values = {
        "simple": simple_annotation_values,
        "transcript": transcript_specific_annotation_values,
        "ID": id_annotation_values,
        "other": other_annotation_values
    }
    return annotation_values

def add_variant_all_annotations(chrom, pos, ref, alt, conn, annotation_values = get_default_annotation_values()):
    variant_id = conn.insert_variant(chr = chrom, pos = pos, ref = ref, alt = alt, orig_chr = chrom, orig_pos = pos, orig_ref = ref, orig_alt = alt, user_id = None)

    # add annotations -> this variant should have ALL annotations which can be possibly available
    annotation_type_ids = conn.get_recent_annotation_type_ids()
    #print(annotation_type_ids)

    annotations_with_values = []
    for annotation_type in annotation_values:
        annotations_with_values.extend(annotation_values[annotation_type].keys())
    assert len(set(annotation_type_ids.keys()) & set(annotations_with_values)) == len(annotation_type_ids.keys()), "The annotation type ids do not match the annotation type values. Please update static data or update test."
    
    for annotation_type in annotation_values:
        current_annotation_group = annotation_values[annotation_type]
        if annotation_type == "simple":
            for annotation_type_name in current_annotation_group:
                annotation_type_id = annotation_type_ids[annotation_type_name]
                annotation_value = current_annotation_group[annotation_type_name]
                conn.insert_variant_annotation(variant_id = variant_id, annotation_type_id = annotation_type_id, value = annotation_value)
            
        if annotation_type == "transcript":
            current_annotation_group = annotation_values[annotation_type]
            for annotation_type_name in current_annotation_group:
                annotation_type_id = annotation_type_ids[annotation_type_name]
                annotation_type_values = current_annotation_group[annotation_type_name]
                for annotation_type_value in annotation_type_values:
                    conn.insert_variant_transcript_annotation(variant_id = variant_id, transcript = annotation_type_value["transcript"], annotation_type_id = annotation_type_id, value = annotation_type_value["value"])

        if annotation_type == "ID":
            current_annotation_group = annotation_values[annotation_type]
            for annotation_type_name in current_annotation_group:
                anotation_type_id = annotation_type_ids[annotation_type_name]
                annotation_value = current_annotation_group[annotation_type_name]
                conn.insert_external_variant_id(variant_id = variant_id, external_id = annotation_value, annotation_type_id = anotation_type_id)


        if annotation_type == "other":
            for annotation_type_name in current_annotation_group:
                if annotation_type_name == "cancerhotspots":
                    annotation_type_id = annotation_type_ids[annotation_type_name]
                    cancerhotspots_annotations = current_annotation_group[annotation_type_name]
                    for cancerhotspots_annotation in cancerhotspots_annotations:
                        conn.insert_cancerhotspots_annotation(variant_id = variant_id, annotation_type_id = annotation_type_id, oncotree_symbol = cancerhotspots_annotation["oncotree_symbol"], cancertype = cancerhotspots_annotation["cancertype"], tissue = cancerhotspots_annotation["tissue"], occurances = cancerhotspots_annotation["occurances"])
                if annotation_type_name == "heredicare":
                    heredicare_annotations = current_annotation_group[annotation_type_name]
                    for heredicare_annotation in heredicare_annotations:
                        conn.insert_heredicare_annotation(variant_id = variant_id, vid = heredicare_annotation["vid"], n_fam = heredicare_annotation["n_fam"], n_pat = heredicare_annotation["n_pat"], consensus_class = heredicare_annotation["consensus_class"], classification_date = heredicare_annotation["classification_date"], comment = heredicare_annotation["comment"], lr_cooc = heredicare_annotation["lr_cooc"], lr_coseg = heredicare_annotation["lr_coseg"], lr_family = heredicare_annotation["lr_family"])

    return variant_id

def test_variant_details_annotations(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    default_annotation_values = get_default_annotation_values()

    # add some variants
    all_variant_ids = [
        add_variant_all_annotations(chrom = "chr2", pos = "214730440", ref = "G", alt = "A", conn = conn, annotation_values = default_annotation_values), # chr2-214730440-G-A BARD1
        conn.insert_variant(chr = "chr1", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T PALB2
    ]

    # insert genes
    conn.insert_gene(hgnc_id = "45908", symbol = "GENE1", name = "GENE1 desc", type = "protein-coding gene", omim_id = "398476", orphanet_id = "324985")
    conn.insert_gene(hgnc_id = "45909", symbol = "GENE2", name = "GENE2 desc", type = "protein-coding gene", omim_id = "", orphanet_id = "")

    # add some transcripts (for transcript annotations)    
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST11111111111", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = True, is_mane_plus_clinical = True, is_ensembl_canonical = True, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST22222222222", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = False, is_mane_plus_clinical = False, is_ensembl_canonical = True, transcript_refseq = None)


    # start test
    utils.login(page, user)
    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.display", variant_id = all_variant_ids[0], _external = True))
    
    # check simple annotations
    page.locator("#pop_score-tab").click()

    annotations_to_check = default_annotation_values["simple"]
    for annotation_type_title in annotations_to_check:
        #print(page.get_by_test_id("annotation-" + annotation_type_title).text_content())
        expect(page.get_by_test_id("annotation-" + annotation_type_title)).to_have_text(annotations_to_check[annotation_type_title])

    annotations_to_check = default_annotation_values["transcript"]
    for annotation_type_title in annotations_to_check:
        current_annotations = default_annotation_values["transcript"][annotation_type_title]
        if annotation_type_title == "revel":
            best_transcript = "ENST11111111111"
            bestannot = get_best_transcript_annotation(current_annotations, best_transcript)
            expect(page.get_by_test_id("annotation-" + annotation_type_title)).to_contain_text(bestannot["value"])
            expect(page.get_by_test_id("annotation-" + annotation_type_title)).to_contain_text(bestannot["transcript"])
            page.get_by_test_id("revel_details").click() # open popover
            expect(page.locator(".popover")).to_be_visible()
            page.get_by_test_id("revel_details").click() # close popover
        if annotation_type_title == "maxentscan" or annotation_type_title == "maxentscan_swa":
            best_transcript = "ENST11111111111"
            bestannot = get_best_transcript_annotation(current_annotations, best_transcript)
            expect(page.get_by_test_id("annotation-" + annotation_type_title)).to_contain_text(bestannot["transcript"])
            value_parts = bestannot["value"].split('|')
            for part in value_parts:
                expect(page.get_by_test_id("annotation-" + annotation_type_title)).to_contain_text(part)

    annotations_to_check = default_annotation_values["other"]["cancerhotspots"]
    for cancerhotspot_annotation in annotations_to_check:
        for cancerhotspot_value in cancerhotspot_annotation.values(): # iterate over single values and assert that each one of them has its own td container
            expect(page.locator("td").get_by_test_id("cancerhotspots").get_by_text(cancerhotspot_value)).to_be_visible()

    annotations_to_check = default_annotation_values["other"]["heredicare"]
    for heredicare_annotation in annotations_to_check: # THIS TEST DOES NOT WORK WHEN THERE ARE MULTIPLE HEREDICARE ANNOTATIONS!
        for annotation_type_title in ["n_fam", "n_pat", "lr_cooc", "lr_coseg", "lr_family"]:
            expect(page.get_by_test_id("annotation-" + annotation_type_title)).to_contain_text(heredicare_annotation[annotation_type_title])

    # check that all external links are working
    utils.check_all_links(page)


def get_best_transcript_annotation(annotations, transcript_oi):
    for annotation in annotations:
        if annotation["transcript"] == transcript_oi:
            return annotation
    return None

def get_max_transcript_annotation(annotations):
    result = None
    for annotation in annotations:
        if result is None or float(result["value"]) < float(annotation["value"]):
            result = annotation
    return result


def test_variant_details_consequences(page, conn):
    # seed database
    user = utils.get_user()
    user_id = conn.get_user_id(user["username"])

    # add some variants
    all_variant_ids = [
        conn.insert_variant(chr = "chr1", pos = "43045752", ref = "C", alt = "A", orig_chr = "chr17", orig_pos = "43045752", orig_ref = "C", orig_alt = "A", user_id = user_id),
        conn.insert_variant(chr = "chr16", pos = "23603525", ref = "C", alt = "T", orig_chr = "chr16", orig_pos = "23603525", orig_ref = "C", orig_alt = "T", user_id = user_id) # chr16-23603525-C-T PALB2
    ]

    # insert genes
    conn.insert_gene(hgnc_id = "45908", symbol = "GENE1", name = "GENE1 desc", type = "protein-coding gene", omim_id = "398476", orphanet_id = "324985")
    conn.insert_gene(hgnc_id = "45909", symbol = "GENE2", name = "GENE2 desc", type = "protein-coding gene", omim_id = "", orphanet_id = "")
    conn.insert_gene(hgnc_id = "45910", symbol = "GENE3", name = "GENE2 desc", type = "protein-coding gene", omim_id = "", orphanet_id = "")

    # add some transcripts (for transcript annotations)    
    conn.insert_transcript(symbol = None, hgnc_id = "45908", transcript_ensembl = "ENST11111111111", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = True, is_mane_plus_clinical = True, is_ensembl_canonical = True, transcript_refseq = None)
    conn.insert_transcript(symbol = None, hgnc_id = "45909", transcript_ensembl = "ENST22222222222", transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = False, is_mane_plus_clinical = False, is_ensembl_canonical = True, transcript_refseq = None)

    conn.insert_transcript(symbol = None, hgnc_id = "45910", transcript_ensembl = None, transcript_biotype = "protein coding", total_length = "1000", chrom = "chr1", start = "100000", end = "101000", orientation = "+", exons = [(100000, 100100, True), (100900, 101000, True)], is_gencode_basic = True, is_mane_select = True, is_mane_plus_clinical = True, is_ensembl_canonical = True, transcript_refseq = "NM_1111111")


    # add some consequences
    consequences = [
        # ensembl
        {"transcript_name": "ENST11111111111", "hgvs_c": "c.100C>A", "hgvs_p": "p.5G>T", "consequence": "missense variant1", "impact": "high", "exon_nr": "exon1", "intron_nr": "intron2", "hgnc_id": "", "symbol": "GENE1", "consequence_source": "ensembl"},
        {"transcript_name": "ENST22222222222", "hgvs_c": "c.101C>A", "hgvs_p": "p.6U>I", "consequence": "missense variant2", "impact": "moderate", "exon_nr": "exon3", "intron_nr": "intron4", "hgnc_id": "", "symbol": "GENE2", "consequence_source": "ensembl"},
        # refseq
        {"transcript_name": "NM_1111111", "hgvs_c": "c.103C>A", "hgvs_p": "p.7A>G", "consequence": "missense variant3", "impact": "low", "exon_nr": "exon5", "intron_nr": "intron6", "hgnc_id": "", "symbol": "GENE3", "consequence_source": "refseq"}
    ]
    for consequence in consequences:
        conn.insert_variant_consequence(variant_id = all_variant_ids[0], **consequence)

    # start test
    utils.login(page, user)
    utils.nav(page.goto, utils.GOOD_STATI, url_for("variant.display", variant_id = all_variant_ids[0], _external = True))
    
    # check simple annotations
    page.locator("#consequence-tab").click()
    utils.screenshot(page)

    for consequence in consequences:
        if consequence["consequence_source"] == "ensembl":
            page.locator("#consequence_ensembl_tab").click()
        elif consequence["consequence_source"] == "refseq":
            page.locator("#consequence_refseq_tab").click()
        check_visible_consequence(page, consequence)


def check_visible_consequence(page, consequence):
    for key_to_check in ["transcript_name", "hgvs_c", "hgvs_p", "consequence", "impact", "exon_nr", "intron_nr", "symbol"]:
        value_oi = consequence[key_to_check]
        if value_oi != "" and value_oi is not None:
            expect(page.locator("#variantConsequenceTable").locator("td").get_by_text(value_oi)).to_be_visible()