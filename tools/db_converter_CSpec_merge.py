from urllib.request import urlopen
from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import argparse
import common.functions as functions
import re

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input csv file will default to stdin")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("-c", "--column", help="The INFO column to merge")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, "r")
else:
    input_file = sys.stdin

info_column_to_merge = args.column

variants = {}

for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        print(line)
        continue

    parts = line.split('\t')

    chrom = parts[0]
    pos = parts[1]
    ref = parts[3]
    alt = parts[4]
    info = parts[7]

    current_assay = None
    info_parts = info.split(';')
    for info_part in info_parts:
        if info_part.startswith(info_column_to_merge + "="):
            current_assay = info_part[len(info_column_to_merge) + 1:]
    variant_str = '-'.join([chrom, pos, ref, alt])
    if current_assay is not None:
        variants = functions.extend_dict(variants, variant_str, current_assay)



for variant in variants:
    variant_parts = variant.split('-')
    chrom = variant_parts[0]
    pos = variant_parts[1]
    ref = variant_parts[2]
    alt = variant_parts[3]

    info = info_column_to_merge + "=" + "&".join(variants[variant])

    #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
    vcf_line_parts = [chrom, pos, ".", ref, alt, ".", ".", info] 
    print("\t".join(vcf_line_parts))
