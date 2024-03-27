from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import argparse
import common.functions as functions


parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")


args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r', encoding='utf-8', errors='ignore')
else:
    input_file = sys.stdin


last_variant = None
last_info = None

for line in input_file:
    line = line.strip()
    if line.startswith('#') or line == '':
        print(line)
        continue

    parts = line.split('\t')

    current_variant = {"chrom": parts[0], "pos": parts[1], "ref": parts[3], "alt": parts[4]}
    info = parts[7]
    current_cancertypes_raw = functions.find_between(info, "cancertypes=", "(;|$)")
    current_cancertypes_raw = current_cancertypes_raw.split('|')
    current_cancertypes = {}
    for cancertype_raw in current_cancertypes_raw:
        cancertype_parts = cancertype_raw.split(':')
        current_cancertypes[cancertype_parts[0]] = cancertype_parts

    current_ac = functions.find_between(info, "AC=", "(;|$)")
    current_af = functions.find_between(info, "AF=", "(;|$)")
    current_info = {"cancertypes": current_cancertypes, "ac": current_ac, "af": current_af}

    if last_variant is None:
        last_variant = current_variant
        last_info = current_info
        continue

    if any([current_variant[key] != last_variant[key] for key in current_variant]):
        cancertype_info_parts = []
        for key in last_info["cancertypes"]:
            cancertype_info_parts.append(':'.join(last_info["cancertypes"][key]))
        cancertype_info = '|'.join(cancertype_info_parts)
        vcf_info = ""
        vcf_info = functions.collect_info(vcf_info, "cancertypes=", cancertype_info)
        vcf_info = functions.collect_info(vcf_info, "AC=", last_info["ac"])
        vcf_info = functions.collect_info(vcf_info, "AF=", last_info["af"])
        if vcf_info == "":
            vcf_info = "."
        vcf_line = '\t'.join([str(x) for x in [last_variant["chrom"], last_variant["pos"], ".", last_variant["ref"], last_variant["alt"], ".", ".", vcf_info]])
        print(vcf_line)

        last_variant = current_variant
        last_info = current_info

    else: # update info if the variant is equal
        functions.eprint(current_variant)
        last_info["ac"] = str(int(last_info['ac']) + int(current_info['ac']))
        last_info["af"] = str(float(last_info['af']) + float(current_info['af']))
        for key in current_info["cancertypes"]:
            if key in last_info["cancertypes"]:
                last_info["cancertypes"][key][3] = str(int(last_info["cancertypes"][key][3]) + int(current_info["cancertypes"][key][3]))
            else:
                last_info["cancertypes"][key] = current_info["cancertypes"][key]


cancertype_info_parts = []
for key in last_info["cancertypes"]:
    cancertype_info_parts.append(':'.join(last_info["cancertypes"][key]))
cancertype_info = '|'.join(cancertype_info_parts)
vcf_info = ""
vcf_info = functions.collect_info(vcf_info, "cancertypes=", cancertype_info)
vcf_info = functions.collect_info(vcf_info, "AC=", last_info["ac"])
vcf_info = functions.collect_info(vcf_info, "AF=", last_info["af"])
if vcf_info == "":
    vcf_info = "."
vcf_line = '\t'.join([str(x) for x in [last_variant["chrom"], last_variant["pos"], ".", last_variant["ref"], last_variant["alt"], ".", ".", vcf_info]])
print(vcf_line)