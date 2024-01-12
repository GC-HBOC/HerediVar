from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import src.common.functions as functions
import pandas as pd
import datetime
import csv

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input.tsv file. If not given will default to stdin")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

has_head = True

# Use these fields:
# Chr	Pos	Ref	Alt -> VCF
# Pathogenicity_all	Clinical Significance	Variant pathogenicity as displayed in the Detail view Example value: Benign(ENIGMA); Benign,Uncertain_significance,Likely_benign (ClinVar); Pending (BIC)
# Pathogenicity_expert	Clinical Significance	Variant pathogenicity as displayed in the Summary view Example value: Benign / Little Clinical Significance

info_header = ["##INFO=<ID=clin_sig_detail,Number=.,Type=String,Description=\"Clinical Significance	Variant pathogenicity as displayed in the Detail view\">",
               "##INFO=<ID=clin_sig_short,Number=.,Type=String,Description=\"Variant pathogenicity as displayed in the Summary view\">"]
functions.write_vcf_header(info_header)

for line in input_file:
    if has_head:
        header = line.split('\t')
        chr_pos = header.index('Chr')
        pos_pos = header.index('Pos')
        ref_pos = header.index('Ref')
        alt_pos = header.index('Alt')
        clin_sig_detail_pos = header.index('Pathogenicity_all')
        clin_sig_short_pos = header.index('Pathogenicity_expert')
        has_head = False
        continue
    
    parts = line.split('\t')
    chr_num = functions.validate_chr(parts[chr_pos])
    if not chr_num:
        continue
    chr = 'chr' + chr_num

    info = ''
    info = functions.collect_info(info, 'clin_sig_detail=', parts[clin_sig_detail_pos].replace(';', ',').replace(' ', '_'))
    info = functions.collect_info(info, 'clin_sig_short=', parts[clin_sig_short_pos].replace(';', ',').replace(' ', '_'))

    vcf_line = [chr, parts[pos_pos], '.', parts[ref_pos], parts[alt_pos], '.', '.', info]
    print('\t'.join(vcf_line))
