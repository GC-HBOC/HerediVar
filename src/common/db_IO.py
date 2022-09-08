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
from functools import cmp_to_key
import os

def get_db_connection():
    conn = None
    try:
        env = os.environ.get('WEBAPP_ENV', 'dev')
        if env == 'dev':
            conn = mysql.connector.connect(user='ahdoebm1', password='20220303',
                                           host='SRV011.img.med.uni-tuebingen.de',
                                           database='HerediVar_ahdoebm1', 
                                           charset = 'utf8')
        elif env == 'githubtest':
            conn = mysql.connector.connect(user='test_user', password='password',
                                           host='0.0.0.0',
                                           database='test_db', 
                                           charset = 'utf8')
        elif env == 'localtest':
            conn = mysql.connector.connect(user='ahdoebm1', password='20220303',
                               host='SRV011.img.med.uni-tuebingen.de',
                               database='HerediVar_ahdoebm1_test', 
                               charset = 'utf8')
        elif env == 'prod': ## TODO
            conn = mysql.connector.connect(user='missing', password='missing',
                                           host='0.0.0.0',
                                           database='missing', 
                                           charset = 'utf8')

    except Error as e:
        raise RuntimeError("Error while connecting to HerediVar database " + str(e))
    finally:
        if conn is not None and conn.is_connected():
            return conn


def enquote(string):
    string = str(string).strip("'") # remove quotes if the input string is already quoted!
    return "'" + string + "'"

