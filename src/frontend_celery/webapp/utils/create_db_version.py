import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
import json
import argparse
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import download.download_functions as download_functions
from pathlib import Path


parser = argparse.ArgumentParser(description="")
parser.add_argument("-d", "--date", help="Date of today")


args = parser.parse_args()
today = args.date



today = functions.get_today()

all_variants_folder = download_functions.get_all_variants_folder()
last_dump_path = path.join(all_variants_folder, ".last_dump.txt")
outpath = path.join(all_variants_folder, today+".vcf")

print(outpath)

conn = Connection(roles = ["db_admin"])
all_variant_ids = conn.get_all_valid_variant_ids(exclude_sv = False)
vcf_file_buffer, status, vcf_errors, err_msg = download_functions.get_vcf(all_variant_ids, conn)
conn.close()

if status == "error":
    msg = functions.collect_info("", "vcf_errors=", vcf_errors)
    msg = functions.collect_info(msg, "err_msg=", err_msg)
    raise IOError(msg)

functions.buffer_to_file_system(vcf_file_buffer, outpath)


with open(last_dump_path, 'w') as last_dump_file:
    last_dump_file.write(today)

