from urllib.request import urlopen
from os import path
import sys
sys.path.append(path.join(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))), "src"))
import argparse
import common.functions as functions
import os

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input csv file will default to stdin")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, "r")
else:
    input_file = sys.stdin





info_header = [
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
    "##INFO=<ID=COSMIC_CMC,Number=1,Type=String,Description=\"The cosmic cmc class for all exons\">",
    "##INFO=<ID=COSMIC_COSV,Number=1,Type=String,Description=\"The COSV identifiers.\">"]
functions.write_vcf_header(info_header)


def print_variant(current_variant, all_cmc, all_cosv):
    info = ''
    cmc_string = ""
    for transcript in all_cmc:
        cmc_string = functions.collect_info(cmc_string, "", transcript + "&" + all_cmc[transcript], "|")
    info = functions.collect_info(info, "COSMIC_CMC=", cmc_string)
    info = functions.collect_info(info, "COSMIC_COSV=", '&'.join(list(set(all_cosv))))

    #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
    vcf_line = [current_variant["chrom"], current_variant['pos'], '.', current_variant['ref'], current_variant['alt'], '.', '.', info]

    print('\t'.join(vcf_line))


def cmc_class_2_num(cmc_class):
    cmc_class = cmc_class.lower()
    if cmc_class == 'synonymous':
        return 0
    if cmc_class == 'other':
        return -1
    if cmc_class == '3':
        return 1
    if cmc_class == '2':
        return 2
    if cmc_class == '1':
        return 3
    functions.eprint(cmc_class)


all_variants = {}

for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue

    parts = line.split('\t')
    variant_barcode = '-'.join([parts[0], parts[1], parts[3], parts[4]])

    info_parts = parts[7].split('|')
    cosv = info_parts[16]
    transcript_name = info_parts[1]
    cmc = info_parts[31]

    if variant_barcode not in all_variants:
        all_variants[variant_barcode] = {'cosv': [cosv], 'cmc': {transcript_name: cmc}}
    else:
        all_variants[variant_barcode]['cosv'].append(cosv)
        if transcript_name not in all_variants[variant_barcode]['cmc']:
            all_variants[variant_barcode]['cmc'][transcript_name] = cmc
        else:
            functions.eprint("Transcript was found multiple times for one variant: " + transcript_name)
            functions.eprint(line)
            previous_cmc = all_variants[variant_barcode]['cmc'][transcript_name]
            if cmc != previous_cmc:
                if cmc_class_2_num(cmc) > cmc_class_2_num(previous_cmc):
                    functions.eprint("Switched from" + previous_cmc + ' to ' + cmc)
                    all_variants[variant_barcode]['cmc'][transcript_name] = cmc
                functions.eprint("Transcript found multiple times for one variant and they have different cmc values " + "(" + cmc + "/" + previous_cmc + ") " + transcript_name + " variant position: " + parts[1])

for barcode in all_variants:
    variant_parts = barcode.split('-')
    variant = {'chrom': variant_parts[0], 'pos': variant_parts[1], 'ref': variant_parts[2], 'alt': variant_parts[3]}
    print_variant(variant, all_variants[barcode]['cmc'], all_variants[barcode]['cosv'])
    
    