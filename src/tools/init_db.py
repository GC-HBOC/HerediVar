import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.paths as paths
import gzip
import common.functions as functions

conn = Connection()

if __name__ == '__main__':
    ## initialize database structure from scheme.sql
    ## REMEMBER TO UPDATE scheme.sql if any changes happened to the database structure!
    #file = open("data/dbs/HGNC/hgnc_complete_set.tsv")
    #sql = file.read()
    #conn.cursor.execute(sql, multi=True)

    ## init gene table with info from HGNC tab
    '''
    print("initializing gene table...")
    hgnc = open(paths.hgnc_path, "r")
    header = hgnc.readline()
    for line in hgnc:
        line = line.strip().split("\t")
        hgnc_id = line[0]
        conn.insert_gene(hgnc_id = hgnc_id, symbol = line[1], name = line[2], type = line[3])

        alt_symbols = functions.collect_info('', '', line[8].strip("\""), sep = '|')
        alt_symbols = functions.collect_info(alt_symbols, '', line[10].strip("\""), sep = '|')
        alt_symbols = alt_symbols.split('|')
        
        for symbol in alt_symbols:
            if symbol != '':
                conn.insert_gene_alias(hgnc_id, symbol)

    hgnc.close()
    '''

    #conn.remove_duplicates("gene_alias", "alt_symbol")



    '''
    ## init transcripts table
    # format info:
    #The 'type' of gene features in gff3 is:
    # * "gene" for protein-coding genes
    # * "ncRNA_gene" for RNA genes
    # * "pseudogene" for pseudogenes
    #The 'type' of transcript features is:
    # * "mRNA" for protein-coding transcripts
    # * a specific type or RNA transcript such as "snoRNA" or "lnc_RNA"
    # * "pseudogenic_transcript" for pseudogenes
    #All transcripts are linked to "exon" features.
    #Protein-coding transcripts are linked to "CDS", "five_prime_UTR", and
    #"three_prime_UTR" features.

    ensembl_transcript = gzip.open(paths.ensembl_transcript_path, 'rb')
    print("initializing transcripts table...")
    for line in ensembl_transcript:
        if line.startswith('#'):
            continue

        parts = line.split('\t')
        biotype = parts[2]
        start = parts[3]
        end = parts[4]
        info = parts[8].split(';')

        name = None
        hgnc_id = None

        if biotype in ['gene', 'ncRNA_gene', 'pseudogene']:
            for info_entry in info:
                if info_entry.startswith('Name='):
                    name = info_entry[5:]
                if info_entry.startswith('description='):
                    hgnc_id = info_entry[info_entry.find('HGNC:')+5:].strip(']')
        
        if biotype in ['mRNA', 'pseudogenic_transcript'] or 'RNA' in biotype:
            pass #TODO
    '''





    
    # init annotation_type table
    #conn.insert_annotation_type("gnomad_af", "Frequency of the alternate allele in samples", "float", "v3.1.2_GRCh38", "2021-10-22") 


    conn.close()