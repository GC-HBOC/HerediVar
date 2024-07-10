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


if include_header:
    info_headers = [
        # write INFO columns for standard gnomAD scores
        '##INFO=<ID=AN,Number=A,Type=Float,Description="Total number of alleles in samples">',
        '##INFO=<ID=AF,Number=A,Type=Float,Description="Alternate allele frequency in samples">',
        '##INFO=<ID=AC,Number=A,Type=Integer,Description="Alternate allele count for samples">',
        '##INFO=<ID=hom,Number=A,Type=Integer,Description="Count of homozygous individuals in samples">',
        '##INFO=<ID=hemi,Number=A,Type=Integer,Description="Count of hemizygous individuals in samples">',
        '##INFO=<ID=het,Number=A,Type=Integer,Description="Count of heterozygous individuals in samples">',
        '##INFO=<ID=faf95,Number=A,Type=Float,Description="Filtering allele frequency (using Poisson 95% CI)">',
        '##INFO=<ID=faf99,Number=A,Type=Float,Description="Filtering allele frequency (using Poisson 99% CI)">',
        # write INFO columns for non cancer gnomAD scores
        '##INFO=<ID=AN_NC,Number=A,Type=Float,Description="Total number of alleles in samples in non_cancer subset">',
        '##INFO=<ID=AF_NC,Number=A,Type=Float,Description="Alternate allele frequency in samples in non_cancer subset">',
        '##INFO=<ID=AC_NC,Number=A,Type=Integer,Description="Alternate allele count for samples in non_cancer subset">',
        '##INFO=<ID=hom_NC,Number=A,Type=Integer,Description="Count of homozygous individuals in samples in non_cancer subset">',
        '##INFO=<ID=hemi_NC,Number=A,Type=Integer,Description="Count of hemizygous individuals in samples in non_cancer subset">',
        '##INFO=<ID=het_NC,Number=A,Type=Integer,Description="Count of heterozygous individuals in samples in non_cancer subset">',
        # write INFO columns for popmax
        '##INFO=<ID=popmax,Number=A,Type=String,Description="Population with maximum AF">',
        '##INFO=<ID=AC_popmax,Number=A,Type=Integer,Description="Allele count in the population with the maximum allele frequency">',
        '##INFO=<ID=AN_popmax,Number=A,Type=Integer,Description="Total number of alleles in the population with the maximum allele frequency">',
        '##INFO=<ID=AF_popmax,Number=A,Type=Float,Description="Maximum allele frequency across populations">',
        '##INFO=<ID=faf95_popmax,Number=A,Type=Float,Description="Filtering allele frequency (using Poisson 95% CI) for the population with the maximum allele frequency">',
        # population specific scores - not downloaded yet
        '##INFO=<ID=AF_afr,Number=A,Type=Float,Description="Alternate allele frequency in samples of African/African-American ancestry">',
        '##INFO=<ID=AF_eas,Number=A,Type=Float,Description="Alternate allele frequency in samples of East Asian ancestry">',
        '##INFO=<ID=AF_nfe,Number=A,Type=Float,Description="Alternate allele frequency in samples of Non-Finnish European ancestry">',
        '##INFO=<ID=AF_amr,Number=A,Type=Float,Description="Alternate allele frequency in samples of Latino ancestry">',
        '##INFO=<ID=AF_sas,Number=A,Type=Float,Description="Alternate allele frequency in samples of South Asian ancestry">'
    ]
    functions.write_vcf_header(info_headers)


def get_annotation(info: str, annot_id: str) -> str:
    an = ""
    if annot_id in info:
        an = info[info.find(annot_id)+len(annot_id):]
        an = an[:an.find(';')]
    return an


