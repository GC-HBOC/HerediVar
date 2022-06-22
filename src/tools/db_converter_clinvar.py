from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import common.functions as functions
import pandas as pd
import datetime
import csv


parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--submissions", help="Path to submission_summary.txt downloaded from clinvar.")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

submission_summary_path = args.submissions
submission_summary = pd.read_csv(submission_summary_path, sep = "\t", compression="gzip", comment='#', quoting=csv.QUOTE_NONE)


def convert_row_to_string(variationid, row):
    last_evaluated = str(row['DateLastEvaluated'])
    if last_evaluated != '-' and last_evaluated != '':
        last_evaluated = datetime.datetime.strptime(last_evaluated, "%b %d, %Y").strftime("%Y-%m-%d")
    else:
        last_evaluated = ''
    
    description = str(row['Description']).strip('\"')
    explanation_of_interpretation = str(row['ExplanationOfInterpretation']).strip('\"')
    if description == '-':
        description = ''
    else:
        description = "description: " + description
    if explanation_of_interpretation == '-':
        explanation_of_interpretation = ''
    else:
        explanation_of_interpretation = "ExplanationOfInterpretation: " + explanation_of_interpretation

    result = str(variationid).replace('|', ' ') + '|' + str(row['ClinicalSignificance']).replace('|', ' ') + '|' \
     + last_evaluated + '|' + str(row['ReviewStatus']).replace('|', ' ') + '|' \
      + str(row['ReportedPhenotypeInfo']).replace('|', ' ') + '|' \
       + str(row['Submitter']).replace('|', ' ') + '|' + functions.collect_info(description, '', explanation_of_interpretation, sep = ' - ').replace('|', ' ')

    result.replace(' ', '_')
    result.replace('\\', '/')
    result.replace(';', '&')
    return result.replace(',', '\\')


# write vcf header
info_headers = ["##INFO=<ID=inpret,Number=.,Type=String,Description=\"Interpretation / clinical significance of the variant. Format: CLNSIG|CLNSIGCONF\">",
                "##INFO=<ID=revstat,Number=.,Type=String,Description=\"Review status of the variant\">",
                "##INFO=<ID=varid,Number=1,Type=String,Description=\"The ClinVar variation identifier\">",
                "##INFO=<ID=submissions,Number=.,Type=String,Description=\"All submissions listed in ClinVar delimited by ','. All ',' in the original sequence were replaced with '\\' and spaces were replaced by '_' Format: VariationID|ClinicalSignificance|LastEvaluated|ReviewStatus|SubmittedPhenotypeInfo|Submitter|ExplanationOfInterpretation\">"]
functions.write_vcf_header(info_headers)

for line in input_file:
    line = line.strip()
    if line.startswith('#'):
        continue
    
    parts = line.split('\t')
    chr_num = functions.validate_chr(parts[0])
    if not chr_num:
        continue
    
    variation_id = parts[2]

    infos = parts[7].split(';')
    interpretation = ''
    rev_stat = ''

    for info in infos:
        if info.startswith('CLNSIG='):
            if interpretation:
                interpretation = info[7:] + '|' + interpretation 
            else:
                interpretation = info[7:]
        if info.startswith('CLNSIGCONF='):
            if interpretation:
                interpretation = interpretation + '|' + info[11:]
            else:
                interpretation = info[11:]
        if info.startswith('CLNREVSTAT='):
            rev_stat = info[11:]
    
    # skip variants which lack an interpretation
    if interpretation == '' or rev_stat == '':
        continue

    parts[5] = '.'
    parts[6] = '.'
    parts[0] = 'chr' + chr_num
    info = ''
    info = functions.collect_info(info, 'inpret=', interpretation)
    info = functions.collect_info(info, 'revstat=', rev_stat)
    info = functions.collect_info(info, 'varid=', variation_id)
    
    current_submissions = submission_summary.loc[submission_summary['VariationID'] == int(variation_id)]
    current_submissions = current_submissions.reset_index()
    all_submissions = current_submissions.apply(lambda x: convert_row_to_string(variation_id, x), axis=1)
    all_submissions = ','.join(all_submissions)

    info = functions.collect_info(info, 'submissions=', all_submissions.replace(' ', '_'))
    parts[7] = info

    print('\t'.join(parts))


## clinvar_variant_annotation table
## - ID (column): variation ID
## - CLNSIG + CLNSIGCONF: interpretation
## - CLNREVSTAT: review status


## clinvar_interpretations table
## - interpretation: ClinicalSignificance column
## - last_evaluated: DateLastEvaluated column
## - review_status: ReviewStatus column
## (- assertion_criteria: CollectionMethod column)
## - condition: SubmittedPhenotypeInfo column
## (- inheritance: OriginCounts column)
## - submitter: Submitter column
## - supporting_information: ExplanationOfInterpretation / description