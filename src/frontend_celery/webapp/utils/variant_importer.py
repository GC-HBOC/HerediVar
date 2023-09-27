from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
from ..tasks import annotate_variant
import annotation_service.main as annotation_service


def start_annotation_service(conn: Connection, user_id, variant_id = None, annotation_queue_id = None, job_config = annotation_service.get_default_job_config()):
    if variant_id is not None:
        annotation_queue_id = conn.insert_annotation_request(variant_id, user_id) # only inserts a new row if there is none with this variant_id & pending
        log_postfix = " for variant " + str(variant_id)
    else:
        log_postfix = " for annotation queue entry " + str(annotation_queue_id)
    task = annotate_variant.apply_async(args=[annotation_queue_id, job_config])
    print("Issued annotation for annotation queue id: " + str(annotation_queue_id) + " with celery task id: " + str(task.id) + log_postfix)
    #current_app.logger.info(session['user']['preferred_username'] + " started the annotation service for annotation queue id: " + str(annotation_queue_id) + " with celery task id: " + str(task.id) + log_postfix)
    conn.insert_celery_task_id(annotation_queue_id, task.id)
    return task.id


def validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn: Connection, user_id, allowed_sequence_letters = "ACGT", perform_annotation = True):
    message = ""
    was_successful = True
    new_variant = {}
    # validate request

    chrom, chrom_is_valid = functions.curate_chromosome(chrom)
    ref, ref_is_valid = functions.curate_sequence(ref, allowed_sequence_letters)
    alt, alt_is_valid = functions.curate_sequence(alt, allowed_sequence_letters)
    pos, pos_is_valid = functions.curate_position(pos)

    if not chrom_is_valid:
        message = "Chromosome is invalid: " + str(chrom)
    elif not ref_is_valid:
        message = "Reference base is invalid: " + str(ref)
    elif not alt_is_valid:
        message = "Alternative base is invalid: " + str(alt)
    elif not pos_is_valid:
        message = "Position is invalid: " + str(pos)
    if not chrom_is_valid or not ref_is_valid or not alt_is_valid or not pos_is_valid:
        was_successful = False
        return was_successful, message, new_variant



    tmp_file_path = functions.get_random_temp_file("vcf")
    functions.variant_to_vcf(chrom, pos, ref, alt, tmp_file_path)

    do_liftover = genome_build == 'GRCh37'
    returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post = functions.preprocess_variant(tmp_file_path, do_liftover = do_liftover)

    
    if returncode != 0:
        message = err_msg
        was_successful = False
        functions.rm(tmp_file_path)
        return was_successful, message, new_variant
    if 'ERROR:' in vcf_errors_pre:
        message = vcf_errors_pre.replace('\n', ' ')
        was_successful = False
        functions.rm(tmp_file_path)
        return was_successful, message, new_variant
    if genome_build == 'GRCh37':
        unmapped_variants_vcf = open(tmp_file_path + '.lifted.unmap', 'r')
        unmapped_variant = None
        for line in unmapped_variants_vcf:
            if line.startswith('#') or line.strip() == '':
                continue
            unmapped_variant = line
            break
        unmapped_variants_vcf.close()
        if unmapped_variant is not None:
            message = 'ERROR: could not lift variant ' + unmapped_variant
            was_successful = False
            functions.rm(tmp_file_path)
            functions.rm(tmp_file_path + ".lifted.unmap")
            return was_successful, message, new_variant
    if 'ERROR:' in vcf_errors_post:
        message = vcf_errors_post.replace('\n', ' ')
        was_successful = False
        functions.rm(tmp_file_path)
        functions.rm(tmp_file_path + ".lifted.unmap")
        return was_successful, message, new_variant

    if was_successful:
        tmp_file = open(tmp_file_path, 'r')
        for line in tmp_file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            parts = line.split('\t')
            new_chr = parts[0]
            new_pos = parts[1]
            new_ref = parts[3]
            new_alt = parts[4]
            new_variant = {'chrom': new_chr, 'pos': new_pos, 'ref': new_ref, 'alt': new_alt}
            break # there is only one variant in the file
        tmp_file.close()

        is_duplicate = conn.check_variant_duplicate(new_chr, new_pos, new_ref, new_alt) # check if variant is already contained
        
        if not is_duplicate:
            # insert it & capture the annotation_queue_id of the newly inserted variant to start the annotation service in celery
            annotation_queue_id = conn.insert_variant(new_chr, new_pos, new_ref, new_alt, chrom, pos, ref, alt, user_id)
            if perform_annotation:
                celery_task_id = start_annotation_service(conn, user_id, annotation_queue_id = annotation_queue_id) # starts the celery background task
        else:
            message = "Variant not imported: already in database!!"
            was_successful = False

    functions.rm(tmp_file_path)
    functions.rm(tmp_file_path + ".lifted.unmap")
    return was_successful, message, new_variant








