import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")  )
import common.functions as functions
import gffutils

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input", help="Path to input GFF3 file downloaded from RefSeq")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")

args = parser.parse_args()

# information on all chr types: https://genome.ucsc.edu/cgi-bin/hgGateway
# explain refseq accession numbers: https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
# nice little mapping table for chromosome accession numbers: https://github.com/biocommons/uta/blob/main/misc/EnsemblUTA/ensembl_90/GRCh37.90/name_to_accession.py



if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_file = open(args.input, 'r')
else:
    input_file = sys.stdin


for line in input_file:
    line = line.strip('\n')
    if line.startswith('#'):
        print(line)
        continue

    parts = line.split('\t')
    info_parts = parts[8].split(';')

    hgnc = None
    description = None
    description_id = -1
    skip = False
    for i in range(len(info_parts)):
        part = info_parts[i]

        if part.startswith('Dbxref='):
            ids = part[7:].split(',')
            for id in ids:
                if id.startswith('HGNC:'):
                    hgnc = id[5:]
        if part.startswith('description='):
            description_id = i
            description = part
        if part.startswith('gene='):
            info_parts.append('gene_id=' + part[5:])
        if part.startswith('transcript_id='):
            dot_index =  part.find('.')
            if dot_index == -1:
                functions.eprint(part)
            else:
                info_parts.append('version=' + part[dot_index+1])
                info_parts[i] = part.split('.')[0]
            info_parts.append('biotype=misc_rna')


    if hgnc is not None:
        hgnc_str = "[Source:HGNC Symbol%3BAcc:" + hgnc + "]"
        if description is not None:
            info_parts[description_id] = description + hgnc_str
        if description is None:
            info_parts.append("description=" + hgnc_str)


    parts[8] = ';'.join(info_parts)
    print('\t'.join(parts))



