from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
import common.functions as functions
import json


parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--header", default=1, help="The line number which has the header (Zero centered, default: 0)")
parser.add_argument("--samples", help="The total number of samples in the maf file")
parser.add_argument("--oncotree", help="Path to Oncotree json file: http://oncotree.mskcc.org/api/tumorTypes")


args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r', encoding='utf-8', errors='ignore')
else:
    input_file = sys.stdin

i_header_line = args.header
tot_samples = int(args.samples)
oncotree_path = args.oncotree


## extract 1:1 mapping of oncotree identifiers and names
oncotree_file = open(oncotree_path, 'r')
json_array = oncotree_file.read()

oncotree = json.loads(json_array)

oncotree_dict = {}

for tumor_type in oncotree:
    current_code = str(tumor_type['code']).strip().upper()
    current_name = str(tumor_type['name']).strip()
    oncotree_dict[current_code] = current_name

# add some legacy codes, see: https://github.com/cBioPortal/cancerhotspots/issues/23
# more abbreviations: https://gdc.cancer.gov/resources-tcga-users/tcga-code-tables/tcga-study-abbreviations (1)
oncotree_dict['MMYL'] = "Multiple Myeloma" # from oncotree_2018_01_01
oncotree_dict['HGG'] = "Malignant High-Grade Glioma" # taken from internet
oncotree_dict['LGG'] = "Low-Grade Glioma" # taken from internet
oncotree_dict['KIRP'] = "Papillary Renal Cell Carcinoma"
oncotree_dict['LAML'] = "Acute Myeloid Leukemia"
oncotree_dict['OV'] = "High-Grade Serous Ovarian Cancer"
oncotree_dict['LIHC'] = "Hepatocellular Carcinoma"
oncotree_dict['KIRC'] = "Renal Clear Cell Carcinoma"
oncotree_dict['CLL'] = "Chronic Lymphocytic Leukemia" # taken from internet
oncotree_dict['KICH'] = "Chromophobe Renal Cell Carcinoma"
oncotree_dict['LUSM'] = "Small Cell Lung Cancer"
oncotree_dict['PIAS'] = "Pilocytic Astrocytoma"
oncotree_dict['DLBC'] = "Diffuse Large B-Cell Lymphoma"
oncotree_dict['LYMBC'] = "Burkitt Lymphoma" 
oncotree_dict['ALL'] = "Acute Lymphoid Leukemia" # from oncotree_2018_01_01
oncotree_dict['PANNET'] = "Pancreatic Neuroendocrine Tumor"
oncotree_dict['SARC'] = "Sarcoma" # from (1)
oncotree_dict['HNSC'] = "Head and Neck Squamous Cell Carcinoma" # from oncotree_2018_01_01



oncotree_file.close()


## parse cancerhotspots
def print_variant(chr, pos, ref, alt, info):
    if functions.is_dna(ref) and functions.is_dna(alt):
        if ref == '-':
            ref = ''
        if alt == '-':
            alt = ''
        chr_symbol = functions.validate_chr(chr)
        if chr_symbol: # save only variants from valid chrs
            line_to_print = ['chr' + chr, pos, '.', ref, alt, '.', '.', info]
            print('\t'.join(line_to_print))
        else:
            #functions.eprint("WARNING: variant was removed as it is from an unsupported chromosome: " + 'chr' + chr + ' ' + pos + ' . ' + ref + ' ' + alt + ' . ' + ' . ' + info)
            pass
    else:
        #functions.eprint("WARNING: variant was removed as it contains non dna nucleotides: "  + 'chr' + chr + ' ' + pos + ' . ' + ref + ' ' + alt + ' . ' + ' . ' + info)
        pass


def convert_oncotree_symbol(oncotree_symbol):
    oncotree_symbol = str(oncotree_symbol).strip().upper()
    if oncotree_symbol != '':
        if oncotree_symbol in oncotree_dict:
            oncotree_name = oncotree_dict[oncotree_symbol]
            return oncotree_name
        #functions.eprint("WARNING: encountered unknown oncotree symbol: " + str(oncotree_symbol) + " writing symbol instead of name...")
        return oncotree_symbol


# cancertype is oncotreecancertype:oncotreetissue
def prepare_cancertype(cancertype):
    parts = cancertype.split(':')
    oncotree_name = convert_oncotree_symbol(parts[0])
    oncotree_name = oncotree_name.replace(' ', '_')
    return oncotree_name + ':' + parts[1]




