import sys
from os import path
sys.path.append(path.dirname(path.abspath(__file__)))
import utils
import json
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("-e", "--exclude",  nargs="+", help="All tables that should not be tuncated on db rollback")
parser.add_argument("-o", "--output", help="The output file path")

args = parser.parse_args()
tables_to_exclude = args.exclude
outpath = args.output

conn = utils.Test_Connection(roles = ['db_admin'])

all_tables = conn.get_tables()


tables_oi = list(set(all_tables) - set(tables_to_exclude))

#print(tables_oi)

#print(outpath)

with open(outpath, "w") as outfile:
    outfile.write("SET FOREIGN_KEY_CHECKS = 0;\n")
    for table_oi in tables_oi:
        outfile.write(f"TRUNCATE table {table_oi};\n")
    outfile.write("SET FOREIGN_KEY_CHECKS = 1;\n")

conn.close()


