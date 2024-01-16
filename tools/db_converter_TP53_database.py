import argparse
from distutils.log import error
from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import common.functions as functions
import sys
import csv

parser = argparse.ArgumentParser(description="this script converts a csv file of HerediCare Variants to a vcf file, column headers should be: VID;GEN;REFSEQ;CHROM;GPOS;REFBAS;ALTBAS;CHGVS;CBIC;CGCHBOC")
parser.add_argument("-i", "--input",  default="", help="path to csv file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("-s", "--sep", default=",", help="separating character in the csv file, defaults to 'tabulator'")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

sep = args.sep

# see: https://tp53.isb-cgc.org/help for more information about the columns
info_headers = [
    "##INFO=<ID=class,Number=.,Type=String,Description=\"Family classification: LFS = strict clinical definition of Li-Fraumeni syndrome, LFL = Li-Fraumeni like for the extended clinical definition of Li-Fraumeni, FH: family history of cancer which does not fulfil LFS or any of the LFL definitions, No FH: no family history of cancer, FH= Family history of cancer (not fulfilling the definition of LFS/LFL),  No= no family history of cancer, ?= unknown\">",
    "##INFO=<ID=bayes_del,Number=1,Type=Float,Description=\"Missense variant functional predictions by BayesDel tool (Feng 2017) used without allele frequency. Score bigger or equal to 0.16: damaging; Score smaller than 0.16: tolerated\">",
    "##INFO=<ID=transactivation_class,Number=.,Type=String,Description=\"Functional classification based on the overall transcriptional activity\">",
    "##INFO=<ID=DNE_LOF_class,Number=.,Type=String,Description=\"Functional classification for loss of growth-suppression and dominant-negative activities based on Z-scores\">",
    "##INFO=<ID=DNE_class,Number=.,Type=String,Description=\"Dominant-negative effect on transactivation by wild-type p53. Yes: dominant-negative activity on WAF1 and RGC promoters, Moderate: dominant-negative activity on some but not all promoters, No: no dominant-negative activity on both WAF1 and RGC promoters, or none of the promoters in the large studies. \">",
    "##INFO=<ID=domain_function,Number=.,Type=String,Description=\"Function of the domain in which the mutated residue is located. \">",
    "##INFO=<ID=pubmed,Number=.,Type=String,Description=\"PubMed of the publications in which was reported the polymorphic status of the variant. \">",
    "##INFO=<ID=number_individuals,Number=1,Type=String,Description=\"The number of individuals with this variant. \">",
    "##INFO=<ID=cases,Number=.,Type=String,Description=\"A list of diseased individuals carrying the variant. Items are separated with an ampersand (&). Format: family_id|age|age_at_diagnosis|topology|morphology \">"
    #"##INFO=<ID=hotspot,Number=1,Type=String,Description=\"Yes: variant is located in a codon defined as a cancer hotspot\">"
]
functions.write_vcf_header(info_headers)

def decomment(csvfile):
    for row in csvfile:
        raw = row.split('#')[0].strip()
        if raw: yield raw

reader = csv.reader(decomment(input_file))

# collect variants in dictionary because the data is patient-centered and not variant-centered -> duplicated variants with different info columns
# we collect all of these info for one variant
# variant identifiers are: pos_ref_alt
# values are dictionaries themselves: keys: info columns from vcf spec (see above), values: list of information
variants = {}
missing_individual_id = 0

for parts in reader:
    # skip entries which are unknown if they actually have the variant
    germline_carrier = parts[51]
    if germline_carrier.lower() not in ['confirmed', 'obligatory']:
        continue

    chr = 'chr17' # there are only variants from TP53!
    pos = parts[12].strip()
    ref = parts[20].strip()
    alt = parts[21].strip()

    variant_id = pos + '_' + ref + '_' + alt

    if variant_id not in variants:
        variants[variant_id] = {'class': [], 'bayes_del': [], 'transactivation_class': [], 'DNE_LOF_class': [], 'DNE_class': [], 'domain_function': [], 'pubmed': [], 'age_at_diagnosis': [], 'individual_ids': [], 'cases': []}

    individual_id = parts[45].strip()
    new_info = {'class': parts[6].strip(),
                'bayes_del': parts[34].strip(), 
                'transactivation_class': parts[35].strip(), 
                'DNE_LOF_class': parts[36].strip(), 
                'DNE_class': parts[37].strip(), 
                'domain_function': parts[43].strip(), 
                'pubmed': parts[73].strip().replace('https://www.ncbi.nlm.nih.gov/pubmed/', ''),
                'cases': '|'.join([parts[0], parts[55], parts[60].strip(), parts[58], parts[59]]), # family_id|age|age_at_diagnosis|topology|morphology
                'individual_ids': str(missing_individual_id) + 'a' if individual_id == '' else individual_id
                }


    for key in new_info:
        if new_info[key].upper() != 'NA' and new_info[key] != '' and new_info[key] not in variants[variant_id][key]:
            variants[variant_id][key].append(new_info[key])

    missing_individual_id += 1

input_file.close()


for key in variants:
    parts = key.split('_')

    chr = 'chr17'
    pos = parts[0]
    ref = parts[1]
    alt = parts[2]

    if 'N' in ref and 'N' in alt:
        continue

    info_dict = variants[key]

    info = ''
    for info_key in info_dict:
        if info_key == 'individual_ids':
            new_info = len(info_dict[info_key])
            info_key = 'number_individuals'
        else:
            new_info = '&'.join(info_dict[info_key])
        info = functions.collect_info(info, info_key + '=', new_info)

    info = info.replace(' ', '_')

    ##CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
    vcf = (chr, pos, '.', functions.complement(ref), functions.complement(alt), '.', '.', info)

    print('\t'.join(vcf))


# hotspot hab ich mir gespart weil ja schon extra geparst
