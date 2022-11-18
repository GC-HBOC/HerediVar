import argparse
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions
import sys
from urllib.parse import urljoin
import requests
import lxml.html
import urllib.request
from urllib.error import HTTPError
from http.client import RemoteDisconnected
import time

parser = argparse.ArgumentParser(description="This script crawls the HCI priors website and writes the prior probability of pathogenicity for each variant to a vcf file.")
parser.add_argument("-g", "--gene",  default="", help="One of the available genes: BRCA1, BRCA2, MLH1, MSH2 or MSH6")
parser.add_argument("-e", "--exon", default="", help="The first exon of the gene. Example for BRCA1: exon2")
parser.add_argument("-c", "--chromosome", default="", help="The chromosome which contains the specified gene. Example for BRCA1: chr17. If left unset it will try to receive the chromosome from an internal dictionary.")
parser.add_argument("-o", "--outfile", default="", help="The output .vcf filepath. If not specified will write to stdout")
parser.add_argument("-s", "--strand", default="", help="The strand on which the gene is defined. Will be inferred automatically if unset for some genes. Use either + (forward strand) or - (reverse strand.)")
parser.add_argument("-r", "--refgenome", default="", help="The reference genome. Either hg19 or hg38. Will be inferred automatically if unset for some genes.")
parser.add_argument("--header", action='store_true', help="boolean, specify if the vcf header should be contained in the output")


args = parser.parse_args()

if args.outfile is not "":
    sys.stdout = open(args.outfile, 'w')

gene = args.gene
first_exon = args.exon
chrom = args.chromosome
include_header = args.header
strand = args.strand
ref_genome = args.refgenome

if chrom == "":
    gene2chom = {"BRCA1": "chr17", "BRCA2": "chr13", "MLH1": "chr3", "MSH2": "chr2", "MSH6": "chr2"}
    if gene not in gene2chom:
        functions.eprint("ERROR: no chromosome could be inferred for your specified gene. Either provide a chromosome using the -c flag or specify another gene.")
    chrom = gene2chom[gene]

if strand == "":
    strand = "+"
    if gene in ["BRCA1", "MLH1"]:
        strand = "-"


if ref_genome == "":
    ref_genome = "hg38"
    if gene in ["BRCA1", "BRCA2"]:
        ref_genome = "hg19"


def extract_prior_probability(variant_container):
    all_strongs = variant_container.xpath("strong")
    return str(all_strongs[-1].text_content())


def extract_ref_alt(variant_container_text):
    asplit = variant_container_text.split('>')
    ref = str(asplit[0][-1]).upper()
    alt = str(asplit[1][0]).upper()
    if strand == "-":
        ref = functions.complement(ref, missing_data="")
        alt = functions.complement(alt, missing_data="")
    return ref, alt


def parse_html(url):
    try:
        resp = requests.get(url)
        html_text = resp.text
        return lxml.html.fromstring(html_text)
    except: #(HTTPError, RemoteDisconnected) as e
        functions.eprint("Got an error for url: " + url + "... retrying")
        return None


def retry_parse_html(url):
    doc = None
    wait_time = 5
    while doc is None:
        time.sleep(wait_time)
        doc = parse_html(url)
        wait_time = (wait_time + 1) * 2
    return doc



base_url = "http://priors.hci.utah.edu/PRIORS/BRCA/"
exon_url = urljoin(base_url, ("viewer.php?gene=%s&exon=%s" % (gene, first_exon)))


if include_header:
    info_headers = [
        "##contig=<ID=chr1>",
        "##contig=<ID=chr2>",
        "##contig=<ID=chr3>",
        "##contig=<ID=chr4>",
        "##contig=<ID=chr5>",
        "##contig=<ID=chr6>",
        "##contig=<ID=chr7>",
        "##contig=<ID=chr8>",
        "##contig=<ID=chr9>",
        "##contig=<ID=chr10>",
        "##contig=<ID=chr11>",
        "##contig=<ID=chr12>",
        "##contig=<ID=chr13>",
        "##contig=<ID=chr14>",
        "##contig=<ID=chr15>",
        "##contig=<ID=chr16>",
        "##contig=<ID=chr17>",
        "##contig=<ID=chr18>",
        "##contig=<ID=chr19>",
        "##contig=<ID=chr20>",
        "##contig=<ID=chr21>",
        "##contig=<ID=chr22>",
        "##contig=<ID=chrX>",
        "##contig=<ID=chrY>",
        "##contig=<ID=chrMT>",
        "##INFO=<ID=HCI_prior,Number=1,Type=Float,Description=\"The HCI prior probability of pathogenicity. This value ranges from 0.02 for exonic variants that do not impact a spice site and 0.97 for variants with high probability to damage a donor or acceptor splice junction. \">"
    ]
    functions.write_vcf_header(info_headers, reference_genome="hg19")


all_exon_urls = []

doc = retry_parse_html(exon_url)
for tr in doc.iter('tr'):
    text_content=tr.text_content()
    if text_content.startswith('EXON'):
        for link_elem in tr.iter('a'):
            new_exon_url = urljoin(base_url, link_elem.attrib['href'] )
            all_exon_urls.append(new_exon_url)



for exon_url in all_exon_urls:
    functions.eprint(exon_url)
    doc = retry_parse_html(exon_url)
    #seq_container = doc.xpath("//td[@class='seqarea']")[0]
    for variant_url_container in doc.xpath("//a[@class='seq']"):
        variant_url = urljoin(base_url, variant_url_container.attrib['href'])
        vdoc = retry_parse_html(variant_url)

        for variant_container in vdoc.iter('td'): # one variant
            variant_container_text = variant_container.text_content()
            if "Applicable Prior" in variant_container_text:
                prior = extract_prior_probability(variant_container)
                pos = functions.find_between(variant_container_text, ref_genome + " Position : ", "(⋅| |$)").replace(',', '')
                ref, alt = extract_ref_alt(variant_container_text)

                #CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
                vcf_line = '\t'.join([chrom, pos, '.', ref, alt, '.', '.', "HCI_prior=" + prior])
                print(vcf_line)
                






