import argparse
from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import common.functions as functions
import sys

parser = argparse.ArgumentParser(description="This script takes a gnomad.vcf file and filters it such that only a few interesting fields in the INFO column are left")
parser.add_argument("-i", "--input",  default="", help="path to gnomad.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--header", action='store_true', help="boolean, specify if the vcf header should be contained in the output")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
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
    # write INFO columns for standard gnomAD scores
    print('##INFO=<ID=AN,Number=A,Type=Float,Description="Total number of alleles in samples">')
    print('##INFO=<ID=AF,Number=A,Type=Float,Description="Alternate allele frequency in samples">')
    print('##INFO=<ID=AC,Number=A,Type=Integer,Description="Alternate allele count for samples">')
    print('##INFO=<ID=hom,Number=A,Type=Integer,Description="Count of homozygous individuals in samples">')
    print('##INFO=<ID=hemi,Number=A,Type=Integer,Description="Count of hemizygous individuals in samples">')
    print('##INFO=<ID=het,Number=A,Type=Integer,Description="Count of heterozygous individuals in samples">')
    # write INFO columns for non cancer gnomAD scores
    print('##INFO=<ID=AN_NC,Number=A,Type=Float,Description="Total number of alleles in samples in non_cancer subset">')
    print('##INFO=<ID=AF_NC,Number=A,Type=Float,Description="Alternate allele frequency in samples in non_cancer subset">')
    print('##INFO=<ID=AC_NC,Number=A,Type=Integer,Description="Alternate allele count for samples in non_cancer subset">')
    print('##INFO=<ID=hom_NC,Number=A,Type=Integer,Description="Count of homozygous individuals in samples in non_cancer subset">')
    print('##INFO=<ID=hemi_NC,Number=A,Type=Integer,Description="Count of hemizygous individuals in samples in non_cancer subset">')
    print('##INFO=<ID=het_NC,Number=A,Type=Integer,Description="Count of heterozygous individuals in samples in non_cancer subset">')
    # write INFO columns for popmax
    print('##INFO=<ID=popmax,Number=A,Type=String,Description="Population with maximum AF">')
    print('##INFO=<ID=AC_popmax,Number=A,Type=Integer,Description="Allele count in the population with the maximum allele frequency">')
    print('##INFO=<ID=AN_popmax,Number=A,Type=Integer,Description="Total number of alleles in the population with the maximum allele frequency">')
    print('##INFO=<ID=AF_popmax,Number=A,Type=Float,Description="Maximum allele frequency across populations">')


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

        # total gnomAD
        an = ''
        ac = ''
        af = ''
        hom = ''
        ac_xy = ''
        hemi = ''
        het = ''

        # non cancer gnomAD
        an_nc = ''
        ac_nc = ''
        af_nc = ''
        hom_nc = ''
        ac_xy_nc = ''
        hemi_nc = ''
        het_nc = ''

        # popmax scores
        popmax = ''
        ac_popmax = ''
        an_popmax = ''
        af_popmax = ''

        for info in infos:
            if info.startswith('AF='):
                af = info[3:]
            elif info.startswith('nhomalt='):
                hom = info[8:]
            elif info.startswith('popmax='):
                popmax = info[7:]
            elif info.startswith('AC_popmax='):
                ac_popmax = info[10:]
            elif info.startswith('AN_popmax='):
                an_popmax = info[10:]
            elif info.startswith('AF_popmax='):
                af_popmax = info[10:]
            elif info.startswith('AC_XY=') and is_gonosome and is_nonpar:
                ac_xy = info[8:]
            elif info.startswith('AC='):
                ac = info[3:]
            elif info.startswith('AN='):
                an = info[3:]
            elif info.startswith('AN_non_cancer='):
                an_nc = info[14:]
            elif info.startswith('AF_non_cancer='):
                af_nc = info[14:]
            elif info.startswith('AC_non_cancer='):
                ac_nc = info[14:]
            elif info.startswith('nhomalt_non_cancer='):
                hom_nc = info[19:]
            elif info.startswith('AC_non_cancer_XY='):
                ac_xy_nc = info[17:]
    
        #calculate the number of heterozygotes
        if hom != '' and ac != '':
            het = str(int(ac) - (2*int(hom)))
        
        #calculate the number of hemizygotes
        if ac_xy != '' and chr_num == "X" and is_nonpar:
            hemi = ac_xy
        elif chr_num == "Y":
            hemi = ac # every variant on Y is hemizygous

        #calculate the number of heterozygotes for non cancer subset
        if hom_nc != '' and ac_nc != '':
            het_nc = str(int(ac_nc) - (2*int(hom_nc)))
        
        #calculate the number of hemizygotes for non cancer subset
        if ac_xy_nc != '' and chr_num == "X" and is_nonpar:
            hemi_nc = ac_xy_nc
        elif chr_num == "Y":
            hemi_nc = ac_nc # every variant on Y is hemizygous


        entries[0] = "chr" + chr_num

        info = ''
        # standard gnomAD scores
        info = functions.collect_info(info, "AN=", an)
        info = functions.collect_info(info, "AF=", af)
        info = functions.collect_info(info, "AC=", ac)
        info = functions.collect_info(info, "hom=", hom)
        info = functions.collect_info(info, "het=", het)
        info = functions.collect_info(info, "hemi=", hemi)
        # non cancer gnomAD scores
        info = functions.collect_info(info, "AN_NC=", an_nc)
        info = functions.collect_info(info, "AF_NC=", af_nc)
        info = functions.collect_info(info, "AC_NC=", ac_nc)
        info = functions.collect_info(info, "hom_NC=", hom_nc)
        info = functions.collect_info(info, "het_NC=", het_nc)
        info = functions.collect_info(info, "hemi_NC=", hemi_nc)
        # popmax
        info = functions.collect_info(info, "popmax=", popmax)
        info = functions.collect_info(info, "AC_popmax=", ac_popmax)
        info = functions.collect_info(info, "AN_popmax=", an_popmax)
        info = functions.collect_info(info, "AF_popmax=", af_popmax)

        if info == '':
            info = '.'

        print('\t'.join(entries[:7]) + '\t' + info)


# für #hemi: 
# check if variant is on the x-y-chromosome
# liegt ausserhalb von pseudoautosomalen regionen (nonpar flag in vcf)
# dann kann man den value aus AC_male nehmen

# für #het:
# AC - (2*nhomalt)