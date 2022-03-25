import argparse
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions
import sys

parser = argparse.ArgumentParser(description="This script takes a gnomad.vcf file and filters it such that only a few interesting fields in the INFO column are left")
parser.add_argument("-i", "--input",  default="", help="path to gnomad.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--header", action='store_true', help="boolean, specify if the vcf header should be contained in the output")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

include_header = args.header

line = None

while(line is None or line.startswith('##')):
    line = input_file.readline()
    if not line.startswith('##INFO') and not line.startswith('#CHROM') and not line.startswith('#FILTER') and include_header:
        print(line.strip())

    
if include_header:
    # write INFO
    print('##INFO=<ID=AF,Number=A,Type=Float,Description="Alternate allele frequency in samples">')
    print('##INFO=<ID=AC,Number=A,Type=Integer,Description="Alternate allele count for samples">')
    print('##INFO=<ID=hom,Number=A,Type=Integer,Description="Count of homozygous individuals in samples">')
    print('##INFO=<ID=popmax,Number=A,Type=String,Description="Population with maximum AF">')
    print('##INFO=<ID=hemi,Number=A,Type=Integer,Description="Count of hemizygous individuals in samples">')
    print('##INFO=<ID=het,Number=A,Type=Integer,Description="Count of heterozygous individuals in samples">')

    print(line.strip()) # prints the column spec


while line != "":
    line = input_file.readline().strip()
    if len(line) > 0:
        entries = line.split('\t')
        infos = entries[7].split(';')

        chr_num = functions.validate_chr(entries[0])
        if not chr_num:
            continue

        is_gonosome = (chr_num == "X") or (chr_num == "Y")
        is_nonpar = "nonpar" in entries[7]

        nhomalt = ''
        ac = ''
        af = ''
        hom = ''
        popmax = ''
        hemi = ''
        het = ''

        for info in infos:
            if info.startswith('AF='):
                af = info[3:]
            elif info.startswith('nhomalt='):
                nhomalt = int(info[8:])
                hom = info[8:]
            elif info.startswith('popmax='):
                popmax = info[7:]
            elif info.startswith('AC_male=') and is_gonosome and is_nonpar:
                hemi = info[8:]
            elif info.startswith('AC='):
                ac = int(info[3:])
                if chr_num == "Y": # gnomad does not record AC_male for chrY as AC_male=AC
                    hemi = str(ac)
    
        #calculate the number of heterozygotes
        if nhomalt != '' and ac != '':
            het = str(ac - (2*nhomalt))

        entries[0] = "chr" + chr_num

        info = ''
        info = functions.collect_info(info, "AF=", af)
        info = functions.collect_info(info, "AC=", ac)
        info = functions.collect_info(info, "hom=", hom)
        info = functions.collect_info(info, "popmax=", popmax)
        info = functions.collect_info(info, "hemi=", hemi)
        info = functions.collect_info(info, "het=", het)

        print('\t'.join(entries[:7]) + '\t' + info)
    

    


# für #hemi: 
# check if variant is on the x-y-chromosome
# liegt ausserhalb von pseudoautosomalen regionen (nonpar flag in vcf)
# dann kann man den value aus AC_male nehmen

# für #het:
# AC - (2*nhomalt)