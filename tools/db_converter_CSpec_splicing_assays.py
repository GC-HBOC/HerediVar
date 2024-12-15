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

header = '\t'.join(["#reference", "hgvs_c", "splicing_assay"])
print(header)

header_found = False
num_head = -1
for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        continue

    # scan for header line
    if not header_found:
        if '||' not in line: # all fields are filled -> this must be the header line
            header_found = True
            num_head = len(line.split('|'))
        continue

    parts = line.split('|')
    #Gene|HGVS c. nomenclature|HGVS p. nomenclature|Final Class|Author|Year|PMID|Patient RNA|Minigene|Result|Type of Aberration|RNA change|WT transcript produced|Percent Aberrant Transcript Reported|Allele-Specific|Comment
    if len(parts) != num_head:
        functions.eprint("Skipping line: Not the right number of columns: " + line)
        continue

    gene = parts[0]
    hgvs_c = parts[1]
    pmid = parts[6]
    patient_rna = parts[7]
    minigene = parts[8]
    percent_aberrant_transcript = parts[13]
    allele_specific = parts[14]
    comment = parts[15]
    result = parts[9]


    transcript = gene2transcript[gene]

    if patient_rna == "NA":
        patient_rna = ""
    if minigene == "NA":
        minigene = ""
    if allele_specific == "NA":
        allele_specific = ""
    
    # extract the minimal percent aberrant transcript recorded
    all_percentages = re.findall(r"\(.*?\)", percent_aberrant_transcript)
    all_percentages_curated = []
    for percentage in all_percentages:
        if not "%" in percentage:
            continue
        for percentage in re.findall(r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+', percentage):
            percentage = float(percentage)
            all_percentages_curated.append(percentage)
    quantification = ""
    if len(all_percentages_curated) > 0:
        quantification = str(sum(all_percentages_curated))
    else: # add quantification 0% if not stated
        if minigene == "Y" or patient_rna == "Y":
            if result == "no aberration" and comment != "Result ignored (design limitations to detect aberration)":
                quantification = "0"


    splicing_assay = [functions.encode_vcf(patient_rna),
                      functions.encode_vcf(minigene), 
                      functions.encode_vcf(quantification),
                      functions.encode_vcf(allele_specific), 
                      functions.encode_vcf(comment),
                      functions.encode_vcf("https://pubmed.ncbi.nlm.nih.gov/" + pmid),
                      functions.encode_vcf(result)]
    splicing_assay = "|".join(splicing_assay)

    csv_line_parts = [transcript, 
                      hgvs_c, 
                      splicing_assay]
    
    print("\t".join(csv_line_parts))
