from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import re


parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--reference", help="The reference sequence. (eg.: NM_007294.3)")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r', encoding='utf-8', errors='ignore')
else:
    input_file = sys.stdin

reference_transcript = args.reference


print('#reference\thgvs_c\tclassification')


# this script tranforms:
# c.311_312delGCins9
# c.244_245insA -> c.244_245ins
# c.38_39delATinsGGG -> c.38_39delinsGGG



first_line = True
cdot  = ''
clsf = ''
for line in input_file:
    line = line.strip()
    if line.startswith('<tr class="data-rows">'):
        if not first_line:
            print(reference_transcript + '\t' + cdot + '\t' + clsf)
        cdot = ''
        clsf = ''
        first_line = False
    if line.startswith('<td class="cDot">'):
        cdot = re.search('cDot">(.*)[<]', line).group(1)
        #matches_deletion_insertions = re.search('(.*del).*(ins.*)', cdot)
        #if matches_deletion_insertions is not None: # check if it is an insertion deletion and remove bases between them
        #    cdot = matches_deletion_insertions.group(1) + matches_deletion_insertions.group(2)
        #else: 
        matches = re.search('dup|del', cdot)
        if matches is not None: # check if it is an insertion duplication or deletion and remove bases preceding these keywords
            cut_here = matches.end(0)
            cdot = cdot[:cut_here]
        # don't do anything if the hgvs is a snv
    if line.startswith('<td class="clsf">'):
        clsf = re.search('clsf">(.*)[<]', line).group(1)
        clsf = clsf[0]
print(reference_transcript + '\t' + cdot + '\t' + clsf)