def fetch_heredicare(vid, heredicare_interface, user_id, conn:Connection):
   
    variant, status, message = heredicare_interface.get_variant(vid)

    if status != 'success':
        return status, message
    

    genome_build = "GRCh38"

    
    # first check if the hg38 information is there
    chrom = variant.get('CHROM')
    pos = variant.get('POS_HG38')
    ref = variant.get('REF_HG38')
    alt = variant.get('ALT_HG38')

    # if there is missing information check if there is hg19 information
    if any([x is None for x in [chrom, pos, ref, alt]]):
        pos = variant.get('POS_HG19')
        ref = variant.get('REF_HG19')
        alt = variant.get('ALT_HG19')
        genome_build = "GRCh37"
    
    # if there is still missing data check if the variant has hgvs_c information
    if any([x is None for x in [chrom, pos, ref, alt]]):
        transcript = variant.get('REFSEQ')
        hgvs_c = variant.get('CHGVS')

        #TODO: maybe check if you can get some transcripts from the gene??? gene = variant.get('GEN')
        if any([x is None for x in [transcript, hgvs_c]]):
            status = "error"
            message = "Not enough data to convert variant!"
            return status, message

        chrom, pos, ref, alt, err_msg = functions.hgvsc_to_vcf(hgvs_c, transcript) # convert to vcf

        if err_msg != "": # catch runtime errors of hgvs to vcf
            status = "error"
            message = "HGVS to VCF yieled an error: " + str(err_msg)
            return status, message
        
        # the conversion was not successful
        if any([x is None for x in [chrom, pos, ref, alt]]): 
            status = "error"
            message = "HGVS could not be converted to VCF: " + str(transcript) + ":" + str(hgvs_c)
            return status, message
    
    validate_and_insert_variant(chrom, pos, ref, alt, genome_build, conn, user_id, allowed_sequence_letters = "ACGT")

    return status, message
        



# 'VID': '19439917' --> variant id
# 'REV_STAT': '2' --> 2: kein review, 3: review erfolgt, 1: neu angelegt?
# 'QUELLE': '2' --> 1: manuell, 2: upload
# 'GEN': 'MSH2' --> das gen
# 'REFSEQ': 'NM_000251.3' --> Transkript
# 'ART': '-1' --> 1-6 sind klar, was bedeutet -1?
# 'CHROM': '2' --> chromosom
# 'POS_HG19': '47630514' --> hg19 position
# 'REF_HG19': 'G' --> hg19 reference base
# 'ALT_HG19': 'C' --> hg19 alternative base
# 'POS_HG38': '47403375' --> hg38 position
# 'REF_HG38': 'G' --> hg38 reference base
# 'ALT_HG38': 'C' --> hg38 alternative base
# 'KONS': '-1' --> consequence, value 1-10
# 'KONS_VCF': 'missense_variant' --> consequence?? was ist der Unterschied zu KONS?
# 'CHGVS': 'c.184G>C' --> c.hgvs
# 'PHGVS': 'Gly62Arg' --> p.hgvs


