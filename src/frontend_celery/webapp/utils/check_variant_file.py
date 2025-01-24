import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
import common.paths as paths
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import frontend_celery.webapp.tasks as tasks
import argparse
import re
import os

# input file format
        #0 vid	
        #1 chrom	
        #2 hg19_pos	
        #3 hg19_ref	
        #4 hg19_alt	
        #5 hg38_pos	
        #6 hg38_ref	
        #7 hg38_alt	
        #8 transcript	
        #9 gene	
        #10 hgvs_c	
# additional lines will not be used but kept


parser = argparse.ArgumentParser(description="Read a tsv file and try to canonicalize / recover hg38 gnomic position")
parser.add_argument("-i", "--input", help="path to input file")
parser.add_argument("-o", "--output", help="output file path.")

args = parser.parse_args()


inpath = args.input
outpath = args.output

_ = tasks.start_check_variants_file(inpath, outpath)


