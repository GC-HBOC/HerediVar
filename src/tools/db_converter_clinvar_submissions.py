from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import common.functions as functions
import pandas as pd
import datetime

def convert_row_to_string(row):
    last_evaluated = str(row['DateLastEvaluated'])
    if last_evaluated != '-':
        last_evaluated = datetime.datetime.strptime(last_evaluated, "%b %d, %Y").strftime("%Y-%m-%d")

    result = str(row['ClinicalSignificance']) + '|' \
     + last_evaluated + '|' + str(row['ReviewStatus']) + '|' \
      + str(row['CollectionMethod']) + '|' + str(row['SubmittedPhenotypeInfo']) + '|' \
       + str(row['OriginCounts']) + '|' + str(row['Submitter']) + '|' + str(row['ExplanationOfInterpretation'])

    return result.replace(',', '/')
    
if __name__ == "__main__":
    submission_summary_path = "/mnt/users/ahdoebm1/HerediVar/data/dbs/ClinVar/submission_summary_preprocessed.txt.gz"
    submission_summary = pd.read_csv(submission_summary_path, sep = "\t", compression="gzip", comment='#')
    current_submissions = submission_summary.loc[submission_summary['VariationID'] == int(9)]
    current_submissions = current_submissions.reset_index()

    #for index,row in current_submissions.iterrows():
    #    print(line)
    all_submissions = current_submissions.apply(lambda x: convert_row_to_string(x), axis=1)
    print(','.join(all_submissions))






# clinvar_interpretations table
# - interpretation: ClinicalSignificance column
# - last_evaluated: DateLastEvaluated column
# - review_status: ReviewStatus column
# (- assertion_criteria: CollectionMethod column)
# - condition: SubmittedPhenotypeInfo column
# (- inheritance: OriginCounts column)
# - submitter: Submitter column
# - supporting_information: ExplanationOfInterpretation / description