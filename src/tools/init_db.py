import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.paths as paths
import gzip
import common.functions as functions
import re

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
    '''
    print("parsing MANE transcripts...")
    mane_file = open(paths.MANE_path, 'r')
    mane_select_transcripts = []
    mane_plus_clinical_transcripts = []
    for line in mane_file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        
        line = line.split('\t')
        info = line[8]

        if line[2] == 'transcript' and 'MANE_Select' in info:
            enst = re.search('ID=[^;]*', info)
            enst = enst.group(0)
            if '.' in enst:
                enst = enst[3:enst.find('.')]
            mane_select_transcripts.append(enst)
        
        if line[2] == 'transcript' and 'MANE_Plus_Clinical' in info:
            enst = re.search('ID=[^;]*', info)
            enst = enst.group(0)
            if '.' in enst:
                enst = enst[3:enst.find('.')]
            mane_plus_clinical_transcripts.append(enst)

    print("parsing ensembl canonical transcripts...")
    ensembl_canonical_file = open(paths.ensembl_canonical_path, 'r')
    ensembl_canonical_transcripts = []
    for line in ensembl_canonical_file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue

        line = line.split('\t')

        if line[2] == 'Ensembl Canonical':
            enst = line[1]
            if '.' in enst:
                enst = enst[:enst.find('.')]
            ensembl_canonical_transcripts.append(enst)
            
    ensembl_transcript = open(paths.ensembl_transcript_path, 'r')
    #ensembl_transcript = open("/mnt/users/ahdoebm1/HerediVar/data/dbs/ensembl/test.gff3")
    print("initializing transcripts table...")
    parent_biotype = None
    first_iter = True
    for line in ensembl_transcript:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue

        parts = line.split('\t')
        biotype = parts[2]
        start = int(parts[3])
        end = int(parts[4])
        info = parts[8]

        #biotype_aggregated = re.search('ID=[^:]*', info)
        #if biotype_aggregated is not None:
        #    print(biotype_aggregated.group(0))

        info = info.split(';')
        
        if biotype in ['gene', 'ncRNA_gene', 'pseudogene']:
            if not first_iter:
                conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                #print("print from gene:")
                #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))

            first_iter = True
            symbol = None
            hgnc_id = None

            parent_biotype = 'gene'

            for info_entry in info:
                if info_entry.startswith('Name='):
                    symbol = info_entry[5:]
                if info_entry.startswith('description='):
                    if 'HGNC:' in info_entry:
                        hgnc_id = info_entry[info_entry.find('HGNC:')+5:].strip(']')
                if info_entry.startswith('ID='):
                    gene_id = info_entry[3:]
        
        if (biotype in ['mRNA', 'pseudogenic_transcript', 'unconfirmed_transcript', 'V_gene_segment', 'D_gene_segment', 'J_gene_segment', 'C_gene_segment'] or 'RNA' in biotype) and biotype != 'ncRNA_gene':
            if not first_iter:
                conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                #print("print from transcript:")
                #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))

            total_length = 0
            transcript_name = None
            transcript_biotype = None
            first_iter = False
            is_gencode_basic = 0

            if biotype == 'mRNA' or 'gene_segment' in biotype:
                parent_biotype = 'coding_transcript'
            else:
                parent_biotype = 'other_transcript'

            for info_entry in info:
                if info_entry.startswith('ID='):
                    if '.' in info_entry: # remove version numbers and preceding transcript:
                        info_entry = info_entry[:info_entry.find('.')]
                    transcript_name = info_entry[info_entry.find(':')+1:]
                if info_entry.startswith('biotype='):
                    transcript_biotype = info_entry[8:]
                if info_entry.startswith('ID='):
                    transcript_id = info_entry[3:]
                if info_entry.startswith('Parent='):
                    parent_id = info_entry[7:]
                if 'tag=basic' in info_entry:
                    is_gencode_basic = 1
            
            is_mane_select = 0
            if transcript_name in mane_select_transcripts:
                is_mane_select = 1
            is_mane_plus_clinical = 0
            if transcript_name in mane_plus_clinical_transcripts:
                is_mane_plus_clinical = 1
            is_ensembl_canonical = 0
            if transcript_name in ensembl_canonical_transcripts:
                is_ensembl_canonical = 1
            
            if parent_id != gene_id:
                print("WARNING: Found transcript which does not match its current parent! (geneid: " + str(gene_id) + ", transcript id: " + str(transcript_id) + ", parent id of transcript: " + str(parent_id))
            
        if biotype in ['exon', 'CDS']:
            if parent_biotype == 'gene':
                print("WARNING: no transcripts found near line: " + line)
            if parent_biotype == 'coding_transcript' and biotype == 'CDS':
                total_length = total_length + (end-start)
            if parent_biotype == 'other_transcript' and biotype == 'exon':
                total_length = total_length + (end-start)

            for info_entry in info:
                if info_entry.startswith('Parent='):
                    parent_id = info_entry[7:]
            if parent_id != transcript_id:
                print("WARNING: Found " + biotype + " which does not match its current parent! (transcript id: " + str(transcript_id) + ", parent id of " + biotype + ": " + str(parent_id))
    
    #print("last print:")
    #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
    conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
    

    ensembl_transcript.close()
    '''

    is_gencode_basic = 0
    is_mane_select = 0
    is_mane_plus_clinical = 0
    is_ensembl_canonical = 0
    keep_it = True # this flag filters nested transcripts where the parent is a transcript itself

    #refseq_transcript = gzip.open(paths.refseq_transcript_path, "rb")
    refseq_transcript = open("/mnt/users/ahdoebm1/HerediVar/data/dbs/RefSeq/test", "r")
    print("parsing refseq transcripts...")
    parent_biotype = None
    first_iter = True
    for line in refseq_transcript:
        #line = line.decode('utf8')
        line = line.strip()
        print(keep_it)
        if line.startswith('#') or line == '':
            continue

        parts = line.split('\t')
        biotype = parts[2]
        start = int(parts[3])
        end = int(parts[4])
        info = parts[8].split(';')
        
        if 'gene' in biotype:
            if not first_iter:
                if keep_it:
                    #conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                    #print("print from gene:")
                    print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
                keep_it = True

            first_iter = True
            symbol = None
            hgnc_id = None
            gene_id = None

            parent_biotype = 'gene'

            for info_entry in info:
                if info_entry.startswith('Name='):
                    symbol = info_entry[5:]
                if info_entry.startswith('Dbxref='):
                    if 'HGNC:' in info_entry:
                        hgnc_id = functions.find_between(info_entry, 'HGNC:', '(,|$)')
                        if ':' in hgnc_id:
                            hgnc_id = hgnc_id[hgnc_id.rfind(':')+1:]
                if info_entry.startswith('ID='):
                    gene_id = info_entry[3:]
        
        elif (biotype in ['mRNA', 'V_gene_segment', 'D_gene_segment', 'J_gene_segment', 'C_gene_segment'] or 'transcript' in biotype or 'RNA' in biotype):
            if not first_iter:
                if keep_it:
                    #conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                    #print("print from transcript:")
                    print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
                keep_it = True

            total_length = 0
            transcript_name = None
            transcript_biotype = None
            first_iter = False
            transcript_id = None

            if biotype == 'mRNA' or 'gene_segment' in biotype:
                parent_biotype = 'coding_transcript'
            else:
                parent_biotype = 'other_transcript'

            for info_entry in info:
                if info_entry.startswith('Dbxref='): # example of such an entry: "Dbxref=GeneID:81399,Genbank:XM_017002409.2,HGNC:HGNC:15079"
                    transcript_name =  functions.find_between(info_entry, 'Genbank:', '(,|$)')
                    if transcript_name is not None:
                        if '.' in transcript_name:
                            transcript_name = transcript_name[:transcript_name.find('.')] # remove version numbers
                if info_entry.startswith('gbkey='):
                    transcript_biotype = info_entry[6:]
                if info_entry.startswith('Parent='):
                    parent_id = info_entry[7:]
                if info_entry.startswith('ID='):
                    transcript_id = info_entry[3:]
            

            if parent_id != gene_id:
                print("WARNING: Found transcript which does not match its current parent! (geneid: " + str(gene_id) + ", transcript id: " + str(transcript_id) + ", parent id of transcript: " + str(parent_id))
                keep_it = False
            
        elif biotype in ['exon', 'CDS']:
            if parent_biotype == 'gene':
                print("WARNING: no transcripts found near line: " + line)
            if parent_biotype == 'coding_transcript' and biotype == 'CDS':
                total_length = total_length + (end-start)
            if parent_biotype == 'other_transcript' and biotype == 'exon':
                total_length = total_length + (end-start)

            for info_entry in info:
                if info_entry.startswith('Parent='):
                    parent_id = info_entry[7:]
            if parent_id != transcript_id:
                print("WARNING: Found " + biotype + " which does not match its current parent! (transcript id: " + str(transcript_id) + ", parent id of " + biotype + ": " + str(parent_id))
    
    if keep_it:
        print("last print:")
        print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
        #conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
    

    refseq_transcript.close()

    
    '''
    ## init pfam auxiliaries tables (pfam_id_mapping and pfam_legacy)
    print("initializing PFAM id mapping table...")
    pfam_id_mapping_file = open(paths.pfam_id_mapping_path, 'r')
    for line in pfam_id_mapping_file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        
        parts = line.split('\t')
        conn.insert_pfam_id_mapping(parts[0], parts[1])
    
    pfam_id_mapping_file.close()
    
    print("inititalizing PFAM legacy table...")
    pfam_legacy_file = open(paths.pfam_legacy_path, 'r')
    for line in pfam_legacy_file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        
        parts = line.split('\t')
        conn.insert_pfam_legacy(parts[0], parts[1])
    
    pfam_legacy_file.close()
    
    
    # init annotation_type table
    #conn.insert_annotation_type("gnomad_af", "Frequency of the alternate allele in samples", "float", "v3.1.2_GRCh38", "2021-10-22") 
    '''

    conn.close()


