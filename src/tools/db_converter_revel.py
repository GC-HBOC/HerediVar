import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
from gc import collect
from ntpath import join
import common.functions as functions

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

# write vcf header
info_headers = ["##INFO=<ID=REVEL,Number=1,Type=Float,Description=\"REVEL pathogenicity score of this variant.\">"]
functions.write_vcf_header(info_headers)


for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue
    
    line = line.split('\t')

    chr = "chr" + line[0].strip()
    pos = int(line[2])
    ref = line[3].strip()
    alt = line[4].strip()
    score = line[7].strip()

    print(chr + '\t' + str(pos) + '\t.\t' + ref + '\t' + alt + '\t.\t.\tREVEL=' + score)