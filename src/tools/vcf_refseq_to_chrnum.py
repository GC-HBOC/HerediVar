import argparse
from gc import collect
from ntpath import join
import sys


parser = argparse.ArgumentParser(description="This script takes a gnomad.vcf file and filters it such that only a few interesting fields in the INFO column are left")
parser.add_argument("-i", "--input",  default="", help="path to gnomad.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

# taken from: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_assembly_report.txt
refseq_dict = {"NC_000001.11": "chr1", "NC_000002.12": "chr2", "NC_000003.12": "chr3", "NC_000004.12": "chr4", "NC_000005.10": "chr5",
               "NC_000006.12": "chr6", "NC_000007.14": "chr7", "NC_000008.11": "chr8", "NC_000009.12": "chr9", "NC_000010.11": "chr10",
               "NC_000011.10": "chr11", "NC_000012.12": "chr12", "NC_000013.11": "chr13", "NC_000014.9": "chr14", "NC_000015.10": "chr15",
               "NC_000016.10": "chr16", "NC_000017.11": "chr17", "NC_000018.10": "chr18", "NC_000019.10": "chr19", "NC_000020.11": "chr20",
               "NC_000021.9": "chr21", "NC_000022.11": "chr22", "NC_000023.11": "chrX", "NC_000024.10": "chrY", "NC_012920.1": "chrMT"}

for line in input_file:
    if line.startswith('#'):
        print(line)
    else:
        line = line.split('\t')
        current_refseq_id = line[0]
        if current_refseq_id in refseq_dict:
            line[0] = refseq_dict[current_refseq_id]
            print('\t'.join(line))