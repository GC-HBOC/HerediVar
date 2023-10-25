import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import argparse
from gc import collect
from ntpath import join
import common.functions as functions
from os import listdir
from os.path import isfile, join, abspath
import gzip
import pandas as pd

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--input",  default="", help="path to input folder")
parser.add_argument("-o", "--output", default="", help="output file path. If not given will default to stdout")
#parser.add_argument("-t", "--transcripts", default="", help="The path to the ensembl gff3 file (eg. http://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.110.gff3.gz)")

args = parser.parse_args()

if args.output != "":
    sys.stdout = open(args.output, 'w')

if args.input != "":
    input_path = args.input
else:
    input_path = sys.stdin

#transcript_path = args.transcripts

info_headers = ["##INFO=<ID=BayesDEL_noAF,Number=1,Type=Float,Description=\"Missense variant functional predictions by BayesDel tool (Feng 2017) used without allele frequency. Score bigger or equal to 0.16: damaging; Score smaller than 0.16: tolerated.\">"]
functions.write_vcf_header(info_headers)


#def read_transcripts(path):
#    transcripts = []
#    with open(path, 'r') as file:
#        for line in file:
#            line = line.strip() 
#            if line.startswith('#') or line == '':
#                continue
#            
#            parts = line.split('\t')
#            biotype = parts[2]
#            chrom = parts[0]
#            start = int(parts[3])
#            end = int(parts[4])
#            orientation = parts[6]
#            info = parts[8]
#            
#            if biotype in ['gene', 'ncRNA_gene', 'pseudogene']:
#                transcript_id = functions.find_between(info, prefix="ID=gene:", postfix="(;|$)")
#                if transcript_id is None:
#                    continue
#
#                transcripts.append([transcript_id, orientation, chrom, start, end])
#    
#    result = pd.DataFrame(transcripts, columns=['transcript', 'orientation', 'chrom', 'start', 'end'])
#    return result


#transcripts = read_transcripts(transcript_path)
#functions.eprint(transcripts)

bayesdel_files = [abspath(join(input_path, f)) for f in listdir(input_path) if isfile(join(input_path, f))]


functions.eprint(len(bayesdel_files))

for bayesdel_file in bayesdel_files:
    functions.eprint(bayesdel_file)
    file=gzip.open(bayesdel_file, 'rb')
    for line in file:
        line = line.decode('utf-8')
        line = line.strip()
        
        if line.startswith('#') or line == '':
            continue
        ##CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
        parts = line.split('\t')
        chrom = parts[0]
        pos = parts[1]
        ref = parts[2]
        alt = parts[3]
        #possible_transcripts = transcripts[(transcripts['chrom'] == chrom) & (transcripts['start'] <= int(pos)) & (transcripts['end'] >= int(pos))]
        #if len(possible_transcripts) == 1 :
        #    orientation = possible_transcripts.iloc[0]['orientation']
        #    if orientation == '-':
        #        ref = functions.reverse_seq(ref)
        #        alt = functions.reverse_seq(alt)
        #        #functions.eprint("reversed: " + str(pos))
        
        vcf_parts = [chrom, pos, '.', ref, alt, '.', '.', "BayesDEL_noAF=" + str(parts[4])]
        vcf_line = '\t'.join(vcf_parts)
        print(vcf_line)


    file.close()