for line in input_file:
    line = line.strip()

    if line.startswith('#') or line == '':
        continue

    parts = line.split('\t')
    info = parts[7]

    chr_num = functions.validate_chr(parts[0])
    if not chr_num:
        continue
    parts[0] = "chr" + chr_num
    parts[6] = "."

    is_gonosome = (chr_num == "X") or (chr_num == "Y")
    is_nonpar = "nonpar" in parts[7]

    # total gnomAD
    an = get_annotation(info, "AN=")
    af = get_annotation(info, "AF=")
    ac = get_annotation(info, "AC=")
    hom = get_annotation(info, "nhomalt=")
    ac_xy = get_annotation(info, "AC_XY=")
    faf95 = get_annotation(info, "faf95=")
    faf99 = get_annotation(info, "faf99=")

    # non cancer gnomAD
    popmax = get_annotation(info, "popmax=")
    ac_popmax = get_annotation(info, "AC_popmax=")
    an_popmax = get_annotation(info, "AN_popmax=")
    af_popmax = get_annotation(info, "AF_popmax=")
    faf95_popmax = get_annotation(info, "faf95_popmax=")
    
    # popmax scores
    an_nc = get_annotation(info, "AN_non_cancer=")
    af_nc = get_annotation(info, "AF_non_cancer=")
    ac_nc = get_annotation(info, "AC_non_cancer=")
    hom_nc = get_annotation(info, "nhomalt_non_cancer=")
    ac_xy_nc = get_annotation(info, "AC_non_cancer_XY=")

    # population specific scores
    af_afr = get_annotation(info, "AF_afr=") # african
    af_eas = get_annotation(info, "AF_eas=") # east asian
    af_nfe = get_annotation(info, "AF_nfe=") # non finnish european
    af_amr = get_annotation(info, "AF_amr=") # latino
    af_sas = get_annotation(info, "AF_sas=") # south asian
    
    #calculate the number of heterozygotes
    het = ""
    if hom != '' and ac != '':
        het = str(int(ac) - (2*int(hom)))
    #calculate the number of hemizygotes
    hemi = ""
    if ac_xy != '' and chr_num == "X" and is_nonpar:
        hemi = ac_xy
    elif chr_num == "Y":
        hemi = ac # every variant on Y is hemizygous

    #calculate the number of heterozygotes for non cancer subset
    het_nc = ""
    if hom_nc != '' and ac_nc != '':
        het_nc = str(int(ac_nc) - (2*int(hom_nc)))
    #calculate the number of hemizygotes for non cancer subset
    hemi_nc = ""
    if ac_xy_nc != '' and chr_num == "X" and is_nonpar:
        hemi_nc = ac_xy_nc
    elif chr_num == "Y":
        hemi_nc = ac_nc # every variant on Y is hemizygous


    info = ''
    # standard gnomAD scores
    info = functions.collect_info(info, "AN=", an)
    info = functions.collect_info(info, "AF=", af)
    info = functions.collect_info(info, "AC=", ac)
    info = functions.collect_info(info, "hom=", hom)
    info = functions.collect_info(info, "het=", het)
    info = functions.collect_info(info, "hemi=", hemi)
    info = functions.collect_info(info, "faf95=", faf95)
    info = functions.collect_info(info, "faf99=", faf99)
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
    info = functions.collect_info(info, "faf95_popmax=", faf95_popmax)
    # population specific scores
    info = functions.collect_info(info, "AF_afr=", af_afr)
    info = functions.collect_info(info, "AF_eas=", af_eas)
    info = functions.collect_info(info, "AF_nfe=", af_nfe)
    info = functions.collect_info(info, "AF_amr=", af_amr)
    info = functions.collect_info(info, "AF_sas=", af_sas)


    if info == '':
        info = '.'

    print('\t'.join(parts[:7]) + '\t' + info)


# für #hemi: 
# check if variant is on the x-y-chromosome
# liegt ausserhalb von pseudoautosomalen regionen (nonpar flag in vcf)
# dann kann man den value aus AC_male nehmen

# für #het:
# AC - (2*nhomalt)