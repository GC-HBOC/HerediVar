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
                                       host='SRV018.img.med.uni-tuebingen.de',
                                       database='bioinf_heredivar_ahdoebm1')
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

    def get_one_variant(self, variant_id):
        self.cursor.execute("SELECT * FROM variant WHERE id =" + str(variant_id))
        result = self.cursor.fetchone()
        return result
    
    def get_gene_id_by_hgnc_id(self, hgnc_id):
        self.cursor.execute("SELECT id FROM gene WHERE hgnc_id = " + enquote(hgnc_id))
        result = self.cursor.fetchone()
        return result

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

    def insert_variant_consequence(self, variant_id, transcript_name, hgvs_c, hgvs_p, consequence, impact, exon_nr, intron_nr, hgnc_id):
        columns_with_info = "variant_id, transcript_name, consequence, impact"
        actual_information = (variant_id, transcript_name, consequence, impact)
        if (hgvs_c != ''):
            columns_with_info = columns_with_info + ", hgvs_c"
            actual_information = actual_information + (hgvs_c,)
        if (hgvs_p != ''):
            columns_with_info = columns_with_info + ", hgvs_p"
            actual_information = actual_information + (hgvs_p,)
        if (exon_nr != ''):
            columns_with_info = columns_with_info + ", exon_nr"
            actual_information = actual_information + (exon_nr,)
        if (intron_nr != ''):
            columns_with_info = columns_with_info + ", intron_nr"
            actual_information = actual_information + (intron_nr,)
        if (hgnc_id != ''):
            gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)[0] # subset the result as fetching only one column still returns a tuple!
            columns_with_info = columns_with_info + ", gene_id"
            actual_information = actual_information + (gene_id,)
        placeholders = "%s, "*len(actual_information)
        command = "INSERT INTO variant_consequence (" + columns_with_info + ") VALUES (" + placeholders[:len(placeholders)-2] + ")"
        #print(command)
        self.cursor.execute(command, actual_information)
        self.conn.commit()

    def insert_gene(self, hgnc_id, symbol, name, type):
        self.cursor.execute("INSERT INTO gene (hgnc_id, symbol, name, type) VALUES (%s, %s, %s, %s)", 
                            (hgnc_id, symbol, name, type))
        self.conn.commit()

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
    
    def insert_clinvar_variant_annotation(self, variant_id, variation_id, interpretation, review_status):
        command = "INSERT INTO clinvar_variant_annotation (variant_id, variation_id, interpretation, review_status) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, variation_id, interpretation, review_status))
        self.conn.commit()

    def insert_clinvar_submission(self, clinvar_variant_annotation_id, interpretation, last_evaluated, review_status, assertion_criteria, condition, allele_origin, submitter, supporting_information):
        columns_with_info = "clinvar_variant_annotation_id, interpretation, review_status, assertion_criteria, condition, allele_origin, submitter"
        actual_information = (clinvar_variant_annotation_id, interpretation, review_status, assertion_criteria, condition, allele_origin, submitter)
        if (supporting_information != '' or supporting_information != '-'):
            columns_with_info = columns_with_info + ", supporting_information"
            actual_information = actual_information + (supporting_information,)
        if (last_evaluated != '' or last_evaluated != '-'):
            columns_with_info = columns_with_info + ", last_evaluated"
            actual_information = actual_information + (last_evaluated,)
        placeholders = "%s, "*len(actual_information)
        command = "INSERT INTO clinvar_submission (" + columns_with_info + ") VALUES (" + placeholders[:len(placeholders)-2] + ")"
        #print(command)
        self.cursor.execute(command, actual_information)
        self.conn.commit()


        


























