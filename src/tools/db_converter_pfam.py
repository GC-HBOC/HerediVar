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


args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r', encoding='utf-8', errors='ignore')
else:
    input_file = sys.stdin


pfam_acc = ''
description = ''
symbol = ''
for line in input_file:
    if line == '//':
        print(pfam_acc + "\t" + symbol + "\t" + description)
        pfam_acc = ''
        description = ''
        symbol = ''
        continue
    
    if line.startswith('#=GF ID'):
        symbol = line[10:]
    if line.startswith('#=GF AC'):
        pfam_acc = line[10:]
    if line.startswith('#=GF DE'):
        description = line[10:]