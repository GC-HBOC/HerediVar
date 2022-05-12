# this script collects information from curated & lifted variants from heredicare and annotates the original variants with these information
# if there were any errors it also reports those
# this script also searches for duplicates among the curated & lifted variants
# !!! this script assumes that the --tsv provided file has following header: #VID	GEN	REFSEQ	CHROM	GPOS	REFBAS	ALTBAS	CHGVS	CBIC	CGCHBOC


import argparse
from distutils.log import error
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions
import sys
import re

parser = argparse.ArgumentParser(description="this script converts a csv file of HerediCare Variants to a vcf file, column headers should be: VID;GEN;REFSEQ;CHROM;GPOS;REFBAS;ALTBAS;CHGVS;CBIC;CGCHBOC")
parser.add_argument("-t", "--tsv",  help="path to original heredicare tsv file")
parser.add_argument("--vcfworked",  help="path to vcf file containing the lifted and leftaligned variants")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("-s", "--sep", default="\t", help="separating character in the csv file, defaults to 'tabulator'")
parser.add_argument("--liftoverfailed", default="", help="path to file which is produced by crossmap which contains unmapped variants (ends with .unmap) defaults to --vcfworked path + .unmap")
parser.add_argument("--hgvstovcffailed", default="hgvstovcf_errors.txt", help="path to file which contains the error messages from hgvs to vcf ngsbits tool (just capture the output stream in file), defaults to hgvstovcf_erros.txt")
parser.add_argument("--hgvs", default="hgvs.tsv", help="path to file which is the input to the hgvs to vcf ngsbits file. Defaults to hgvs.tsv")
parser.add_argument('--notparsed', default='notparsed.tsv', help="path to file which was produced by db_converter_heredicare.py which contains all variants which lack vcf information AND HGVS information. Should have fields equal to the input tsv + additional comment column")
parser.add_argument('--vcfcheck_error', default='vcfcheck_errors.txt', help="path to file which contains the stderr of vcfcheck, defaults to vcfcheck_errors.txt")
parser.add_argument('--legacysymbols', default='legacy_gene_names.tsv', help="path to a file which was calculated using the ngs-bits GenesToApproved tool. This file should at least contain all legacy gene names which are present in the input --tsv")

#parser.add_argument("-e", "--errorfile", default="notparsed.tsv", help="this file contains the lines of the input tsv which had too much missing information to even have a chance to convert them to vcf")




args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

sep = args.sep

liftoverfailed_path = args.liftoverfailed
if liftoverfailed_path == '':
    liftoverfailed_path = args.vcfworked + '.unmap'

hgvstovcffailed_path = args.hgvstovcffailed

notparsed_path = args.notparsed

vcfcheck_error_path = args.vcfcheck_error

legacysymbols_path = args.legacysymbols


vcf_worked_file = open(args.vcfworked, 'r')

duplicate_groups = {} # keys: vcf representation values: comma seperated list of seqids
for line in vcf_worked_file:
    if line.startswith('#') or line.strip() == '':
        continue

    parts = line.split('\t')

    vcf = '\t'.join([parts[0], parts[1], parts[3], parts[4]])
    seqid = functions.find_between(parts[7].strip(), 'seqid=', '(;|$)')

    if vcf in duplicate_groups:
        duplicate_groups[vcf] = functions.collect_info(duplicate_groups[vcf], '', seqid, sep = ',')
    else:
        duplicate_groups[vcf] = seqid
vcf_worked_file.close()

vcf_worked_file = open(args.vcfworked, 'r')
lifted_variants = {} # prepare a dictionary to match seqid -> variant in vcf style
for line in vcf_worked_file:
    if line.startswith('#') or line.strip() == '':
        continue

    parts = line.split('\t')
    
    chr_num = functions.validate_chr(parts[0].strip())
    if not chr_num:
        continue
    chr = 'chr' + chr_num
    pos = parts[1].strip()
    ref = parts[3].strip()
    alt = parts[4].strip()

    # each variant must have a seqid at this point because variants were 
    # filtered out previously if they did not have a seqid
    seqid = functions.find_between(parts[7].strip(), 'seqid=', '(;|$)') 
    if seqid in lifted_variants:
        functions.eprint("WARNING seqid: " + seqid + " occurs multiple times")
        continue
    
    comment = functions.find_between(parts[7].strip(), 'comment=', '(;|$)')
    if comment is None:
        comment = ''
    
    # fetch dupicates
    vcf = '\t'.join([parts[0], parts[1], parts[3], parts[4]])
    duplicates = duplicate_groups[vcf]
    duplicates = duplicates.replace(seqid, '').replace(',,', ',').strip(',') # remove the id itself from the duplicates
    if duplicates != '':
        comment = functions.collect_info(comment, 'duplicates: ', duplicates)

    lifted_variants[seqid] = (chr, pos, ref, alt, comment)

# 11914486	ATM	NM_001127510.1					c.423-4del			chr5	112775612	TA	T	vcf style variant calculated using ngsbits (hgvsToVcf tool);duplicates: 11914515,8854230,13492041
# 8854230	APC	NM_000038.5	5	112111309	TA	T	c.423-16delA			chr5	112775612	TA	T	duplicates: 11914486,11914515,13492041
# 13492041	APC	NM_001127511.2	5	112111309	TA	T	c.453-16delA			chr5	112775612	TA	T	duplicates: 11914486,11914515,8854230
# 11914515	APC	NM_001127510.1					c.423-4del			chr5	112775612	TA	T	vcf style variant calculated using ngsbits (hgvsToVcf tool);duplicates: 11914486,8854230,13492041

