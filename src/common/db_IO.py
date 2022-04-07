from logging import raiseExceptions
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import mysql.connector
from mysql.connector import Error
import common.functions as functions


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
    return "'" + str(string) + "'"


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
        self.cursor.execute("SELECT * FROM variant WHERE id =" + str(variant_id))
        result = self.cursor.fetchone()
        return result
    
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


    def insert_gene(self, hgnc_id, symbol, name, type):
        hgnc_id = functions.trim_hgnc(hgnc_id)
        self.cursor.execute("INSERT INTO gene (hgnc_id, symbol, name, type) VALUES (%s, %s, %s, %s)", 
                            (hgnc_id, symbol, name, type))
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
    


    def insert_transcript(self, symbol, hgnc_id, transcript_name, transcript_biotype, total_length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical):
        # transcript names are here usually ENST-ids
        gene_id = None
        if symbol is None and hgnc_id is None:
            print("WARNING: transcript: " + transcript_name + ", transcript_biotype: " + transcript_biotype + " was not imported as gene symbol and hgnc id were missing")
            return
        if hgnc_id is not None:
            gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)
        elif symbol is not None:
            gene_id = self.get_gene_id_by_symbol(symbol)
        if gene_id is not None:
            command = "INSERT INTO transcript (gene_id, name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(command, (int(gene_id), transcript_name, transcript_biotype.replace('_', ' '), int(total_length), int(is_gencode_basic), int(is_mane_select), int(is_mane_plus_clinical), int(is_ensembl_canonical)))
            self.conn.commit()
        else:
            print("WARNING: transcript: " + transcript_name + ", transcript_biotype: " + transcript_biotype + " was not imported as the corresponding gene is not in the database (gene-table) " + "hgncid: " + str(hgnc_id) + ", gene symbol: " + str(symbol))

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
    
    def insert_variant_literature(self, variant_id, pmid, title, authors, journal):
        command = "INSERT INTO variant_literature (variant_id, pmid, title, authors, journal_publisher) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, pmid, title, authors, journal))
        self.conn.commit()










