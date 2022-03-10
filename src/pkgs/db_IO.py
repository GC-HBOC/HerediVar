import mysql.connector
from mysql.connector import Error
import time


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
    return "'" + string + "'"


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


        


























