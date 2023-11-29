from logging import raiseExceptions
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import mysql.connector
from mysql.connector import Error
import common.functions as functions
import common.models as models
from operator import itemgetter
import datetime
import re
from functools import cmp_to_key
import os


def get_db_connection(roles):
    conn = None

    host = os.environ.get('DB_HOST')
    if host is None: # this should be checked to make sure the .env file was read in, especially problematic during testing
        functions.read_dotenv()
        host = os.environ.get('DB_HOST')

    try:
        #env = os.environ.get('WEBAPP_ENV', 'dev')
        user, pw = get_db_user(roles)
        conn = mysql.connector.connect(user=user, password=pw,
                               host=host,
                               database=os.environ.get("DB_NAME"), 
                               charset = 'utf8') # , buffered = True
    except Error as e:
        raise RuntimeError("Error while connecting to HerediVar database " + str(e))
    finally:
        if conn is not None and conn.is_connected():
            return conn



def get_db_user(roles):
    if "super_user" in roles:
        #print("using super user role")
        return os.environ.get("DB_SUPER_USER"), os.environ.get("DB_SUPER_USER_PW")
    if "user" in roles:
        #print("using user role")
        return os.environ.get("DB_USER"), os.environ.get("DB_USER_PW")
    if 'annotation' in roles:
        #print("using annotation role")
        return os.environ.get("DB_ANNOTATION_USER"), os.environ.get("DB_ANNOTATION_USER_PW")
    if 'read_only' in roles:
        return os.environ.get("DB_READ_ONLY"), os.environ.get("DB_READ_ONLY_PW")
    if 'db_admin' in roles:
        return os.environ.get("DB_ADMIN"), os.environ.get("DB_ADMIN_PW")
    raise ValueError(str(roles) + " doesn't contain a valid db user role!")



class Connection:
    def __init__(self, roles = ["read_only"]):
        self.conn = get_db_connection(roles)
        self.cursor = self.conn.cursor()
        self.set_connection_encoding()


    def set_connection_encoding(self):
        self.cursor.execute("SET NAMES 'utf8'")
        self.cursor.execute("SET CHARACTER SET utf8")
        self.cursor.execute('SET character_set_connection=utf8;')


    # This function removes ALL occurances of duplicated items
    def remove_duplicates(self, table, unique_column):
        command = "DELETE FROM " + table + " WHERE " + unique_column + " IN (SELECT * FROM (SELECT " + unique_column + " FROM " + table + " GROUP BY " + unique_column + " HAVING (COUNT(*) > 1)) AS A)"
        #command = "DELETE FROM " + table + " WHERE " + unique_column + " IN (SELECT * FROM (SELECT %s FROM %s GROUP BY %s HAVING (COUNT(*) > 1)) AS A)"
        self.cursor.execute(command)
        self.conn.commit()

    
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

    #def get_pending_requests(self):
    #    self.cursor.execute("SELECT id,variant_id,user_id FROM annotation_queue WHERE status = 'pending'")
    #    pending_variant_ids = self.cursor.fetchall()
    #    return pending_variant_ids

    def get_annotation_queue(self, status = []):
        placeholders = self.get_placeholders(len(status))
        command = "SELECT id, status, celery_task_id FROM annotation_queue WHERE status IN " + placeholders
        self.cursor.execute(command, tuple(status))
        result = self.cursor.fetchall()
        return result



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
                self.cursor.execute(command, (pfam_acc, ))
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
            hgnc_id = functions.trim_hgnc(hgnc_id)
            columns_with_info = columns_with_info + ", hgnc_id"
            actual_information = actual_information + (hgnc_id, )
            #gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)
            #if gene_id is not None:
            #    columns_with_info = columns_with_info + ", gene_id"
            #    actual_information = actual_information + (gene_id,)
            #else:
            #    print("WARNING: there was no row in the gene table for hgnc_id " + str(hgnc_id) + ". geneid will be empty even though hgncid was given. Error occured during insertion of variant consequence: " + str(variant_id) + ", " + str(transcript_name) + ", " + str(hgvs_c) + ", " +str(hgvs_p) + ", " +str(consequence) + ", " + str(impact) + ", " + str(exon_nr) + ", " + str(intron_nr) + ", " + str(hgnc_id) + ", " + str(symbol) + ", " + str(consequence_source))
        elif symbol != '':
            gene_id = self.get_gene_id_by_symbol(symbol)
            if gene_id is not None:
                gene = self.get_gene(gene_id)
                columns_with_info = columns_with_info + ", hgnc_id"
                actual_information = actual_information + (gene[1], )
            else:
                print("WARNING: there was no row in the gene table for symbol " + str(symbol) + ". geneid will be empty even though symbol was given. Error occured during insertion of variant consequence: " + str(variant_id) + ", " + str(transcript_name) + ", " + str(hgvs_c) + ", " +str(hgvs_p) + ", " +str(consequence) + ", " + str(impact) + ", " + str(exon_nr) + ", " + str(intron_nr) + ", " + str(hgnc_id) + ", " + str(symbol) + ", " + str(consequence_source))
        placeholders = "%s, "*len(actual_information)
        placeholders = placeholders[:len(placeholders)-2]
        command = "INSERT INTO variant_consequence (" + columns_with_info + ") VALUES (" + placeholders + ")"
        #command = "INSERT INTO variant_consequence (" + columns_with_info + ") \
        #            SELECT " + placeholders +  " FROM DUAL WHERE NOT EXISTS (SELECT * FROM variant_consequence \
        #                WHERE " + columns_with_info.replace(', ', '=%s AND ') + '=%s ' + " LIMIT 1)"
        #actual_information = actual_information * 2
        self.cursor.execute(command, actual_information)
        self.conn.commit()

    def delete_variant_consequences(self, variant_id, is_refseq = False):
        command = "DELETE FROM variant_consequence WHERE variant_id = %s AND source = %s"
        source = 'ensembl'
        if is_refseq:
            source = 'refseq'
        self.cursor.execute(command, (variant_id, source))
        self.conn.commit()




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


    #def insert_annotation_type(self, name, description, value_type, version, version_date):
    #    command = "SELECT id FROM annotation_type WHERE name = %s AND version = %s AND version_date = %s"
    #    self.cursor.execute(command, (name, version, version_date))
    #    result = self.cursor.fetchall()
    #    if len(result) == 0:
    #        command = "INSERT INTO annotation_type (name, description, value_type, version, version_date) VALUES (%s, %s, %s, %s, %s)"
    #        self.cursor.execute(command, (name, description, value_type, version, version_date))
    #        self.conn.commit()
    
    def insert_variant_annotation(self, variant_id, annotation_type_id, value, supplementary_document = None):
        # supplementary documents are not supported yet! see: https://stackoverflow.com/questions/10729824/how-to-insert-blob-and-clob-files-in-mysql
        #command = "INSERT INTO variant_annotation (`variant_id`, `annotation_type_id`, `value`) \
        #           SELECT %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM variant_annotation \
        #                WHERE `variant_id`=%s AND `annotation_type_id`=%s AND `value`=%s LIMIT 1)"
        #self.cursor.execute(command, (variant_id, annotation_type_id, value, variant_id, annotation_type_id, value))
        command = "INSERT INTO variant_annotation (`variant_id`, `annotation_type_id`, `value`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE `value`=%s"
        self.cursor.execute(command, (variant_id, annotation_type_id, value, value))
        self.conn.commit()

    def insert_variant(self, chr, pos, ref, alt, orig_chr, orig_pos, orig_ref, orig_alt, user_id):
        ref = ref.upper()
        alt = alt.upper()
        command = "INSERT INTO variant (chr, pos, ref, alt, orig_chr, orig_pos, orig_ref, orig_alt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (chr, pos, ref, alt, orig_chr, orig_pos, orig_ref, orig_alt))
        self.conn.commit()
        variant_id = self.get_variant_id(chr, pos, ref, alt)
        return variant_id # return the annotation_queue_id of the new variant
    
    def insert_external_variant_id(self, variant_id, external_id, annotation_type_id):
        command = "INSERT INTO variant_ids (variant_id, external_id, annotation_type_id) \
                    SELECT %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM variant_ids \
	                    WHERE `variant_id`=%s AND `external_id`=%s AND `annotation_type_id`=%s LIMIT 1)"
        self.cursor.execute(command, (variant_id, external_id, annotation_type_id, variant_id, external_id, annotation_type_id))
        self.conn.commit()
    
    #def update_external_variant_id(self, variant_id, external_id, annotation_type_id):
    #    command = "UPDATE variant_ids SET external_id = %s WHERE variant_id = %s AND annotation_type_id = %s"
    #    self.cursor.execute(command, (external_id, variant_id, annotation_type_id))
    #    self.conn.commit()
