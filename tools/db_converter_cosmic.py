from urllib.request import urlopen
from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
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


previous_variant = {'chrom': "", 'pos': "", 'ref': "", 'alt': ""}
all_cmc = {}
all_cosv = []
first_iteration = True
prev_line = ""

for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue

    parts = line.split('\t')
    info_parts = parts[7].split('|')
    current_variant = {'chrom': parts[0], 'pos': parts[1], 'ref': parts[3], 'alt': parts[4]}
    all_cosv.append(info_parts[16])
    current_transcript = info_parts[1]
    current_cmc = info_parts[31]

    if first_iteration:
        previous_variant = current_variant
    elif current_variant['chrom'] != previous_variant['chrom'] or current_variant['pos'] != previous_variant['pos'] or current_variant['ref'] != previous_variant['ref'] or current_variant['alt'] != previous_variant['alt']:
        print_variant(previous_variant, all_cmc, all_cosv)

        # reset
        previous_variant = current_variant
        all_cmc = {}
        all_cosv = []

    if current_transcript not in all_cmc:
        all_cmc[current_transcript] = current_cmc
    else:
        functions.eprint("Transcript was found multiple times for one variant: " + current_transcript)
        functions.eprint(line)
        functions.eprint(prev_line)
        if current_cmc != all_cmc[current_transcript]:
            if cmc_class_2_num(current_cmc) > cmc_class_2_num(all_cmc[current_transcript]):
                functions.eprint("Switched from" + all_cmc[current_transcript] + ' to ' + current_cmc)
                all_cmc[current_transcript] = current_cmc
            functions.eprint("Transcript found multiple times for one variant and they have different cmc values " + "(" + current_cmc + "/" + all_cmc[current_transcript] + ") " + current_transcript + " variant position: " + str(current_variant['pos']))

    first_iteration = False
    prev_line = line

# SAVE THE LAST VARIANT!
print_variant(current_variant, all_cmc, all_cosv)

