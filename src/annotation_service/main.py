from db_IO import Connection
import functions
import subprocess
import paths
import os
import tempfile

db_io = Connection()


def get_pending_requests():
    db_io.cursor.execute("SELECT variant_id FROM annotation_log WHERE status = 'pending'")
    pending_variant_ids = db_io.cursor.fetchall()
    # fetchall ALWAYS returns a list of tuples (here: variant_id[1] always empty)
    pending_variant_ids = [x[0] for x in pending_variant_ids]
    return pending_variant_ids




def start_vep(input_vcf, output_vcf):
    command = [paths.vep_path,
            "-i", input_vcf, "--format vcf"
            "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite"]
    subprocess.run(command)


if __name__ == '__main__':
    pending_variant_ids = get_pending_requests()

    temp_file_path = tempfile.gettempdir()
    print(temp_file_path)
    one_variant_path = temp_file_path + "/variant_temp.vcf"

    for variant_id in pending_variant_ids:
        one_variant = db_io.get_one_variant(variant_id)
        functions.variant_to_vcf(one_variant, one_variant_path)

        output_path = temp_file_path + "/variant_vep_" + str(variant_id) + ".vcf"
        #start_vep(one_variant_path, output_path)







    db_io.close_connection()






    #conn = get_db_connection()
    #try:
    #    cursor = conn.cursor()
    #finally:
    #    conn.close()

    #retrieve_vep("2:214730440", "A")