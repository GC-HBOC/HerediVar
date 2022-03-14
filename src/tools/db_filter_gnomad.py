import argparse
from gc import collect
from ntpath import join
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
    if not line.startswith('##INFO') and not line.startswith('#CHROM') and include_header:
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

        is_gonosome = (entries[0] == "chrX") or (entries[0] == "chrY")
        is_nonpar = "nonpar" in entries[7]

        nhomalt = None
        ac = None

        af = ''
        hom = ''
        popmax = ''
        hemi = ''
        het = ''

        for info in infos:
            if info.startswith('AF='):
                af = "AF=" + info[3:]
            elif info.startswith('nhomalt='):
                nhomalt = int(info[8:])
                hom = "hom=" + info[8:]
            elif info.startswith('popmax='):
                popmax = "popmax=" + info[7:]
            elif info.startswith('AC_male=') and is_gonosome and is_nonpar:
                hemi = "hemi=" + info[8:]
            elif info.startswith('AC='):
                ac = int(info[3:])
                if entries[0] == "chrY": # gnomad does not record AC_male for chrY as AC_male=AC
                    hemi = "hemi=" + str(ac)
    
        #calculate the number of heterozygotes
        het = "het=" + str(ac - (2*nhomalt))

        print('\t'.join(entries[:6]) + '\t' + af + ';' + 'AC=' + str(ac) + ';' + hom + ';' + popmax + ';' + hemi + ';' + het)
    

    


# für #hemi: 
# check if variant is on the x-y-chromosome
# liegt ausserhalb von pseudoautosomalen regionen (nonpar flag in vcf)
# dann kann man den value aus AC_male nehmen

# für #het:
# AC - (2*nhomalt)