def enbrace(string):
    #string = str(string).strip("(").strip(")")
    string = "(" + string + ")"
    return string



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
        #command = "DELETE FROM " + table + " WHERE " + unique_column + " IN (SELECT * FROM (SELECT " + unique_column + " FROM " + table + " GROUP BY " + unique_column + " HAVING (COUNT(*) > 1)) AS A)"
        command = "DELETE FROM %s WHERE %s IN (SELECT * FROM (SELECT %s FROM %s GROUP BY %s HAVING (COUNT(*) > 1)) AS A)"
        self.cursor.execute(command, (table, unique_column, unique_column, table, unique_column))
        self.conn.commit()
    

    def get_one_variant(self, variant_id):
        command = "SELECT id,chr,pos,ref,alt FROM variant WHERE id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchone()
        return result
    
    def get_variant_id(self, chr, pos, ref, alt):
        #command = "SELECT id FROM variant WHERE chr = " + enquote(chr) + " AND pos = " + str(pos) + " AND ref = " + enquote(ref) + " AND alt = " + enquote(alt)
        command = "SELECT id FROM variant WHERE chr = %s AND pos = %s AND ref = %s AND alt = %s"
        self.cursor.execute(command, (chr, pos, ref, alt))
        variant_id = self.cursor.fetchone()
        if variant_id is not None:
            return variant_id[0]
        return None
    
    def get_gene_id_by_hgnc_id(self, hgnc_id):
        hgnc_id = functions.trim_hgnc(hgnc_id)
        command = "SELECT id FROM gene WHERE hgnc_id = %s"
        self.cursor.execute(command, (hgnc_id, ))
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
        self.cursor.execute("SELECT id,variant_id,user_id FROM annotation_queue WHERE status = 'pending'")
        pending_variant_ids = self.cursor.fetchall()
        return pending_variant_ids

    def update_annotation_queue(self, row_id, status, error_msg):
        error_msg = error_msg.replace("\n", " ")
        #print("UPDATE annotation_queue SET status = " + status + ", finished_at = " + time.strftime('%Y-%m-%d %H:%M:%S') + ", error_message = " + error_msg + " WHERE id = " + str(row_id))
        command = "UPDATE annotation_queue SET status = %s, finished_at = NOW(), error_message = %s WHERE id = %s"
        self.cursor.execute(command, (status, error_msg, row_id))
        self.conn.commit()

    def get_current_annotation_status(self, variant_id):
        # return the most recent annotation queue entry for the variant 
        command = "SELECT * FROM annotation_queue WHERE variant_id = %s ORDER BY requested DESC LIMIT 1"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchone()
        return result

    def get_pfam_description_by_pfam_acc(self, pfam_acc):
        pfam_acc = functions.remove_version_num(pfam_acc)
        orig_pfam_acc = pfam_acc
        found_description = False
        
        while not found_description:
            command = "SELECT accession_id,description FROM pfam_id_mapping WHERE accession_id = %s"
            self.cursor.execute(command, (pfam_acc, ))
            pfam_description = self.cursor.fetchone()
            if pfam_description is None:
                command = "SELECT old_accession_id,new_accession_id FROM pfam_legacy WHERE old_accession_id = %s"
                self.cursor.execute(command, (pfam_acc))
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
        placeholders = placeholders[:len(placeholders)-2]
        #command = "INSERT INTO variant_consequence (" + columns_with_info + ") VALUES (" + placeholders + ")"
        command = "INSERT INTO variant_consequence (" + columns_with_info + ") \
                    SELECT " + placeholders +  " WHERE NOT EXISTS (SELECT * FROM variant_consequence \
                        WHERE " + columns_with_info.replace(', ', '=%s AND ') + '=%s ' + " LIMIT 1)"
        #print(command)
        self.cursor.execute(command, actual_information + actual_information)
        self.conn.commit()

    def get_gene_id_by_symbol(self, symbol):
        command = "SELECT id,symbol FROM gene WHERE symbol=%s"
        self.cursor.execute(command, (symbol, ))
        res = self.cursor.fetchone()
        if res is None:
            command = "SELECT gene_id,alt_symbol FROM gene_alias WHERE alt_symbol=%s"
            self.cursor.execute(command, (symbol, ))
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
            command = "INSERT INTO gene_alias (gene_id, alt_symbol) VALUES (%s, %s)"
            self.cursor.execute(command, (gene_id, symbol))
            self.conn.commit()
        else:
            print("WARNING: there was no row in the gene table for hgnc_id " + str(hgnc_id) + ". Error occured during insertion of gene alias " + str(symbol))


    def insert_annotation_type(self, name, description, value_type, version, version_date):
        command = "SELECT id FROM annotation_type WHERE name = %s AND version = %s AND version_date = %s"
        self.cursor.execute(command, (name, version, version_date))
        result = self.cursor.fetchall()
        if len(result) == 0:
            command = "INSERT INTO annotation_type (name, description, value_type, version, version_date) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(command, (name, description, value_type, version, version_date))
            self.conn.commit()
    
    def insert_variant_annotation(self, variant_id, annotation_type_id, value, supplementary_document = None):
        # supplementary documents are not supported yet! see: https://stackoverflow.com/questions/10729824/how-to-insert-blob-and-clob-files-in-mysql
        #command = "INSERT INTO variant_annotation (`variant_id`, `annotation_type_id`, `value`) \
        #           SELECT %s, %s, %s WHERE NOT EXISTS (SELECT * FROM variant_annotation \
        #                WHERE `variant_id`=%s AND `annotation_type_id`=%s AND `value`=%s LIMIT 1)"
        #self.cursor.execute(command, (variant_id, annotation_type_id, value, variant_id, annotation_type_id, value))
        command = "INSERT INTO variant_annotation (`variant_id`, `annotation_type_id`, `value`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE `value`=%s"
        self.cursor.execute(command, (variant_id, annotation_type_id, value, value))
        self.conn.commit()

    def insert_variants_from_vcf(self, path):
        # deprecated
        variants = functions.read_variants(path)

        for variant in variants:
            chr = variant.CHROM
            pos = variant.POS
            ref = variant.REF
            alt = variant.ALT
            command = "INSERT INTO variant (chr, pos, ref, alt) VALUES (%s, %s, %s, %s)"
            self.cursor().execute(command, (chr, pos, ref, alt))
        self.conn.commit()
    
    def insert_variant(self, chr, pos, ref, alt, orig_chr, orig_pos, orig_ref, orig_alt, user_id):
        ref = ref.upper()
        alt = alt.upper()
        command = "INSERT INTO variant (chr, pos, ref, alt, orig_chr, orig_pos, orig_ref, orig_alt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (chr, pos, ref, alt, orig_chr, orig_pos, orig_ref, orig_alt))
        self.conn.commit()
        variant_id = self.get_variant_id(chr, pos, ref, alt)
        self.insert_annotation_request(variant_id, user_id)
        return self.get_last_insert_id() # return the annotation_queue_id of the new variant
    
    #def insert_external_variant_id_from_vcf(self, chr, pos, ref, alt, external_id, id_source):
    #    command = "INSERT INTO variant_ids (variant_id, external_id, id_source) (SELECT id, %s, %s FROM variant WHERE chr=%s AND pos=%s AND ref=%s AND alt=%s LIMIT 1)"
    #    self.cursor.execute(command, (external_id, id_source, chr, pos, ref, alt))
    #    self.conn.commit()
    
    def insert_external_variant_id(self, variant_id, external_id, id_source):
        command = "INSERT INTO variant_ids (variant_id, external_id, id_source) \
                    SELECT %s, %s, %s WHERE NOT EXISTS (SELECT * FROM variant_ids \
	                    WHERE `variant_id`=%s AND `external_id`=%s AND `id_source`=%s LIMIT 1)"
        self.cursor.execute(command, (variant_id, external_id, id_source, variant_id, external_id, id_source))
        self.conn.commit()
    
    def update_external_variant_id(self, variant_id, external_id, id_source):
        command = "UPDATE variant_ids SET external_id = %s WHERE variant_id = %s AND id_source = %s"
        self.cursor.execute(command, (external_id, variant_id, id_source))
        self.conn.commit()

    def insert_update_external_variant_id(self, variant_id, external_id, id_source):
        previous_external_variant_id = self.get_external_ids_from_variant_id(variant_id, id_source=id_source)
        print(previous_external_variant_id)
        if (len(previous_external_variant_id) == 1): # do update
            self.update_external_variant_id(variant_id, external_id, id_source)
        else: # save new
            self.insert_external_variant_id(variant_id, external_id, id_source)

    def insert_annotation_request(self, variant_id, user_id): # this inserts only if there is not an annotation request for this variant which is still pending
        #command = "INSERT INTO annotation_queue (variant_id, status, user_id) VALUES (%s, %s, %s)"
        command = "INSERT INTO annotation_queue (`variant_id`, `user_id`) \
                    SELECT %s, %s WHERE NOT EXISTS (SELECT * FROM annotation_queue \
	                    WHERE `variant_id`=%s AND `status`='pending' LIMIT 1)"
        self.cursor.execute(command, (variant_id, user_id, variant_id))
        self.conn.commit()

        command = "SELECT id from annotation_queue WHERE variant_id=%s AND status='pending'"
        self.cursor.execute(command, (variant_id, ))
        annotation_queue_id = self.cursor.fetchone()
        if annotation_queue_id is not None:
            return annotation_queue_id[0]
        return None

    def insert_celery_task_id(self, annotation_queue_id, celery_task_id):
        command = "UPDATE annotation_queue SET celery_task_id = %s WHERE id = %s"
        self.cursor.execute(command, (celery_task_id, annotation_queue_id))
        self.conn.commit()
    
    def insert_clinvar_variant_annotation(self, variant_id, variation_id, interpretation, review_status):
        command = "INSERT INTO clinvar_variant_annotation (variant_id, variation_id, interpretation, review_status) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, variation_id, interpretation, review_status))
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
        #command = "SELECT a.id,a.variant_id,a.version_date \
        #            FROM clinvar_variant_annotation a \
        #            INNER JOIN ( \
        #                SELECT variant_id, max(version_date) AS version_date FROM clinvar_variant_annotation GROUP BY variant_id \
        #            ) b ON a.variant_id = b.variant_id AND a.variant_id = " + enquote(variant_id) + " AND a.version_date = b.version_date"
        command = "SELECT id FROM clinvar_variant_annotation WHERE variant_id=%s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None
    

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
                #transcript_ensembl_list = ', '.join([enquote(x) for x in transcript_ensembl.split(',')])
                transcript_ensembl_list = transcript_ensembl.split(',')
                transcript_ensembl_placeholders = ', '.join(['%s'] * len(transcript_ensembl_list))
                self.cursor.execute("SELECT COUNT(*) FROM transcript WHERE name IN (" + transcript_ensembl_placeholders + ")", tuple(transcript_ensembl_list))
                has_ensembl = self.cursor.fetchone()[0]
                if has_ensembl:
                    # The command inserts a new refseq transcript while it searches for a matching ensembl transcripts (which should already be contained in the transcripts table) and copies their gencode, mane and canonical flags
                    infos = (gene_id, transcript_refseq, transcript_biotype, total_length) + tuple(transcript_ensembl_list)
                    command = "INSERT INTO transcript (gene_id, name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) \
	                                    (SELECT %s, %s, %s, %s, SUM(is_gencode_basic) > 0, SUM(is_mane_select) > 0, SUM(is_mane_plus_clinical)  > 0, SUM(is_ensembl_canonical)  > 0 FROM transcript WHERE name IN (" + transcript_ensembl_placeholders + "));"
            if command == '':
                if transcript_refseq is not None:
                    transcript_name = transcript_refseq
                else:
                    transcript_name = transcript_ensembl
                infos = (gene_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                command = "INSERT INTO transcript (gene_id, name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            
            self.cursor.execute(command, infos)
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
    
    def insert_task_force_protein_domain(self, chromsome, start, end, description, source):
        command = "INSERT INTO task_force_protein_domains (chr, start, end, description, source) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(command, (chromsome, start, end, description, source))
        self.conn.commit()
    
    def get_task_force_protein_domains(self, chromosome, variant_start, variant_end):
        command = "SELECT * FROM task_force_protein_domains WHERE chr = %s and ((start <= %s) and (%s <= end))"
        self.cursor.execute(command, (chromosome, variant_end, variant_start))
        result = self.cursor.fetchall()
        return result
    
    def insert_variant_literature(self, variant_id, pmid, title, authors, journal, year):
        #command = "INSERT INTO variant_literature (variant_id, pmid, title, authors, journal_publisher, year) VALUES (%s, %s, %s, %s, %s, %s)"
        command = "INSERT INTO variant_literature (variant_id, pmid, title, authors, journal_publisher, year) \
                    SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT * FROM variant_literature \
                        WHERE `variant_id`=%s AND `pmid`=%s LIMIT 1)"
        self.cursor.execute(command, (variant_id, pmid, title, authors, journal, year, variant_id, pmid))
        self.conn.commit()

    def clean_clinvar(self, variant_id):
        command = "DELETE FROM clinvar_variant_annotation WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        self.conn.commit()

    
    def get_recent_annotations(self, variant_id): # ! the ordering of the columns in the outer select statement is important and should not be changed
        command = "SELECT variant_annotation.id, title, description, version, version_date, variant_id, value, supplementary_document, group_name FROM variant_annotation INNER JOIN ( \
                        SELECT * \
	                        FROM annotation_type WHERE (title, version_date) IN ( \
		                        select title, MAX(version_date) version_date from annotation_type INNER JOIN ( \
				                    select variant_id, annotation_type_id, value, supplementary_document from variant_annotation where variant_id=%s \
			                ) x \
			                ON annotation_type.id = x.annotation_type_id \
		                    GROUP BY title \
	                    )  \
                    ) y  \
                    ON y.id = variant_annotation.annotation_type_id \
                    WHERE variant_id=%s"
        self.cursor.execute(command, (variant_id, variant_id))
        result = self.cursor.fetchall()
        return result
    
    def get_variant_annotation(self, variant_id, annotation_type_id):
        command = "SELECT * FROM variant_annotation WHERE variant_id = %s AND annotation_type_id = %s"
        self.cursor.execute(command, (variant_id, annotation_type_id))
        res = self.cursor.fetchall()
        return res

    def get_all_valid_variant_ids(self):
        command = "SELECT id FROM variant"
        self.cursor.execute(command)
        res = self.cursor.fetchall()
        return [x[0] for x in res]


    def add_constraints_to_command(self, command, constraints, operator = 'AND'): # constraints should not contain actual data, but rather %s placeholders!!!
        if 'WHERE' not in command:
            command = command + " WHERE "
        else:
            command = command + ' ' + operator + ' '
        command = command + constraints
        return command
    
    def preprocess_range(self, range_constraint):
        parts = range_constraint.split(':')
        if len(parts) != 2:
            return None, None, None
        chr = parts[0]
        positions = parts[1].split('-')
        if len(positions) != 2:
            return None, None, None
        start = int(positions[0])
        end = int(positions[1])
        return chr, start, end

    def convert_to_gene_id(self, string):
        gene_id = self.get_gene_id_by_symbol(string)
        if gene_id is None:
            gene_id = self.get_gene_id_by_hgnc_id(string)
        return gene_id # can return none
    

    def get_variant_more_info(self, variant_id, user_id = None):
        command = "SELECT * FROM variant WHERE id = %s"
        command = self.annotate_genes(command)
        command = self.annotate_consensus_classification(command)
        actual_information = (variant_id, )
        if user_id is not None:
            command = self.annoate_specific_user_classification(command)
            actual_information += (user_id, )
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchone()
        return result

    # these functions add additional columns to the variant table
    def annotate_genes(self, command):
        prefix = """
        				SELECT id, chr, pos, ref, alt, group_concat(gene_id SEPARATOR '; ') as gene_id, group_concat(symbol SEPARATOR '; ') as symbol FROM (
							SELECT * FROM (
        """
        postfix = """
        						) a LEFT JOIN (
                                    SELECT DISTINCT variant_id, gene_id FROM variant_consequence WHERE gene_id IS NOT NULL) b ON a.id=b.variant_id
					) c LEFT JOIN (
                                SELECT id AS gene_id_2, symbol FROM gene WHERE id
				) d ON c.gene_id=d.gene_id_2
                        GROUP BY id, chr, pos, ref, alt
        """
        return prefix + command + postfix

    def annotate_specific_user_classification(self, command, user_id):
        prefix = """
        SELECT g.*, h.user_classification FROM (
        """
        postfix = """
        		) g LEFT JOIN (
                    SELECT variant_id, classification as user_classification FROM user_classification WHERE user_id = %s) h ON g.id = h.variant_id ORDER BY chr, pos, ref, alt
        """
        return prefix + command + postfix
    
    def annotate_consensus_classification(self, command):
        prefix = """
            SELECT e.*, f.classification FROM (
        """
        postfix = """
        	) e LEFT JOIN (
                SELECT variant_id, classification FROM consensus_classification WHERE is_recent=1) f ON e.id = f.variant_id
        """
        return prefix + command + postfix

    # this function returns a list of variant tuples (can have length more than one if there are multiple mane select transcripts for this variant)
    def annotate_preferred_transcripts(self, variant):
        result = []
        consequences = self.get_variant_consequences(variant_id = variant[0])
        if consequences is not None:
            consequences = self.order_consequences(consequences)
            best_consequence = consequences[0]
                
            if best_consequence[14] == 1: # if the best one is a mane select transcript scan also the following and add them as well
                for consequence in consequences:
                    if consequence[14] == 1: # append one variant entry for each mane select transcript (in case of multiple genes, usually a low number)
                        result.append(variant + consequence)
                    else:
                        break # we can do this because the list is sorted
            else: # in case the best consequence is no mane select transcrip
                result.append(variant + best_consequence)

        else:
            result.append(variant + (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None))
        return result
    
    def order_consequences(self, consequences):
        keyfunc = cmp_to_key(mycmp = self.sort_consequences)
                
        consequences.sort(key = keyfunc) # sort by preferred transcript
        return consequences


    """
    # this function adds additional columns to the variant table (ie. gene symbol, gene_id)
    def finalize_search_query(self, command):
        prefix = '''
        SELECT id, chr, pos, ref, alt, gene_id, symbol, classification, user_classification,hgvs_c,hgvs_p,symbol_details,gene_id_details FROM (
            SELECT id, chr, pos, ref, alt, gene_id, symbol, classification, user_classification FROM (
	            SELECT id, chr, pos, ref, alt, gene_id, symbol, classification FROM (
		            SELECT id, chr, pos, ref, alt, group_concat(gene_id SEPARATOR '; ') as gene_id, group_concat(symbol SEPARATOR '; ') as symbol FROM (
			            SELECT * FROM (
        '''
        postfix = '''
			    ) a
			    LEFT JOIN (
				    SELECT DISTINCT variant_id, gene_id FROM variant_consequence WHERE gene_id IS NOT NULL) b ON a.id=b.variant_id
		        ) c LEFT JOIN (
			        SELECT id AS gene_id_2, symbol FROM gene WHERE id
		    ) d ON c.gene_id=d.gene_id_2 
		        GROUP BY id, chr, pos, ref, alt
	        ) e LEFT JOIN (
	            SELECT variant_id, classification FROM consensus_classification WHERE is_recent=1) f ON e.id = f.variant_id
            ) g LEFT JOIN (
	            SELECT variant_id, classification as user_classification FROM user_classification WHERE user_id = %s) h ON g.id = h.variant_id ORDER BY chr, pos, ref, alt
            ) h  LEFT JOIN (
		        SELECT variant_id,hgvs_c,hgvs_p,is_mane_select,symbol_details,gene_id as gene_id_details FROM (
		        	SELECT variant_id,transcript_name,hgvs_c,hgvs_p,is_mane_select,gene_id FROM transcript INNER JOIN (SELECT variant_id,transcript_name,hgvs_c,hgvs_p FROM variant_consequence WHERE source='ensembl') x ON transcript.name=x.transcript_name WHERE is_mane_select=1
                    ) x LEFT JOIN (SELECT id,symbol as symbol_details FROM gene) y ON x.gene_id = y.id
        ) i ON h.id=i.variant_id ORDER BY chr, pos, ref, alt
        '''
        #				SELECT variant_id,transcript_name,hgvs_c,hgvs_p,is_mane_select FROM transcript  INNER JOIN (SELECT variant_id,transcript_name,hgvs_c,hgvs_p FROM variant_consequence WHERE source='ensembl') x ON transcript.name=x.transcript_name WHERE is_mane_select=1

        command = prefix + command + postfix
        return command
    """


    def get_variants_page_merged(self, page, page_size, user_id, ranges = None, genes = None, consensus = None, hgvs = None, variant_ids_oi = None):
        # get one page of variants determined by offset & pagesize
        offset = (page - 1) * page_size
        prefix = "SELECT id, chr, pos, ref, alt FROM variant"
        postfix = ""
        actual_information = ()
        if ranges is not None and len(ranges) > 0: # if it is None this means it was not specified or there was an error. If it has len == 0 it means that there was no error but the user did not specify any 
            new_constraints = []
            for range_constraint in ranges:
                chr, start, end = self.preprocess_range(range_constraint)
                new_constraints.append("(chr=%s AND pos BETWEEN %s AND %s)")
                actual_information += (chr, start, end)
            new_constraints = ' OR '.join(new_constraints)
            new_constraints = enbrace(new_constraints)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if genes is not None and len(genes) > 0:
            genes = [self.convert_to_gene_id(x) for x in genes]
            placeholders = ["%s"] * len(genes)
            placeholders = ', '.join(placeholders)
            placeholders = enbrace(placeholders)
            new_constraints = "id IN (SELECT DISTINCT variant_id FROM variant_consequence WHERE gene_id IN " + placeholders + ")"
            actual_information += tuple(genes)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if consensus is not None and len(consensus) > 0:
            new_constraints_inner = ''
            if '-' in consensus:
                new_constraints_inner = "SELECT id FROM variant WHERE id NOT IN (SELECT variant_id FROM consensus_classification WHERE is_recent=1)"
                consensus.remove('-')
                if len(consensus) > 0: # if we have - AND some other class(es) we need to add an or between them
                    new_constraints_inner = new_constraints_inner + " UNION ALL "
            if len(consensus) > 0: # if we have one or more classes without the -
                placeholders = ["%s"] * len(consensus)
                placeholders = ', '.join(placeholders)
                placeholders = enbrace(placeholders)
                new_constraints_inner = new_constraints_inner + "SELECT variant_id FROM consensus_classification WHERE classification IN " + placeholders + " AND is_recent = 1"
                actual_information += tuple(consensus)
            new_constraints = "id IN (" + new_constraints_inner + ")"
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if hgvs is not None and len(hgvs) > 0:
            all_variants = []
            for hgvs_string in hgvs:
                ref, hgvs = functions.split_hgvs(hgvs_string) # ref could be a reference transcript or a gene name
                if ref is not None:
                    variant_id = self.get_variant_id_by_hgvs(ref, hgvs) # see if the reference transcript is a transcript
                    if variant_id is None:
                        variant_ids = self.get_variant_ids_from_gene_and_hgvs(ref, hgvs)
                        #variant_id = self.get_variant_id_by_hgvs(reference_transcript, hgvs)
                        all_variants.extend(variant_ids)
                    else:
                        all_variants.append(variant_id)
                else:
                    variant_ids = self.get_variant_ids_by_hgvs(hgvs)
                    all_variants.extend(variant_ids)
            if len(all_variants) == 0: # we need this because we get an error if the list is empty
                all_variants = [''] # empty string can never be found
            placeholders = ["%s"] * len(all_variants)
            placeholders = ', '.join(placeholders)
            placeholders = enbrace(placeholders)
            new_constraints = "id IN " + placeholders
            actual_information += tuple(all_variants)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if variant_ids_oi is not None and len(variant_ids_oi) > 0:
            placeholders = ["%s"] * len(variant_ids_oi)
            placeholders = ', '.join(placeholders)
            placeholders = enbrace(placeholders)
            new_constraints = "id IN " + placeholders
            actual_information += tuple(variant_ids_oi)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        
        command = prefix + postfix + " ORDER BY chr, pos, ref, alt LIMIT %s, %s"
        actual_information += (offset, page_size)
        command = self.annotate_genes(command)
        command = self.annotate_consensus_classification(command)
        command = self.annotate_specific_user_classification(command, user_id = user_id)
        actual_information += (user_id, ) # this is required to get the user-classifications of the currently logged in user for the variants
        self.cursor.execute(command, actual_information)
        variants = self.cursor.fetchall()

        variants_and_transcripts = []
        for variant in variants:
            annotated_variant = self.annotate_preferred_transcripts(variant)
            variants_and_transcripts.extend(annotated_variant)
        variants = variants_and_transcripts
        #print(variants)

        # get number of variants
        prefix = "SELECT COUNT(id) FROM variant"
        command = prefix + postfix
        self.cursor.execute(command, actual_information[:len(actual_information)-3])
        num_variants = self.cursor.fetchone()
        if num_variants is None:
            return [], 0
        return variants, num_variants[0]



    def get_variant_ids_from_gene_and_hgvs(self, gene, hgvs_c, source = 'ensembl'):
        gene_id = self.convert_to_gene_id(gene)

        command = "SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,exon_nr,intron_nr,symbol,z.gene_id,source,pfam_accession,pfam_description,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags,biotype,variant_id  FROM transcript RIGHT JOIN ( \
                        SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,symbol,gene_id,exon_nr,intron_nr,source,pfam_accession,pfam_description,variant_id FROM gene RIGHT JOIN ( \
                            SELECT * FROM variant_consequence INNER JOIN ( \
	                            SELECT DISTINCT variant_id as variant_id_trash FROM variant_consequence WHERE source = %s AND gene_id = %s AND hgvs_c = %s \
                            ) x ON x.variant_id_trash = variant_consequence.variant_id  \
                        ) y ON gene.id = y.gene_id \
                    ) z ON transcript.name = z.transcript_name WHERE z.gene_id=%s ORDER BY variant_id asc"
        self.cursor.execute(command, (source, gene_id, hgvs_c, gene_id))
        possible_consequences = self.cursor.fetchall()
        
        # extract all matching variant ids
        # these are identified where the given hgvs_c string is matching with the preferred transcript's hgvs_c. 
        # for this
        # (1) find all consequences from one variant where the hgvsc string is matching in at least one consequence
        # (2) from this set extract the preferred transcript(s)
        # (3) save the variant_id as this is the one we are looking for
        matching_variant_ids = []
        current_batch = []
        batches = []
        for consequence in possible_consequences:
            if len(current_batch) == 0 or consequence[19] == current_batch[0][19]:
                # (1)
                current_batch.append(consequence)
            elif consequence[19] != current_batch[0][19]:
                batches.append(current_batch)
                current_batch = [consequence]
        if len(current_batch) > 0:
            batches.append(current_batch)

        for current_batch in batches:
            # (2)
            current_batch = self.order_consequences(current_batch)
            best_consequence = current_batch[0]

            # (3)
            if best_consequence[1] == hgvs_c:
                matching_variant_ids.append(best_consequence[19])
            
            if best_consequence[14] == 1: # is mane select
                for c in current_batch:
                    if c[14] == 1 and c[1] == hgvs_c:
                        
                        matching_variant_ids.append(c[19]) # this can lead to duplicated variant ids
                    elif c[14] == 0:
                        break

        matching_variant_ids = list(set(matching_variant_ids)) # removes duplicates

        return matching_variant_ids

                    







    

    def sort_consequences(self, a, b):
        # sort by ensembl/refseq
        if a[9] == 'ensembl' and b[9] == 'refseq':
            return -1
        elif a[9] == 'refseq' and b[9] == 'ensembl':
            return 1
        elif a[9] == b[9]:

            # sort by mane select
            if a[14] is None or b[14] is None:
                return 1
            elif a[14] == 1 and b[14] == 0:
                return -1
            elif a[14] == 0 and b[14] == 1:
                return 1
            elif a[14] == b[14]:

                # sort by biotype
                if a[18] == 'protein coding' and b[18] != 'protein coding':
                    return -1
                elif a[18] != 'protein coding' and b[18] == 'protein coding':
                    return 1
                elif (a[18] != 'protein coding' and b[18] != 'protein coding') or (a[18] == 'protein coding' and b[18] == 'protein coding'):

                    # sort by length
                    if a[12] > b[12]:
                        return -1
                    elif a[12] < b[12]:
                        return 1
                    else:
                        return 0

    """
    def get_mane_select_for_gene(self, gene, source):
        gene_id = self.convert_to_gene_id(gene)
        command = "SELECT DISTINCT transcript_name FROM variant_consequence WHERE transcript_name IN (SELECT name FROM transcript WHERE is_mane_select=1) AND gene_id=%s AND source=%s"
        self.cursor.execute(command, (gene_id, source))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None
    """




    def get_clinvar_variant_annotation(self, variant_id):
        command = "SELECT * FROM clinvar_variant_annotation WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall()
        if len(result) > 1:
            functions.eprint("WARNING: more than one clinvar annotation for variant " + str(variant_id) + " in: get_clinvar_variant_annotation, defaulting to the first one")
        if len(result) == 0:
            return None
        result = result[0]
        return result
    
    def get_clinvar_submissions(self, clinvar_variant_annotation_id):
        command = "SELECT * FROM clinvar_submission WHERE clinvar_variant_annotation_id = %s"
        self.cursor.execute(command, (clinvar_variant_annotation_id, ))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        for i in range(len(result)):
            processed_entry = list(result[i])
            processed_entry[5] = processed_entry[5].split(':')
            result[i] = processed_entry
        
        #result = sorted(result, key=lambda x: x[3] or datetime.date(datetime.MINYEAR,1,1), reverse=True) # sort table by last evaluated date

        return result
    
    def get_variant_consequences(self, variant_id):
        command = "SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,exon_nr,intron_nr,symbol,x.gene_id,source,pfam_accession,pfam_description,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags,biotype FROM transcript RIGHT JOIN ( \
	                    SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,symbol,gene_id,exon_nr,intron_nr,source,pfam_accession,pfam_description FROM gene RIGHT JOIN ( \
		                    SELECT * FROM variant_consequence WHERE variant_id=%s \
	                    ) y \
	                    ON gene.id = y.gene_id \
                    ) x \
                    ON transcript.name = x.transcript_name"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall()

        #result = sorted(result, key=lambda x: functions.convert_none_infinite(x[12]), reverse=True) # sort table by transcript length
        #result = sorted(result, key=lambda x: functions.convert_none_infinite(x[17]), reverse=True) # sort table by number of flags
        if len(result) == 0:
            return None
        return result

    def get_variant_literature(self, variant_id, sort_year = True):
        command = "SELECT * FROM variant_literature WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        if sort_year:
            result = sorted(result, key=lambda x: functions.convert_none_infinite(x[6]), reverse=True)
        return result
    
    def check_variant_duplicate(self, chr, pos, ref, alt):
        # The command checks if the length of the table returned by the subquery is empty (result = 0) or not (result = 1)
        command = "SELECT EXISTS (SELECT * FROM variant WHERE chr = %s AND pos = %s AND ref = %s AND alt = %s)"
        self.cursor.execute(command, (chr, pos, ref, alt))
        result = self.cursor.fetchone()[0] # get the first element as result is always a tuple
        if result == 0:
            return False
        else:
            return True

    def get_gene(self, gene_id): # return all info of a gene for the gene page
        command = "SELECT * FROM gene WHERE id = %s"
        self.cursor.execute(command, (gene_id, ))
        result = self.cursor.fetchone()
        return result

    def get_transcripts(self, gene_id):
        command = "SELECT gene_id,name,biotype,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags FROM transcript WHERE gene_id = %s"
        self.cursor.execute(command, (gene_id, ))
        result = self.cursor.fetchall()
        return result

    def get_variant_id_by_hgvs(self, reference_transcript, hgvs):
        command = "SELECT variant_id FROM variant_consequence WHERE transcript_name=%s"
        actual_information = (reference_transcript, )
        if hgvs.startswith('c.'):
            command = command + " AND hgvs_c= %s"
            actual_information += (hgvs, )
        elif hgvs.startswith('p.'):
            command = command + " AND hgvs_p=%s"
            actual_information += (hgvs, )
        else:
            return None
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchone()
        if result is not None:
            result = result[0]
        return result

    # this funciton does not require a reference transcript and just returns all variants which could be right one...
    def get_variant_ids_by_hgvs(self, hgvs):
        command = "SELECT DISTINCT variant_id FROM (SELECT variant_id,transcript_name,hgvs_c,hgvs_p FROM variant_consequence WHERE hgvs_c=%s AND transcript_name IN (SELECT name FROM transcript WHERE is_mane_select=1) ) x"
        self.cursor.execute(command, (hgvs, ))
        result = self.cursor.fetchall()
        return [x[0] for x in result]


    def get_vid_list(self):
        command = "SELECT external_id FROM variant_ids WHERE id_source='heredicare'"
        self.cursor.execute(command)
        vids = self.cursor.fetchall()
        vids = [x[0] for x in vids]
        return vids

    '''
    def insert_consensus_classification_from_vcf(self, user_id, chr, pos, ref, alt, consensus_classification, comment, date = "CURDATE()", evidence_document = None):
        self.invalidate_previous_consensus_classifications(self.get_one_variant(chr, pos, ref, alt)[0])
        if date != "CURDATE()":
            date = enquote(date)
        if evidence_document is None:
            return
        command = "INSERT INTO consensus_classification (user_id, variant_id, classification, comment, date, evidence_document) (SELECT %s, id, %s, %s, " + date + ", %s FROM variant WHERE chr=%s AND pos=%s AND ref=%s AND alt=%s LIMIT 1)"
        self.cursor.execute(command, (user_id, consensus_classification, comment, evidence_document.decode(), chr, pos, ref, alt))
        self.conn.commit()
    '''
    
    def insert_consensus_classification_from_variant_id(self, user_id, variant_id, consensus_classification, comment, evidence_document, date):
        self.invalidate_previous_consensus_classifications(variant_id)
        command = "INSERT INTO consensus_classification (user_id, variant_id, classification, comment, date, evidence_document) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (user_id, variant_id, consensus_classification, comment, date, evidence_document.decode()))
        self.conn.commit()
    
    def invalidate_previous_consensus_classifications(self, variant_id):
        command = "UPDATE consensus_classification SET is_recent = '0' WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id,))
        self.conn.commit()
    
    def insert_heredicare_center_classification(self, variant_id, classification, center_name, comment, date):
        command = "INSERT INTO heredicare_center_classification (variant_id, classification, center_name, comment, date) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, classification, center_name, comment, date))
        self.conn.commit()

    def check_heredicare_center_classification(self, variant_id, classification, center_name, comment, date): # this returns true if this classification is already in there and fals if it is not
        command = "SELECT EXISTS (SELECT * FROM heredicare_center_classification WHERE variant_id = %s AND classification = %s AND center_name = %s AND comment = %s AND date = %s)"
        self.cursor.execute(command, (variant_id, classification, center_name, comment, date))
        result = self.cursor.fetchone()[0]
        if result == 0:
            return False
        else:
            return True

    def check_consensus_classification(self, variant_id, consensus_classification, comment, date):
        command = "SELECT EXISTS (SELECT * FROM consensus_classification WHERE variant_id = %s AND classification = %s AND comment = %s AND date = %s)"
        self.cursor.execute(command, (variant_id, consensus_classification, comment, date))
        result = self.cursor.fetchone()[0]
        if result == 0:
            return False
        else:
            return True
    
    def get_variant_id_from_external_id(self, id, id_source): #!! assumed that the external_id column contains unique entries for id, id_source pairs!
        command = "SELECT variant_id FROM variant_ids WHERE external_id = %s AND id_source = %s"
        self.cursor.execute(command, (id, id_source))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return result

    def get_consensus_classification(self, variant_id, most_recent = False, sql_modifier=None): # it is possible to have multiple consensus classifications
        command = "SELECT id,user_id,variant_id,classification,comment,date,is_recent FROM consensus_classification WHERE variant_id = %s"
        if most_recent:
            command = command  + " AND is_recent = '1'"
        else:
            command = command + " ORDER BY DATE(date) DESC, is_recent DESC"
        
        if sql_modifier is not None:
            command = sql_modifier(command)

        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        return result
    
    def get_evidence_document(self, consensus_classificatoin_id):
        command = "SELECT evidence_document FROM consensus_classification WHERE id = %s"
        self.cursor.execute(command, (consensus_classificatoin_id, ))
        result = self.cursor.fetchone()
        return result
    
    def get_user_classifications(self, variant_id): # id,classification,variant_id,user_id,comment,date
        #command = "SELECT * FROM user_classification WHERE variant_id = %s"
        command = "SELECT * FROM user_classification a INNER JOIN (SELECT * FROM user) b ON a.user_id = b.id WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        result = sorted(result, key=lambda x: functions.convert_none_infinite(x[5]), reverse=True)
        return result

    def insert_user_classification(self, variant_id, classification, user_id, comment, date):
        command = "INSERT INTO user_classification (variant_id, classification, user_id, comment, date) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, classification, user_id, comment, date))
        self.conn.commit()
    
    def update_user_classification(self, user_classification_id, classification, comment, date):
        command = "UPDATE user_classification SET classification = %s, comment = %s, date = %s WHERE id = %s"
        self.cursor.execute(command, (classification, comment, date, user_classification_id))
        self.conn.commit()
    
    def get_user_classification(self, user_id, variant_id = None):
        actual_information = (user_id, )
        command = "SELECT * FROM user_classification WHERE user_id = %s"
        if variant_id is not None:
            command = command + " AND variant_id = %s"
            actual_information = actual_information + (variant_id, )
        command = command + " ORDER BY DATE(date) DESC LIMIT 1" # probably not neccessary
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchone()
        return result

    def delete_variant(self, variant_id):
        command = "DELETE FROM variant WHERE id = %s"
        self.cursor.execute(command, (variant_id,))
        self.conn.commit()

    def get_orig_variant(self, variant_id):
        command = "SELECT orig_chr, orig_pos, orig_ref, orig_alt FROM variant WHERE id = %s"
        self.cursor.execute(command, (variant_id, ))
        res = self.cursor.fetchone()
        return res

    def insert_import_request(self, user_id):
        command = "INSERT INTO import_queue (user_id) VALUES (%s)"
        self.cursor.execute(command, (user_id, ))
        self.conn.commit()
        return self.get_last_insert_id()
    
    def close_import_request(self, import_queue_id):
        command = "UPDATE import_queue SET status = 'finished', finished_at = NOW() WHERE id = %s"
        self.cursor.execute(command, (import_queue_id, ))
        self.conn.commit()

    def get_most_recent_import_request(self):
        self.cursor.execute("SELECT * FROM import_queue ORDER BY requested_at DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result

    def get_external_ids_from_variant_id(self, variant_id, id_source=''):
        command = "SELECT external_id FROM variant_ids WHERE variant_id = %s"
        information = (variant_id,)
        if id_source != '':
            command = command + " AND id_source = %s"
            information = information + (id_source, )
        self.cursor.execute(command, information)
        result = self.cursor.fetchall()
        if result is None:
            return []
        return [x[0] for x in result]

    def delete_external_id(self, external_id, id_source):
        command = "DELETE FROM variant_ids WHERE external_id = %s AND id_source = %s"
        self.cursor.execute(command, (external_id, id_source))
        self.conn.commit()

    def update_variant_annotation(self, variant_id, annotation_type_id, value): # use with caution!
        command = "UPDATE variant_annotation SET value = %s  WHERE variant_id = %s AND annotation_type_id = %s"
        self.cursor.execute(command, (value, variant_id, annotation_type_id))
        self.conn.commit()

    def get_import_request(self, import_queue_id = '', date = ''):
        command = ''
        if import_queue_id != '':
            command = 'SELECT * FROM import_queue WHERE id = %s'
            information = (import_queue_id, )
        if date != '':
            date_parts = date.split('-')
            information = (date_parts[0] + '-' + date_parts[1] + '-' + date_parts[2] + ' ' + date_parts[3] + ':' + date_parts[4] + ':' + date_parts[5], )
            command = 'SELECT * FROM import_queue WHERE requested_at = %s'

        if command != '':
            self.cursor.execute(command, information)
            res = self.cursor.fetchone()
            return res
        return None

    def get_heredicare_center_classifications(self, variant_id):
        command = 'SELECT * FROM heredicare_center_classification WHERE variant_id = %s'
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        #result = sorted(result, key=lambda x: functions.convert_none_infinite(x[5]), reverse=True)
        return result
    
    def insert_user(self, username, first_name, last_name, affiliation):
        #command = "INSERT INTO user (username, first_name, last_name, affiliation) \
        #            SELECT %s WHERE NOT EXISTS (SELECT * FROM user \
        #                WHERE `username`=%s LIMIT 1)"
        command = "INSERT INTO user (username, first_name, last_name, affiliation) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE first_name=%s, last_name=%s, affiliation=%s"
        self.cursor.execute(command, (username, first_name, last_name, affiliation, first_name, last_name, affiliation))
        self.conn.commit()
    
    def get_user(self, user_id):
        command = "SELECT * FROM user WHERE id=%s"
        self.cursor.execute(command, (user_id,))
        result = self.cursor.fetchone()
        return result
    
    def get_user_id(self, username):
        command = "SELECT id FROM user WHERE username=%s"
        self.cursor.execute(command, (username, ))
        result = self.cursor.fetchone()[0]
        return result

    def insert_user_variant_list(self, user_id, list_name):
        command = "INSERT INTO user_variant_lists (user_id, name) VALUES (%s, %s)"
        self.cursor.execute(command, (user_id, list_name))
        self.conn.commit()

    # if you set a variant id the result will contain information if this variant is contained in the list or not (list[3] != None ==> variant is conatined in list)
    def get_lists_for_user(self, user_id, variant_id = None):
        command = "SELECT * FROM user_variant_lists"
        actual_information = ()
        if variant_id is not None:
            command = command + " LEFT JOIN (SELECT list_id FROM list_variants WHERE variant_id=%s) x ON user_variant_lists.id = x.list_id"
            actual_information = actual_information + (variant_id, )
        command = command + " WHERE user_id = %s ORDER BY id ASC"
        actual_information = actual_information + (user_id, )
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchall()
        return result
    
    def add_variant_to_list(self, list_id, variant_id):
        command = "INSERT INTO list_variants (list_id, variant_id) \
                    SELECT %s, %s WHERE NOT EXISTS (SELECT * FROM list_variants \
                        WHERE `list_id`=%s AND `variant_id`=%s LIMIT 1)"
        self.cursor.execute(command, (list_id, variant_id, list_id, variant_id))
        self.conn.commit()

    def get_variant_ids_from_list(self, list_id):
        command = "SELECT variant_id FROM list_variants WHERE list_id=%s"
        self.cursor.execute(command, (list_id, ))
        result = self.cursor.fetchall()
        result = [str(x[0]) for x in result] # extract variant_id
        return result
    
    # list_id to get the right list
    # user_id for security such that you can not edit lists which were not made by you
    # list_name is the value which will be updated
    def update_user_variant_list(self, list_id, user_id, new_list_name):
        command = "UPDATE user_variant_lists SET name = %s WHERE id = %s AND user_id = %s"
        self.cursor.execute(command, (new_list_name, list_id, user_id))
        self.conn.commit()

    
    def check_user_list_ownership(self, user_id, list_id):
        command = "SELECT EXISTS (SELECT * FROM user_variant_lists WHERE user_id = %s AND id = %s)"
        self.cursor.execute(command, (user_id, list_id))
        result = self.cursor.fetchone()
        result = result[0]
        if result == 1:
            return True
        else:
            return False

    def delete_variant_from_list(self, list_id, variant_id):
        command = "DELETE FROM list_variants WHERE list_id=%s AND variant_id=%s"
        self.cursor.execute(command, (list_id, variant_id))
        self.conn.commit() 

    def delete_user_variant_list(self, list_id):
        command = "DELETE FROM user_variant_lists WHERE id = %s"
        self.cursor.execute(command, (list_id, ))
        self.conn.commit()

    def get_all_variant_annotations(self, variant_id, group_output=False, most_recent_scheme_consensus=True):
        variant_annotations = self.get_recent_annotations(variant_id)
        standard_annotations = {} # used for grouping hierarchy: 'standard_annotations' -> group -> annotation_label
        variant_annot_dict = {}

        if group_output: # all groups are grouped into one dictionary except for the special group 'None' which is inserted as key directly into variant_annot_dict
            for annot in variant_annotations:
                current_group = annot[8]
                new_value = annot[2:len(annot)] + (annot[0], ) # put annotation id last and remove title
                new_annotation_type = annot[1]
                if current_group == 'None':
                    variant_annot_dict[new_annotation_type] = new_value
                    continue
                if current_group in standard_annotations:
                    updated_annots = standard_annotations[current_group]
                    updated_annots[new_annotation_type] = new_value
                    standard_annotations[current_group] = updated_annots
                else:
                    standard_annotations[current_group] = {new_annotation_type: new_value}
            variant_annot_dict['standard_annotations'] = standard_annotations
        else:
            for annot in variant_annotations:
                new_value = annot[2:len(annot)] + (annot[0], )  # put annotation id last and remove title
                new_annotation_type = annot[1]
                variant_annot_dict[new_annotation_type] = new_value
        
        clinvar_variant_annotation = self.get_clinvar_variant_annotation(variant_id)
        if clinvar_variant_annotation is not None:
            variant_annot_dict["clinvar_variant_annotation"] = clinvar_variant_annotation # 0id,1variant_id,2variation_id,3interpretation,4review_status,5version_date
            clinvar_variant_annotation_id = clinvar_variant_annotation[0]
            variant_annot_dict['clinvar_submissions'] = self.get_clinvar_submissions(clinvar_variant_annotation_id)

        variant_consequences = self.get_variant_consequences(variant_id) # 0transcript_name,1hgvs_c,2hgvs_p,3consequence,4impact,5exon_nr,6intron_nr,7symbol,8transcript.gene_id,9source,10pfam_accession,11pfam_description,12length,13is_gencode_basic,14is_mane_select,15is_mane_plus_clinical,16is_ensembl_canonical,17total_flag
        if variant_consequences is not None:
            variant_annot_dict['variant_consequences'] = variant_consequences

        literature = self.get_variant_literature(variant_id, sort_year=False)
        if literature is not None:
            variant_annot_dict['literature'] = literature

        consensus_classification = self.get_consensus_classification(variant_id, most_recent=True)
        if consensus_classification is not None:
            variant_annot_dict['consensus_classification'] = consensus_classification[0]

        user_classifications = self.get_user_classifications(variant_id) # 0user_classification_id,1classification,2variant_id,3user_id,4comment,5date,6user_id,7username,8first_name,9last_name,10affiliation
        if user_classifications is not None:
            variant_annot_dict['user_classifications'] = user_classifications

        heredicare_center_classifications = self.get_heredicare_center_classifications(variant_id)
        if heredicare_center_classifications is not None:
            variant_annot_dict['heredicare_center_classifications'] = heredicare_center_classifications
        
        user_scheme_classifications = self.get_user_scheme_classification(variant_id, sql_modifier = self.add_userinfo)
        annotated_user_scheme_classifications = []
        if user_scheme_classifications is not None:
            for classification in user_scheme_classifications:
                current_criteria = self.get_scheme_criteria(classification[0])
                classification += (current_criteria, )
                annotated_user_scheme_classifications.append(classification)
            variant_annot_dict['user_scheme_classifications'] = annotated_user_scheme_classifications
        
        consensus_scheme_classifications = self.get_consensus_scheme_classification(variant_id, scheme='all', most_recent=most_recent_scheme_consensus, sql_modifier=self.add_userinfo)
        annotated_consensus_scheme_classifications = []
        if consensus_scheme_classifications is not None:
            for classification in consensus_scheme_classifications:
                current_criteria = self.get_scheme_criteria(classification[0])
                classification += (current_criteria, )
                annotated_consensus_scheme_classifications.append(classification)
            variant_annot_dict['consensus_scheme_classifications'] = annotated_consensus_scheme_classifications
        

        assays = self.get_assays(variant_id, assay_types = 'all')
        if assays is not None:
            variant_annot_dict['assays'] = assays
        #print(variant_annot_dict['standard_annotations'])

    
        return variant_annot_dict


    def get_assays(self, variant_id, assay_types = 'all'):
        command = "SELECT id, assay_type, score, date FROM assay WHERE variant_id = %s"
        actual_information = (variant_id, )

        if assay_types is not 'all':
            placeholders = ["%s"] * len(assay_types)
            placeholders = ', '.join(placeholders)
            placeholders = enbrace(placeholders)
            new_constraints = " id IN " + placeholders
            command += new_constraints
            actual_information += tuple(assay_types)
        
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        return result


    def get_last_insert_id(self):
        command = "SELECT LAST_INSERT_ID()"
        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    ### scheme classification functions
    # this function is mainly for internal use. Use insert_user_classification or insert_consensus_classification instead
    def insert_scheme_classification(self, variant_id, scheme, is_consensus):
        command = "INSERT INTO scheme_classification (variant_id, scheme, date, is_consensus) VALUES (%s, %s, %s, %s)"
        curdate = datetime.datetime.today().strftime('%Y-%m-%d')
        self.cursor.execute(command, (variant_id, scheme, curdate, is_consensus))
        self.conn.commit()

        return self.get_last_insert_id()

    # each user can have one scheme classification per scheme
    def insert_user_scheme_classification(self, variant_id, user_id, scheme):
        scheme_classification_id = self.insert_scheme_classification(variant_id, scheme, 0)

        command = "INSERT INTO scheme_user_classification (scheme_classification_id, user_id) VALUES (%s, %s)"
        self.cursor.execute(command, (scheme_classification_id, user_id))
        self.conn.commit()


    def get_user_scheme_classification(self, variant_id, user_id = 'all', scheme = 'all', get_criteria=False, sql_modifier=None):
        inner_command = "SELECT id as classification_id, variant_id, scheme, date, is_consensus FROM scheme_classification WHERE variant_id=%s AND is_consensus=0"
        actual_information = (variant_id, )
        if scheme != 'all':
            inner_command += " AND scheme=%s"
            actual_information += (scheme, )
        
        command = "SELECT classification_id, variant_id, user_id, scheme, date FROM scheme_user_classification a INNER JOIN \
	                    (" + inner_command + ") b \
	                    ON a.scheme_classification_id = b.classification_id"

        if user_id != 'all':
            command += ' WHERE user_id=%s'
            actual_information += (user_id, )

        if sql_modifier is not None:
            command = sql_modifier(command)
        
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchall()
        if len(result) > 1 and scheme != 'all':
            raise RuntimeError("ERROR: There are multiple user scheme classifications for variant_id: " + str(variant_id) + ", scheme: " + scheme + ", user_id: " + str(user_id) + "\n The result was: " + str(result))
        if len(result) == 0:
            return None

        return result


    def insert_consensus_scheme_classification(self, user_id, variant_id, scheme):
        scheme_classification_id = self.insert_scheme_classification(variant_id, scheme, 1)

        self.invalidate_previous_scheme_consensus_classifications(variant_id)

        command = "INSERT INTO scheme_consensus_classification (scheme_classification_id, user_id, is_recent) VALUES (%s, %s, %s)"
        self.cursor.execute(command, (scheme_classification_id, user_id, 1))
        self.conn.commit()
        return scheme_classification_id



    def invalidate_previous_scheme_consensus_classifications(self, variant_id):
        command = "UPDATE scheme_consensus_classification SET is_recent = %s WHERE scheme_classification_id IN (SELECT id FROM scheme_classification WHERE variant_id=%s AND is_consensus=1)"
        self.cursor.execute(command, (0, variant_id))
        self.conn.commit()

    
    def get_consensus_scheme_classification(self, variant_id, scheme = 'all', most_recent=True, sql_modifier=None):
        command = "SELECT id, variant_id, scheme, date, is_consensus FROM scheme_consensus_classification a INNER JOIN \
	                    (SELECT id as inner_id, variant_id, scheme, date, is_consensus FROM scheme_classification WHERE variant_id=%s AND is_consensus=1) b \
	                ON a.scheme_classification_id = b.inner_id "

        inner_command = "SELECT id as classification_id, variant_id, scheme, date, is_consensus FROM scheme_classification WHERE variant_id=%s AND is_consensus=1"
        actual_information = (variant_id, )
        if scheme != 'all':
            inner_command += " AND scheme=%s"
            actual_information += (scheme, )
        
        command = "SELECT classification_id, variant_id, is_recent, scheme, date, user_id FROM scheme_consensus_classification a INNER JOIN \
	                    (" + inner_command + ") b \
	                    ON a.scheme_classification_id = b.classification_id"
        if most_recent:
            command += " WHERE is_recent=1"

        if sql_modifier is not None:
            command = sql_modifier(command)

        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchall()
        if len(result) == 0:
            return None
        return result
    

    def add_userinfo(self, command):
        prefix = 'SELECT * FROM (('
        postfix = ') uid_a INNER JOIN (SELECT id as outer_id, first_name,last_name,affiliation FROM user) uid_b ON uid_a.user_id = uid_b.outer_id)'
        result = prefix + command + postfix
        return result



    def update_scheme_classification_date(self, scheme_classification_id):
        curdate = datetime.datetime.today().strftime('%Y-%m-%d')
        command = "UPDATE scheme_classification SET DATE=%s WHERE id=%s"
        self.cursor.execute(command, (curdate, scheme_classification_id))
        self.conn.commit()

    def insert_scheme_criterium(self, scheme_classification_id, criterium, strength, evidence):
        command = "INSERT INTO scheme_criteria (scheme_classification_id, criterium, strength, evidence) VALUES (%s, %s, %s, %s)"
        actual_information = (scheme_classification_id, criterium, strength, evidence)
        self.cursor.execute(command, actual_information)
        self.conn.commit()

    def update_scheme_criterium(self, scheme_criterium_id, updated_strength, updated_evidence):
        command = "UPDATE scheme_criteria SET strength=%s, evidence=%s WHERE id=%s"
        self.cursor.execute(command, (updated_strength, updated_evidence, scheme_criterium_id))
        self.conn.commit()

    def delete_scheme_criterium(self, scheme_criterium_id):
        command = "DELETE FROM scheme_criteria WHERE id=%s"
        self.cursor.execute(command, (scheme_criterium_id, ))
        self.conn.commit()

    def get_scheme_criteria(self, scheme_classification_id):
        command = "SELECT * FROM scheme_criteria WHERE scheme_classification_id=%s"
        self.cursor.execute(command, (scheme_classification_id, ))
        result = self.cursor.fetchall()
        return result

    def insert_assay(self, variant_id, assay_type, report, filename, score, date):
        command = "INSERT INTO assay (variant_id, assay_type, report, filename, score, date) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, assay_type, report, filename, score, date))
        self.conn.commit()

    def get_assay_report(self, assay_id):
        command = "SELECT report,filename FROM assay WHERE id = %s"
        self.cursor.execute(command, (assay_id, ))
        result = self.cursor.fetchone()
        return result

    def get_annotation_queue_entry(self, annotation_queue_id):
        command = "SELECT * FROM annotation_queue WHERE id = %s"
        self.cursor.execute(command, (annotation_queue_id, ))
        result  = self.cursor.fetchone()
        return result
