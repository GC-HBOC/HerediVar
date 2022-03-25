from urllib.request import urlopen
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import common.functions as functions

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input csv file will default to stdin")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
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
    "##INFO=<ID=num_eur,Number=1,Type=Integer,Description=\"Number of individuals with this variant in the european american cohort. (n=7325)\">",
    "##INFO=<ID=num_afr,Number=1,Type=Integer,Description=\"Number of individuals with this variant in the african american cohort. (n=2559)\">"]
functions.write_vcf_header(info_header)

for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue
    
    if line.startswith('\"Chrom\"'):
        header = line.split(',')
        header = [x.strip('\"') for x in header]
        chr_pos = header.index('Chrom')
        pos_pos = header.index('Position')
        ref_pos = header.index('Reference')
        alt_pos = header.index('Alternate')
        num_eur_pos = [i for i, s in enumerate(header) if 'European' in s][0]
        num_afr_pos = [i for i, s in enumerate(header) if 'African' in s][0]
    

    
    
    parts = line.split(',')
    parts = [x.strip('\"') for x in parts]

    chr_num = functions.validate_chr(parts[chr_pos])
    if not chr_num:
        continue
    
    info = ''
    info = functions.collect_info(info, "num_eur=", parts[num_eur_pos])
    info = functions.collect_info(info, "num_afr=", parts[num_afr_pos])

    #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
    vcf_line = ['chr' + chr_num, parts[pos_pos], '.', parts[ref_pos], parts[alt_pos], '.', '.', info]

    print('\t'.join(vcf_line))

