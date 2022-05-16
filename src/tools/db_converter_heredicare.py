# this script converts a csv file of HerediCare Variants to a vcf file
# column headers should be: VID;GEN;REFSEQ;CHROM;GPOS;REFBAS;ALTBAS;CHGVS;CBIC;CGCHBOC
# the id field in the output vcf is the heredicare seqid
# keep in mind that the header line should start with a '#' symbol!!!

import argparse
from distutils.log import error
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import common.functions as functions
import sys
import re

parser = argparse.ArgumentParser(description="this script converts a csv file of HerediCare Variants to a vcf file, column headers should be: VID;GEN;REFSEQ;CHROM;GPOS;REFBAS;ALTBAS;CHGVS;CBIC;CGCHBOC")
parser.add_argument("-i", "--input",  default="", help="path to csv file")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
parser.add_argument("-s", "--sep", default="\t", help="separating character in the csv file, defaults to 'tabulator'")
parser.add_argument("-e", "--errorfile", default="notparsed.tsv", help="this file contains the lines of the input tsv which had too much missing information to even have a chance to convert them to vcf")
parser.add_argument("--hgvsfile", default="hgvs.tsv", help="this file contains hgvs strings and reference transcripts which can be used by the hgvs to vcf tool of ngsbits")

args = parser.parse_args()

if args.output is not "":
    sys.stdout = open(args.output, 'w')

if args.input is not "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin

sep = args.sep


error_file = open(args.errorfile, 'w')
hgvs_file = open(args.hgvsfile, 'w')
hgvs_file.write('\t'.join(['#reference', 'hgvsc', 'seqid']))
hgvs_file.write('\n')

# write vcf header
info_headers = [
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
    "##INFO=<ID=seqid,Number=1,Type=Integer,Description=\"The HerediCare SeqId of this variant.\">",
    "##INFO=<ID=gene,Number=1,Type=String,Description=\"The gene where the variant is located.\">",
    "##INFO=<ID=HGVSc,Number=1,Type=String,Description=\"The HGVS c dot notation of this variant.\">",
    "##INFO=<ID=cbic,Number=1,Type=String,Description=\"???.\">",
    "##INFO=<ID=cgchboc,Number=1,Type=String,Description=\"????.\">"

]
functions.write_vcf_header(info_headers)


def write_error_file_line(line, reason):
    parts = line.split(sep)
    cdot = parts[7]
    cdot = "".join(cdot.split()) # remove all whitespace
    reference = parts[2].strip()
    seqid = parts[0].strip()

    # remove everything after dup or del 
    #matches = re.search('dup|del', cdot)
    #if matches is not None: # check if it is an insertion duplication or deletion and remove bases preceding these keywords
    #    cut_here = matches.end(0)
    #    cdot = cdot[:cut_here]


    # if hgvs or reference transcript is missing the variant is lost for sure!
    if cdot == '' or reference == '':
        error_file.write('\t'.join([line.strip('\n'), reason + ', missing hgvs information' + '\n']))
    else:
        hgvs_file.write('\t'.join([reference, cdot, seqid]))
        hgvs_file.write('\n')




for line in input_file:
    if line.startswith('#') or (line.strip() == ''):
        continue

    parts = line.split(sep)

    chr_num = functions.validate_chr(parts[3].strip())
    if not chr_num:
        write_error_file_line(line, reason = 'missing vcfstyle information')
        continue
    chr = 'chr' + chr_num
    
    pos = parts[4].strip()
    ref = parts[5].strip()
    alt = parts[6].strip()

    seqid = parts[0].strip()

    info = ''
    info = functions.collect_info(info, 'seqid=', seqid)
    info = functions.collect_info(info, 'gene=', parts[1].strip())
    info = functions.collect_info(info, 'HGVSc=', parts[2].strip() + ':' + parts[7].strip())
    info = functions.collect_info(info, 'cbic=', parts[8].strip())
    info = functions.collect_info(info, 'cgchboc=', parts[9].strip())

    vcf_parts = [chr, pos, '.', ref, alt, '.', '.', info]

    if chr == '' or pos == '' or ref == '' or alt == '':
        write_error_file_line(line, reason= "missing chr, pos, ref or alt")
        continue
    
    if seqid == '':
        error_file.write('\t'.join([line, 'missing seqid'])) # do not collect variants which lack a heredicare seqid
        continue

    print('\t'.join(vcf_parts))
    
    #print(line)


