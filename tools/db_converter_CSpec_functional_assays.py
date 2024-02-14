from urllib.request import urlopen
from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import argparse
import common.functions as functions
import re

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input csv file will default to stdin")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, "r")
else:
    input_file = sys.stdin


gene2transcript={"BRCA1": "NM_007294.3", "BRCA2": "NM_000059.3"}

header = '\t'.join(["#reference", "hgvs_c", "functional_assay"])
print(header)

header_found = False
num_head = -1
for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue

    # scan for header line
    if not header_found:
        if '||' not in line and '|\n' not in line and '\n|' not in line: # all fields are filled -> this must be the header line
            header_found = True
            num_head = len(line.split('|'))
        continue

    parts = line.split('|')
    #ID|Gene|Variant|Protein|SourceName|Mutalyzer Input|Chromosomal Location|Functional Category Assigned|IARC Classification|Excluded Intronic, Splice Predicted and Start Codon Variants (Y=excluded from calibration of functional assays of predicted missense changes)|Potential splice variant based on prior (http://priors.hci.utah.edu/PRIORS/)|Findlay_Function|Findlay_RNAscore|Findlay_RNAclass|Starita Depleted|Mesman_Complementation|Mesman_HDR|Mesman_Cisplatin|Mesman_Class|Bouwman_Selection|Bouwman_FxnClass|Fernandes2019_fClass|Fernandes2019_fCategory|Petitalot2019_ControlGroup|Petitalot2019_Class|Hart2018_Functional Class|Hart2018_HDR ratio
    if len(parts) != num_head:
        functions.eprint("Skipping line: Not the right number of columns: " + line)
        continue

    gene = parts[1]
    hgvs_c = parts[2]
    link = "https://cspec.genome.network/cspec/ui/svi/doc/GN092"
    functional_category = parts[7]


    transcript = gene2transcript[gene]

    if functional_category == "Functional impact - complete":
        functional_category = "pathogenic"
    elif functional_category == "No functional impact":
        functional_category = "benign"
    else:
        functional_category = "ambigous"

    functional_assay = [functions.encode_vcf(functional_category), functions.encode_vcf(link)]
    functional_assay = "|".join(functional_assay)

    csv_line_parts = [transcript, 
                      hgvs_c, 
                      functional_assay]
    print("\t".join(csv_line_parts))
