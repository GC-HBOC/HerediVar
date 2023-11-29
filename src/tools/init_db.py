import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from common.db_IO import Connection
import common.paths as paths
import gzip
import common.functions as functions
import re
import xml.etree.ElementTree as ET

conn = Connection(['db_admin'])




if __name__ == '__main__':
    ## initialize database structure from scheme.sql
    ## REMEMBER TO UPDATE scheme.sql if any changes happened to the database structure!
    #file = open("data/dbs/HGNC/hgnc_complete_set.tsv")
    #sql = file.read()
    #conn.cursor.execute(sql, multi=True)

    """
    print("parsing OMIM ids...")
    omim = open(paths.omim_path, "r")
    symbol_to_omim = {}
    for line in omim:
        if line.startswith('#') or line.strip() == '':
            continue

        parts = line.split('\t')
        omim_id = parts[0]
        gene_symbol = parts[3]
        if gene_symbol is not None:
            symbol_to_omim[gene_symbol] = omim_id

    omim.close()
    """

    """
    print("parsing orphanet ids...")
    orphanet = ET.parse(paths.orphanet_path)
    root = orphanet.getroot()
    symbol_to_orphanet = {}
    duplicates = []
    for gene in root.findall(".//Gene"):
        symbols = [gene.find('Symbol').text]
        orphanet_id = gene.get('id')

        for alias in gene.findall('.//Synonym'):
            alias_symbol = alias.text
            symbols.append(alias_symbol)

        for symbol in symbols:
            if symbol in duplicates:
                continue
            if symbol in symbol_to_orphanet and symbol_to_orphanet.get(symbol) != orphanet_id:
                duplicates.append(symbol) # mark symbol to delete it later as it occurs mutliple times with different orphanet ids
            symbol_to_orphanet[symbol] = orphanet_id
        
    for symbol in set(duplicates):
        del symbol_to_orphanet[symbol]
    """
    
    """
    ## init gene table with info from HGNC tab
    print("initializing gene table...")
    hgnc = open(paths.hgnc_path, "r")
    header = hgnc.readline()
    for line in hgnc:
        line = line.strip().split("\t")
        hgnc_id = line[0]
        symbol = line[1]
        omim_id = symbol_to_omim.get(symbol) # this is save as omim also uses hgnc to extract gene symbols
        orphanet_id = symbol_to_orphanet.get(symbol)

        conn.insert_gene(hgnc_id = hgnc_id, symbol = symbol, name = line[2], type = line[3], omim_id = omim_id, orphanet_id = orphanet_id)

        alt_symbols = functions.collect_info('', '', line[8].strip("\""), sep = '|')
        alt_symbols = functions.collect_info(alt_symbols, '', line[10].strip("\""), sep = '|')
        alt_symbols = alt_symbols.split('|')
        
        for symbol in alt_symbols:
            if symbol != '':
                conn.insert_gene_alias(hgnc_id, symbol)
                #pass

    
    hgnc.close()
    conn.remove_duplicates("gene_alias", "alt_symbol")
    """




    """
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

    ## THIS INFORMATION IS NOW IN THE GFF3 FILE FROM ENSEMBL!
    ##print("parsing ensembl canonical transcripts...")
    ##ensembl_canonical_file = open(paths.ensembl_canonical_path, 'r')
    ##ensembl_canonical_transcripts = []
    ##for line in ensembl_canonical_file:
    ##    line = line.strip()
    ##    if line.startswith('#') or line == '':
    ##        continue
    ##
    ##    line = line.split('\t')
    ##
    ##    if line[2] == 'Ensembl Canonical':
    ##        enst = line[1]
    ##        if '.' in enst:
    ##            enst = enst[:enst.find('.')]
    ##        ensembl_canonical_transcripts.append(enst)
            
    
    ensembl_transcript = open(paths.ensembl_transcript_path, 'r')
    #ensembl_transcript = open("/mnt/storage2/users/ahdoebm1/HerediVar/data/dbs/ensembl/test.gff3")
    print("initializing transcripts table...")
    parent_biotype = None
    first_iter = True
    for line in ensembl_transcript:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        
        #print(line)

        parts = line.split('\t')
        chrnum = functions.validate_chr(parts[0])
        if not chrnum:
            continue
        chrom = 'chr' + chrnum
        biotype = parts[2]
        orientation = parts[6]
        start = int(parts[3])
        end = int(parts[4])
        info = parts[8]
        
        if biotype in ['gene', 'ncRNA_gene', 'pseudogene']:
            if not first_iter:
                conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, transcript_chrom, transcript_start, transcript_end, transcript_orientation, exons, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                #print("print from gene:")
                #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))

            first_iter = True
            symbol = None
            hgnc_id = None

            parent_biotype = 'gene'

            #for info_entry in info:
            #    if info_entry.startswith('Name='):
            #        symbol = info_entry[5:]
            #    if info_entry.startswith('description='):
            #        if 'HGNC:' in info_entry:
            #            hgnc_id = info_entry[info_entry.find('HGNC:')+5:].strip(']')
            #    if info_entry.startswith('ID='):
            #        gene_id = info_entry[3:]

            symbol = functions.find_between(info, 'Name=', '(;|$)')
            hgnc_id = functions.find_between(info, 'description=.*HGNC:', '(;|$|]|,)')
            gene_id = functions.find_between(info, 'ID=', '(;|$)')
        
        if (biotype in ['mRNA', 'pseudogenic_transcript', 'unconfirmed_transcript', 'V_gene_segment', 'D_gene_segment', 'J_gene_segment', 'C_gene_segment', 'transcript'] or 'RNA' in biotype) and biotype != 'ncRNA_gene':
            if not first_iter:
                conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, transcript_chrom, transcript_start, transcript_end, transcript_orientation, exons, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                #print("print from transcript:")
                #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))

            total_length = 0
            transcript_name = None
            transcript_biotype = None
            first_iter = False
            is_gencode_basic = 0
            is_ensembl_canonical = 0
            is_mane_plus_clinical = 0
            is_mane_select = 0
            transcript_chrom = chrom
            transcript_start = start
            transcript_end = end
            transcript_orientation = orientation
            first_cds = True
            exons = []

            if biotype == 'mRNA' or 'gene_segment' in biotype:
                parent_biotype = 'coding_transcript'
            else:
                parent_biotype = 'other_transcript'
            
            transcript_id = functions.find_between(info, 'ID=', '(;|$)')
            transcript_name = functions.find_between(info, 'ID=transcript:', '(\.|;|$)')
            transcript_biotype = functions.find_between(info, 'biotype=', '(;|$)')
            parent_id = functions.find_between(info, 'Parent=', '(;|$)')
            if 'tag=basic' in info:
                is_gencode_basic = 1
            if "Ensembl_canonical" in info:
                is_ensembl_canonical = 1
            if transcript_name in mane_select_transcripts:
                is_mane_select = 1
            if transcript_name in mane_plus_clinical_transcripts:
                is_mane_plus_clinical = 1

            #print(line)
            #print(transcript_name)

            #for info_entry in info:
            #    if info_entry.startswith('ID='):
            #        if '.' in info_entry: # remove version numbers and preceding transcript:
            #            info_entry = info_entry[:info_entry.find('.')]
            #        transcript_name = info_entry[info_entry.find(':')+1:]
            #    if info_entry.startswith('biotype='):
            #        transcript_biotype = info_entry[8:]
            #    if info_entry.startswith('ID='):
            #        transcript_id = info_entry[3:]
            #    if info_entry.startswith('Parent='):
            #        parent_id = info_entry[7:]
            #    if 'tag=basic' in info_entry:
            #        is_gencode_basic = 1
            
            if parent_id != gene_id:
                print("WARNING: Found transcript which does not match its current parent! (geneid: " + str(gene_id) + ", transcript id: " + str(transcript_id) + ", parent id of transcript: " + str(parent_id))
            
        if biotype in ['exon', 'CDS']:
            if parent_biotype == 'gene':
                print("WARNING: no transcripts found near line: " + line)
            is_cds = 0
            if parent_biotype == 'coding_transcript' and biotype == 'CDS':
                total_length = total_length + (end-start)
                is_cds = 1
            if parent_biotype == 'other_transcript' and biotype == 'exon':
                total_length = total_length + (end-start)
            
            exons.append([start, end, is_cds])

            parent_id = functions.find_between(info, 'Parent=', '(;|$)')
            if parent_id != transcript_id:
                print("WARNING: Found " + biotype + " which does not match its current parent! (transcript id: " + str(transcript_id) + ", parent id of " + biotype + ": " + str(parent_id))
    
    #print("last print:")
    #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
    conn.insert_transcript(symbol, hgnc_id, transcript_name, transcript_biotype, total_length, transcript_chrom, transcript_start, transcript_end, transcript_orientation, exons,  is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)

    ensembl_transcript.close()
    
    

    
    print("parsing refseq ensembl identifier table...")
    refseq_to_ensembl = functions.get_refseq_to_ensembl_transcript_dict()

    is_gencode_basic = 0
    is_mane_select = 0
    is_mane_plus_clinical = 0
    is_ensembl_canonical = 0
    keep_it = True # this flag filters nested transcripts where the parent is a transcript itself
    parent_biotype = None
    first_iter = True

    refseq_transcript = gzip.open(paths.refseq_transcript_path, "rb")
    #refseq_transcript = open("/mnt/storage2/users/ahdoebm1/HerediVar/data/dbs/RefSeq/test.gff3", "r")
    # what is being skipped from the gff files:
    # - any 'match' records
    # - silencer & enhancer & promoter regions, basically any features which conatin or come from 'region' entries
    # - any products of primary transcripts (eg. miRNAs)
    # - additional (misc) sequence features
    print("parsing refseq transcripts...")
    refseq2chrnum = functions.get_refseq_chom_to_chrnum()
    for line in refseq_transcript:
        line = line.decode('utf8')
        line = line.strip()
        if line.startswith('#') or line == '':
            continue

        #print(line)

        parts = line.split('\t')
        chrom = refseq2chrnum.get(parts[0])
        biotype = parts[2]
        orientation = parts[6]
        start = int(parts[3])
        end = int(parts[4])
        info = parts[8]

        if chrom is None: # skip all scaffolds (eg. NT_, NW)
            continue
        
        if biotype in ['gene', 'pseudogene']:
            if not first_iter:
                if keep_it:
                    conn.insert_transcript(symbol, hgnc_id, refseq_to_ensembl.get(transcript_name, None), transcript_biotype, total_length, transcript_chrom, transcript_start, transcript_end, transcript_orientation, exons, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, transcript_name)
                    #print("print from gene:")
                    #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
                    #pass
                keep_it = True

            first_iter = True
            symbol = None
            hgnc_id = None
            gene_id = None

            parent_biotype = 'gene'

            #for info_entry in info:
            #    if info_entry.startswith('Name='):
            #        symbol = info_entry[5:]
            #    if info_entry.startswith('Dbxref='):
            #        if 'HGNC:' in info_entry:
            #            hgnc_id = functions.find_between(info_entry, 'HGNC:', '(,|$)')
            #            if ':' in hgnc_id:
            #                hgnc_id = hgnc_id[hgnc_id.rfind(':')+1:]
            #    if info_entry.startswith('ID='):
            #        gene_id = info_entry[3:]

            symbol = functions.find_between(info, 'Name=', '(,|$)')
            hgnc_id = functions.find_between(info, 'Dbxref=', '(;|$|])')
            if hgnc_id is not None:
                hgnc_id = functions.find_between(hgnc_id, 'HGNC:', '(,|;|$)')
                if hgnc_id is not None:
                    if ':' in hgnc_id:
                        hgnc_id = hgnc_id[hgnc_id.rfind(':')+1:]
            gene_id = functions.find_between(info, 'ID=', '(;|$)')
        
        elif (biotype in ['mRNA', 'V_gene_segment', 'D_gene_segment', 'J_gene_segment', 'C_gene_segment', 'transcript', 'primary_transcript', 'transcript'] or 'RNA' in biotype):
            parent_id = functions.find_between(info, 'Parent=', '(;|$)')
            if 'gene' in parent_id:
                if not first_iter:
                    if keep_it:
                        conn.insert_transcript(symbol, hgnc_id, refseq_to_ensembl.get(transcript_name, None), transcript_biotype, total_length, transcript_chrom, transcript_start, transcript_end, transcript_orientation, exons, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, transcript_name)
                        #print("print from transcript:")
                        #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
                        #pass
                    keep_it = True

                total_length = 0
                transcript_name = None
                transcript_biotype = None
                first_iter = False
                transcript_id = None
                transcript_chrom = chrom
                transcript_start = start
                transcript_end = end
                transcript_orientation = orientation
                first_cds = True

                if biotype == 'mRNA' or 'gene_segment' in biotype:
                    parent_biotype = 'coding_transcript'
                else:
                    parent_biotype = 'other_transcript'

                transcript_id = functions.find_between(info, 'ID=', '(;|$)')
                transcript_name = functions.find_between(info, 'Dbxref=', '(;|$)')
                if transcript_name is not None:
                    transcript_name = functions.find_between(transcript_name, 'Genbank:', '(\.|,|;|$)')
                    if transcript_name is not None and ':' in transcript_name:
                        transcript_name = transcript_name[transcript_name.rfind(':')+1:]
                transcript_biotype = functions.find_between(info, 'gbkey=', '(;|$)')
                
                #if refseq_to_ensembl.get(transcript_name) is not None:
                #    print(transcript_name + ":" + refseq_to_ensembl.get(transcript_name))
            

                if parent_id != gene_id:
                    print("WARNING: Found transcript which does not match its current parent! (geneid: " + str(gene_id) + ", transcript id: " + str(transcript_id) + ", parent id of transcript: " + str(parent_id))
                    keep_it = False
            
        elif biotype in ['exon', 'CDS']:
            if parent_biotype == 'gene':
                print("WARNING: no transcripts found near line: " + line)

            parent_id = functions.find_between(info, 'Parent=', '(;|$)')
            if parent_id == transcript_id:
                if parent_biotype == 'coding_transcript' and biotype == 'CDS':
                    total_length = total_length + (end-start)
                if parent_biotype == 'other_transcript' and biotype == 'exon':
                    total_length = total_length + (end-start)
                
                #print("WARNING: Found " + biotype + " which does not match its current parent! (transcript id: " + str(transcript_id) + ", parent id of " + biotype + ": " + str(parent_id))
    
    if keep_it:
        #print("last print:")
        #print("Symbol: " + str(symbol) + ", hgnc_id: " + str(hgnc_id) + ", transcript name: " + str(transcript_name) + ", transcript_biotype: " + str(transcript_biotype) + ", length: " + str(total_length))
        conn.insert_transcript(symbol, hgnc_id, refseq_to_ensembl.get(transcript_name, None), transcript_biotype, total_length, transcript_chrom, transcript_start, transcript_end, transcript_orientation, exons, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, transcript_name)
        #pass

    refseq_transcript.close()
    """

    """
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
    """
    
    
    # init annotation_type table
    #conn.insert_annotation_type("gnomad_af", "Frequency of the alternate allele in samples", "float", "v3.1.2_GRCh38", "2021-10-22") 
    

    
    ## init VUS task force protein domains table (no download for this one, it was sent by mail)
    print("initializing VUS-Task-Force protein domain table")
    task_force_protein_domains_file = open(paths.task_force_protein_domains_path)
    for line in task_force_protein_domains_file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue

        parts = line.split('\t')

        description = parts[1].strip('\"')
        chromosome = parts[2]
        chr_num = functions.validate_chr(chromosome)
        if not chr_num:
            print('skipping protein domain because of unsupported chromosome')
            continue
        chromosome = 'chr' + chr_num
        start = parts[3]
        end = parts[4]
        if end < start:
            temp = end
            end = start
            start = temp
        source = parts[7].strip('\"')

        gene_id = conn.get_gene_id_by_symbol(parts[0])

        conn.insert_task_force_protein_domain(gene_id, chromosome, start, end, description, source)
    


    conn.close()


