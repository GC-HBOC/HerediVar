from logging import raiseExceptions
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import mysql.connector
from mysql.connector import Error
import common.functions as functions
from operator import itemgetter
import datetime
import re


def get_db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(user='ahdoebm1', password='20220303',
                                       host='SRV011.img.med.uni-tuebingen.de',
                                       database='HerediVar_ahdoebm1', 
                                       charset = 'utf8')
    except Error as e:
        print("Error while connecting to DB", e)
    finally:
        if conn is not None and conn.is_connected():
            return conn


def enquote(string):
    string = str(string).strip("'") # remove quotes if the input string is already quoted!
    return "'" + string + "'"


class Connection:
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        self.set_connection_encoding()


    def set_connection_encoding(self):
        self.cursor.execute("SET NAMES 'utf8'")
        self.cursor.execute("SET CHARACTER SET utf8")
        self.cursor.execute('SET character_set_connection=utf8;')


    # This function removes ALL occurances of duplicated items
    def remove_duplicates(self, table, unique_column):
        command = "DELETE FROM " + table + " WHERE " + unique_column + " IN (SELECT * FROM (SELECT " + unique_column + " FROM " + table + " GROUP BY " + unique_column + " HAVING (COUNT(*) > 1)) AS A)"
        self.cursor.execute(command)
        self.conn.commit()
    

    def get_one_variant(self, variant_id):
        self.cursor.execute("SELECT id,chr,pos,ref,alt FROM variant WHERE id =" + str(variant_id))
        result = self.cursor.fetchone()
        return result
    
    def get_variant_id(self, chr, pos, ref, alt):
        self.cursor.execute("SELECT id FROM variant WHERE chr = " + enquote(chr) + " AND pos = " + str(pos) + " AND ref = " + enquote(ref) + " AND alt = " + enquote(alt))
        variant_id = self.cursor.fetchone()
        if variant_id is not None:
            return variant_id[0]
        return None
    
    def get_gene_id_by_hgnc_id(self, hgnc_id):
        hgnc_id = functions.trim_hgnc(hgnc_id)
        self.cursor.execute("SELECT id FROM gene WHERE hgnc_id = " + enquote(hgnc_id))
        result = self.cursor.fetchall()
        if len(result) > 1:
            print("WARNING: there were multiple gene ids for hgnc id " + str(hgnc_id))
        if len(result) == 0:
            return None
        return result[0][0] # subset the result as fetching only one column still returns a tuple!

    def close(self):
        self.conn.close()
        self.cursor.close()

    def get_pending_requests(self):
        self.cursor.execute("SELECT id,variant_id FROM annotation_queue WHERE status = 'pending'")
        pending_variant_ids = self.cursor.fetchall()
        return pending_variant_ids

    def update_annotation_queue(self, row_id, status, error_msg):
        error_msg = enquote(error_msg.replace("\n", " "))
        status = enquote(status)
        #print("UPDATE annotation_queue SET status = " + status + ", finished_at = " + time.strftime('%Y-%m-%d %H:%M:%S') + ", error_message = " + error_msg + " WHERE id = " + str(row_id))
        self.cursor.execute("UPDATE annotation_queue SET status = " + status + ", finished_at = NOW(), error_message = " + error_msg + " WHERE id = " + str(row_id))
        self.conn.commit()

    def get_current_annotation_status(self, variant_id):
        # return the most recent annotation queue entry for the variant 
        self.cursor.execute("SELECT * FROM annotation_queue WHERE variant_id = %s ORDER BY requested DESC LIMIT 1" % (enquote(variant_id)))
        result = self.cursor.fetchone()
        return result

    def get_pfam_description_by_pfam_acc(self, pfam_acc):
        pfam_acc = functions.remove_version_num(pfam_acc)
        orig_pfam_acc = pfam_acc
        found_description = False
        
        while not found_description:
            command = "SELECT accession_id,description FROM pfam_id_mapping WHERE accession_id = " + enquote(pfam_acc)
            self.cursor.execute(command)
            pfam_description = self.cursor.fetchone()
            if pfam_description is None:
                command = "SELECT old_accession_id,new_accession_id FROM pfam_legacy WHERE old_accession_id = " + enquote(pfam_acc)
                self.cursor.execute(command)
                pfam_description = self.cursor.fetchone()
                if pfam_description is not None:
                    if pfam_description[1] == 'removed':
                        found_description = True
                    else:
                        pfam_acc = pfam_description[1]
                else:
                    found_description = True
            else:
                found_description = True
        if pfam_description is None:
            print("WARNING: there was no description for pfam accession id: " + orig_pfam_acc)
            return None, None
        else:
            return pfam_description[0], pfam_description[1]

    def insert_variant_consequence(self, variant_id, transcript_name, hgvs_c, hgvs_p, consequence, impact, exon_nr, intron_nr, hgnc_id, symbol, consequence_source, pfam_acc):
        columns_with_info = "variant_id, transcript_name, consequence, impact, source"
        actual_information = (variant_id, transcript_name, consequence, impact, consequence_source)
        if pfam_acc != '':
            pfam_acc, domain_description = self.get_pfam_description_by_pfam_acc(pfam_acc)
            if domain_description is not None and pfam_acc is not None and domain_description != 'removed':
                columns_with_info = columns_with_info + ", pfam_accession, pfam_description"
                actual_information = actual_information + (pfam_acc, domain_description)
        if hgvs_c != '':
            columns_with_info = columns_with_info + ", hgvs_c"
            actual_information = actual_information + (hgvs_c,)
        if hgvs_p != '':
            columns_with_info = columns_with_info + ", hgvs_p"
            actual_information = actual_information + (hgvs_p,)
        if exon_nr != '':
            columns_with_info = columns_with_info + ", exon_nr"
            actual_information = actual_information + (exon_nr,)
        if intron_nr != '':
            columns_with_info = columns_with_info + ", intron_nr"
            actual_information = actual_information + (intron_nr,)
        if hgnc_id != '':
            gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)
            if gene_id is not None:
                columns_with_info = columns_with_info + ", gene_id"
                actual_information = actual_information + (gene_id,)
            else:
                print("WARNING: there was no row in the gene table for hgnc_id " + str(hgnc_id) + ". geneid will be empty even though hgncid was given. Error occured during insertion of variant consequence: " + str(variant_id) + ", " + str(transcript_name) + ", " + str(hgvs_c) + ", " +str(hgvs_p) + ", " +str(consequence) + ", " + str(impact) + ", " + str(exon_nr) + ", " + str(intron_nr) + ", " + str(hgnc_id) + ", " + str(symbol) + ", " + str(consequence_source))
        elif symbol != '':
            gene_id = self.get_gene_id_by_symbol(symbol)
            if gene_id is not None:
                columns_with_info = columns_with_info + ", gene_id"
                actual_information = actual_information + (gene_id,)
            else:
                print("WARNING: there was no row in the gene table for symbol " + str(symbol) + ". geneid will be empty even though symbol was given. Error occured during insertion of variant consequence: " + str(variant_id) + ", " + str(transcript_name) + ", " + str(hgvs_c) + ", " +str(hgvs_p) + ", " +str(consequence) + ", " + str(impact) + ", " + str(exon_nr) + ", " + str(intron_nr) + ", " + str(hgnc_id) + ", " + str(symbol) + ", " + str(consequence_source))
        placeholders = "%s, "*len(actual_information)
        command = "INSERT INTO variant_consequence (" + columns_with_info + ") VALUES (" + placeholders[:len(placeholders)-2] + ")"
        #print(command)
        self.cursor.execute(command, actual_information)
        self.conn.commit()

    def get_gene_id_by_symbol(self, symbol):
        command = "SELECT id,symbol FROM gene WHERE symbol=" + enquote(symbol)
        self.cursor.execute(command)
        res = self.cursor.fetchone()
        if res is None:
            self.cursor.execute("SELECT gene_id,alt_symbol FROM gene_alias WHERE alt_symbol=" + enquote(symbol))
            res = self.cursor.fetchone() # ! each symbol is only contained once and all duplicates were removed
        if res is not None:
            gene_id = res[0]
            return gene_id
        else:
            return None


    def insert_gene(self, hgnc_id, symbol, name, type, omim_id, orphanet_id):
        hgnc_id = functions.trim_hgnc(hgnc_id)
        columns_with_info = "hgnc_id, symbol, name, type"
        actual_information = (hgnc_id, symbol, name, type)
        if omim_id != '' and omim_id is not None:
            columns_with_info = columns_with_info + ", omim_id"
            actual_information = actual_information + (omim_id, )
        if orphanet_id != '' and orphanet_id is not None:
            columns_with_info = columns_with_info + ", orphanet_id"
            actual_information = actual_information + (orphanet_id, )
        
        placeholders = "%s, "*len(actual_information)
        command = "INSERT INTO gene (" + columns_with_info + ") VALUES (" + placeholders[:len(placeholders)-2] + ")"
        self.cursor.execute(command, actual_information)
        self.conn.commit()
    

    def insert_gene_alias(self, hgnc_id, symbol):
        gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)
        if gene_id is not None:
            self.cursor.execute("INSERT INTO gene_alias (gene_id, alt_symbol) VALUES (%s, %s)",
                            (gene_id, symbol))
            self.conn.commit()
        else:
            print("WARNING: there was no row in the gene table for hgnc_id " + str(hgnc_id) + ". Error occured during insertion of gene alias " + str(symbol))


    def insert_annotation_type(self, name, description, value_type, version, version_date):
        command = "SELECT id FROM annotation_type WHERE name =" + enquote(name) + " AND version = " + enquote(version) + " AND version_date = " + enquote(version_date)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        if len(result) == 0:
            command = "INSERT INTO annotation_type (name, description, value_type, version, version_date) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(command, (name, description, value_type, version, version_date))
            self.conn.commit()
    
    def insert_variant_annotation(self, variant_id, annotation_type_id, value, supplementary_document = None):
        # supplementary documents are not supported yet! see: https://stackoverflow.com/questions/10729824/how-to-insert-blob-and-clob-files-in-mysql
        command = "INSERT INTO variant_annotation (variant_id, annotation_type_id, value) VALUES (%s, %s, %s)"
        self.cursor.execute(command, (variant_id, annotation_type_id, value))
        self.conn.commit()

    def insert_variants_from_vcf(self, path):
        variants = functions.read_variants(path)

        for variant in variants:
            chr = variant.CHROM
            pos = variant.POS
            ref = variant.REF
            alt = variant.ALT
            self.cursor().execute("INSERT INTO variant (chr, pos, ref, alt) VALUES (%s, %s, %s, %s)",
                                  (chr, pos, ref, alt))
        self.conn.commit()
    
    def insert_variant(self, chr, pos, ref, alt):
        ref = ref.upper()
        alt = alt.upper()
        self.cursor.execute("INSERT INTO variant (chr, pos, ref, alt) VALUES (%s, %s, %s, %s)",
                         (chr, pos, ref, alt))
        self.conn.commit()
    
    def insert_annotation_request(self, variant_id, user_id):
        command = "INSERT INTO annotation_queue (variant_id, status, user_id) VALUES (%s, %s, %s)"
        self.cursor.execute(command, (variant_id, "pending", user_id))
        self.conn.commit()
    
    def insert_clinvar_variant_annotation(self, variant_id, variation_id, interpretation, review_status, version_date):
        command = "INSERT INTO clinvar_variant_annotation (variant_id, variation_id, interpretation, review_status, version_date) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, variation_id, interpretation, review_status, version_date))
        self.conn.commit()

    def insert_clinvar_submission(self, clinvar_variant_annotation_id, interpretation, last_evaluated, review_status, condition, submitter, comment):
        columns_with_info = "clinvar_variant_annotation_id, interpretation, review_status, submission_condition, submitter"
        actual_information = (clinvar_variant_annotation_id, interpretation, review_status, condition, submitter)
        if (comment != '' and comment != '-'):
            columns_with_info = columns_with_info + ", comment"
            actual_information = actual_information + (comment,)
        if (last_evaluated != '' and last_evaluated != '-'):
            columns_with_info = columns_with_info + ", last_evaluated"
            actual_information = actual_information + (last_evaluated,)
        placeholders = "%s, "*len(actual_information)
        command = "INSERT INTO clinvar_submission (" + columns_with_info + ") VALUES (" + placeholders[:len(placeholders)-2] + ")"
        self.cursor.execute(command, actual_information)
        self.conn.commit()

    def get_clinvar_variant_annotation_id_by_variant_id(self, variant_id):
        command = "SELECT a.id,a.variant_id,a.version_date \
                    FROM clinvar_variant_annotation a \
                    INNER JOIN ( \
                        SELECT variant_id, max(version_date) AS version_date FROM clinvar_variant_annotation GROUP BY variant_id \
                    ) b ON a.variant_id = b.variant_id AND a.variant_id = " + enquote(variant_id) + " AND a.version_date = b.version_date"
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        else:
            return False
    

    def insert_transcript(self, symbol, hgnc_id, transcript_ensembl, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, transcript_refseq = None):
        if transcript_ensembl is None and transcript_refseq is None: # abort if the transcript name is missing!
            return
        
        # get the gene for the current transcript
        gene_id = None
        transcript_biotype = transcript_biotype.replace('_', ' ')
        if symbol is None and hgnc_id is None:
            print("WARNING: transcript: " + str(transcript_ensembl) + ", transcript_biotype: " + transcript_biotype + " was not imported as gene symbol and hgnc id were missing")
            return
        if hgnc_id is not None:
            gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)
        elif symbol is not None:
            gene_id = self.get_gene_id_by_symbol(symbol)
        
        # insert transcript
        if gene_id is not None:
            command = ''
            if transcript_refseq is not None and transcript_ensembl is not None:
                self.cursor.execute("SELECT COUNT(*) FROM transcript WHERE name=" + enquote(transcript_ensembl))
                has_ensembl = self.cursor.fetchone()[0]
                if has_ensembl:
                    # The command inserts a new refseq transcript while it searches for a matching ensembl transcripts (which should already be contained in the transcripts table) and copies their gencode, mane and canonical flags
                    infos = (int(gene_id), enquote(transcript_refseq), enquote(transcript_biotype), int(total_length), enquote(transcript_ensembl))
                    command = "INSERT INTO transcript (gene_id, name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) \
	                                    (SELECT %d, %s, %s, %d, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical FROM transcript WHERE name = %s);"  % infos
            if command == '':
                if transcript_refseq is not None:
                    transcript_name = transcript_refseq
                else:
                    transcript_name = transcript_ensembl
                command = "INSERT INTO transcript (gene_id, name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) VALUES (%d, %s, %s, %d, %d, %d, %d, %d)" % (int(gene_id), enquote(transcript_name), enquote(transcript_biotype), int(total_length), int(is_gencode_basic), int(is_mane_select), int(is_mane_plus_clinical), int(is_ensembl_canonical))
            
            self.cursor.execute(command)
            self.conn.commit()
        else:
            print("WARNING: transcript: " + str(transcript_ensembl) + "/" + str(transcript_refseq) + ", transcript_biotype: " + transcript_biotype + " was not imported as the corresponding gene is not in the database (gene-table) " + "hgncid: " + str(hgnc_id) + ", gene symbol: " + str(symbol))

    def insert_pfam_id_mapping(self, accession_id, description):
        # remove version numbers first
        accession_id = functions.remove_version_num(accession_id)
        command = "INSERT INTO pfam_id_mapping (accession_id, description) VALUES (%s, %s)"
        self.cursor.execute(command, (accession_id, description))
        self.conn.commit()
       
       
    def insert_pfam_legacy(self, old_accession_id, new_accession_id):
        #remove version numbers first
        old_accession_id = functions.remove_version_num(old_accession_id)
        new_accession_id = functions.remove_version_num(new_accession_id)
        command = "INSERT INTO pfam_legacy (old_accession_id, new_accession_id) VALUES (%s, %s)"
        self.cursor.execute(command, (old_accession_id, new_accession_id))
        self.conn.commit()
    
    def insert_variant_literature(self, variant_id, pmid, title, authors, journal, year):
        command = "INSERT INTO variant_literature (variant_id, pmid, title, authors, journal_publisher, year) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, pmid, title, authors, journal, year))
        self.conn.commit()

    
    def get_recent_annotations(self, variant_id): # ! the ordering of the columns in the outer select statement is important and should not be changed
        command = "SELECT title, description, version, version_date, variant_id, value, supplementary_document FROM variant_annotation INNER JOIN ( \
                        SELECT * \
	                        FROM annotation_type WHERE (title, version_date) IN ( \
		                        select title, MAX(version_date) version_date from annotation_type INNER JOIN ( \
				                    select variant_id, annotation_type_id, value, supplementary_document from variant_annotation where variant_id=%d \
			                ) x \
			                ON annotation_type.id = x.annotation_type_id \
		                    GROUP BY title \
	                    )  \
                    ) y  \
                    ON y.id = variant_annotation.annotation_type_id \
                    WHERE variant_id=%d" % (variant_id, variant_id)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result
    

    # functions specific for frontend!
    def get_paginated_variants(self, page, page_size, query_type = '', query = ''):
        offset = (page - 1) * page_size
        result = []
        num_variants = 0
        if query == '' or query is None:
            self.cursor.execute(
                "SELECT id,chr,pos,ref,alt FROM variant ORDER BY chr, pos, ref, alt LIMIT %d, %d"
                % (offset, page_size)
            )  
            result = self.cursor.fetchall()

            self.cursor.execute("SELECT COUNT(id) FROM variant")
            num_variants = self.cursor.fetchone()
            num_variants = num_variants[0]
        else:
            if query_type == 'standard':
                result, num_variants = self.standard_search(query, offset, page_size)
            elif query_type == 'hgvs':
                result, num_variants = self.hgvs_search(query)
            elif query_type == 'range':
                result, num_variants = self.range_search(query, offset, page_size)
            elif query_type == 'gene':
                result, num_variants = self.gene_search(query, offset, page_size)

        return result, num_variants
    
    def gene_search(self, query, offset, page_size): # example: 'BARD1%gene%' (this also works with gene aliases and hgnc ids)
        gene_id = self.get_gene_id_by_symbol(query)
        if gene_id is None:
            gene_id = self.get_gene_id_by_hgnc_id(query)
        command = "SELECT DISTINCT variant_id FROM variant_consequence WHERE gene_id=" + enquote(gene_id)
        self.cursor.execute(command)
        variant_ids = self.cursor.fetchall()
        variant_ids = [x[0] for x in variant_ids]
        if len(variant_ids) == 0:
            return [], 0

        num_variants = len(variant_ids)

        variant_ids_string = str(variant_ids).replace('[', '(').replace(']', ')')
        command = "SELECT id,chr,pos,ref,alt FROM variant WHERE id IN " + variant_ids_string + " LIMIT %d, %d" % (offset, page_size)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result, num_variants

    def range_search(self, query, offset, page_size): # example: 'chr2:214767531-214780740'
        parts = query.split(':')
        chr = parts[0]
        positions = parts[1].split('-')
        start = int(positions[0])
        end = int(positions[1])
        command = "SELECT id,chr,pos,ref,alt FROM variant WHERE chr=%s AND pos BETWEEN %d AND %d LIMIT %d, %d" % (enquote(chr), start, end, offset, page_size)        
        self.cursor.execute(command)
        result = self.cursor.fetchall()

        self.cursor.execute("SELECT COUNT(id) FROM variant WHERE chr=%s AND pos BETWEEN %d AND %d" % (enquote(chr), start, end))
        num_variants = self.cursor.fetchone()
        num_variants = num_variants[0]
        return result, num_variants

    def hgvs_search(self, query): # example: 'ENST00000260947:c.1972C>T'
        reference_transcript, hgvs = functions.split_hgvs(query)
        variant_id = self.get_variant_id_by_hgvs(reference_transcript, hgvs)
        result = []
        if variant_id is not None:
            command = "SELECT id,chr,pos,ref,alt FROM variant WHERE id=%s" % (enquote(variant_id))
            self.cursor.execute(command)
            result = [self.cursor.fetchone()] # list is required for the eazy iteration in frontend
        return result, len(result)

    def standard_search(self, query, offset, page_size):
        query = enquote(query)
        command = "SELECT id,chr,pos,ref,alt FROM variant WHERE chr=%s OR pos=%s OR ref=%s OR alt=%s ORDER BY chr, pos, ref, alt LIMIT %d, %d" % (query, query, query, query, offset, page_size)
        self.cursor.execute(command)
        result = self.cursor.fetchall()

        self.cursor.execute(
            "SELECT COUNT(id) FROM variant WHERE chr=%s OR pos=%s OR ref=%s OR alt=%s" 
            % (query, query, query, query)
        )
        num_variants = self.cursor.fetchone()
        num_variants = num_variants[0]
        return result, num_variants





    def get_clinvar_variant_annotation(self, variant_id):
        command = "SELECT * FROM clinvar_variant_annotation WHERE variant_id = " + enquote(variant_id)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        if len(result) > 1:
            functions.eprint("WARNING: more than one clinvar annotation for variant " + str(variant_id) + " in: get_clinvar_variant_annotation, defaulting to the first one")
        if len(result) == 0:
            return None
        result = result[0]
        return result
    
    def get_clinvar_submissions(self, clinvar_variant_annotation_id):
        command = "SELECT * FROM clinvar_submission WHERE clinvar_variant_annotation_id = " + enquote(clinvar_variant_annotation_id)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        for i in range(len(result)):
            processed_entry = list(result[i])
            processed_entry[5] = processed_entry[5].split(':')
            result[i] = processed_entry
        
        result = sorted(result, key=lambda x: x[3] or datetime.date(datetime.MINYEAR,1,1), reverse=True) # sort table by last evaluated date
        return result
    
    def get_variant_consequences(self, variant_id):
        command = "SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,exon_nr,intron_nr,symbol,x.gene_id,source,pfam_accession,pfam_description,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags FROM transcript RIGHT JOIN ( \
	                    SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,symbol,gene_id,exon_nr,intron_nr,source,pfam_accession,pfam_description FROM gene RIGHT JOIN ( \
		                    SELECT * FROM variant_consequence WHERE variant_id=%d \
	                    ) y \
	                    ON gene.id = y.gene_id \
                    ) x \
                    ON transcript.name = x.transcript_name" % (variant_id)
        self.cursor.execute(command)
        result = self.cursor.fetchall()

        #result = sorted(result, key=lambda x: functions.convert_none_infinite(x[12]), reverse=True) # sort table by transcript length
        #result = sorted(result, key=lambda x: functions.convert_none_infinite(x[17]), reverse=True) # sort table by number of flags

        return result

    def get_variant_literature(self, variant_id, sort_year = True):
        command = "SELECT * FROM variant_literature WHERE variant_id = " + enquote(variant_id)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        if sort_year:
            result = sorted(result, key=lambda x: functions.convert_none_infinite(x[6]), reverse=True)    
        return result
    
    def check_variant_duplicate(self, chr, pos, ref, alt):
        # The command checks if the length of the table returned by the subquery is empty (result = 0) or not (result = 1)
        command = "SELECT EXISTS (SELECT * FROM variant WHERE chr = %s AND pos = %d AND ref = %s AND alt = %s)" % (enquote(chr), int(pos), enquote(ref), enquote(alt))
        self.cursor.execute(command)
        result = self.cursor.fetchone()[0] # get the first element as result is always a tuple
        if result == 0:
            return False
        else:
            return True

    def get_gene(self, gene_id): # return all info of a gene for the gene page
        command = "SELECT * FROM gene WHERE id = %s" % (gene_id)
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        return result

    def get_transcripts(self, gene_id):
        command = "SELECT gene_id,name,biotype,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags FROM transcript WHERE gene_id = %s" % (gene_id)
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result

    def get_variant_id_by_hgvs(self, reference_transcript, hgvs):
        command = "SELECT variant_id FROM variant_consequence WHERE transcript_name=" + enquote(reference_transcript) 
        if hgvs.startswith('c.'):
            command = command + " AND hgvs_c=" + enquote(hgvs)
        if hgvs.startswith('p.'):
            command = command + " AND hgvs_p=" + enquote(hgvs)
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        if result is not None:
            result = result[0]
        return result

