from urllib.request import urlopen
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input data-uris, will default to stdin. Comments in this file start with a #. Each line should correspond to one data-uri")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--header", action='store_true', help="boolean, specify if there is a header line that should be contained in the output. If true: writes the headerline one time. If false: write the whole document without skipping of (header)lines")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    data_uri_file = open(args.input, "r")
else:
    data_uri_file = sys.stdin

header_in_file = args.header


print_header = True

for data_uri in data_uri_file:
    if data_uri.startswith('#') or data_uri.strip() == '':
        continue
    first_line = True
    with urlopen(data_uri) as response:
        for line in response:
            if header_in_file:
                if not print_header and first_line:
                    first_line = False
                    continue
                print_header = False
                first_line = False

            line = line.decode('utf-8').strip()
            print(line)

data_uri_file.close()

