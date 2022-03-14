import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection

conn = Connection()

if __name__ == '__main__':
    # initialize database structure from scheme.sql
    ## REMEMBER TO UPDATE scheme.sql if any changes happened to the database structure!
    #file = open("data/dbs/HGNC/hgnc_complete_set.tsv")
    #sql = file.read()
    #conn.cursor.execute(sql, multi=True)

    # init gene table with info from HGNC tab
    hgnc_path = "data/dbs/HGNC/hgnc_complete_set.tsv"
    file = open(hgnc_path, "r")
    header = file.readline()
    print("initializing gene table...")
    for line in file:
        line = line.strip().split("\t")
        #conn.insert_gene(hgnc_id = line[0], symbol = line[1], name = line[2], type = line[3])
    
    # init annotation_type table
    conn.insert_annotation_type("gnomad_af", "Frequency of the alternate allele in samples", "float", "v3.1.2_GRCh38", "2021-10-22") 


    conn.close()