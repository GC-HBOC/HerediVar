# this script checks that all HerediCaRe VIDs are consistent with the HerediVar variants


import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
from common.heredicare_interface import Heredicare
import frontend_celery.webapp.tasks as tasks

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


conn = Connection()
heredicare = Heredicare()

err_out_path = path.dirname(path.abspath(__file__)) + "/heredicare_errors.tsv"
err_out_file = open(err_out_path, 'w')

user_id = -1

variant_ids = conn.get_all_valid_variant_ids()
print_progress_bar(0, len(variant_ids), prefix = 'Progress:', suffix = 'Complete', length = 50)

for i, variant_id in enumerate(variant_ids):
    variant = conn.get_variant(variant_id, include_external_ids = True, include_annotations = False, include_consensus = False, include_user_classifications = False, include_automatic_classification = False, include_clinvar = False, include_consequences = False, include_assays = False, include_literature = False)
    variant_id = str(variant.id)
    vids = variant.get_external_ids('heredicare_vid', how = 'list')

    for vid in vids:
        status, message = tasks.fetch_heredicare(vid, user_id, conn, insert_variant = False, perform_annotation = False)
        if status != 'success':
            line = "\t".join([variant.get_string_repr(), "", variant_id, vid, "HerediCaRe API error: " + message])
            err_out_file.write(line + "\n")
            continue
    
        heredicare_variant = functions.find_between(message, 'HG38 variant would be: ', '( ~~ |$)')
        if heredicare_variant is None:
            line = "\t".join([variant.get_string_repr(), '', variant_id, vid, "The heredicare_variant was not found in message: " + message])
            err_out_file.write(line + "\n")
            continue
        heredicare_variant = heredicare_variant.strip().split('-')

        if len(heredicare_variant) != 4:
            line = "\t".join([variant.get_string_repr(), '-'.join(heredicare_variant), variant_id, vid, "Number of fields of heredicare variant is incorrect: " + str(len(heredicare_variant))])
            err_out_file.write(line + "\n")
            continue
        
        if variant.chrom != heredicare_variant[0] or str(variant.pos) != heredicare_variant[1] or variant.ref != heredicare_variant[2] or variant.alt != heredicare_variant[3]:
            line = "\t".join([variant.get_string_repr(), '-'.join(heredicare_variant), variant_id, vid, "Incorrect variant match!"])
            err_out_file.write(line + "\n")
            continue

    print_progress_bar(i+1, len(variant_ids), prefix = 'Progress:', suffix = 'Complete', length = 50)




err_out_file.close()
conn.close()