# contig header lines are required for crossmap lifting of genomic positions
info_header = [
    "##contig=<ID=chr1>",
    "##contig=<ID=chr2>",
    "##contig=<ID=chr3>",
    "##contig=<ID=chr4>",
    "##contig=<ID=chr5>",
    "##contig=<ID=chr6>",
    "##contig=<ID=chr7>",
    "##contig=<ID=chr8>",
    "##contig=<ID=chr9>",
    "##contig=<ID=chr10>",
    "##contig=<ID=chr11>",
    "##contig=<ID=chr12>",
    "##contig=<ID=chr13>",
    "##contig=<ID=chr14>",
    "##contig=<ID=chr15>",
    "##contig=<ID=chr16>",
    "##contig=<ID=chr17>",
    "##contig=<ID=chr18>",
    "##contig=<ID=chr19>",
    "##contig=<ID=chr20>",
    "##contig=<ID=chr21>",
    "##contig=<ID=chr22>",
    "##contig=<ID=chrX>",
    "##contig=<ID=chrY>",
    "##contig=<ID=chrMT>",
    "##INFO=<ID=cancertypes,Number=.,Type=String,Description=\"A | delimited list of all cancertypes associated to this variant according to cancerhotspots. FORMAT: tumortype:tissue\">",
    "##INFO=<ID=AC,Number=1,Type=Integer,Description=\"Number of samples showing the variant from cancerhotspots\">",
    "##INFO=<ID=AF,Number=1,Type=Float,Description=\"Allele Frequency of the variant (AC / num samples cancerhotspots)\">",
    "##INFO=<ID=tissue,Number=1,Type=String,Description=\"Oncotree tissue type according to the cancertype. \">"]
functions.write_vcf_header(info_header)


i_current_line = -1


is_first_variant = True
for line in input_file:
    line = line.strip()
    i_current_line += 1

    if line.startswith('#') or line == '':
        continue

    if i_current_line == i_header_line:
        parts = line.split('\t')
        for i in range(len(parts)):
            part = parts[i]
            if part == 'Chromosome':
                i_chr = i
            elif part == 'Start_Position':
                i_start = i
            elif part == 'Reference_Allele':
                i_ref = i
            elif part == 'Tumor_Seq_Allele2': # this is the alt allele
                i_alt = i
            elif part == 'Tumor_Seq_Allele1': # this is the alt allele
                i_alt_1 = i
            elif part == 'TUMORTYPE':
                i_cancertype = i
            elif part == 'Tumor_Sample_Barcode':
                i_barcode = i
            elif part == "oncotree_organtype":
                i_tissue = i
            header_len = len(parts)
        continue

    parts = line.split('\t')
    if len(parts) != header_len:
        #functions.eprint("WARNING: skipping variant because it did not have the correct number of fields. line number in input file: " + str(i_current_line))
        continue

    chr = parts[i_chr]
    pos = parts[i_start]
    ref = parts[i_ref]
    alt = parts[i_alt]
    alt_1 = parts[i_alt_1]
    barcode = parts[i_barcode]

    if is_first_variant:
        previous_chr = chr
        previous_pos = pos
        previous_ref = ref
        previous_alt = alt
        previous_barcode = barcode
        all_cancer_types = []
        ac = 1
        is_first_variant = False
    
    
    
    # test if previous variant is equal to the current one
    if chr != previous_chr or pos != previous_pos or ref != previous_ref or alt != previous_alt:
        info = ''
        info = functions.collect_info(info, 'cancertypes=', '|'.join([prepare_cancertype(x) for x in set(all_cancer_types)]))
        info = functions.collect_info(info, 'AC=', ac)
        info = functions.collect_info(info, 'AF=', ac/tot_samples)
        print_variant(previous_chr, previous_pos, previous_ref, previous_alt, info)

        previous_chr = chr
        previous_pos = pos
        previous_ref = ref
        previous_alt = alt
        previous_barcode = barcode
        if parts[i_cancertype] != '' or parts[i_tissue] != '': # collect cancertypes only if there is at least some information available
            all_cancer_types = [parts[i_cancertype] + ':' + parts[i_tissue]]
        else:
            all_cancer_types = []
        ac = 1
    else:
        if parts[i_cancertype] != '' or parts[i_tissue] != '':
            all_cancer_types.append(parts[i_cancertype] + ':' + parts[i_tissue])
        if previous_barcode != barcode:
            ac += 1



# dont forget to print the last variant which is not captured in the loop
info = ''
info = functions.collect_info(info, 'cancertypes=', '|'.join([convert_oncotree_symbol(x) for x in set(all_cancer_types)]))
info = functions.collect_info(info, 'AC=', ac)
info = functions.collect_info(info, 'AF=', ac/tot_samples)
print_variant(previous_chr, previous_pos, previous_ref, previous_alt, info)

    

    
    
    


