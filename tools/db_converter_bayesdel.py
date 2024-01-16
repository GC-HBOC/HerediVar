import sys
from os import path
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import argparse
from gc import collect
from ntpath import join
import common.functions as functions
from os import listdir
from os.path import isfile, join, abspath
import gzip

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input folder")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_path = args.input
else:
    input_path = sys.stdin


info_headers = ["##INFO=<ID=BayesDEL_noAF,Number=1,Type=Float,Description=\"Missense variant functional predictions by BayesDel tool (Feng 2017) used without allele frequency. Score bigger or equal to 0.16: damaging; Score smaller than 0.16: tolerated.\">",
                "##INFO=<ID=BayesDEL_addAF,Number=1,Type=Float,Description=\"Missense variant functional predictions by BayesDel tool (Feng 2017) used with allele frequency.\">"]
functions.write_vcf_header(info_headers)


bayesdel_files = [abspath(join(input_path, f)) for f in listdir(input_path) if isfile(join(input_path, f))]


for bayesdel_file in bayesdel_files:
    functions.eprint(bayesdel_file)
    file=gzip.open(bayesdel_file, 'rb')
    for line in file:
        line = line.decode('utf-8')
        line = line.strip()
        
        if line.startswith('#') or line == '':
            continue
        ##CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
        parts = line.split('\t')
        chrom = parts[0]
        pos = parts[1]
        ref = parts[2]
        alt = parts[3]
        info = ""
        bayesdel_noaf = parts[104]
        if bayesdel_noaf != '.':
            info = functions.collect_info(info, "BayesDEL_noAF=", parts[104])

        bayesdel_addaf = parts[101]
        if bayesdel_addaf != '.':
            info = functions.collect_info(info, "BayesDEL_addAF=", parts[101])

        if info != "": # keep only variants which have at least one annotation
            chrom = functions.validate_chr(chrom)
            if not chrom:
                continue
            chrom = 'chr' + chrom
            vcf_parts = [chrom, pos, '.', ref, alt, '.', '.', info]
            vcf_line = '\t'.join(vcf_parts)
            print(vcf_line)


    file.close()