vcf_worked_file.close()


liftover_failed_file = open(liftoverfailed_path, 'r')
failed_variants = {} # this contains all variants which have some error in the pipeline and the error message
for line in liftover_failed_file:
    if line.startswith('#') or line.strip() == '':
        continue

    parts = line.split('\t')
    seqid = functions.find_between(parts[7].strip(), 'seqid=', '(;|$)') 
    comment = 'liftover error: ' + parts[8].strip()
    if seqid in failed_variants:
        failed_variants[seqid] = functions.collect_info(failed_variants[seqid], '', comment)
    else:
        failed_variants[seqid] = comment
liftover_failed_file.close()


hgvs_file = open(args.hgvs, 'r')
hgvs_to_seqid = {}
for line in hgvs_file:
    if line.startswith('#') or line.strip() == '':
        continue
    
    parts = line.split('\t')
    seqid = parts[2]
    cdot = functions.remove_version_num(parts[0]) + ':' + parts[1]
    hgvs_to_seqid[cdot] = seqid
hgvs_file.close()


hgvstovcffailed_file = open(hgvstovcffailed_path, 'r')
for line in hgvstovcffailed_file:
    if line.startswith('#') or line.startswith('-') or line.strip() == '':
        continue
    
    cdot = functions.find_between(line, 'Warning: ', ' skipped')
    if cdot is None:
        functions.eprint("WARNING: could not find cdot in hgvs to vcf error file: " + line)
        continue

    seqid = hgvs_to_seqid.get(cdot, None)
    if seqid is None:
        functions.eprint("WARNING: seqid not found for cdot: " + cdot)
        continue

    comment = 'HgvsToVcf error: ' + functions.find_between(line, 'skipped: ', '$')

    if seqid in failed_variants:
        failed_variants[seqid] = functions.collect_info(failed_variants[seqid], '', comment)
    else:
        failed_variants[seqid] = comment
hgvstovcffailed_file.close()


notparsed_file = open(notparsed_path, 'r')
for line in notparsed_file:
    if line.startswith('#') or line.strip() == '':
        continue
    
    parts = line.split('\t')
    seqid = parts[0].strip()
    comment = parts[10].strip()

    if seqid in failed_variants:
        failed_variants[seqid] = functions.collect_info(failed_variants[seqid], '', comment)
    else:
        failed_variants[seqid] = comment
notparsed_file.close()



vcfcheck_error_file = open(vcfcheck_error_path, 'r')
in_error = False
for line in vcfcheck_error_file:
    if line.startswith('#') or line.strip() == '':
        continue

    if line.startswith('ERROR:'):
        in_error = True
        comment = 'vcfcheck error: ' + functions.find_between(line, 'ERROR: ', ' - ')
    
    if line.startswith('WARNING:'):
        in_error = False
    
    if in_error and not line.startswith('ERROR:'):
        parts = line.split('\t')
        seqid = functions.find_between(parts[7].strip(), 'seqid=', '(;|$)')
        failed_variants[seqid] = comment
vcfcheck_error_file.close()


transcript_to_gene = functions.get_transcript_to_gene_dict()

legacysymbols_file = open(legacysymbols_path, 'r')
legacysymbols_mapping = {}
for line in legacysymbols_file:
    if line.startswith('#') or line.strip() == '':
        continue
    
    parts = line.split('\t')
    new_symbol = parts[0]
    old_symbol = functions.find_between(parts[1], 'REPLACED: ', ' is')

    if old_symbol not in legacysymbols_mapping:
        legacysymbols_mapping[old_symbol] = new_symbol
    elif legacysymbols_mapping[old_symbol] != new_symbol:
            functions.eprint("There are multiple new symbols for one legacy symbol: " + old_symbol + ' in file ' + legacysymbols_path + ' skipping the new one!')
legacysymbols_file.close()






original_heredicare = open(args.tsv, 'r')
print('#VID	GEN	REFSEQ	CHROM	GPOS	REFBAS	ALTBAS	CHGVS	CBIC	CGCHBOC	CHROM_GRCH38	GPOS_GRCH38	REFBAS_GRCH38	ALTBAS_GRCH38	COMMENT')
for line in original_heredicare:
    line = line.strip('\n')
    if line.startswith('#') or line.strip() == '':
        continue
    
    parts = line.split(sep)

    seqid = parts[0].strip()

    lifted_variant = lifted_variants.get(seqid, None)

    comment = failed_variants.get(seqid, '')

    gene_symbol = parts[1]
    # map the gene symbol to the current version as the transcript to gene mapping table has only current gene symbols
    # we do not want to say that the gene for a transcript is wrong because it is simply outdated!
    new_gene_symbol = legacysymbols_mapping.get(gene_symbol, gene_symbol)

    transcript = functions.remove_version_num(parts[2])
    actual_gene_symbol = transcript_to_gene.get(transcript, None)
    if actual_gene_symbol is not None:
        if new_gene_symbol not in actual_gene_symbol:
            comment = functions.collect_info(comment, '', 'gene symbol in GEN column is wrong or outdated should be ' + actual_gene_symbol)

    if lifted_variant is not None:
        #comment = functions.collect_info(lifted_variant[len(lifted_variant)-1], '', comment)
        lifted_variant_string = '\t'.join(lifted_variant)
        print('\t'.join([line, lifted_variant_string, comment]))
    else:
        variant_string = '\t' * 3 # variant was not mapped to hg 38 thus, enter empty fields
        print('\t'.join([line, variant_string, comment]))
    