hgvs_file.close()
error_file.close()





# problems encountered and solutions:
# - hgvsc column sometimes contains hgvsp as well (eg: c.200-?_5105+?del, p.Cys27-?_Phe1662+?del)
# - some of the variants dont have a vcf representation especially if there is some unknown information -> try to convert hgvs to vcf, if this does not work leave them out
# - there are a total of 3175 variants which do not have a vcf representation in the input file
# - approx 500 recovered from hgvs using genome build grch37 and approx 1600 using genome build grch38?!

# vcf check results in two errors:
#$ngsbits/VcfCheck -in heredicare_variants_11.05.22.vcf.gz -ref $data/genomes/GRCh37.fa
#ERROR: Reference base(s) not correct. Is 'G', should be 'T'! - in line 96:
#chr1    45797441        12470388        G       GGGGGAAGTTGACCACTCCCAGGGTCTGGTCCCAGGGCTCCGAGGGAGGCAGGCACAGGTGGCACTGTCCAGTGTTGGGAGCTGGGAACGGAGATCCCCGAATCCAGGTACCTGAGTTGGGCCTCTGCACCAGCAGAATTTGGGCCCCAAGGGCCCCAGGCTGTTCCAGAACACAGGTGGCAGAGCTCTCCTCCCTGGGGGGCTTGCGGCTGGCCTTTCT    .   .seqid=12470388;gene=MUTYH;ref_transcript=NM_001128425;hgvsc=c.1077_1078insAGAAAGGCCAGCCGCAAGCCCCCCAGGGAGGAGAGCTCTGCCACCTGTGTTCTGGAACAGCCTGGGGCCCTTGGGGCCCAAATTCTGCTGGTGCAGAGGCCCAACTCAGGTACCTGGATTCGGGGATCTCCGTTCCCAGCTCCCAACACTGGACAGTGCCACCTGTGCCTGCCTCCCTCGGAGCCCTGGGACCAGACCCTGGGAGTGGTCAACTTCCCC
#ERROR: Reference base(s) not correct. Is 'A', should be 'C'! - in line 169:
#chr1    45806062        12453155        A       AAAGCTTCAGAGGACTGCTCCTTCCGCCTGAACTAGCCACGAGGAGACTACAAGTTCCGTTGTACACCGCGGCTCCGGCTGCAAAAGCCTGGAGCGTTGGGTCCAGCGTACCCACAGACGACTCAGGCGGGAGACGAGCGGTGTCATGGCCGCCGACAGTGACGATGGCGCAGTTTCAGCTCCCGCAGCTTCCGACGGTGAGCGGCTTCCCAGAGGTAGCCTTCAAAGCCTCTGCGCTCTGGGAGAGGGGAAGGCCTCGGGCTCATAGTTCTAGAGGCTCCTC  .       .       seqid=12453155;gene=MUTYH;ref_transcript=NM_001128425;hgvsc=c.-137_-136insGAGGAGCCTCTAGAACTATGAGCCCGAGGCCTTCCCCTCTCCCAGAGCGCAGAGGCTTTGAAGGCTACCTCTGGGAAGCCGCTCACCGTCGGAAGCTGCGGGAGCTGAAACTGCGCCATCGTCACTGTCGGCGGCCATGACACCGCTCGTCTCCCGCCTGAGTCGTCTGTGGGTACGCTGGACCCAACGCTCCAGGCTTTTGCAGCCGGAGCCGCGGTGTACAACGGAACTTGTAGTCTCCTCGTGGCTAGTTCAGGCGGAAGGAGCAGTCCTCTGAAGCTT