from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import src.common.functions as functions
import pandas as pd
import datetime
import csv
import gzip



parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input.vcf file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--submissions", help="Path to submission_summary.txt downloaded from clinvar.")
parser.add_argument("--submissions_header", default=15, help="The row index of the header row. Will default to 15 (zero-based) if not given. Program will raise error if the index is wrong.")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin


submissions_summary_header_row = int(args.submissions_header)


submission_summary_path = args.submissions
#submission_summary = pd.read_csv(submission_summary_path, sep = "\t", compression="gzip", quoting=csv.QUOTE_NONE, skiprows=submissions_summary_header_row)

def read_submission_summary(path):
    file=gzip.open(path, 'rb')

    result = {}

    for line in file:
        line = line.decode('utf-8')
        if line.startswith('#') or line.strip() == '':
            continue
        
        parts = line.split('\t')
        if len(parts) != 13:
            raise IOError("Line does not have the correct number of columns (13): " + line)
        
        variation_id = parts[0]
        new_submission = [parts[0], parts[1], parts[2], parts[6], parts[5], parts[9], parts[3], parts[12]] # variation_id, clinicalsignificance, lastevaluated, review status, reportedphenotypeinfo, submitter, description, expalanationofinterpretation
        new_submission = [x.strip() for x in new_submission]

        if variation_id not in result:
            result[variation_id] = [new_submission]
        else:
            result[variation_id].append(new_submission)

    file.close()

    return result


def submission2str(info):
    #variation_id, clinicalsignificance, lastevaluated, reviewstatus, reportedphenotypeinfo, submitter, description, expalanationofinterpretation
    last_evaluated = info[2]
    if last_evaluated != '-' and last_evaluated != '':
        last_evaluated = datetime.datetime.strptime(last_evaluated, "%b %d, %Y").strftime("%Y-%m-%d")
    else:
        last_evaluated = ''
    
    description = info[6].strip('\"')
    explanation_of_interpretation = info[7].strip('\"')
    if description == '-' or description.strip() == '':
        description = ''
    else:
        description = "description: " + description
    if explanation_of_interpretation == '-' or explanation_of_interpretation.strip() == '':
        explanation_of_interpretation = ''
    else:
        explanation_of_interpretation = "ExplanationOfInterpretation: " + explanation_of_interpretation

    data = [
        info[0], # variation_id
        info[1], # clinical_significance
        last_evaluated,
        info[3], # review_status
        info[4], # reportedphenotypeinfo
        info[5], # submitter
        functions.collect_info(description, '', explanation_of_interpretation, sep = ' - ')
    ]
    data = [functions.encode_vcf(str(x)) for x in data]
    data = '|'.join(data)

    return data


# write vcf header
info_headers = ["##INFO=<ID=inpret,Number=.,Type=String,Description=\"Interpretation / clinical significance of the variant. Format: CLNSIG|CLNSIGCONF\">",
                "##INFO=<ID=revstat,Number=.,Type=String,Description=\"Review status of the variant\">",
                "##INFO=<ID=varid,Number=1,Type=String,Description=\"The ClinVar variation identifier\">",
                "##INFO=<ID=submissions,Number=.,Type=String,Description=\"All submissions listed in ClinVar delimited by ','. All ',' in the original sequence were replaced with '\\' and spaces were replaced by '_' Format: VariationID|ClinicalSignificance|LastEvaluated|ReviewStatus|SubmittedPhenotypeInfo|Submitter|ExplanationOfInterpretation\">"]
functions.write_vcf_header(info_headers)


functions.eprint("reading submission summary...")
submission_summary = read_submission_summary(submission_summary_path)

functions.eprint("converting clinvar...")
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
    # if interpretation == '' or rev_stat == '':
        # continue

    parts[5] = '.'
    parts[6] = '.'
    parts[0] = 'chr' + chr_num
    info = ''
    info = functions.collect_info(info, 'inpret=', functions.encode_vcf(interpretation))
    info = functions.collect_info(info, 'revstat=', functions.encode_vcf(rev_stat))
    info = functions.collect_info(info, 'varid=', functions.encode_vcf(variation_id))
    
    current_submissions = submission_summary.get(variation_id, []) #.loc[submission_summary['#VariationID'] == int(variation_id)]
    #current_submissions = current_submissions.reset_index()
    
    all_submissions = []
    for submission in current_submissions:
        submission_str = submission2str(submission)
        all_submissions.append(submission_str)
    #all_submissions = current_submissions.apply(lambda x: convert_row_to_string(variation_id, x), axis=1)
    
    
    all_submissions = '&'.join(all_submissions)
    info = functions.collect_info(info, 'submissions=', all_submissions)
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


# 


