import sys
from os import path
import argparse
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

# write vcf header
info_headers = ["##INFO=<ID=REVEL,Number=1,Type=String,Description=\"REVEL pathogenicity score of this variant for all transcripts. FORMAT: value&transcript separated by |.\">"]
functions.write_vcf_header(info_headers)

variants = {}

for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue
    
    line = line.split('\t')

    chrom = "chr" + line[0].strip()
    pos = line[2].strip()
    ref = line[3].strip()
    alt = line[4].strip()
    score = line[7].strip()
    transcript = line[8].strip()

    chrom_num = functions.validate_chr(chrom)
    if not chrom_num:
        functions.eprint("Found unknown chromosome: " + str(chrom) + "near line " + line)
        continue
    chrom = 'chr' + chrom_num

    variant_str = '-'.join([chrom, pos, ref, alt])
    new_score = (score, transcript)

    if variant_str not in variants:
        variants[variant_str] = [new_score]
    else:
        variants[variant_str].append(new_score)

    

for variant in variants:
    parts = variant.split('-')
    chrom = parts[0]
    pos = parts[1]
    ref = parts[2]
    alt = parts[3]

    scores = variants[variant]
    info = "REVEL=" + '|'.join(['&'.join(score).replace(';', '+') for score in scores])

    #"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
    vcf_line = '\t'.join([chrom, pos, ".", ref, alt, ".", ".", info])

    print(vcf_line)