#
    #def insert_update_external_variant_id(self, variant_id, external_id, annotation_type_id):
    #    previous_external_variant_id = self.get_external_ids_from_variant_id(variant_id, annotation_type_id=annotation_type_id)
    #    #print(previous_external_variant_id)
    #    if (len(previous_external_variant_id) == 1): # do update
    #        self.update_external_variant_id(variant_id, external_id, annotation_type_id)
    #    else: # save new
    #        self.insert_external_variant_id(variant_id, external_id, annotation_type_id)

    def insert_annotation_request(self, variant_id, user_id): # this inserts only if there is not an annotation request for this variant which is still pending
        #command = "INSERT INTO annotation_queue (variant_id, status, user_id) VALUES (%s, %s, %s)"
        command = "INSERT INTO annotation_queue (`variant_id`, `user_id`) \
                    SELECT %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM annotation_queue \
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
        #            ) b ON a.variant_id = b.variant_id AND a.variant_id = " + functions.enquote(variant_id) + " AND a.version_date = b.version_date"
        command = "SELECT id FROM clinvar_variant_annotation WHERE variant_id=%s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None
    

    def insert_transcript(self, symbol, hgnc_id, transcript_ensembl, transcript_biotype, total_length, chrom, start, end, orientation, exons, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, transcript_refseq = None):
        if transcript_ensembl is None and transcript_refseq is None: # abort if the transcript name is missing!
            return
        
        # get the gene for the current transcript
        gene_id = None
        transcript_biotype = transcript_biotype.replace('_', ' ')
        if symbol is None and hgnc_id is None:
            #print("WARNING: transcript: " + str(transcript_ensembl) + ", transcript_biotype: " + transcript_biotype + " was not imported as gene symbol and hgnc id were missing")
            return
        if hgnc_id is not None:
            gene_id = self.get_gene_id_by_hgnc_id(hgnc_id)
        if symbol is not None and gene_id is None:
            gene_id = self.get_gene_id_by_symbol(symbol)
        
        # insert transcript
        if gene_id is not None:
            command = ''
            if transcript_refseq is not None and transcript_ensembl is not None:
                #transcript_ensembl_list = ', '.join([functions.enquote(x) for x in transcript_ensembl.split(',')])
                transcript_ensembl_list = transcript_ensembl.split(',')
                placeholders = self.get_placeholders(len(transcript_ensembl_list))
                self.cursor.execute("SELECT COUNT(*) FROM transcript WHERE name IN " + placeholders, tuple(transcript_ensembl_list))
                has_ensembl = self.cursor.fetchone()[0]
                if has_ensembl:
                    # The command inserts a new refseq transcript while it searches for a matching ensembl transcripts (which should already be contained in the transcripts table) and copies their gencode, mane and canonical flags
                    infos = (gene_id, transcript_refseq, transcript_biotype, total_length, chrom, start, end, orientation,) + tuple(transcript_ensembl_list)
                    command = "INSERT INTO transcript (gene_id, name, biotype, length, chrom, start, end, orientation, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) \
	                                    (SELECT %s, %s, %s, %s, %s, %s, %s, %s, SUM(is_gencode_basic) > 0, SUM(is_mane_select) > 0, SUM(is_mane_plus_clinical)  > 0, SUM(is_ensembl_canonical)  > 0 FROM transcript WHERE name IN " + placeholders + ");"
            if command == '':
                if transcript_refseq is not None:
                    transcript_name = transcript_refseq
                else:
                    transcript_name = transcript_ensembl
                infos = (gene_id, transcript_name, transcript_biotype, total_length, chrom, start, end, orientation, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical)
                command = "INSERT INTO transcript (gene_id, name, biotype, length, chrom, start, end, orientation, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            
            #print(command % infos)
            self.cursor.execute(command, infos)
            self.conn.commit()

            transcript_id = self.get_last_insert_id()

            #insert exons
            last_cdna_end = 0
            exons = self.order_exons(exons, orientation)
            for exon in exons:
                start = exon[0]
                end = exon[1]
                is_cds = exon[2]
                cdna_start = None
                cdna_end = None
                if is_cds:
                    cdna_start = last_cdna_end + 1
                    cdna_end = cdna_start + end - start
                    last_cdna_end = cdna_end
                command = "INSERT INTO exon (transcript_id, start, end, cdna_start, cdna_end, is_cds) VALUES (%s, %s, %s, %s, %s, %s)"
                self.cursor.execute(command, (transcript_id, start, end, cdna_start, cdna_end, is_cds))
        else:
            print("WARNING: transcript: " + str(transcript_ensembl) + "/" + str(transcript_refseq) + ", transcript_biotype: " + transcript_biotype + " was not imported as the corresponding gene is not in the database (gene-table) " + "hgncid: " + str(hgnc_id) + ", gene symbol: " + str(symbol))

    def order_exons(self, exons, orientation):
        keyfunc = cmp_to_key(mycmp = self.sort_exons)
        if orientation == '-':
            exons.sort(key = keyfunc, reverse = True) # reverse
        else:
            exons.sort(key = keyfunc)
        return exons
    
    def sort_exons(self, a, b):
        # sort by ensembl/refseq
        a_start = a[0]
        b_start = b[0]
        if int(a_start) > int(b_start):
            return 1
        elif int(a_start) < int(b_start):
            return -1
        return 0



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
    
    def insert_task_force_protein_domain(self, gene_id, chromsome, start, end, description, source):
        command = "INSERT INTO task_force_protein_domains (gene_id, chr, start, end, description, source) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (gene_id, chromsome, start, end, description, source))
        self.conn.commit()

    def has_task_force_protein_domains(self, gene_symbol) -> bool:
        gene_id = self.get_gene_id_by_symbol(gene_symbol)
        if gene_id is None:
            return False
        command = "SELECT COUNT(id) FROM task_force_protein_domains WHERE gene_id = %s"
        self.cursor.execute(command, (gene_id, ))
        result = self.cursor.fetchone()[0]
        if result > 0:
            return True
        return False

    def get_task_force_protein_domains(self, chromosome, variant_start, variant_end):
        command = "SELECT * FROM task_force_protein_domains WHERE chr = %s and ((start <= %s) and (%s <= end))"
        self.cursor.execute(command, (chromosome, variant_end, variant_start))
        result = self.cursor.fetchall()
        return result
    
    def insert_variant_literature(self, variant_id, pmid, title, authors, journal, year, source):
        #command = "INSERT INTO variant_literature (variant_id, pmid, title, authors, journal_publisher, year) VALUES (%s, %s, %s, %s, %s, %s)"
        command = "INSERT INTO variant_literature (variant_id, pmid, title, authors, journal_publisher, year, source) \
                    SELECT %s, %s, %s, %s, %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM variant_literature \
                        WHERE `variant_id`=%s AND `pmid`=%s LIMIT 1)"
        self.cursor.execute(command, (variant_id, pmid, title, authors, journal, year, source, variant_id, pmid))
        self.conn.commit()

    def clean_clinvar(self, variant_id):
        command = "DELETE FROM clinvar_variant_annotation WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        self.conn.commit()


    
    def get_most_recent_annotation_type_id(self, title):
        command = "SELECT id FROM annotation_type WHERE title = %s ORDER BY version_date DESC LIMIT 1"
        self.cursor.execute(command, (title, ))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None
    
    def get_variant_annotation(self, variant_id, annotation_type_id):
        command = "SELECT * FROM variant_annotation WHERE variant_id = %s AND annotation_type_id = %s"
        self.cursor.execute(command, (variant_id, annotation_type_id))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        return res

    def get_all_valid_variant_ids(self):
        command = "SELECT id FROM variant"
        self.cursor.execute(command)
        res = self.cursor.fetchall()
        return [x[0] for x in res]

    def get_variant_ids_with_consensus_classification(self):
        command = "SELECT DISTINCT variant_id FROM consensus_classification UNION SELECT DISTINCT variant_id FROM variant_heredicare_annotation WHERE consensus_class is not NULL"
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
        parts = range_constraint.split('-')
        if len(parts) != 3:
            return None, None, None
        chr = parts[0]
        start = int(parts[1])
        end = int(parts[2])
        return chr, start, end
    
    def preprocess_cdna_range(self, cdna_range):
        parts = cdna_range.split(':')
        if len(parts) != 3:
            return None, None, None
        source = parts[0] # transcript
        start, start_modifier, beyond_cds_operation_start = self.preprocess_cdna_position(parts[1], operation_suffix = "start")
        end, end_modifier, beyond_cds_operation_end = self.preprocess_cdna_position(parts[2], operation_suffix = "end")
        return source, start, start_modifier, beyond_cds_operation_start, end, end_modifier, beyond_cds_operation_end
    
    def preprocess_cdna_position(self, position, operation_suffix):
        beyond_cds_operation = None
        modifier = 0

        if position.startswith('*') or position.startswith('-'): # cds position is beyond the cds boundary
            position = position.strip('-').strip('*')
            beyond_cds_operation = "extend_" + operation_suffix 
        elif '-' in position:
            parts = position.split('-')
            position = parts[0]
            modifier = int(parts[1]) * -1
        elif '+' in position:
            parts = position.split('+')
            position = parts[0]
            modifier = int(parts[1])
        return int(position), int(modifier), beyond_cds_operation
        

    def convert_to_gene_id(self, string):
        gene_id = self.get_gene_id_by_symbol(string)
        if gene_id is None:
            gene_id = self.get_gene_id_by_hgnc_id(string)
        return gene_id # can return none
    
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

    def convert_to_hgnc_id(self, string):
        if self.is_hgnc(string):
            return string
        hgnc_id = self.get_hgnc_id_by_gene(string)
        return hgnc_id
    
    def get_hgnc_id_by_gene(self, string):
        command = "SELECT hgnc_id FROM gene WHERE symbol = %s"
        self.cursor.execute(command, (string, ))
        result = self.cursor.fetchone()
        if result is None: # search for alternative or outdated symbols
            command = "SELECT (SELECT hgnc_id FROM gene WHERE gene.id = gene_alias.gene_id) hgnc_id FROM gene_alias WHERE alt_symbol = %s"
            self.cursor.execute(command, (string, ))
            result = self.cursor.fetchone()
        if result is not None: # we found one
            hgnc_id = result[0]
            return hgnc_id
        else: # we found nothing
            return None

    def is_hgnc(self, string):
        command = "SELECT hgnc_id FROM gene WHERE hgnc_id = %s"
        self.cursor.execute(command, (string, ))
        result = self.cursor.fetchone()
        if result is None:
            return False
        return True

    def get_variant_more_info(self, variant_id, user_id = None):
        command = "SELECT * FROM variant WHERE id = %s"
        command = self.annotate_genes(command)
        command = self.annotate_consensus_classification(command)
        actual_information = (variant_id, )
        if user_id is not None:
            command = self.annotate_specific_user_classification(command)
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

    def annotate_specific_user_classification(self, command):
        prefix = """
        SELECT g.*, h.user_classification FROM (
        """
        postfix = """
        		) g LEFT JOIN (
                    SELECT user_classification.variant_id, user_classification.classification as user_classification FROM user_classification
                        LEFT JOIN user_classification x ON x.variant_id = user_classification.variant_id AND x.date > user_classification.date
                    WHERE x.variant_id IS NULL AND user_classification.user_id=%s
                    ORDER BY user_classification.variant_id) h ON g.id = h.variant_id ORDER BY chr, pos, ref, alt
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

    ### DEPRECATED!
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
    
    # DEPRECATED
    def order_consequences(self, consequences):
        keyfunc = cmp_to_key(mycmp = self.sort_consequences)
                
        consequences.sort(key = keyfunc) # sort by preferred transcript
        return consequences
    
    # DEPRECATED
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


    def get_variants_page_merged(self, page, page_size, sort_by, include_hidden, user_id, 
                                 ranges = None, genes = None, consensus = None, user = None, automatic = None, hgvs = None, variant_ids_oi = None, external_ids = None, cdna_ranges = None, annotation_restrictions = None, include_heredicare_consensus = False):
        # get one page of variants determined by offset & pagesize
        
        prefix = "SELECT id, chr, pos, ref, alt FROM variant"
        postfix = ""
        actual_information = ()
        if ranges is not None and len(ranges) > 0: # if it is None this means it was not specified or there was an error. If it has len == 0 it means that there was no error but the user did not specify any 
            new_constraints = []
            for range_constraint in ranges:
                chrom, start, end = self.preprocess_range(range_constraint)
                new_constraints.append("(chr=%s AND pos BETWEEN %s AND %s)")
                actual_information += (chrom, start, end)
            new_constraints = ' OR '.join(new_constraints)
            new_constraints = functions.enbrace(new_constraints)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if cdna_ranges is not None and len(cdna_ranges) > 0:
            new_constraints = []
            for cdna_range in cdna_ranges:
                # preprocess range
                source, start, start_modifier, beyond_cds_operation_start, end, end_modifier, beyond_cds_operation_end = self.preprocess_cdna_range(cdna_range)
                transcripts = self.get_transcripts_from_names([source], remove_unknown=True)
                if len(transcripts) == 0:
                    gene_id = self.get_gene_id_by_symbol(source)
                    transcripts = self.get_preferred_transcripts(gene_id, return_all = False)
                #print("Transcripts: " + str(transcripts))
                for transcript in transcripts:
                    chrom = transcript.chrom
                    start_pos = self.cdna_pos_to_genomic_pos(transcript.id, start, transcript.orientation, start_modifier, beyond_cds_operation_start)
                    end_pos = self.cdna_pos_to_genomic_pos(transcript.id, end, transcript.orientation, end_modifier, beyond_cds_operation_end)
                    if transcript.orientation == '-':
                        tmp = start_pos
                        start_pos = end_pos
                        end_pos = tmp
                    if start_pos is None or end_pos is None:
                        start_pos = -1
                        end_pos = -1
                    new_constraints.append("(chr=%s AND pos BETWEEN %s AND %s)")
                    actual_information += (chrom, start_pos, end_pos)
            if len(new_constraints) > 0:
                new_constraints = ' OR '.join(new_constraints)
                new_constraints = functions.enbrace(new_constraints)
            else:
                new_constraints = "(chr='chr1' AND pos BETWEEN 0 AND 0)"
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if annotation_restrictions is not None and len(annotation_restrictions) > 0:
            for annotation_restriction in annotation_restrictions:
                table = annotation_restriction[0]
                annotation_type_id = annotation_restriction[1]
                operation = annotation_restriction[2]
                value = annotation_restriction[3]
                annotation_type_title = annotation_restriction[4]
                if annotation_type_title in ['maxentscan_ref', 'maxentscan_alt']:
                    maxentpart = annotation_type_title[11:]
                    new_constraints = """id IN (SELECT variant_id FROM (
                                            SELECT DISTINCT variant_id,
                                            substring_index((substring_index(`value`,'|',1)),'|',-1) AS ref,
                                            substring_index((substring_index(`value`,'|',2)),'|',-1) AS alt
                                            FROM variant_transcript_annotation WHERE annotation_type_id = %s)split_maxent WHERE """ + maxentpart + " " + operation + """ %s)
                                      """
                    actual_information += (annotation_type_id, value)
                elif annotation_type_title in ['maxentscan_swa_donor_ref', 'maxentscan_swa_donor_alt', 'maxentscan_swa_acceptor_ref', 'maxentscan_swa_acceptor_alt']:
                    maxentpart = annotation_type_title[15:]
                    new_constraints = """id IN (SELECT variant_id FROM (
                                            SELECT DISTINCT variant_id,
                                            substring_index((substring_index(`value`,'|',1)),'|',-1) AS donor_ref,
                                            substring_index((substring_index(`value`,'|',2)),'|',-1) AS donor_alt,
                                            substring_index((substring_index(`value`,'|',4)),'|',-1) AS acceptor_ref,
                                            substring_index((substring_index(`value`,'|',5)),'|',-1) AS acceptor_alt
                                            FROM variant_transcript_annotation WHERE annotation_type_id = %s)split_maxent_swa WHERE """ + maxentpart + " " + operation + """ %s)
                                      """
                    actual_information += (annotation_type_id, value)
                elif annotation_type_title in ["clinvar_interpretation"]:
                    new_constraints = "id IN (SELECT DISTINCT variant_id FROM " + table + " WHERE interpretation " + operation + " %s)"
                    actual_information += (value, )
                elif annotation_type_title in ["heredicare_n_fam", "heredicare_n_pat"]:
                    column_oi = annotation_type_title[11:]
                    new_constraints = "id IN (SELECT DISTINCT variant_id FROM " + table + " WHERE " + column_oi + " " + operation + " %s)"
                    actual_information += (value, )
                else:
                    new_constraints = "id IN (SELECT DISTINCT variant_id FROM " + table + " WHERE annotation_type_id = %s AND value " + operation + " %s)"
                    actual_information += (annotation_type_id, value)
                postfix = self.add_constraints_to_command(postfix, new_constraints)
        if genes is not None and len(genes) > 0:
            #genes = [self.get_gene(self.convert_to_gene_id(x))[1] for x in genes]
            hgnc_ids = set()
            for gene in genes:
                current_gene_id = self.convert_to_gene_id(gene)
                if current_gene_id is not None:
                    new_hgnc = self.get_gene(current_gene_id)[1]
                    hgnc_ids.add(new_hgnc)
            if len(hgnc_ids) > 0:
                placeholders = ["%s"] * len(hgnc_ids)
                placeholders = ', '.join(placeholders)
                placeholders = functions.enbrace(placeholders)
                new_constraints = "id IN (SELECT DISTINCT variant_id FROM variant_consequence WHERE hgnc_id IN " + placeholders + ")"
                actual_information += tuple(hgnc_ids)
                postfix = self.add_constraints_to_command(postfix, new_constraints)
            else:
                return [], 0
        if consensus is not None and len(consensus) > 0:
            new_constraints_inner = ''
            consensus_without_dash = [value for value in consensus if value != '-']
            if '-' in consensus:
                new_constraints_inner = "SELECT id FROM variant WHERE id NOT IN (SELECT variant_id FROM consensus_classification WHERE is_recent=1)"
                if include_heredicare_consensus:
                    new_constraints_inner += " AND id NOT IN (SELECT variant_id FROM variant_heredicare_annotation WHERE consensus_class IS NOT NULL)"
                if len(consensus_without_dash) > 0: # if we have - AND some other class(es) we need to add an or between them
                    new_constraints_inner = new_constraints_inner + " UNION "
            if len(consensus_without_dash) > 0: # if we have one or more classes without the -
                placeholders = self.get_placeholders(len(consensus_without_dash))
                new_constraints_inner = new_constraints_inner + "SELECT variant_id FROM consensus_classification WHERE classification IN " + placeholders + " AND is_recent = 1"
                actual_information += tuple(consensus_without_dash)
            new_constraints = "variant.id IN (" + new_constraints_inner + ")"
            #postfix = self.add_constraints_to_command(postfix, new_constraints)
            constraints_complete = new_constraints
            if include_heredicare_consensus and len(consensus_without_dash) > 0:
                heredicare_consensus = []
                for c in consensus_without_dash:
                    heredicare_consensus.extend(functions.num2heredicare(c))
                placeholders1 = self.get_placeholders(len(heredicare_consensus))
                placeholders2 = self.get_placeholders(len(consensus_without_dash))
                new_constraints = "variant.id IN (SELECT variant_id FROM variant_heredicare_annotation WHERE consensus_class IN " + placeholders1 +  " AND variant_id NOT IN (SELECT variant_id FROM consensus_classification WHERE classification NOT IN " + placeholders2 + " AND is_recent = 1))"
                actual_information += tuple(heredicare_consensus)
                actual_information += tuple(consensus_without_dash)
                constraints_complete = functions.enbrace(constraints_complete + " OR " + new_constraints)
            postfix = self.add_constraints_to_command(postfix, constraints_complete)
        if user is not None and len(user) > 0:
            new_constraints_inner = ''
            user_without_dash = [value for value in user if value != '-']
            if '-' in user:
                new_constraints_inner = "SELECT id FROM variant WHERE id NOT IN (SELECT variant_id FROM user_classification WHERE user_id=%s AND deleted_date IS NULL)"
                actual_information += (user_id, )
                if len(user_without_dash) > 0: # if we have - AND some other class(es) we need to add an or between them
                    new_constraints_inner = new_constraints_inner + " UNION "
            if len(user_without_dash) > 0: # if we have one or more classes without the -
                placeholders = self.get_placeholders(len(user_without_dash))
                # search for the most recent user classifications from the user which is searching for variants and which are in the list of user classifications (variable: user)
                new_constraints_inner = new_constraints_inner + "SELECT * FROM ( SELECT user_classification.variant_id FROM user_classification \
                                                                LEFT JOIN user_classification uc ON uc.variant_id = user_classification.variant_id AND uc.date > user_classification.date \
                                                                    WHERE uc.variant_id IS NULL AND user_classification.user_id=%s AND uc.deleted_date IS NULL AND user_classification.classification IN " + placeholders + " \
                                                                ORDER BY user_classification.variant_id )ub"
                actual_information += (user_id, )
                actual_information += tuple(user_without_dash)
            new_constraints = "id IN (" + new_constraints_inner + ")"
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if automatic is not None and len(automatic) > 0:
            new_constraints_inner = ''
            automatic_without_dash = [value for value in automatic if value != '-']
            if '-' in automatic:
                new_constraints_inner = "SELECT id FROM variant WHERE id NOT IN (SELECT variant_id FROM automatic_classification)"
                if len(automatic_without_dash) > 0: # if we have - AND some other class(es) we need to add an or between them
                    new_constraints_inner = new_constraints_inner + " UNION "
            if len(automatic_without_dash) > 0: # if we have one or more classes without the -
                placeholders = self.get_placeholders(len(automatic_without_dash))
                # search for the most recent user classifications from the user which is searching for variants and which are in the list of user classifications (variable: user)
                new_constraints_inner = new_constraints_inner + "SELECT variant_id FROM automatic_classification WHERE classification IN " + placeholders
                actual_information += tuple(automatic_without_dash)
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
            placeholders = functions.enbrace(placeholders)
            new_constraints = "id IN " + placeholders
            actual_information += tuple(all_variants)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if external_ids is not None and len(external_ids) > 0:
            ids_unknown_source = []
            ids_known_source = {}
            for external_id in external_ids:
                # handle rsids
                if external_id.startswith('rs') or external_id[-5:].lower() == ':rsid':
                    external_id = external_id.strip('rs').strip(':rsid')
                    functions.extend_dict(ids_known_source, 'rsid', external_id)
                    continue
                if external_id.startswith('COSV') or external_id[-7:].lower() == ':cosmic':
                    external_id = external_id.strip(':cosmic')
                    functions.extend_dict(ids_known_source, 'cosmic', external_id)
                    continue
                if external_id[-8:].lower() == ':clinvar':
                    external_id = external_id.strip(':clinvar')
                    functions.extend_dict(ids_known_source, 'clinvar', external_id)
                    continue
                if external_id[-11:] == ':heredicare':
                    external_id = external_id.strip(':heredicare')
                    functions.extend_dict(ids_known_source, 'heredicare_vid', external_id)
                    continue
                ids_unknown_source.append(external_id)
            new_constraints = []

            for id_source in ids_known_source:
                annotation_type_id = self.get_most_recent_annotation_type_id(id_source)
                current_external_ids = ids_known_source[id_source]
                placeholders = self.get_placeholders(len(current_external_ids))
                new_constraints.append("id IN (SELECT variant_id FROM variant_ids WHERE external_id IN " + placeholders + " AND annotation_type_id = %s )")
                actual_information += tuple(current_external_ids)
                actual_information += (annotation_type_id, )

            if len(ids_unknown_source) > 0:
                placeholders = self.get_placeholders(len(ids_unknown_source))
                new_constraints.append("id IN (SELECT variant_id FROM variant_ids WHERE external_id IN " + placeholders + ")")
                actual_information += tuple(ids_unknown_source)
            new_constraints = ' OR '.join(new_constraints)
            postfix = self.add_constraints_to_command(postfix, new_constraints)


        if variant_ids_oi is not None and len(variant_ids_oi) > 0:
            placeholders = ["%s"] * len(variant_ids_oi)
            placeholders = ', '.join(placeholders)
            placeholders = functions.enbrace(placeholders)
            new_constraints = "id IN " + placeholders
            actual_information += tuple(variant_ids_oi)
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        if not include_hidden:
            new_constraints = " variant.is_hidden = 0"
            postfix = self.add_constraints_to_command(postfix, new_constraints)
        
        command = prefix + postfix        
        if sort_by == 'genomic position':
            command += " ORDER BY chr, pos, ref, alt"
        elif sort_by == 'recent':
            command += " ORDER BY id DESC"
        if page_size != 'unlimited':
            page_size = int(page_size)
            offset = (page - 1) * page_size
            command = command + " LIMIT %s, %s"
            actual_information += (offset, page_size)
        #print(command % actual_information)
        self.cursor.execute(command, actual_information)
        variants_raw = self.cursor.fetchall()

        # get variant objects
        variants = []
        for variant_raw in variants_raw:
            variant = self.get_variant(variant_id=variant_raw[0], include_annotations = False, include_heredicare_classifications = True, include_clinvar = False, include_assays = False, include_literature = False)
            variants.append(variant)

        if page_size == 'unlimited':
            return variants, len(variants)

        # get number of variants
        prefix = "SELECT COUNT(id) FROM variant"
        command = prefix + postfix
        self.cursor.execute(command, actual_information[:len(actual_information)-2])
        num_variants = self.cursor.fetchone()
        if num_variants is None:
            return [], 0
        return variants, num_variants[0]


    def cdna_pos_to_genomic_pos(self, transcript_id, cdna_pos, orientation, modifier = 0, beyond_cds_operation = None):
        command = "SELECT start, end, cdna_start, cdna_end  FROM exon WHERE transcript_id = %s"
        actual_information = (transcript_id, )
        if beyond_cds_operation is not None:
            if beyond_cds_operation == 'extend_end':
                sort_by = "DESC"
            if beyond_cds_operation == 'extend_start':
                sort_by = "ASC"
            command = self.add_constraints_to_command(command, "is_cds = 1 ORDER BY cdna_start " + sort_by + " LIMIT 1")
        else:
            command = self.add_constraints_to_command(command, "cdna_start <= %s AND cdna_end >= %s")
            actual_information += (cdna_pos, cdna_pos)
            #command = "SELECT start, cdna_start FROM exon WHERE transcript_id = %s AND cdna_start <= %s AND cdna_end >= %s"
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchone()
        if result is None:
            return None
        genomic_start = int(result[0])
        genomic_end = int(result[1])
        cdna_start = int(result[2])
        cdna_end = int(result[3])
        cdna_pos = int(cdna_pos)

        if orientation == '-':
            if beyond_cds_operation is not None:
                if beyond_cds_operation == 'extend_end': # modifier is always 0
                    genomic_pos = genomic_start - cdna_pos
                if beyond_cds_operation == 'extend_start': # cdna_start is always 1 in this case, modifier is always 0
                    genomic_pos = genomic_end + cdna_pos
            else:
                genomic_pos = genomic_start + (cdna_end - cdna_pos) + (modifier * -1)
        elif orientation == '+':
            if beyond_cds_operation is not None:
                if beyond_cds_operation == 'extend_end': # modifier is always 0
                    genomic_pos = genomic_end + cdna_pos
                if beyond_cds_operation == 'extend_start': # cdna_start is always 1 in this case, modifier is always 0
                    genomic_pos = genomic_start - cdna_pos
            else:
                genomic_pos = cdna_pos - cdna_start + genomic_start + modifier
        return genomic_pos




    def get_variant_ids_from_gene_and_hgvs(self, gene, hgvs_c, source = 'ensembl'):
        hgnc_id = self.convert_to_hgnc_id(gene)

        command = "SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,exon_nr,intron_nr,symbol,z.hgnc_id,source,pfam_accession,pfam_description,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags,biotype,variant_id  FROM transcript RIGHT JOIN ( \
                        SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,symbol,y.hgnc_id,exon_nr,intron_nr,source,pfam_accession,pfam_description,variant_id FROM gene RIGHT JOIN ( \
                            SELECT * FROM variant_consequence INNER JOIN ( \
	                            SELECT DISTINCT variant_id as variant_id_trash FROM variant_consequence WHERE source = %s AND hgnc_id = %s AND hgvs_c = %s \
                            ) x ON x.variant_id_trash = variant_consequence.variant_id  \
                        ) y ON gene.hgnc_id = y.hgnc_id \
                    ) z ON transcript.name = z.transcript_name WHERE z.hgnc_id=%s ORDER BY variant_id asc"
        #print(command % (source, hgnc_id, hgvs_c, hgnc_id))
        self.cursor.execute(command, (source, hgnc_id, hgvs_c, hgnc_id))
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
            submission_conditions = processed_entry[5].split(';')
            submission_conditions = [self.preprocess_submission_condition(submission_condition) for submission_condition in submission_conditions]

            processed_entry[5] = submission_conditions
            result[i] = processed_entry
        
        #result = sorted(result, key=lambda x: x[3] or datetime.date(datetime.MINYEAR,1,1), reverse=True) # sort table by last evaluated date

        return result

    def preprocess_submission_condition(self, submission_condition):
        submission_condition = submission_condition.split(':')
        if len(submission_condition) == 1:
            submission_condition.append("missing")
        elif len(submission_condition) > 2:
            functions.eprint("WARNING: the clinvar submission condition: " + str(submission_condition) + " has more than two entries. Although it should only have 2: id and description. Will be neglecting everything after the first two entries.")
            submission_condition = submission_condition[0:2]
        return submission_condition
    
    def get_variant_consequences(self, variant_id):
        command = "SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,exon_nr,intron_nr,symbol,x.gene_id,source,pfam_accession,pfam_description,length,is_gencode_basic,is_mane_select,is_mane_plus_clinical,is_ensembl_canonical,is_gencode_basic+is_mane_select+is_mane_plus_clinical+is_ensembl_canonical total_flags,biotype,transcript.id,start,end,transcript.chrom,orientation FROM transcript RIGHT JOIN ( \
	                    SELECT transcript_name,hgvs_c,hgvs_p,consequence,impact,symbol,gene.id gene_id,exon_nr,intron_nr,source,pfam_accession,pfam_description FROM gene RIGHT JOIN ( \
		                    SELECT * FROM variant_consequence WHERE variant_id=%s \
	                    ) y \
	                    ON gene.hgnc_id = y.hgnc_id \
                    ) x \
                    ON transcript.name = x.transcript_name"
        #import time
        #start_time = time.time()
        self.cursor.execute(command, (variant_id, ))
        #print("--- consequences: %s seconds ---" % (time.time() - start_time))
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

    def get_gene_ids_with_variants(self):
        command = "SELECT gene_id AS symbol FROM transcript WHERE name in (SELECT transcript_name FROM variant_consequence) GROUP BY gene_id"
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return [x[0] for x in result]

    def get_transcripts(self, gene_id):
        command = "SELECT id, gene_id, (SELECT symbol FROM gene WHERE transcript.gene_id = gene.id), name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, start, end, chrom, orientation FROM transcript WHERE gene_id = %s"
        self.cursor.execute(command, (gene_id, ))
        raw_transcripts = self.cursor.fetchall()
        transcripts = [self.convert_raw_transcript(raw_transcript) for raw_transcript in raw_transcripts]
        return transcripts
    
    def convert_raw_transcript(self, raw_transcript):
        return models.Transcript(
            id = int(raw_transcript[0]),
            gene = models.Gene(id = raw_transcript[1], symbol = raw_transcript[2]),
            name = raw_transcript[3],
            biotype = raw_transcript[4],
            length = int(raw_transcript[5]),
            chrom = raw_transcript[12],
            start = int(raw_transcript[10]),
            end = int(raw_transcript[11]),
            orientation = raw_transcript[13],
            source = "ensembl" if raw_transcript[3].startswith('ENST') else "refseq",
            is_gencode_basic = True if raw_transcript[6] == 1 else False,
            is_mane_select = True if raw_transcript[7] == 1 else False,
            is_mane_plus_clinical = True if raw_transcript[8] == 1 else False,
            is_ensembl_canonical = True if raw_transcript[9] == 1 else False
        )

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

    def insert_consensus_classification(self, user_id, variant_id, consensus_classification, comment, evidence_document, date, scheme_id, scheme_class):
        self.invalidate_previous_consensus_classifications(variant_id)
        command = "INSERT INTO consensus_classification (user_id, variant_id, classification, comment, date, evidence_document, classification_scheme_id, scheme_class) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (user_id, variant_id, str(consensus_classification), comment, date, evidence_document.decode(), scheme_id, scheme_class))
        self.conn.commit()

    def update_consensus_classification_report(self, consensus_classification_id, report):
        command = "UPDATE consensus_classification SET evidence_document = %s WHERE id = %s"
        self.cursor.execute(command, (report, consensus_classification_id))
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
    
    def get_variant_id_from_external_id(self, external_id, annotation_type_id): #!! assumed that the external_id column contains unique entries for id, id_source pairs!
        command = "SELECT variant_id FROM variant_ids WHERE external_id = %s AND annotation_type_id = %s"
        self.cursor.execute(command, (external_id, annotation_type_id))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return result
    


    def get_consensus_classification(self, variant_id, most_recent = False, sql_modifier=None): # it is possible to have multiple consensus classifications
        command = "SELECT id,user_id,variant_id,classification,comment,date,is_recent,classification_scheme_id,scheme_class FROM consensus_classification WHERE variant_id = %s"
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

    def get_user_classifications(self, variant_id, user_id = 'all', scheme_id = 'all', sql_modifier = None):
        command = "SELECT id, classification, variant_id, user_id, comment, date, classification_scheme_id, scheme_class FROM user_classification WHERE variant_id=%s AND deleted_date IS NULL"
        actual_information = (variant_id, )
        if user_id != 'all':
            command = command + ' AND user_id=%s'
            actual_information += (user_id, )
        if scheme_id != 'all':
            command += ' AND classification_scheme_id = %s'
            actual_information += (scheme_id, )

        if sql_modifier is not None:
            command = sql_modifier(command)

        self.cursor.execute(command, actual_information)
        user_classifications = self.cursor.fetchall()
        if len(user_classifications) == 0:
            return None
        return user_classifications

    def delete_user_classification(self, user_classification_id):
        command = "UPDATE user_classification SET deleted_date = %s WHERE id = %s"
        self.cursor.execute(command, (functions.get_now(), user_classification_id))
        self.conn.commit()


    def add_classification_scheme_info(self, command):
        prefix = 'SELECT * FROM (('
        postfix = ') cs_a INNER JOIN (SELECT id as outer_id, name, display_name, type, reference FROM classification_scheme) cs_b ON cs_a.classification_scheme_id = cs_b.outer_id)'
        result = prefix + command + postfix
        return result


    
    def get_evidence_document(self, consensus_classificatoin_id):
        command = "SELECT evidence_document FROM consensus_classification WHERE id = %s"
        self.cursor.execute(command, (consensus_classificatoin_id, ))
        result = self.cursor.fetchone()
        return result

    def get_classification_criterium_id(self, scheme_id, classification_criterium_name):
        #classification_scheme_id = self.get_scheme_id_from_scheme_name(scheme)
        command = "SELECT id FROM classification_criterium WHERE name = %s and classification_scheme_id = %s"
        self.cursor.execute(command, (classification_criterium_name, scheme_id))
        classification_criterium_id = self.cursor.fetchone()
        if classification_criterium_id is not None:
            return classification_criterium_id[0]
        return None


    def get_classification_criterium_strength_id(self, classification_criterium_id, classification_criterium_strength_name):
        command = "SELECT id FROM classification_criterium_strength WHERE name = %s and classification_criterium_id = %s"
        self.cursor.execute(command, (classification_criterium_strength_name, classification_criterium_id))
        classification_criterium_strength_id = self.cursor.fetchone()
        if classification_criterium_strength_id is None:
            return -1
        return classification_criterium_strength_id[0]
    
    def get_classification_criterium_strength(self, classification_criterium_strength_id):
        command = "SELECT * FROM classification_criterium_strength WHERE id = %s"
        self.cursor.execute(command, (classification_criterium_strength_id, ))
        result = self.cursor.fetchone()
        return result

    def insert_scheme_criterium_applied(self, classification_id, classification_criterium_id, criterium_strength_id, evidence, where="user"):
        if where == "user":
            command = "INSERT INTO user_classification_criteria_applied (user_classification_id"
        elif where == "consensus":
            command = "INSERT INTO consensus_classification_criteria_applied (consensus_classification_id"
        else:
            functions.eprint("no valid \"where\" given in insert_scheme_criterium function. It was: " + str(where))
            return
        command = command + ", classification_criterium_id, criterium_strength_id, evidence) VALUES (%s, %s, %s, %s)"
        actual_information = (classification_id, classification_criterium_id, criterium_strength_id, evidence)
        self.cursor.execute(command, actual_information)
        self.conn.commit()

        

    def get_scheme_criteria_applied(self, classification_id, where="user"):
        if where == "user":
            # command = "SELECT * FROM user_classification_criteria_applied WHERE user_classification_id=%s"
            table_oi = "user_classification_criteria_applied"
            prefix = "user"
        elif where == "consensus":
            table_oi = "consensus_classification_criteria_applied"
            prefix = "consensus"
        else:
            functions.eprint("no valid \"where\" given in insert_scheme_criterium function. It was: " + str(where))
            return
        command = "SELECT y.id,y." + prefix + "_classification_id,y.classification_criterium_id,y.criterium_strength_id,y.evidence,y.name as classification_criterium_name,classification_criterium_strength.name as classification_criterium_strength_name, classification_criterium_strength.description, classification_criterium_strength.display_name FROM classification_criterium_strength INNER JOIN ( \
                    SELECT id," + prefix + "_classification_id,classification_criterium_id,criterium_strength_id,evidence,name FROM " + table_oi + " \
	                    INNER JOIN (SELECT id as inner_id,name FROM classification_criterium)x \
                    ON x.inner_id = " + table_oi + ".classification_criterium_id WHERE " + prefix + "_classification_id=%s\
                    )y ON y.criterium_strength_id = classification_criterium_strength.id"
        self.cursor.execute(command, (classification_id, ))
        result = self.cursor.fetchall()
        return result

    def update_scheme_criterium_applied(self, scheme_criterium_id, updated_strength, updated_evidence, where="user"):
        if where == "user":
            command = "UPDATE user_classification_criteria_applied"
        elif where == "consensus":
            command = "UPDATE consensus_classification_criteria_applied"
        else:
            functions.eprint("no valid \"where\" given in insert_scheme_criterium function. It was: " + str(where))
            return
        command = command + " SET criterium_strength_id=%s, evidence=%s WHERE id=%s"
        self.cursor.execute(command, (updated_strength, updated_evidence, scheme_criterium_id))
        self.conn.commit()


    def delete_scheme_criterium_applied(self, scheme_criterium_id, where="user"):
        if where == "user":
            command = "DELETE FROM user_classification_criteria_applied WHERE id=%s"
        elif where == "consensus":
            command = "DELETE FROM consensus_classification_criteria_applied WHERE id=%s"
        else:
            functions.eprint("no valid \"where\" given in insert_scheme_criterium function. It was: " + str(where))
            return
        self.cursor.execute(command, (scheme_criterium_id, ))
        self.conn.commit()





    def update_classification_date(self, scheme_classification_id, current_datetime):
        command = "UPDATE user_classification SET date=%s WHERE id=%s"
        self.cursor.execute(command, (current_datetime, scheme_classification_id))
        self.conn.commit()

    def get_classification_scheme(self, scheme_id):
        command = "SELECT id,name,display_name,type,reference,is_active,is_default from classification_scheme WHERE id = %s"
        self.cursor.execute(command, (scheme_id, ))
        scheme = self.cursor.fetchone()
        return scheme

    def get_all_classification_schemes(self):
        command = "SELECT id,name, display_name,type,reference,is_active,is_default FROM classification_scheme"
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        result = [self.convert_raw_scheme(raw_scheme) for raw_scheme in result]
        return result
    
    def convert_raw_scheme(self, raw_scheme):
        return models.Scheme(id = raw_scheme[0],
                             display_name = raw_scheme[2],
                             type = raw_scheme[3],
                             criteria = [],
                             reference = raw_scheme[4],
                             selected_class = '-',
                             is_active = True if raw_scheme[5] == 1 else False,
                             is_default = True if raw_scheme[6] == 1 else False
                             )
    
    def update_active_state_classification_scheme(self, scheme_id, is_active):
        command = "UPDATE classification_scheme SET is_active = %s WHERE id = %s"
        self.cursor.execute(command, (is_active, scheme_id))
        self.conn.commit()

    def set_default_scheme(self, scheme_id):
        command = "UPDATE classification_scheme SET is_default = 0 WHERE is_default = 1"
        self.cursor.execute(command)
        self.conn.commit()

        command = "UPDATE classification_scheme SET is_default = 1 WHERE id = %s"
        self.cursor.execute(command, (scheme_id, ))
        self.conn.commit()

    def insert_user_classification(self, variant_id, classification, user_id, comment, date, scheme_id, scheme_class):
        command = "INSERT INTO user_classification (variant_id, classification, user_id, comment, date, classification_scheme_id, scheme_class) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, str(classification), user_id, comment, date, scheme_id, str(scheme_class)))
        self.conn.commit()

    def update_user_classification(self, user_classification_id, classification, comment, date, scheme_class):
        command = "UPDATE user_classification SET classification = %s, comment = %s, date = %s, scheme_class = %s WHERE id = %s"
        self.cursor.execute(command, (str(classification), comment, date, str(scheme_class), user_classification_id))
        self.conn.commit()

    #def delete_variant(self, variant_id):
    #    status = "deleted"
    #    message  = "Deleted variant " + str(variant_id)
    #    consensus_classification = self.get_consensus_classification(variant_id)
    #    if consensus_classification is None:
    #        consensus_classification = []
    #    if len(consensus_classification) > 0: # do not delete if the variant has a consensus classification
    #        status = "skipped"
    #        message = "Did not delete variant because it has consensus classifications"
    #        return status, message
    #    user_classifications = self.get_user_classifications(variant_id)
    #    if user_classifications is None:
    #        user_classifications = []
    #    if len(user_classifications) > 0: # do not delete if the variant has a user classification
    #        status = "skipped"
    #        message = "Did not delete variant because it has user classifications"
    #        return status, message
    #    command = "DELETE FROM variant WHERE id = %s"
    #    self.cursor.execute(command, (variant_id,))
    #    self.conn.commit()
    #    return status, message

    #def get_orig_variant(self, variant_id):
    #    command = "SELECT orig_chr, orig_pos, orig_ref, orig_alt FROM variant WHERE id = %s"
    #    self.cursor.execute(command, (variant_id, ))
    #    res = self.cursor.fetchone()
    #    return res




    def insert_import_request(self, user_id):
        command = "INSERT INTO import_queue (user_id) VALUES (%s)"
        self.cursor.execute(command, (user_id, ))
        self.conn.commit()
        return self.get_most_recent_import_request()
    
    def get_most_recent_import_request(self):
        self.cursor.execute("SELECT id, user_id, requested_at, status, finished_at, message FROM import_queue WHERE status != 'error' ORDER BY requested_at DESC LIMIT 1")
        import_request_raw = self.cursor.fetchone()
        import_request = self.convert_raw_import_request(import_request_raw)
        return import_request
    
    def get_import_request(self, import_queue_id):
        command = "SELECT id, user_id, requested_at, status, finished_at, message FROM import_queue WHERE id = %s"
        self.cursor.execute(command, (import_queue_id, ))
        import_request_raw = self.cursor.fetchone()
        import_request = self.convert_raw_import_request(import_request_raw)
        return import_request

    def get_import_request_overview(self):
        command = "SELECT id FROM import_queue ORDER BY requested_at DESC"
        self.cursor.execute(command)
        import_queue_ids = self.cursor.fetchall()
        import_requests = [self.get_import_request(import_queue_id[0]) for import_queue_id in import_queue_ids]
        return import_requests


    
    def get_max_finished_at_import_variant(self, import_queue_id):
        command = "SELECT MAX(finished_at) FROM import_variant_queue WHERE import_queue_id = %s"
        self.cursor.execute(command, (import_queue_id, ))
        result = self.cursor.fetchone()
        return result[0]
    
    def get_number_of_import_variants(self, import_queue_id):
        command = "SELECT COUNT(id) FROM import_variant_queue WHERE import_queue_id = %s"
        self.cursor.execute(command, (import_queue_id, ))
        result = self.cursor.fetchone()
        return result[0]

    def convert_raw_import_request(self, import_request_raw):
        if import_request_raw is None:
            return None
        import_queue_id = import_request_raw[0]
        user = self.parse_raw_user(self.get_user(import_request_raw[1]))
        variant_summary = self.get_variant_summary(import_queue_id)
        num_var = self.get_number_of_import_variants(import_queue_id)
        requested_at = import_request_raw[2] # datetime object
        import_variant_list_finished_at = import_request_raw[4] # datetime object

        import_variant_list_status = import_request_raw[3]

        #1. pending: from status of import
        #2. fetching vids: status of import is processing
        #3. fetching variants: status of import is success and there are still non finished variants
        #4. error: import status is error
        #5. success: all variants are processed and
        status = "unknown"
        finished_at = None
        if import_variant_list_status == "retry":
            status = "retry"
        elif import_variant_list_status == "pending":
            status = "pending"
        elif import_variant_list_status == "progress":
            status = "fetching vids"
        elif import_variant_list_status == "success" and any([key_oi in variant_summary for key_oi in ["pending", "progress"]]):
            status = "fetching variants"
        elif import_variant_list_status  == "error":
            status = "error"
            finished_at = import_variant_list_finished_at
        elif import_variant_list_status == "success":
            status = "finished"
            finished_at = self.get_max_finished_at_import_variant(import_queue_id)
            if finished_at is None: # there are no variants 
                finished_at = import_variant_list_finished_at

        result = models.import_request(id = import_queue_id, 
                                       user = user, 
                                       requested_at = requested_at, 
                                       status = status, 
                                       finished_at = finished_at,
                                       total_variants = num_var,
                                       import_variant_list_status = import_variant_list_status,
                                       import_variant_list_finished_at = import_variant_list_finished_at,
                                       import_variant_list_message = import_request_raw[5],
                                       variant_summary = variant_summary
                                    )
        return result
    
    def get_variant_summary(self, import_queue_id):
        command = "SELECT count(*) as count, status from import_variant_queue WHERE import_queue_id = %s GROUP BY status"
        self.cursor.execute(command, (import_queue_id, ))
        result_raw = self.cursor.fetchall()
        result = {}
        for elem in result_raw:
            result[elem[1]] = elem[0]
        return result
    
    def update_import_queue_status(self, import_queue_id, status, message):
        command = "UPDATE import_queue SET status = %s, message = %s WHERE id = %s"
        self.cursor.execute(command, (status, message, import_queue_id))
        self.conn.commit()

    def update_import_queue_celery_task_id(self, import_queue_id, celery_task_id):
        command = "UPDATE import_queue SET celery_task_id = %s WHERE id = %s"
        self.cursor.execute(command, (celery_task_id, import_queue_id))
        self.conn.commit()

    def close_import_request(self, import_queue_id, status, message):
        self.update_import_queue_status(import_queue_id, status, message)
        command = "UPDATE import_queue SET finished_at = NOW() WHERE id = %s" # \"1999-01-01 00:00:00\"
        self.cursor.execute(command, (import_queue_id, ))
        self.conn.commit()





    def insert_variant_import_request(self, vid, import_queue_id):
        command = "INSERT INTO import_variant_queue (vid, import_queue_id) VALUES (%s, %s)"
        self.cursor.execute(command, (vid, import_queue_id))
        self.conn.commit()
        return self.get_last_insert_id()
    
    def update_import_variant_queue_celery_id(self, variant_import_queue_id, celery_task_id):
        command = "UPDATE import_variant_queue SET celery_task_id = %s WHERE id = %s"
        self.cursor.execute(command, (celery_task_id, variant_import_queue_id))
        self.conn.commit()

    def update_import_variant_queue_status(self, variant_import_queue_id, status, message):
        command = "UPDATE import_variant_queue SET status = %s, message = %s WHERE id = %s"
        self.cursor.execute(command, (status, message, variant_import_queue_id))
        self.conn.commit()

    def close_import_variant_request(self, variant_import_queue_id, status, message):
        self.update_import_variant_queue_status(variant_import_queue_id, status, message)
        command = "UPDATE import_variant_queue SET finished_at = NOW() WHERE id = %s"
        self.cursor.execute(command, (variant_import_queue_id, ))
        self.conn.commit()

    def get_imported_variants(self, import_queue_id, status = None):
        command = "SELECT id, status, requested_at, finished_at, message, vid FROM import_variant_queue WHERE import_queue_id = %s"
        actual_information = (import_queue_id, )
        if status is not None:
            command += " AND status IN " + self.get_placeholders(len(status))
            actual_information += tuple(status)
        #print(command % actual_information)
        self.cursor.execute(command, actual_information)
        raw_results = self.cursor.fetchall()
        return [self.convert_raw_import_variant_request(raw_result) for raw_result in raw_results]

    def get_single_vid_imports(self):
        command = "SELECT id, status, requested_at, finished_at, message, vid FROM import_variant_queue WHERE import_queue_id is NULL"
        self.cursor.execute(command)
        raw_results = self.cursor.fetchall()
        return [self.convert_raw_import_variant_request(raw_result) for raw_result in raw_results]
        

    def convert_raw_import_variant_request(self, import_variant_request_raw):
        if import_variant_request_raw is None:
            return None
        requested_at = import_variant_request_raw[2] # datetime object
        finished_at = import_variant_request_raw[3] # datetime object
        result = models.Import_variant_request(id = import_variant_request_raw[0], 
                                               status = import_variant_request_raw[1], 
                                               requested_at = requested_at, 
                                               finished_at = finished_at, 
                                               message = import_variant_request_raw[4], 
                                               vid = import_variant_request_raw[5]
                                            )
        return result


    #returns a list of tuples with all information for each external id
    def get_all_external_ids(self, variant_id):
        command = """
            SELECT variant_ids.id, title, description, version, version_date, variant_id, external_id, group_name, display_title, value_type FROM variant_ids INNER JOIN ( 
                SELECT * 
	                FROM annotation_type WHERE (title, version_date) IN ( 
		                select title, MAX(version_date) version_date from annotation_type INNER JOIN ( 
			                select variant_id, annotation_type_id, external_id from variant_ids where variant_id=%s
			        ) x 
			        ON annotation_type.id = x.annotation_type_id 
		            GROUP BY title 
	            )  
            ) y  
            ON y.id = variant_ids.annotation_type_id 
            WHERE variant_id=%s AND group_name = 'ID'
        """
        self.cursor.execute(command, (variant_id, variant_id))
        result = self.cursor.fetchall()
        return result

    def get_all_external_ids_from_annotation_type(self, annotation_type_id):
        command = "SELECT external_id FROM variant_ids WHERE annotation_type_id = %s"
        self.cursor.execute(command, (annotation_type_id, ))
        result = self.cursor.fetchall()
        return [x[0] for x in result]
    
    # returns a list of external ids of a specific type
    def get_external_ids_from_variant_id(self, variant_id, annotation_type_id):
        command = "SELECT external_id FROM variant_ids WHERE variant_id = %s AND annotation_type_id = %s"
        information = (variant_id, annotation_type_id)
        self.cursor.execute(command, information)
        result = self.cursor.fetchall()
        return [x[0] for x in result]

    def delete_external_id(self, external_id, annotation_type_id, variant_id = None):
        command = "DELETE FROM variant_ids WHERE external_id = %s AND annotation_type_id = %s"
        actual_information = (external_id, annotation_type_id)
        if variant_id is not None:
            command += " AND variant_id = %s"
            actual_information += (variant_id, )
        self.cursor.execute(command, actual_information)
        self.conn.commit()

    def update_variant_annotation(self, variant_id, annotation_type_id, value): # use with caution!
        command = "UPDATE variant_annotation SET value = %s  WHERE variant_id = %s AND annotation_type_id = %s"
        self.cursor.execute(command, (value, variant_id, annotation_type_id))
        self.conn.commit()

    """
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
    """

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
        #            SELECT %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM user \
        #                WHERE `username`=%s LIMIT 1)"
        command = "INSERT INTO user (username, first_name, last_name, affiliation) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE first_name=%s, last_name=%s, affiliation=%s"
        self.cursor.execute(command, (username, first_name, last_name, affiliation, first_name, last_name, affiliation))
        self.conn.commit()
    
    def get_user(self, user_id):
        command = "SELECT id,username,first_name,last_name,affiliation FROM user WHERE id=%s"
        self.cursor.execute(command, (user_id,))
        result = self.cursor.fetchone()
        return result
    
    def parse_raw_user(self, raw_user):
        return models.User(id = raw_user[0], 
                   full_name = raw_user[2] + ' ' + raw_user[3], 
                   affiliation = raw_user[4])
    
    def get_user_id(self, username):
        command = "SELECT id FROM user WHERE username=%s"
        self.cursor.execute(command, (username, ))
        result = self.cursor.fetchone()[0]
        return result

    def insert_user_variant_list(self, user_id, list_name, public_read, public_edit):
        command = "INSERT INTO user_variant_lists (user_id, name, public_read, public_edit) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(command, (user_id, list_name, public_read, public_edit))
        self.conn.commit()
        return self.get_last_insert_id()

    # if you set a variant id the result will contain information if this variant is contained in the list or not (list[3] != None ==> variant is conatined in list)
    def get_lists_for_user(self, user_id, variant_id = None, is_editable = False):
        command = "SELECT * FROM user_variant_lists"
        actual_information = ()
        if variant_id is not None:
            command = command + " LEFT JOIN (SELECT list_id FROM list_variants WHERE variant_id=%s) x ON user_variant_lists.id = x.list_id"
            actual_information = actual_information + (variant_id, )
        command = command + " WHERE user_id = %s OR public_read = 1"
        if is_editable:
            command = command + " OR public_edit = 1"
        command = command + " ORDER BY id DESC"
        actual_information = actual_information + (user_id, )
        self.cursor.execute(command, actual_information)
        result = self.cursor.fetchall()

        for i in range(len(result)):
            current_list = result[i]
            is_owner = 0
            if current_list[1] == user_id:
                is_owner = 1
            current_list = list(current_list) # convert tuple to list
            current_list.insert(5, is_owner)
            
            if variant_id is None:
                current_list.append('')
            else:
                current_list[-1] = "active" if current_list[-1] is not None else "" # this adds the css class if the variant is in that list -> background color to blue
            result[i] = tuple(current_list) # convert back to tuple
        return result
    
    def get_list_size(self, list_id):
        command = "SELECT COUNT(id) FROM list_variants WHERE list_id = %s"
        self.cursor.execute(command, (list_id, ))
        result = self.cursor.fetchone()[0]
        return result

    def add_variant_to_list(self, list_id, variant_id):
        num_vars_before = self.get_list_size(list_id)
        command = "INSERT INTO list_variants (list_id, variant_id) \
                    SELECT %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM list_variants \
                        WHERE `list_id`=%s AND `variant_id`=%s LIMIT 1)"
        self.cursor.execute(command, (list_id, variant_id, list_id, variant_id))
        self.conn.commit()
        num_vars_after = self.get_list_size(list_id)
        return num_vars_after - num_vars_before # number of new variants

    def get_variant_ids_from_list(self, list_id):
        command = "SELECT variant_id FROM list_variants WHERE list_id=%s"
        self.cursor.execute(command, (list_id, ))
        result = self.cursor.fetchall()
        result = [str(x[0]) for x in result] # extract variant_id
        return result
    
    # list_id to get the right list
    # list_name is the value which will be updated
    def update_user_variant_list(self, list_id, new_list_name, public_read, public_edit):
        command = "UPDATE user_variant_lists SET name = %s, public_read=%s, public_edit=%s WHERE id = %s"
        self.cursor.execute(command, (new_list_name, public_read, public_edit, list_id))
        self.conn.commit()
    
    def get_user_variant_list(self, list_id):
        command = "SELECT * FROM user_variant_lists WHERE id=%s"
        self.cursor.execute(command, (list_id,))
        result = self.cursor.fetchone()
        return result

    def check_list_permission(self, user_id, list_id):
        list_oi = self.get_user_variant_list(list_id)
        if list_oi is None:
            return None
        
        result = {'read': False, 'edit': False, 'owner': False}
        if list_oi[1] == user_id: # this user is the owner of the list
            result['read'] = True
            result['edit'] = True
            result['owner'] = True
        if list_oi[3] == 1: # this is a public read list -> the user can read it
            result['read'] = True
        if list_oi[4] == 1: # this is a public editable list -> the use rcan edit it as well
            result['edit'] = True 
        return result

    #### DELETE LATER!
    #def check_user_list_ownership(self, user_id, list_id, requests_write=False):
    #    inner_command = "SELECT * FROM user_variant_lists WHERE (user_id = %s OR public_read = 1)"
    #    if requests_write:
    #        inner_command += " AND public_edit = 1"
    #    inner_command += " AND id = %s"
    #    command = "SELECT EXISTS (" + inner_command + ")"
    #    self.cursor.execute(command, (user_id, list_id))
    #    result = self.cursor.fetchone()
    #    result = result[0]
    #    if result == 1:
    #        return True
    #    else:
    #        return False
    
    # this is used in tests
    def get_latest_list_id(self):
        command = "SELECT MAX(id) FROM user_variant_lists"
        self.cursor.execute(command)
        res = self.cursor.fetchone()
        if res is not None:
            return res[0]
        return None


    def delete_variant_from_list(self, list_id, variant_id):
        command = "DELETE FROM list_variants WHERE list_id=%s AND variant_id=%s"
        self.cursor.execute(command, (list_id, variant_id))
        self.conn.commit() 

    def delete_user_variant_list(self, list_id):
        command = "DELETE FROM user_variant_lists WHERE id = %s"
        self.cursor.execute(command, (list_id, ))
        self.conn.commit()

    def duplicate_list(self, list_id, user_id, list_name, public_read, public_edit):
        self.insert_user_variant_list(user_id, list_name, public_read, public_edit)
        new_list_id = self.get_last_insert_id()
        variant_ids = self.get_variant_ids_from_list(list_id)
        for variant_id in variant_ids:
            self.add_variant_to_list(new_list_id, variant_id)
        return new_list_id

    def intersect_lists(self, first_list_id, second_list_id, target_list_id):
        first_list_variant_ids = self.get_variant_ids_from_list(first_list_id)
        second_list_variant_ids = self.get_variant_ids_from_list(second_list_id)
        variant_ids_for_target_list = list(set(first_list_variant_ids) & set(second_list_variant_ids))

        self.clear_list(target_list_id)
        for variant_id in variant_ids_for_target_list:
            self.add_variant_to_list(target_list_id, variant_id)
    
    def subtract_lists(self, first_list_id, second_list_id, target_list_id):
        first_list_variant_ids = self.get_variant_ids_from_list(first_list_id)
        second_list_variant_ids = self.get_variant_ids_from_list(second_list_id)
        variant_ids_for_target_list = list(set(first_list_variant_ids) - set(second_list_variant_ids))

        self.clear_list(target_list_id)
        for variant_id in variant_ids_for_target_list:
            self.add_variant_to_list(target_list_id, variant_id)


    def add_lists(self, first_list_id, second_list_id, target_list_id):
        first_list_variant_ids = self.get_variant_ids_from_list(first_list_id)
        second_list_variant_ids = self.get_variant_ids_from_list(second_list_id)
        variant_ids_for_target_list = list(set(first_list_variant_ids) | set(second_list_variant_ids))
        #print(variant_ids_for_target_list)

        self.clear_list(target_list_id)
        for variant_id in variant_ids_for_target_list:
            self.add_variant_to_list(target_list_id, variant_id)

    def clear_list(self, list_id):
        #"DELETE FROM " + db_table + " WHERE classification_id = %s AND pmid = %s"
        command = "DELETE FROM list_variants WHERE list_id = %s"
        self.cursor.execute(command, (list_id, ))
        self.conn.commit()

    def get_one_variant(self, variant_id):
        command = "SELECT id,chr,pos,ref,alt,is_hidden FROM variant WHERE id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchone()
        return result
    
    def get_variant_id(self, chr, pos, ref, alt):
        #command = "SELECT id FROM variant WHERE chr = " + functions.enquote(chr) + " AND pos = " + str(pos) + " AND ref = " + functions.enquote(ref) + " AND alt = " + functions.enquote(alt)
        command = "SELECT id FROM variant WHERE chr = %s AND pos = %s AND ref = %s AND alt = %s"
        self.cursor.execute(command, (chr, pos, ref, alt))
        variant_id = self.cursor.fetchone()
        if variant_id is not None:
            return variant_id[0]
        return None


    def get_recent_annotations(self, variant_id): # ! the ordering of the columns in the outer select statement is important and should not be changed
        command = "SELECT variant_annotation.id, title, description, version, version_date, variant_id, value, supplementary_document, group_name, display_title, value_type, group_name FROM variant_annotation INNER JOIN ( \
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
                    WHERE variant_id=%s AND group_name != 'ID'"
        self.cursor.execute(command, (variant_id, variant_id))
        result = self.cursor.fetchall()
        return result



    # DEPRECATED!!!
    def get_consensus_classifications_extended(self, variant_id, most_recent = True):
        consensus_classifications = self.get_consensus_classification(variant_id, most_recent=most_recent, sql_modifier=self.add_userinfo)
        if consensus_classifications is None:
            return None
        consensus_classifications_preprocessed = []
        for consensus_classification in consensus_classifications:
            consensus_classification = list(consensus_classification)
            current_scheme = self.get_classification_scheme(consensus_classification[7])
            consensus_classification.append(current_scheme[2])# append the scheme description (which is used as display name)
            consensus_classification.append(current_scheme[3]) # append scheme type
            current_scheme_criteria_applied = self.get_scheme_criteria_applied(consensus_classification[0], where = "consensus")
            consensus_classification.append(current_scheme_criteria_applied)
            previous_selected_literature = self.get_selected_literature(is_user = False, classification_id = consensus_classification[0])
            consensus_classification.append(previous_selected_literature)
            consensus_classifications_preprocessed.append(consensus_classification)
        return consensus_classifications_preprocessed
    # DEPRECATED!!!
    def get_user_classifications_extended(self, variant_id, user_id='all', scheme_id='all'):
        user_classifications = self.get_user_classifications(variant_id, user_id=user_id, scheme_id=scheme_id, sql_modifier=self.add_userinfo) # 0id,1classification,2variant_id,3user_id,4comment,5date,6classification_scheme_id,7user_id,8first_name,9last_name,10affiliation
        if user_classifications is None:
            return None
        user_classifications_preprocessed = []
        for user_classification in user_classifications:
            user_classification = list(user_classification)
            current_scheme = self.get_classification_scheme(user_classification[6])
            user_classification.append(current_scheme[2]) # append the scheme description (which is used as display name)
            user_classification.append(current_scheme[3]) # append scheme type
            current_scheme_criteria_applied = self.get_scheme_criteria_applied(user_classification[0], where = "user")
            user_classification.append(current_scheme_criteria_applied)
            previous_selected_literature = self.get_selected_literature(is_user = True, classification_id = user_classification[0])
            user_classification.append(previous_selected_literature)
            user_classifications_preprocessed.append(user_classification)
        return user_classifications_preprocessed





    def get_heredicare_annotations(self, variant_id):
        command = "SELECT id, vid, n_fam, n_pat, consensus_class, comment, date FROM variant_heredicare_annotation WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        res = self.cursor.fetchall()
        return res




    def get_variant(self, variant_id, 
                    include_annotations = True, 
                    include_consensus = True, 
                    include_user_classifications = True, 
                    include_heredicare_classifications = True, 
                    include_automatic_classification = True,
                    include_clinvar = True, 
                    include_consequences = True, 
                    include_assays = True, 
                    include_literature = True,
                    include_external_ids = True
                ) -> models.Variant:
        variant_raw = self.get_one_variant(variant_id)
        if variant_raw is None:
            return None

        variant_id = variant_raw[0]
        chrom = variant_raw[1]
        pos = variant_raw[2]
        ref = variant_raw[3]
        alt = variant_raw[4]

        is_hidden = True if variant_raw[5] == 1 else False

        annotations = None
        if include_annotations:
            annotations = models.AllAnnotations()
            annotations_raw = self.get_recent_annotations(variant_id)

            for annot in annotations_raw:
                annotation_id = annot[0]
                title = annot[1]
                display_title = annot[9]
                description = annot[2]
                version = annot[3]
                version_date = annot[4].strftime('%Y-%m-%d')
                value = annot[6]
                value_type = annot[10]
                group_name = annot[11]

                new_annotation = models.Annotation(id = annotation_id, value = value, title = title, display_title = display_title, description = description, version = version, version_date = version_date, value_type = value_type, group_name = group_name)
                setattr(annotations, annot[1], new_annotation)
                #annotations.insert_annotation(new_annotation)
            
            transcript_annotations = self.get_recent_transcript_annotations(variant_id)

            for annot in transcript_annotations:
                setattr(annotations, annot.title, annot)
            
            annotations.flag_linked_annotations()

        
        # add external ids
        external_ids = None
        if include_external_ids:
            external_ids = []
            external_ids_raw = self.get_all_external_ids(variant_id)
            #variant_ids.id, title, description, version, version_date, variant_id, external_id, group_name, display_title, value_type
            for external_id_raw in external_ids_raw:
                new_external_id = models.Annotation(id = external_id_raw[0], 
                                                    value = external_id_raw[6], 
                                                    title = external_id_raw[1], 
                                                    display_title = external_id_raw[8], 
                                                    description = external_id_raw[2], 
                                                    version = external_id_raw[3], 
                                                    version_date = external_id_raw[4], 
                                                    value_type = external_id_raw[9], 
                                                    group_name = external_id_raw[7]
                                                )
                external_ids.append(new_external_id)

        
        # add all consensus classifications
        consensus_classifications = None
        if include_consensus:
            cls_raw = self.get_consensus_classification(variant_id) # get all consensus classifications

            if cls_raw is not None:
                consensus_classifications = []

                for cl_raw in cls_raw:

                    # basic information
                    selected_class = cl_raw[3]
                    comment = cl_raw[4]
                    date = cl_raw[5].strftime('%Y-%m-%d %H:%M:%S')
                    classification_id = int(cl_raw[0])
                    scheme_class = cl_raw[8]

                    # get further information from database (could use join to get them as well)
                    current_userinfo = self.get_user(user_id = cl_raw[1]) # id,username,first_name,last_name,affiliation
                    current_scheme = self.get_classification_scheme(scheme_id = cl_raw[7]) # id,name,display_name,type,reference
                    current_scheme_criteria_applied = self.get_scheme_criteria_applied(classification_id, where = "consensus") # id,classification_id,classification_criterium_id,criterium_strength_id,evidence,classification_criterium_name,classification_criterium_strength_name,strength_description (display name)
                    previous_selected_literature = self.get_selected_literature(is_user = False, classification_id = classification_id)


                    # user information
                    user = self.parse_raw_user(current_userinfo)

                    # scheme information
                    scheme_id = current_scheme[0]
                    scheme_type = current_scheme[3]
                    scheme_display_name = current_scheme[2]
                    reference = current_scheme[4]
                    is_active = True if current_scheme[5] == 1 else False
                    is_default = True if current_scheme[6] == 1 else False
                    criteria = []
                    for criterium_raw in current_scheme_criteria_applied:
                        criterium_id = criterium_raw[0] # criterium applied id
                        criterium_name = criterium_raw[5]
                        criterium_type = criterium_raw[6]
                        criterium_evidence = criterium_raw[4]
                        criterium_strength = criterium_raw[7]
                        strength_display_name = criterium_raw[8]
                        criterium = models.Criterium(id = criterium_id, name = criterium_name, type=criterium_type, evidence = criterium_evidence, strength = criterium_strength, strength_display_name = strength_display_name)
                        criteria.append(criterium)
                    scheme = models.Scheme(id = scheme_id, display_name = scheme_display_name, type = scheme_type, criteria = criteria, reference = reference, selected_class = scheme_class, is_active = is_active, is_default = is_default)

                    # selected literature information
                    literatures = None
                    for literature_raw in previous_selected_literature:
                        if literatures is None:
                            literatures = []
                        new_literature = models.SelectedLiterature(id = literature_raw[0], pmid = literature_raw[2], text_passage = literature_raw[3])
                        literatures.append(new_literature)

                    # save the new classification object
                    new_classification = models.Classification(id = classification_id, type = 'consensus classification', selected_class=selected_class, comment=comment, date=date, submitter=user, scheme=scheme, literature = literatures)
                    consensus_classifications.append(new_classification)


        # add all user classifications
        user_classifications = None
        if include_user_classifications:
            user_classifications_raw = self.get_user_classifications(variant_id) # id, classification, variant_id, user_id, comment, date, classification_scheme_id
            if user_classifications_raw is not None:
                user_classifications = []
                for cl_raw in user_classifications_raw:

                    # basic information
                    selected_class = cl_raw[1]
                    comment = cl_raw[4]
                    date = cl_raw[5].strftime('%Y-%m-%d %H:%M:%S')
                    classification_id = int(cl_raw[0])
                    scheme_class = cl_raw[7]

                    # get further information
                    current_userinfo = self.get_user(user_id = cl_raw[3])
                    current_scheme = self.get_classification_scheme(cl_raw[6])
                    current_scheme_criteria_applied = self.get_scheme_criteria_applied(classification_id = classification_id, where = "user")
                    previous_selected_literature = self.get_selected_literature(is_user = True, classification_id = classification_id)

                    # user information
                    user = models.User(id = current_userinfo[0], 
                                       full_name = current_userinfo[2] + ' ' + current_userinfo[3], 
                                       affiliation = current_userinfo[4])

                    # scheme information
                    scheme_id = current_scheme[0]
                    scheme_type = current_scheme[3]
                    scheme_display_name = current_scheme[2]
                    reference = current_scheme[4]
                    is_active = True if current_scheme[5] == 1 else False
                    is_default = True if current_scheme[6] == 1 else False
                    criteria = []
                    for criterium_raw in current_scheme_criteria_applied:
                        criterium_id = criterium_raw[0] # criterium applied id
                        criterium_name = criterium_raw[5]
                        criterium_type = criterium_raw[6]
                        criterium_evidence = criterium_raw[4]
                        criterium_strength = criterium_raw[7]
                        strength_display_name = criterium_raw[8]
                        criterium = models.Criterium(id = criterium_id, name = criterium_name, type=criterium_type, evidence = criterium_evidence, strength = criterium_strength, strength_display_name=strength_display_name)
                        criteria.append(criterium)
                    scheme = models.Scheme(id = scheme_id, display_name = scheme_display_name, type = scheme_type, criteria = criteria, reference = reference, selected_class = scheme_class, is_active = is_active, is_default = is_default)

                    # selected literature information
                    literatures = None
                    for literature_raw in previous_selected_literature:
                        if literatures is None:
                            literatures = []
                        new_literature = models.SelectedLiterature(id = literature_raw[0], pmid = literature_raw[2], text_passage = literature_raw[3])
                        literatures.append(new_literature)
                    
                    new_user_classification = models.Classification(id = classification_id, type = 'user classification', selected_class=selected_class, comment=comment, date=date, submitter=user, scheme=scheme, literature = literatures)
                    user_classifications.append(new_user_classification)

        automatic_classification = None
        if include_automatic_classification:
            automatic_classification_raw = self.get_automatic_classification(variant_id)
            if automatic_classification_raw is not None:
                automatic_classification_id = int(automatic_classification_raw[0]) # id, scheme_name, classification, date
                automatic_classification_criteria = self.get_automatic_classification_criteria_applied(automatic_classification_raw[0]) # id, name, rule_type, evidence_type, is_selected, strength, type, comment

                all_criteria = []
                for automatic_classification_criterium in automatic_classification_criteria:
                    automatic_classification_criterium_id = int(automatic_classification_criterium[0])
                    name = automatic_classification_criterium[1]
                    rule_type = automatic_classification_criterium[2]
                    evidence_type = automatic_classification_criterium[3]
                    is_selected = automatic_classification_criterium[4] == 1
                    strength = automatic_classification_criterium[5]
                    strength_type = automatic_classification_criterium[6]
                    evidence = automatic_classification_criterium[7]
                    new_criterium = models.AutomaticClassificationCriterium(id = automatic_classification_criterium_id, name = name, rule_type = rule_type, evidence_type = evidence_type, is_selected = is_selected, strength = strength, type = strength_type, evidence = evidence)
                    all_criteria.append(new_criterium)
                
                classification = automatic_classification_raw[2]
                scheme_name = automatic_classification_raw[1]
                date = automatic_classification_raw[3]
                automatic_classification = models.AutomaticClassification(id = automatic_classification_id, scheme_name = scheme_name, classification = classification, date = date, criteria = all_criteria)


        heredicare_classifications = None
        all_heredicare_annotations = None
        if include_heredicare_classifications:
            heredicare_classifications_raw = self.get_heredicare_center_classifications(variant_id)
            if heredicare_classifications_raw is not None:
                heredicare_classifications = []
                for cl_raw in heredicare_classifications_raw:
                    id = int(cl_raw[0])
                    selected_class = cl_raw[1]
                    comment = cl_raw[4]
                    center = cl_raw[3]
                    date = cl_raw[5].strftime('%Y-%m-%d')
                    new_heredicare_classification = models.HeredicareClassification(id = id, selected_class = selected_class, comment = comment, center = center, classification_date = date, vid="")
                    heredicare_classifications.append(new_heredicare_classification)


            heredicare_annotations_raw = self.get_heredicare_annotations(variant_id)
            all_heredicare_annotations = []
            for annot in heredicare_annotations_raw:
                #id, vid, n_fam, n_pat, consensus_class, comment, date
                heredicare_annotation_id = annot[0]
                vid = annot[1]
                n_fam = annot[2]
                n_pat = annot[3]
                consensus_class = annot[4]
                comment = annot[5]
                classification_date = annot[6]

                classification = models.HeredicareClassification(id = heredicare_annotation_id, selected_class = consensus_class, comment = comment, classification_date = classification_date, center = "VUSTF", vid = vid)
                new_heredicare_annotation = models.HeredicareAnnotation(id = heredicare_annotation_id, vid = vid, n_fam = n_fam, n_pat = n_pat, vustf_classification = classification)
                all_heredicare_annotations.append(new_heredicare_annotation)
        
        # add clinvar annotation
        clinvar = None
        if include_clinvar:
            clinvar_summary = self.get_clinvar_variant_annotation(variant_id)
            if clinvar_summary is not None:
                id = clinvar_summary[0]
                variation_id = clinvar_summary[2]
                review_status = clinvar_summary[4]
                interpretation = clinvar_summary[3]

                submissions_raw = self.get_clinvar_submissions(id)
                clinvar_submissions = None
                if submissions_raw is not None:
                    clinvar_submissions = []
                    for submission in submissions_raw:
                        conditions = []
                        for condition in submission[5]:
                            conditions.append(models.ClinvarCondition(condition_id = condition[0], title = condition[1]))
                        last_evaluated = submission[3]
                        if last_evaluated is not None:
                            last_evaluated = last_evaluated.strftime('%Y-%m-%d')
                        new_clinvar_submission = models.ClinvarSubmission(id = int(submission[0]), interpretation = submission[2], last_evaluated = last_evaluated, review_status = submission[4], conditions=conditions, submitter = submission[6], comment = submission[7])
                        clinvar_submissions.append(new_clinvar_submission)
            
                clinvar = models.Clinvar(id = id, variation_id = variation_id, review_status = review_status, interpretation_summary = interpretation, submissions = clinvar_submissions)
        
        
        # add consequences
        consequences = None
        if include_consequences:
            consequences_raw = self.get_variant_consequences(variant_id)
            if consequences_raw is not None:
                consequences = []
                for consequence in consequences_raw:
                    new_consequence = models.Consequence(transcript = models.Transcript(
                                                            id = consequence[19],
                                                            gene = models.Gene(symbol = consequence[7], id = consequence[8]),
                                                            name = consequence[0],
                                                            biotype = consequence[18],
                                                            length = consequence[12],
                                                            source = consequence[9],
                                                            chrom = consequence[21],
                                                            start = consequence[19],
                                                            end = consequence[20],
                                                            orientation = consequence[22],
                                                            is_gencode_basic = True if consequence[13] == 1 else False,
                                                            is_mane_select = True if consequence[14] == 1 else False,
                                                            is_mane_plus_clinical = True if consequence[15] == 1 else False,
                                                            is_ensembl_canonical = True if consequence[16] == 1 else False
                                                         ), 
                                                         hgvs_c = consequence[1], 
                                                         hgvs_p = consequence[2], 
                                                         consequence = consequence[3], 
                                                         impact = consequence[4], 
                                                         exon = consequence[5], 
                                                         intron = consequence[6],
                                                         protein_domain_title = consequence[10], 
                                                         protein_domain_id = consequence[11],
                                                    )
                    consequences.append(new_consequence)
       

        assays = None
        if include_assays:
            assays_raw = self.get_assays(variant_id, assay_types = 'all')
            if assays_raw is not None:
                assays = []
                for assay in assays_raw:
                    new_assay = models.Assay(id = int(assay[0]), type = assay[1], score = assay[2], date = assay[3].strftime('%Y-%m-%d'))
                    assays.append(new_assay)
        

        literature = None
        if include_literature:
            literature_raw = self.get_variant_literature(variant_id, sort_year=False)
            if literature_raw is not None:
                literature = []
                for paper in literature_raw:
                    new_paper = models.Paper(year = paper[6], authors = paper[4], title = paper[3], journal = paper[5], pmid = paper[2], source = paper[7])
                    literature.append(new_paper)

        variant = models.Variant(id=variant_id, chrom = chrom, pos = pos, ref = ref, alt = alt, is_hidden = is_hidden,
                                annotations = annotations, 
                                consensus_classifications = consensus_classifications, 
                                user_classifications = user_classifications,
                                heredicare_classifications = heredicare_classifications,
                                automatic_classification = automatic_classification,
                                heredicare_annotations = all_heredicare_annotations,
                                clinvar = clinvar,
                                consequences = consequences,
                                assays = assays,
                                literature = literature,
                                external_ids = external_ids
                            )
        return variant



    def hide_variant(self, variant_id, is_hidden):
        command = "UPDATE variant SET is_hidden = %s WHERE id = %s"
        is_hidden = 0 if is_hidden else 1
        self.cursor.execute(command, (is_hidden, variant_id))
        self.conn.commit()




    def get_all_variant_annotations(self, variant_id, group_output=False):
        variant_annotations = self.get_recent_annotations(variant_id)
        standard_annotations = {} # used for grouping hierarchy: 'standard_annotations' -> group -> annotation_label
        variant_annot_dict = {}

        if group_output: # all items from the same group are put into one dictionary except for the special group 'None' which is inserted as key directly into variant_annot_dict
            for annot in variant_annotations:
                current_group = annot[8]
                new_value = annot[2:len(annot)] + (annot[0], ) # put annotation id last and remove title / display text
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

        consensus_classification = self.get_consensus_classifications_extended(variant_id, most_recent=True)
        if consensus_classification is not None:
            variant_annot_dict['consensus_classification'] = consensus_classification

        user_classifications = self.get_user_classifications_extended(variant_id) # 0id,1classification,2variant_id,3user_id,4comment,5date,6classification_scheme_id,7user_id,8first_name,9last_name,10affiliation
        if user_classifications is not None:
            variant_annot_dict['user_classifications'] = user_classifications
        
        heredicare_center_classifications = self.get_heredicare_center_classifications(variant_id)
        if heredicare_center_classifications is not None:
            variant_annot_dict['heredicare_center_classifications'] = heredicare_center_classifications

        assays = self.get_assays(variant_id, assay_types = 'all')
        if assays is not None:
            variant_annot_dict['assays'] = assays
        #print(variant_annot_dict['standard_annotations'])

    
        return variant_annot_dict




    def get_assays(self, variant_id, assay_types = 'all'):
        command = "SELECT id, assay_type, score, date FROM assay WHERE variant_id = %s"
        actual_information = (variant_id, )

        if assay_types != 'all':
            placeholders = ["%s"] * len(assay_types)
            placeholders = ', '.join(placeholders)
            placeholders = functions.enbrace(placeholders)
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


    def invalidate_previous_scheme_consensus_classifications(self, variant_id):
        command = "UPDATE scheme_consensus_classification SET is_recent = %s WHERE scheme_classification_id IN (SELECT id FROM scheme_classification WHERE variant_id=%s AND is_consensus=1)"
        self.cursor.execute(command, (0, variant_id))
        self.conn.commit()

    def add_userinfo(self, command):
        prefix = 'SELECT * FROM (('
        postfix = ') uid_a INNER JOIN (SELECT id as outer_id, first_name,last_name,affiliation FROM user) uid_b ON uid_a.user_id = uid_b.outer_id)'
        result = prefix + command + postfix
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


    def get_classification_schemas(self):
        # it should look like this:
        # {schema_id -> display_name(description), scheme_type, reference, criteria}
        #                                         -> {name,description,default_strength,possible_strengths,selectable,disable_group,mutually_exclusive_buttons}
        command = "SELECT * FROM classification_scheme WHERE is_active = 1"
        self.cursor.execute(command)
        classification_schemas = self.cursor.fetchall()

        command = "SELECT source,target,name FROM mutually_exclusive_criteria INNER JOIN (SELECT id as inner_id,name FROM classification_criterium)x ON x.inner_id = mutually_exclusive_criteria.target"
        self.cursor.execute(command)
        mutually_exclusive_criteria = self.cursor.fetchall()
        mutually_exclusive_criteria_dict = {}
        for mutually_exclusive_criterium in mutually_exclusive_criteria:
            source = mutually_exclusive_criterium[0]
            target = mutually_exclusive_criterium[2]
            if source not in mutually_exclusive_criteria:
                mutually_exclusive_criteria_dict[source] = [target]
            else:
                mutually_exclusive_criteria_dict[source].append(target)

        result = {}
        for classification_schema in classification_schemas:
            classification_schema_id = classification_schema[0]
            #name = classification_schema[1]
            description = classification_schema[2]
            scheme_type = classification_schema[3]
            online_reference = classification_schema[4]
            is_default = classification_schema[6]

            command = "SELECT * FROM classification_criterium WHERE classification_scheme_id = %s"
            self.cursor.execute(command, (classification_schema_id, ))
            classification_criteria = self.cursor.fetchall()
            classification_criteria_dict = {}
            for criterium in classification_criteria:
                classification_criterium_id = criterium[0]
                classification_criterium_name = criterium[2]
                classification_criterium_description = criterium[3]
                classification_criterium_is_selectable = criterium[4]
                classification_criterium_relevant_information = criterium[5]

                new_criterium_dict = {}
                new_criterium_dict["id"] = classification_criterium_id
                new_criterium_dict["name"] = classification_criterium_name
                new_criterium_dict["description"] = classification_criterium_description
                new_criterium_dict["is_selectable"] = classification_criterium_is_selectable
                new_criterium_dict["relevant_information"] = classification_criterium_relevant_information

                command = "SELECT id, classification_criterium_id, name, description, is_default, display_name FROM classification_criterium_strength WHERE classification_criterium_id = %s"
                self.cursor.execute(command, (classification_criterium_id, ))
                classification_criterium_strengths = self.cursor.fetchall()

                all_criteria_strengths = []
                strength_display_titles = {}
                for classification_criterium_strength in classification_criterium_strengths:
                    is_default = classification_criterium_strength[4] == 1
                    classification_criterium_strength_name = classification_criterium_strength[2]
                    if is_default:
                        new_criterium_dict["default_strength"] = classification_criterium_strength_name
                    all_criteria_strengths.append(classification_criterium_strength_name)
                    strength_display_name = classification_criterium_strength[5]
                    strength_display_titles[classification_criterium_strength_name] = strength_display_name
                new_criterium_dict["possible_strengths"] = all_criteria_strengths
                new_criterium_dict["strength_display_names"] = strength_display_titles
                new_criterium_dict['mutually_exclusive_criteria'] = mutually_exclusive_criteria_dict.get(classification_criterium_id, []) 

                classification_criteria_dict[classification_criterium_name] = new_criterium_dict

            result[classification_schema_id] = {"description": description, "scheme_type": scheme_type, "reference": online_reference, 'is_default': is_default, 'criteria': classification_criteria_dict}

        return result


    def get_selected_literature_table(self, is_user):
        db_table = "user_classification_selected_literature"
        if not is_user:
            db_table = "consensus_classification_selected_literature"
        return db_table

    def insert_update_selected_literature(self, is_user, classification_id, pmid, text_passage):
        db_table = self.get_selected_literature_table(is_user)
        command = "INSERT INTO " + db_table + " (classification_id, pmid, text_passage) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE text_passage=VALUES(text_passage)"
        self.cursor.execute(command, (classification_id, pmid, text_passage))
        self.conn.commit()

    def delete_selected_literature(self, is_user, classification_id, pmid):
        db_table = self.get_selected_literature_table(is_user)
        command = "DELETE FROM " + db_table + " WHERE classification_id = %s AND pmid = %s"
        self.cursor.execute(command, (classification_id, pmid))
        self.conn.commit()

    def get_selected_literature(self, is_user, classification_id):
        db_table = self.get_selected_literature_table(is_user)
        command = "SELECT * FROM " + db_table + " WHERE classification_id = %s"
        self.cursor.execute(command, (classification_id, ))
        result = self.cursor.fetchall()
        return result




    def insert_update_heredivar_clinvar_submission(self, variant_id, submission_id, accession_id, status, message, last_updated, previous_clinvar_accession):
        if previous_clinvar_accession is None:
            command = "INSERT INTO heredivar_clinvar_submissions (variant_id, submission_id, accession_id, status, message, last_updated) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE submission_id=VALUES(submission_id), accession_id=VALUES(accession_id), status=VALUES(status),message=VALUES(message), last_updated=VALUES(last_updated)"
        else: # do not reset the accession id - this one is stable once it was created by clinvar
            command = "INSERT INTO heredivar_clinvar_submissions (variant_id, submission_id, status, message, last_updated) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE submission_id=VALUES(submission_id), status=VALUES(status),message=VALUES(message), last_updated=VALUES(last_updated)"
        self.cursor.execute(command, (variant_id, submission_id, accession_id, status, message, last_updated))
        self.conn.commit()

    def get_heredivar_clinvar_submission(self, variant_id):
        command = "SELECT id,variant_id,submission_id,accession_id,status,message,last_updated FROM heredivar_clinvar_submissions WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchone()
        return result

    #def update_heredivar_clinvar_submission_accession_id(self, accession_id):
    #    command = "UPDATE heredivar_clinvar_submissions SET accession_id = %s"
    #    self.cursor.execute(command, (accession_id, ))
    #    self.conn.commit()


    def get_current_annotation_staus_all_variants(self):
        command = """
        SELECT a1.variant_id, a1.user_id, a1.requested, a1.status, a1.finished_at, a1.error_message
            FROM annotation_queue a1 LEFT JOIN annotation_queue a2
                ON (a1.variant_id = a2.variant_id AND a1.requested < a2.requested)
        WHERE a2.id IS NULL
        """
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result

    def get_annotation_statistics(self):
        # return the most recent annotation queue entry for the variant 
        result = self.get_current_annotation_staus_all_variants()
        annotation_status_types = self.get_enumtypes("annotation_queue", "status")
        
        annotation_stati = {}
        for annotation_status_type in annotation_status_types:
            annotation_stati[annotation_status_type] = []
        #annotation_stati = {'success': [], 'pending': [], 'error': [], 'retry': [], 'aborted': []} <- it should look like this
        errors = {}
        warnings = {}
        total_num_variants = len(result)
        for annotation_status in result:
            variant_id = annotation_status[0]
            annotation_stati[annotation_status[3]].append(variant_id)
            if annotation_status[3] == 'error':
                errors[variant_id] = annotation_status[5]
            if annotation_status[3] != 'error' and annotation_status[5] != '':
                warnings[variant_id] = annotation_status[5]
                
        return annotation_stati, errors, warnings, total_num_variants
    

    def get_annotation_types(self, exclude_groups = []):
        annotation_type_ids = self.get_recent_annotation_type_ids()
        annotation_type_ids = annotation_type_ids.values()
        placeholders = self.get_placeholders(len(annotation_type_ids))
        command = "SELECT id, title, display_title, description, value_type, version, version_date, group_name, is_transcript_specific FROM annotation_type WHERE id IN " + placeholders
        self.cursor.execute(command, tuple(annotation_type_ids))
        result = self.cursor.fetchall()
        annotation_types = [self.convert_annotation_type_raw(annotation_type_raw) for annotation_type_raw in result if annotation_type_raw]
        annotation_types = [annotation_type for annotation_type in annotation_types if annotation_type.group_name not in exclude_groups]
        return annotation_types

    def get_annotation_type(self, annotation_type_id):
        command = "SELECT id, title, display_title, description, value_type, version, version_date, group_name, is_transcript_specific FROM annotation_type WHERE id = %s"
        self.cursor.execute(command, (annotation_type_id, ))
        result = self.cursor.fetchone()
        if result is None:
            return None
        return self.convert_annotation_type_raw(result)


    def convert_annotation_type_raw(self, annotation_type_raw):
        return models.Annotation_type(id = int(annotation_type_raw[0]),
                                      title = annotation_type_raw[1], 
                                      display_title = annotation_type_raw[2], 
                                      description = annotation_type_raw[3], 
                                      value_type = annotation_type_raw[4], 
                                      version = annotation_type_raw[5], 
                                      version_date = annotation_type_raw[6], 
                                      group_name = annotation_type_raw[7], 
                                      is_transcript_specific = annotation_type_raw[8]
                                    )
    
    def get_number_of_classified_variants(self):
        command = "SELECT DISTINCT variant_id FROM consensus_classification"
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return len(result)
    
    def get_number_of_variants(self):
        command = "SELECT COUNT(id) from variant"
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        return result[0]
    
    def get_recent_annotation_type_ids(self, only_transcript_specific = False):
        addon = ""
        if only_transcript_specific:
            addon = "WHERE is_transcript_specific = 1"
        command = """
            SELECT n.id, n.title
                FROM annotation_type n 
                INNER JOIN (
                  SELECT title, MAX(version_date) as max_version_date
                  FROM annotation_type %s GROUP BY title
                ) AS max ON max.title = n.title and max.max_version_date = n.version_date
        """ % (addon, )
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        recent_annotation_ids = {}    
        for entry in result:
            recent_annotation_ids[entry[1]] = entry[0]
        
        return recent_annotation_ids


    def get_placeholders(self, num):
        placeholders = ["%s"] * num
        placeholders = ', '.join(placeholders)
        placeholders = functions.enbrace(placeholders)
        return placeholders
    


    def insert_heredicare_annotation(self, variant_id, vid, n_fam, n_pat, consensus_class, classification_date, comment):
        command = "INSERT INTO variant_heredicare_annotation (variant_id, vid, n_fam, n_pat, consensus_class, date, comment) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, vid, n_fam, n_pat, consensus_class, classification_date, comment))
        self.conn.commit()

    def clear_heredicare_annotation(self, variant_id):
        command = "DELETE FROM variant_heredicare_annotation WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        self.conn.commit()
    
    def get_enumtypes(self, tablename, columnname):
        allowed_tablenames = ["consensus_classification", "user_classification", "variant", "annotation_queue", "automatic_classification"]
        if tablename in allowed_tablenames:
            command = "SHOW COLUMNS FROM " + tablename + " WHERE FIELD = %s"
        else:
            return None
        self.cursor.execute(command, (columnname, ))
        result = self.cursor.fetchone()
        column_type = result[1]
        column_type = column_type.strip('enum()')
        allowed_enum = column_type.split(',')
        allowed_enum = [x.strip('\'') for x in allowed_enum]
        return allowed_enum
    


    def get_gencode_basic_transcripts(self, gene_id):
        if gene_id is None:
            return None
        command = "SELECT name FROM transcript WHERE gene_id = %s AND (is_gencode_basic=1 or is_mane_select=1 or is_mane_plus_clinical=1)"
        self.cursor.execute(command, (gene_id, ))
        result = self.cursor.fetchall()
        return [x[0] for x in result if x[0].startswith("ENST")]

    
    
    # this function returns a list of consequence objects of the preferred transcripts 
    # (can be multiple if there are eg. 2 mane select transcripts for this variant)
    def get_preferred_transcripts(self, gene_id, return_all=False):
        transcripts = self.get_transcripts(gene_id)
        transcripts = functions.order_transcripts(transcripts)

        result = []
        if not return_all and len(transcripts) > 0:
            result.append(transcripts.pop(0))
            for transcript in transcripts: # scan for all mane select transcripts
                if transcript.is_mane_select:
                    result.append(transcript)
                else:
                    break # we can do this because the list is sorted
        else:
            result = transcripts
        
        return result

        #result = []
        #command = "SELECT name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical FROM transcript WHERE gene_id = %s"
        #self.cursor.execute(command, (gene_id, ))
        #result_raw = self.cursor.fetchall()
        #transcripts = []
        #for elem in result_raw:
        #    if elem[0].startswith("ENST"):
        #        source = "ensembl" if elem[0].startswith("ENST") else "refseq"
        #        new_elem = {"name": elem[0],
        #                    "biotype": elem[1],
        #                    "length": elem[2],
        #                    "is_gencode_basic": elem[3],
        #                    "is_mane_select": elem[4],
        #                    "is_mane_plus_clinical": elem[5],
        #                    "is_ensembl_canonical": elem[6],
        #                    "source": source
        #                }
        #        transcripts.append(new_elem)
        #
        #if len(transcripts) > 0:
        #    transcripts = self.order_transcripts(transcripts)
        #
        #    if not return_all:
        #        result.append(transcripts.pop(0)) # always append the first one
        #
        #        for transcript in transcripts: # scan for all mane select transcripts
        #            if transcript["is_mane_select"]:
        #                result.append(transcript)
        #            else:
        #                break # we can do this because the list is sorted
        #    else:
        #        result = transcripts
        #else: # the variant does not have any consequences
        #    return None
        #return result

    #def order_transcripts(self, consequences):
    #    keyfunc = cmp_to_key(mycmp = self.sort_transcripts)
    #    consequences.sort(key = keyfunc) # sort by preferred transcript
    #    return consequences
    # 
    #def sort_transcripts(self, a, b):
    #    # sort by ensembl/refseq
    #    if a["source"] == 'ensembl' and b["source"] == 'refseq':
    #        return -1
    #    elif a["source"] == 'refseq' and b["source"] == 'ensembl':
    #        return 1
    #    elif a["source"] == b["source"]:
#
    #        # sort by mane select
    #        if a["is_mane_select"] is None or b["is_mane_select"] is None:
    #            return 1
    #        elif a["is_mane_select"] and not b["is_mane_select"]:
    #            return -1
    #        elif not a["is_mane_select"] and b["is_mane_select"]:
    #            return 1
    #        elif a["is_mane_select"] == b["is_mane_select"]:
#
    #            # sort by biotype
    #            if a["biotype"] == 'protein coding' and b["biotype"] != 'protein coding':
    #                return -1
    #            elif a["biotype"] != 'protein coding' and b["biotype"] == 'protein coding':
    #                return 1
    #            elif (a["biotype"] != 'protein coding' and b["biotype"] != 'protein coding') or (a["biotype"] == 'protein coding' and b["biotype"] == 'protein coding'):
#
    #                # sort by length
    #                if a["length"] > b["length"]:
    #                    return -1
    #                elif a["length"] < b["length"]:
    #                    return 1
    #                else:
    #                    return 0
                    




    def insert_criterium_scheme(self, classification_scheme_id, name, display_name, scheme_type, reference):
        if classification_scheme_id != "":
            command = "UPDATE classification_scheme SET name = %s, display_name = %s, type = %s, reference = %s WHERE id = %s"
            actual_information = (name, display_name, scheme_type, reference, classification_scheme_id)
        else:
            command = "INSERT INTO classification_scheme (name, display_name, type, reference) VALUES (%s,%s,%s,%s)"
            actual_information = (name, display_name, scheme_type, reference)
        self.cursor.execute(command, actual_information)
        self.conn.commit()
        if classification_scheme_id != "":
            return classification_scheme_id
        else:
            return self.get_last_insert_id()
            
        
    def insert_criterium(self, classification_scheme_id, name, description, is_selectable, relevant_info):
        command = "INSERT INTO classification_criterium (classification_scheme_id, name, description, is_selectable, relevant_info) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE description = %s, is_selectable = %s, relevant_info=%s"
        actual_information = (classification_scheme_id, name, description, is_selectable, relevant_info, description, is_selectable, relevant_info)
        self.cursor.execute(command, actual_information)
        self.conn.commit()
        command = "SELECT id FROM classification_criterium WHERE classification_scheme_id = %s AND name = %s"
        self.cursor.execute(command, (classification_scheme_id, name))
        res = self.cursor.fetchone()
        return res[0]

    def delete_criterium(self, classification_scheme_id, name):
        command = "DELETE FROM classification_criterium WHERE classification_scheme_id = %s AND name = %s"
        self.cursor.execute(command, (classification_scheme_id, name))
        self.conn.commit()
        

    def insert_criterium_strength(self, criterium_id, name, display_name, description, is_default):
        command = "INSERT INTO classification_criterium_strength (classification_criterium_id, name, display_name, description, is_default) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE description = %s, is_default=%s, display_name=%s"
        self.cursor.execute(command, (criterium_id, name, display_name, description, is_default, description, is_default, display_name))
        self.conn.commit()
    
    def delete_criterium_strength(self, criterium_id, strength):
        command = "DELETE FROM classification_criterium_strength WHERE classification_criterium_id = %s AND name = %s"
        self.cursor.execute(command, (criterium_id, strength))
        self.conn.commit()

    def insert_mutually_exclusive_criterium(self, source, target):
        command = "INSERT INTO mutually_exclusive_criteria (source, target) VALUES (%s,%s) ON DUPLICATE KEY UPDATE source = %s, target=%s"
        self.cursor.execute(command, (source, target, source, target))
        self.conn.commit()
    
    def delete_mutually_exclusive_criteria(self, source):
        command = "DELETE FROM mutually_exclusive_criteria WHERE source = %s"
        self.cursor.execute(command, (source, ))
        self.conn.commit()


    def insert_variant_transcript_annotation(self, variant_id, transcript, annotation_type_id, value):
        transcript = transcript.split('.')[0]
        command = "INSERT INTO variant_transcript_annotation (variant_id, transcript, annotation_type_id, value) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `value`=%s"
        self.cursor.execute(command, (variant_id, transcript, annotation_type_id, value, value))
        self.conn.commit()

    def get_recent_transcript_annotations(self, variant_id):
        recent_annotation_type_ids = self.get_recent_annotation_type_ids(only_transcript_specific=True)
        final_result = []
        for annotation_type_title in recent_annotation_type_ids:
            command = """SELECT id,
                                (SELECT title FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) title,
                                (SELECT description FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) description,
                                (SELECT version FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) version,
                                (SELECT version_date FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) version_date,
                                (SELECT title FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) title,
                                variant_id, value, transcript,
                                (SELECT group_name FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) title,
                                (SELECT display_title FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) display_title,
                                (SELECT value_type FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) value_type,
                                (SELECT group_name FROM annotation_type WHERE annotation_type.id = variant_transcript_annotation.annotation_type_id) group_name
                         FROM variant_transcript_annotation WHERE variant_id = %s and annotation_type_id = %s
            """
            self.cursor.execute(command, (variant_id, recent_annotation_type_ids[annotation_type_title]))
            result = self.cursor.fetchall()
            if len(result) == 0:
                continue
            
            all_annotations = {}
            for elem in result:
                all_annotations[elem[8]] = elem[7]
            new_annotation = models.TranscriptAnnotation(id = elem[0], value = all_annotations, title = elem[1], display_title = elem[10], description = elem[2], version = elem[3],
                                                             version_date = elem[4], value_type = elem[11], draw = False, is_transcript_specific = True, group_name = elem[12])
            final_result.append(new_annotation)
        return final_result
    

    def get_transcripts_from_names(self, transcript_names, remove_unknown = False):
        command = "SELECT id, gene_id, (SELECT symbol FROM gene WHERE transcript.gene_id = gene.id), name, biotype, length, is_gencode_basic, is_mane_select, is_mane_plus_clinical, is_ensembl_canonical, start, end, chrom, orientation FROM transcript WHERE name IN "
        placeholders = self.get_placeholders(len(transcript_names))
        command += placeholders
        self.cursor.execute(command, tuple(transcript_names))
        transcripts_raw = self.cursor.fetchall()
        transcripts = [self.convert_raw_transcript(transcript_raw) for transcript_raw in transcripts_raw]

        if not remove_unknown:
            transcripts_not_in_db = list(set(transcript_names) - set([x[3] for x in transcripts_raw]))
            transcripts_not_in_db = [models.Transcript(id=None, gene=None, name=transcript_name, biotype=None, length=None, chrom="", start=0, end=0, orientation="", source="ensembl" if transcript_name.startswith('ENST') else "refseq", is_gencode_basic=None,is_mane_select=None,is_mane_plus_clinical=None,is_ensembl_canonical=None) for transcript_name in transcripts_not_in_db]
            transcripts.extend(transcripts_not_in_db)

        return transcripts
    
    def insert_automatic_classification(self, variant_id, scheme, classification):
        date = functions.get_now()
        command = "INSERT INTO automatic_classification (variant_id, scheme_name, classification, date) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(command, (variant_id, scheme, classification, date))
        self.conn.commit()
        return self.get_last_insert_id()

    def insert_automatic_classification_criterium_applied(self, automatic_classification_id, name, rule_type, evidence_type, strength, type, comment, is_selected):
        comment = functions.encode_html(comment)
        command = "INSERT INTO automatic_classification_criteria_applied (automatic_classification_id, name, rule_type, evidence_type, strength, type, comment, is_selected) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, (automatic_classification_id, name, rule_type, evidence_type, strength, type, comment, is_selected))
        self.conn.commit()

    def clear_automatic_classification(self, variant_id):
        command = "DELETE FROM automatic_classification WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id,))
        self.conn.commit()

    def get_automatic_classification(self, variant_id):
        command = "SELECT id, scheme_name, classification, date FROM automatic_classification WHERE variant_id = %s"
        self.cursor.execute(command, (variant_id, ))
        result = self.cursor.fetchall() # prevent unfetched result
        if len(result) == 0:
            return None
        result = result[len(result) - 1] # take the newest one, this should not be neccessary
        return result

    def get_automatic_classification_criteria_applied(self, automatic_classification_id):
        command = "SELECT id, name, rule_type, evidence_type, is_selected, strength, type, comment FROM automatic_classification_criteria_applied WHERE automatic_classification_id = %s"
        self.cursor.execute(command, (automatic_classification_id, ))
        result = self.cursor.fetchall()
        return result