from os import path
import sys
sys.path.append(  path.join(path.dirname(path.dirname(path.abspath(__file__))), "src")  )
import argparse
import common.functions as functions
import json


parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input maf file")
parser.add_argument("-s", "--significant",  default="", help="path to input file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("--header", default=1, help="The line number which has the header (Zero centered, default: 1)")
parser.add_argument("--oncotree", help="Path to Oncotree json file: http://oncotree.mskcc.org/api/tumorTypes")


args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r', encoding='utf-8', errors='ignore')
else:
    input_file = sys.stdin

i_header_line = args.header
oncotree_path = args.oncotree
significant_path = args.significant



## extract significant cancerhotspots from xls file (converted to tsv)
functions.eprint("parsing significant hotspots")
significant_file = open(significant_path, 'r')

significant_hotspots = []
for line in significant_file:
    parts = line.split('\t')
    if line.startswith('Hugo_Symbol'):
        for i, part in enumerate(parts):
            if part == "Amino_Acid_Position":
                i_amino_acid_pos = i
            if part == "Reference_Amino_Acid":
                i_reference_aa = i
            if part == "Variant_Amino_Acid":
                i_alternative_aa = i
            if part == "Hugo_Symbol":
                i_gene_symbol = i
        continue

    current_gene_symbol = parts[i_gene_symbol]
    current_amino_acid_pos = parts[i_amino_acid_pos]
    current_reference_aa = parts[i_reference_aa].split(':')[0]
    current_alternative_aa = parts[i_alternative_aa].split(':')[0]
    

    significant_hotspots.append('-'.join([current_gene_symbol, current_amino_acid_pos, current_reference_aa, current_alternative_aa]))

significant_file.close()

## extract 1:1 mapping of oncotree identifiers and names
functions.eprint("parsing oncotree")
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
def prepare_cancertype(cancertype, ac):
    parts = cancertype.split(':')
    oncotree_name = convert_oncotree_symbol(parts[0])
    oncotree_name = oncotree_name.replace(' ', '_')
    return ':'.join([parts[0], oncotree_name, parts[1], str(ac)])

def print_line(cancerhotspots_barcode, all_cancer_types, ac, tot_samples):
    cancertypes = '|'.join([prepare_cancertype(x, all_cancer_types[x]) for x in all_cancer_types])
    af = round(ac/tot_samples, 3)
    print('\t'.join([cancerhotspots_barcode, cancertypes, str(ac), str(af)]))


# contig header lines are required for crossmap lifting of genomic positions
functions.eprint("parsing maf")

i_current_line = -1

#found_hotspots = []
all_data = {} # cancerhotspotbarcode -> info
all_samples = []
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
            elif part == 'oncotree_detailed':
                i_barcode = i
            elif part == "oncotree_organtype":
                i_tissue = i
            elif part == "Amino_Acid_Position":
                i_pos_aa = i
            elif part == "Reference_Amino_Acid":
                i_ref_aa = i
            elif part == "Variant_Amino_Acid":
                i_alt_aa = i
            elif part == "Hugo_Symbol":
                i_gene_symbol = i
            elif part == "Transcript_ID":
                i_transcript = i
            elif part == "Tumor_Sample_Barcode":
                i_sample = i
            header_len = len(parts)
        continue

    parts = line.split('\t')
    if len(parts) != header_len:
        #functions.eprint("WARNING: skipping variant because it did not have the correct number of fields. line number in input file: " + str(i_current_line))
        continue

    gene_symbol = parts[i_gene_symbol]
    transcript = parts[i_transcript]
    pos_aa = parts[i_pos_aa]
    ref_aa = parts[i_ref_aa]
    alt_aa = parts[i_alt_aa]
    current_hotspot = '-'.join([gene_symbol, pos_aa, ref_aa, alt_aa])
    if current_hotspot not in significant_hotspots: # skip non significant variants
        continue
    
    all_samples.append(parts[i_sample])
    #found_hotspots.append(current_hotspot)
    cancerhotspots_barcode = '-'.join([transcript, pos_aa, ref_aa, alt_aa])

    if cancerhotspots_barcode not in all_data:
        all_data[cancerhotspots_barcode] = {"cancertypes": {}, "ac": 0}

    # update cancertypes
    current_key = parts[i_barcode] + ':' + parts[i_tissue]
    if current_key not in all_data[cancerhotspots_barcode]["cancertypes"]:
        all_data[cancerhotspots_barcode]["cancertypes"][current_key] = 1
    else:
        all_data[cancerhotspots_barcode]["cancertypes"][current_key] += 1

    all_data[cancerhotspots_barcode]["ac"] += 1
    
tot_samples = len(list(set(all_samples)))
for cancerhotspots_barcode in all_data:
    data = all_data[cancerhotspots_barcode]
    print_line(cancerhotspots_barcode, data['cancertypes'], data["ac"], tot_samples)

    

#found_hotspots = list(set(found_hotspots))
#functions.eprint(found_hotspots)
#functions.eprint(len(found_hotspots))
    


