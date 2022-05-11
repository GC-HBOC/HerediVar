# this script collects information from curated & lifted variants from heredicare and annotates the original variants with these information
# if there were any errors it also reports those
# this script also searches for duplicates among the curated & lifted variants
# !!! this script assumes that the --tsv provided file has following header: #VID	GEN	REFSEQ	CHROM	GPOS	REFBAS	ALTBAS	CHGVS	CBIC	CGCHBOC


import argparse
from distutils.log import error
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions
import sys
import re

parser = argparse.ArgumentParser(description="this script converts a csv file of HerediCare Variants to a vcf file, column headers should be: VID;GEN;REFSEQ;CHROM;GPOS;REFBAS;ALTBAS;CHGVS;CBIC;CGCHBOC")
parser.add_argument("-t", "--tsv",  help="path to original heredicare tsv file")
parser.add_argument("--vcfworked",  help="path to vcf file containing the lifted and leftaligned variants")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("-s", "--sep", default="\t", help="separating character in the csv file, defaults to 'tabulator'")


parser.add_argument("-e", "--errorfile", default="notparsed.tsv", help="this file contains the lines of the input tsv which had too much missing information to even have a chance to convert them to vcf")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

sep = args.sep


# prepare a dictionary to match seqid -> variant in vcf style
vcf_worked_file = open(args.vcfworked, 'r')
lifted_variants = {}
for line in vcf_worked_file:
    if line.startswith('#') or line.strip() == '':
        continue

    parts = line.split('\t')
    
    chr_num = functions.validate_chr(parts[0].strip())
    if not chr_num:
        continue
    chr = 'chr' + chr_num


    pos = parts[1].strip()
    ref = parts[3].strip()
    alt = parts[4].strip()

    seqid = functions.find_between(parts[7], 'seqid=', '(;|$)')
    if seqid in lifted_variants:
        functions.eprint("WARNING seqid: " + seqid + " occurs multiple times")
        continue
    lifted_variants[seqid] = (chr, pos, ref, alt)
vcf_worked_file.close()


original_heredicare = open(args.tsv, 'r')
print('#VID	GEN	REFSEQ	CHROM	GPOS	REFBAS	ALTBAS	CHGVS	CBIC	CGCHBOC	CHROM_GRCH38	GPOS_GRCH38	REFBAS_GRCH38	ALTBAS_GRCH38	COMMENT')
for line in original_heredicare:
    line = line.strip('\n')
    if line.startswith('#') or line.strip() == '':
        continue
    
    parts = line.split(sep)

    seqid = parts[0].strip()

    lifted_variant = lifted_variants.get(seqid, None)

    comment = ''

    if lifted_variant is not None:
        lifted_variant_string = '\t'.join(lifted_variant)
        print('\t'.join([line, lifted_variant_string, comment]))
    else:
        variant_string = '\t' * 3 # variant was not mapped to hg 38 thus, enter empty fields
        print('\t'.join([line, variant_string, comment]))
    
