from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import argparse


parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--deadfile", action='store_true', help="boolean, if set assumes the data to be Pfam-A.dead otherwise assumes Pfam-A.seed or Pfam-A.full.")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r', encoding='utf-8', errors='ignore')
else:
    input_file = sys.stdin

deadfile = args.deadfile

if deadfile:
    second_col_start = "#=GF FW"
    print("#OLD_PFAM_ACC\tNEW_PFAM_ACC")
else:
    second_col_start = "#=GF DE"
    print("#PFAM_ACC\tdescription")


pfam_acc = ''
second_col = ''
for line in input_file:
    line = line.strip()
    if line == '//':
        print(pfam_acc + "\t" + second_col)
        pfam_acc = ''
        second_col = ''
        continue
    
    #if line.startswith('#=GF ID'):
    #    symbol = line[10:]
    if line.startswith('#=GF AC'):
        pfam_acc = line[10:]
    if line.startswith(second_col_start):
        second_col = line[10:]
        if second_col == '':
            second_col = "removed"