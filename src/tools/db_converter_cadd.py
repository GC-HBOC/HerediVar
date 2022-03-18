import argparse
from gc import collect
from ntpath import join
import sys
import datetime

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
print("##fileformat=VCFv4.2\n")
print("##fileDate=" + datetime.datetime.today().strftime('%Y-%m-%d') + "\n")
print("##reference=GRCh38\n")
print("##INFO=<ID=CADD,Number=1,Type=Float,Description=\"CADD scaled score (PHRED) score of this variant.\">\n")
print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")

for line in input_file:
    line = line.strip()
    if line.startswith('#') or (line == ''):
        continue

    line = line.split('\t')

    chr = "chr" + line[0].strip()
    pos = int(line[1])
    ref = line[2].strip()
    alt = line[3].strip()
    score = line[5].strip()

    print(chr + '\t' + str(pos) + '\t.\t' + ref + '\t' + alt + '\t.\t.\tCADD=' + score)
