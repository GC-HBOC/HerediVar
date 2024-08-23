import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
import common.paths as paths
import json
import argparse
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import download.download_functions as download_functions
from pathlib import Path


parser = argparse.ArgumentParser(description="")
parser.add_argument("-d", "--date", help="Date of today")


args = parser.parse_args()
today = args.date


#### GENERATE VCF WITH ALL ANNOTATIONS ####
all_variants_folder = download_functions.get_all_variants_folder()
last_dump_path = path.join(all_variants_folder, ".last_dump.txt")
outpath = path.join(all_variants_folder, today+".vcf")

print(outpath)

conn = Connection(roles = ["db_admin"])
all_variant_ids = conn.get_all_valid_variant_ids(exclude_sv = False)
status, message = download_functions.write_vcf_file(all_variant_ids, outpath, conn)
#vcf_file_buffer, status, vcf_errors, err_msg = download_functions.get_vcf(all_variant_ids, conn)
conn.close()

if status == "error":
    with open(all_variants_folder + "/errors_" + today + ".txt", 'w') as f:
        f.write(message)

with open(last_dump_path, 'w') as last_dump_file:
    last_dump_file.write(today)

#### GENERATE CONSENSUS CLASSIFICATION ONLY VCF ####
conn = Connection(['db_admin'])
variant_types = conn.get_enumtypes("variant", "variant_type")
conn.close()
download_functions.generate_consensus_only_vcf(variant_types, dummy = False)



