from db_IO import Connection
import functions
import subprocess
import paths
import os
import tempfile

conn = Connection()


def start_vep(input_vcf, output_vcf):
    command = [paths.vep_path,
               "-i", input_vcf, "--format", "vcf",
               "-o", output_vcf, "--vcf", "--no_stats", "--force_overwrite",
               "--species", "homo_sapiens", "--assembly", "GRCh38",
               "--fork", "1",
               "--offline", "--cache", "--dir_cache", "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache",
               "--fasta", "/mnt/storage2/GRCh38/share/data/genomes/GRCh38.fa",
               "--numbers", "--hgvs", "--domains", "--transcript_version",
               "--regulatory",
               "--sift", "b", "--polyphen", "b",
               "--af", "--af_gnomad", "--failed", "1",
               "--pubmed",
               "--fields",
               "Allele,Consequence,IMPACT,SYMBOL,HGNC_ID,Feature,Feature_type,EXON,INTRON,HGVSc,HGVSp,DOMAINS,SIFT,PolyPhen,Existing_variation,AF,gnomAD_AF,gnomAD_AFR_AF,gnomAD_AMR_AF,gnomAD_EAS_AF,gnomAD_NFE_AF,gnomAD_SAS_AF,BIOTYPE,PUBMED"]
    completed_process = subprocess.run(command, capture_output=True) # catch errors and warnings here from STDERR
    exit_status = completed_process.returncode
    stderr = completed_process.stderr.decode()
    return exit_status, stderr


if __name__ == '__main__':
    pending_requests = conn.get_pending_requests()

    temp_file_path = tempfile.gettempdir()
    # print(temp_file_path)
    one_variant_path = temp_file_path + "/variant_temp.vcf"

    for request_id, variant_id in pending_requests:
        one_variant = conn.get_one_variant(variant_id)
        functions.variant_to_vcf(one_variant, one_variant_path)

        output_path = temp_file_path + "/variant_vep_" + variant_id + ".vcf"
        exit_status_vep, stderr_vep = start_vep(one_variant_path, output_path)

        print(exit_status_vep)
        print(stderr_vep)

        #conn.update_annotation_log(request_id, status, error_msg)


    conn.close()
