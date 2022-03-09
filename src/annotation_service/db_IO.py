import mysql.connector
from mysql.connector import Error


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


class Connection:
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def get_one_variant(self, variant_id):
        self.cursor.execute("SELECT * FROM variant WHERE id =" + str(variant_id))
        result = self.cursor.fetchone()
        return result

    def close_connection(self):
        self.conn.close()
        self.cursor.close()
