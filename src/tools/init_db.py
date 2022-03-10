import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from pkgs.db_IO import Connection

conn = Connection()

if __name__ == '__main__':
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
        conn.insert_gene(hgnc_id = line[0], symbol = line[1], name = line[2], type = line[3])
    
    
    conn.close()