from os import path
from os import listdir
from os.path import isfile, join
import sys

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import common.paths as paths

import io
import shutil
import os
from pathlib import Path




def validate_variant_types(variant_types, allowed_variant_types):
    status = 'success'
    message = ""
    for variant_type in variant_types:
        if variant_type not in allowed_variant_types:
            status = "error"
            message = "Variant type " + str(variant_type) + " is unknown."
    return status, message


def get_classified_variants_folder():
    classified_variants_folder = path.join(paths.downloads_dir, "classified_variants")
    Path(classified_variants_folder).mkdir(parents=True, exist_ok=True)
    return classified_variants_folder

def get_all_variants_folder():
    all_variants_folder = path.join(paths.downloads_dir, "all_variants")
    Path(all_variants_folder).mkdir(parents=True, exist_ok=True)
    return all_variants_folder

def get_available_heredivar_versions(folder):
    versions = [f.strip('.vcf.gz') for f in listdir(folder) if isfile(join(folder, f)) and not f.startswith('.') and not f.startswith('errors_')]
    return versions

def generate_consensus_only_vcf(variant_types, dummy = False):
    classified_variants_folder = get_classified_variants_folder()

    last_dump_path = classified_variants_folder + "/.last_dump.txt"
    last_dump_date = functions.get_today()
    path_to_download = classified_variants_folder + "/" + last_dump_date + ".vcf"

    functions.remove_oldest_file(classified_variants_folder, maxfiles=10)

    conn = Connection(['read_only'])
    variant_ids_oi = []
    if not dummy:
        variant_ids_oi = conn.get_variant_ids_with_consensus_classification(variant_types = variant_types)
    status, message = write_vcf_file(variant_ids_oi, path_to_download, conn, get_variant_vcf_line_only_consensus, check_vcf = False)
    conn.close()
    if status == "error":
        raise IOError("There was an error during vcf generation: " + str(message))
    
    with open(last_dump_path, 'w') as last_dump_file:
        last_dump_file.write(last_dump_date)


def get_variant_vcf_line_only_consensus(variant_id, conn: Connection):
    variant = conn.get_variant(variant_id)
    headers, info = variant.to_vcf(simple = True)

    return headers, info


def merge_info_headers(old_headers, new_headers):
    return {**old_headers, **new_headers}


def get_variant_vcf_line(variant_id, conn: Connection):
    variant = conn.get_variant(variant_id)
    # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
    headers, info = variant.to_vcf()
    return headers, info


def get_vcf(variants_oi, conn, worker=get_variant_vcf_line, check_vcf=True):
    status = 'success'
    buffer = io.BytesIO()

    if variants_oi is None:
        buffer.seek(0)
        return buffer, status, "", ""

    final_info_headers = {}
    all_variant_vcf_lines = []
    for id in variants_oi:
        info_headers, variant_vcf = worker(id, conn)
        all_variant_vcf_lines.append(variant_vcf)
        final_info_headers = merge_info_headers(final_info_headers, info_headers)
    
    printable_info_headers = list(final_info_headers.values())
    printable_info_headers.sort()
    functions.write_vcf_header(printable_info_headers, lambda l: buffer.write(l.encode()), tail='\n')
    for line in all_variant_vcf_lines:
        line += '\n'
        buffer.write(line.encode())
    buffer.seek(0)

    # check vcf
    if check_vcf:
        temp_file_path = functions.get_random_temp_file(fileending = ".vcf", filename_ext = "variant_download") #tempfile.gettempdir() + "/variant_download_" + str(uuid.uuid4()) + ".vcf"
        with open(temp_file_path, 'wb') as tf:
            shutil.copyfileobj(buffer, tf)
        returncode, err_msg, vcf_errors = functions.check_vcf(temp_file_path)
        os.remove(temp_file_path)

        buffer.seek(0) # reset the buffer to be able to read from it again

        if returncode != 0:
            status = "error"
        
        return buffer, status, vcf_errors, err_msg
    return buffer, status, "", ""



def write_vcf_file(variant_ids, path, conn: Connection, worker=get_variant_vcf_line, check_vcf = True):
    status = "success"
    message = ""

    # write file in reverse to disc
    generator = get_vcf_stream(variant_ids, conn, worker)
    with open(path, "w") as file:
        for line in generator:
            file.write(line)

    # reverse vcf
    path2 = path + ".rev"
    command = ["tac", path]
    with open(path2, "w") as f:
        returncode, serr, sout = functions.execute_command(command, "tac", stdout = f)
    if returncode != 0:
        status = "error"
        message = functions.collect_info(message, "", serr)
        message = functions.collect_info(message, "", sout)
        functions.rm(path2)
        return status, message
    functions.rm(path)
    returncode, err_msg, command_output = functions.execute_command(["mv", path2, path], "mv")
    if returncode != 0: return "error", err_msg
    
    # check vcf
    if check_vcf:
        returncode, err_msg, vcf_errors = functions.check_vcf(path)
        if returncode != 0:
            status = "error"
            message = functions.collect_info(message, "", err_msg)
            message = functions.collect_info(message, "", vcf_errors)
            return status, message

    return status, message


# this is a generator to get a vcf file in reverse order
def get_vcf_stream(variant_ids, conn, worker=get_variant_vcf_line):
    final_info_headers = {}
    for variant_id in variant_ids:
        info_headers, variant_vcf = worker(variant_id, conn)
        yield variant_vcf + "\n"
        final_info_headers = merge_info_headers(final_info_headers, info_headers)

    printable_info_headers = list(final_info_headers.values())
    printable_info_headers.sort()
    buffer = io.StringIO()
    functions.write_vcf_header(printable_info_headers, lambda l: buffer.write(l), tail='\n')
    buffer.seek(0)
    for line in reversed(list(buffer)):
        yield line


def stream_file(file_path, remove_after = False):
    file = open(file_path, 'r')
    yield from file
    file.close()
    if remove_after:
        os.remove(file_path)






############################################################
########### GET POSSIBLE CLASSES FOR EACH SCHEME ###########
############################################################

def get_possible_classes_acmg(class_counts):
    
    possible_classes = set()

    # numbering comments are nubmers from the official ACMG paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4544753/ (TABLE 5)
    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1: # 1
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2: # 2 
        possible_classes.add(5)
    if class_counts['ps'] == 1: # 3
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pm'] == 1: # 1
        possible_classes.add(4)
    if class_counts['ps'] == 1 and (1 <= class_counts['pm'] <= 2): # 2
        possible_classes.add(4)
    if class_counts['ps'] == 1 and class_counts['pp'] >= 2: # 3
        possible_classes.add(4)
    if class_counts['pm'] >= 3: # 4
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2: # 5
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4: # 6
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1: # 1
        possible_classes.add(1)
    if class_counts['bs'] >=2: # 2
        possible_classes.add(1)
    
    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1: # 1
        possible_classes.add(2)
    if class_counts['bp'] >= 2: # 2
        possible_classes.add(2)
    
    #print(selected_classes)
    #print(class_counts)
    #print(possible_classes)

    return possible_classes



def get_possible_classes_acmg_svi(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2: 
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pm'] == 1:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1:
        possible_classes.add(4)
    if class_counts['ps'] == 1 and (1 <= class_counts['pm'] <= 2):
        possible_classes.add(4)
    if class_counts['ps'] == 1 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >=2:
        possible_classes.add(1)
    
    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)


    return possible_classes


def get_possible_classes_enigma_pten(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2: 
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pm'] == 1:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >=2:
        possible_classes.add(1)
    
    # likely benign
    if class_counts['bs'] == 1:
        possible_classes.add(2)
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)


    return possible_classes



def get_possible_classes_enigma_pten_310(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2: 
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1:
        if class_counts['pm'] == 1 or class_counts['pp'] == 1:
            possible_classes.add(4)
    if class_counts['ps'] == 1:
        if class_counts['pm'] == 1 or class_counts['pm'] == 2 or class_counts['pp'] >= 2:
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >=2:
        possible_classes.add(1)
    
    # likely benign
    if class_counts['bs'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)

    return possible_classes



def get_possible_classes_enigma_atm_1_1_0(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2:
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pm'] == 1:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pm2_pp'] == 1:
        possible_classes.add(4)
    if class_counts['ps'] == 1:
        if class_counts['pp'] >= 2 or (class_counts['pm'] >= 1 and class_counts['pm'] <=2):
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1:
        possible_classes.add(2)
    if class_counts['bs'] == 1: 
        if class_counts['bp'] == 1:
            possible_classes.add(2)
    if class_counts['bp'] >= 2 or class_counts['bm'] >= 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes


def get_possible_classes_enigma_atm_1_3_0(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2:
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pm'] == 1:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pm2_pp'] == 1:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1 and class_counts['pvs1_pp'] == 0: #  (PS3_Supporting, PM2_Supporting, PM3_Supporting, PM5_Supporting, PP3)
        possible_classes.add(4)
    if class_counts['ps'] == 1:
        if class_counts['pp'] >= 2 or (class_counts['pm'] >= 1 and class_counts['pm'] <=2):
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1:
        possible_classes.add(2)
    if class_counts['bs'] == 1: 
        if class_counts['bp'] == 1:
            possible_classes.add(2)
    if class_counts['bp'] >= 2 or class_counts['bm'] >= 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes



def get_possible_classes_enigma_tp53(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2:
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)
    if class_counts['pvs'] == 1:
        if class_counts['pm'] == 1 or class_counts['pp'] == 1:
            possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes




def get_possible_classes_enigma_palb2(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] == 1 or class_counts['pm'] >= 2 or (class_counts['pm'] == 1 and class_counts['pp'] == 1) or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2:
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['ps'] == 1:
        if class_counts['pm'] == 1 or class_counts['pp'] >= 2 or class_counts['pm'] == 2:
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)
    if class_counts['pvs'] == 1:
        if class_counts['pm'] == 1 or class_counts['pp'] == 1:
            possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)
    if class_counts['bs'] == 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes


def get_possible_classes_enigma_brca2_1_0_0(class_counts):
    
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 3:
        possible_classes.add(5)
    if class_counts['ps'] == 2:
        if class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['ps'] == 1 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)
    if class_counts['bs'] == 1 and class_counts['bm'] >= 2:
        possible_classes.add(1)
    if class_counts['bs'] == 1 and class_counts['bm'] == 1 and class_counts['bp'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] == 1 and class_counts['bp'] >= 3:
        possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)
    if class_counts['bp1_bs'] == 1:
        possible_classes.add(2)
    if class_counts['bs'] == 1 and class_counts['bm'] == 1:
        possible_classes.add(2)
    if class_counts['bm'] == 1 and class_counts['bp'] >= 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes





def get_possible_classes_enigma_brca1_1_0_0(class_counts):

    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 3:
        possible_classes.add(5)
    if class_counts['ps'] == 2:
        if class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['ps'] == 2:
        possible_classes.add(4)
    if class_counts['ps'] == 1 and (1 <= class_counts['pm'] <= 2):
        possible_classes.add(4)
    if class_counts['ps'] == 1 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)
    if class_counts['bs'] == 1 and class_counts['bm'] >= 2:
        possible_classes.add(1)
    if class_counts['bs'] == 1 and class_counts['bm'] == 1 and class_counts['bp'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] == 1 and class_counts['bp'] >= 3:
        possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)
    if class_counts['bp1_bs'] == 1:
        possible_classes.add(2)
    if class_counts['bs'] == 1 and class_counts['bm'] == 1:
        possible_classes.add(2)
    if class_counts['bm'] == 1 and class_counts['bp'] >= 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes


def get_possible_classes_enigma_brca12_1_1_0(class_counts):

    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 3:
        possible_classes.add(5)
    if class_counts['ps'] == 2:
        if class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1:
        possible_classes.add(4)
    if class_counts['ps'] == 2:
        possible_classes.add(4)
    if class_counts['ps'] == 1:
        if (class_counts['pm'] >= 1 and class_counts['pm'] <= 2) or class_counts['pp'] >= 2:
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bvs'] == 1:
        if class_counts['bs'] == 1 or class_counts['bm'] == 1 or class_counts['bp'] == 1:
            possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)
    if class_counts['bs'] == 1:
        if class_counts['bm'] >= 2 or (class_counts['bm'] == 1 and class_counts['bp'] >= 1) or class_counts['bp'] >= 3:
            possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1:
        if class_counts['bm'] == 1 or class_counts['bp'] == 1:
            possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)
    if class_counts['bp1_bs'] == 1:
        possible_classes.add(2)

    if class_counts['bm'] == 1 and class_counts['bp'] >= 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes



def get_possible_classes_enigma_brca12_1_2_0(class_counts):

    possible_classes = set()

    # pathogenic
    #if class_counts['pvs'] >= 2:
    #    possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 3:
        possible_classes.add(5)
    if class_counts['ps'] == 2:
        if class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1:
        possible_classes.add(4)
    if class_counts['ps'] == 2:
        possible_classes.add(4)
    if class_counts['ps'] == 1:
        if (class_counts['pm'] >= 1 and class_counts['pm'] <= 2) or class_counts['pp'] >= 2:
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)

    # benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bvs'] == 1:
        if class_counts['bs'] == 1 or class_counts['bm'] == 1 or class_counts['bp'] == 1:
            possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)
    if class_counts['bs'] == 1:
        if class_counts['bm'] >= 2 or (class_counts['bm'] == 1 and class_counts['bp'] >= 1) or class_counts['bp'] >= 3:
            possible_classes.add(1)

    # likely benign
    if class_counts['bs'] == 1:
        if class_counts['bm'] == 1 or class_counts['bp'] == 1:
            possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)
    if class_counts['bp1_bs'] == 1:
        possible_classes.add(2)

    if class_counts['bm'] == 1 and class_counts['bp'] >= 1:
        possible_classes.add(2)

    #print(class_counts)
    #print(possible_classes)

    return possible_classes


def get_possible_classes_enigma_pms2_100(class_counts):
    possible_classes = set()

    # pathogenic
    #1 Very Strong (PVS1) AND ≥ 1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong)
    #USELESS: 1 Very Strong (PVS1) AND ≥ 2 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate)
    #1 Very Strong (PVS1) AND ≥ 1 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate)
    #1 Very Strong (PVS1) AND ≥ 2 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    

    #≥ 2 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong)
    #1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong) AND ≥ 3 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate)
    #1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong) AND 2 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate) AND ≥ 2 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    #1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong) AND 1 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate) AND ≥ 4 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 2:
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    # likely pathogenic
    #1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong) AND 1 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate)
    #1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong) AND ≥ 2 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    #1 Strong (PVS1_Strong, PS1, PS2, PS3, PP1_Strong, PP4_Strong) AND 2 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate)

    #≥ 3 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate)
    #2 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate) AND ≥ 2 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    #1 Moderate (PVS1_Moderate, PS1_Moderate, PS2_Moderate, PS3_Moderate, PM3, PM5, PM6, PP1_Moderate, PP3_Moderate, PP4_Moderate) AND ≥ 4 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    
    #1 Very Strong (PVS1) AND 1 Supporting (PS3_Supporting, PM2_Supporting, PM5_Supporting, PP1, PP3, PP4)
    if class_counts['ps'] == 1:
        if (class_counts['pm'] >= 1 and class_counts['pm'] <= 2) or class_counts['pp'] >= 2:
            possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1:
        possible_classes.add(4)

    # benign
    #1 Stand Alone (BA1)
    #≥ 2 Strong (BS1, BS2, BS3, BS4, BP5_Strong)
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)

    # likely benign
    #1 Strong (BS1, BS2, BS3, BS4, BP5_Strong) AND 1 Supporting (BS3_Supporting, BS4_Supporting, BP4, BP5, BP7)
    #≥ 2 Supporting (BS3_Supporting, BS4_Supporting, BP4, BP5, BP7)
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)

    return possible_classes






def get_possible_classes_enigma_insight_mmr_100(class_counts):
    print(class_counts)
    possible_classes = set()

    # pathogenic
    if class_counts['pvs'] >= 2:
        possible_classes.add(5)
    if class_counts['pvs'] == 1:
        if class_counts['ps'] >= 1 or class_counts['pm'] >= 1 or class_counts['pp'] >= 2:
            possible_classes.add(5)
    if class_counts['ps'] >= 3:
        possible_classes.add(5)
    if class_counts['ps'] == 1:
        if class_counts['pm'] >= 3 or (class_counts['pm'] == 2 and class_counts['pp'] >= 2) or (class_counts['pm'] == 1 and class_counts['pp'] >= 4):
            possible_classes.add(5)
    
    #Likely Pathogenic
    if class_counts['ps'] == 1:
        if (class_counts['pm'] >= 1 and class_counts['pm'] <= 2) or class_counts['pp'] >= 2:
            possible_classes.add(4)
    if class_counts['ps'] == 2:
        possible_classes.add(4)
    if class_counts['pm'] >= 3:
        possible_classes.add(4)
    if class_counts['pm'] == 2 and class_counts['pp'] >= 2:
        possible_classes.add(4)
    if class_counts['pm'] == 1 and class_counts['pp'] >= 4:
        possible_classes.add(4)
    if class_counts['pvs'] == 1 and class_counts['pp'] == 1:
        possible_classes.add(4)

    #Benign
    if class_counts['ba'] >= 1:
        possible_classes.add(1)
    if class_counts['bs'] >= 2:
        possible_classes.add(1)

    #Likely Benign
    if class_counts['bs'] == 1 and class_counts['bp'] == 1:
        possible_classes.add(2)
    if class_counts['bp'] >= 2:
        possible_classes.add(2)

    return possible_classes







#######################################
########### DECISION MAKING ###########
#######################################

def decide_for_class_task_force(selected_classes):
    if '1.1' in selected_classes:
        return 1
    if '2.1' in selected_classes:
        return 2
    if any(x in ['5.1', '5.2', '5.3', '5.4', '5.5', '5.6'] for x in selected_classes):
        return 5
    if any(x in ['1.2', '1.3'] for x in selected_classes):
        return 1
    if any(x in ['2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8', '2.9', '2.10'] for x in selected_classes):
        return 2
    if any(x in ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7', '4.8', '4.9'] for x in selected_classes):
        return 4
    #if any(x in ['3.1', '3.2', '3.3', '3.4', '3.5'] for x in selected_classes):
    #    return 3
    return 3

def get_class_counts(data):
    result = {'pvs':0, 'ps':0, 'pm':0, 'pp':0, 'bp':0, 'bs':0, 'bm':0, 'bvs':0, 'ba':0, 'pm2_pp':0, 'bp1_bs': 0, 'pvs1_pp': 0} 
    # special cases:
    # - pm2_pp: ATM 1.1.0 scheme or ATM 1.3.0 scheme
    # - pvs1_pp: ATM 1.3.0 scheme
    # - bp1_bs: brca1/2 1.1.0 scheme
    data = [x.lower().strip('0123456789') for x in data]
    for key in result:
        key = key.lower()
        result[key] = sum(class_comparer(key, x) for x in data)
    return result

def class_comparer(key: str, value: str):
    if key == value:
        return True
    # key: pp
    # value: pm2_pp
    if value.endswith(key):
        return True
    return False

def decide_for_class_acmg(possible_classes):
    # uncertain significance if criteria for benign and pathogenic are contradictory
    if (1 in possible_classes or 2 in possible_classes) and (4 in possible_classes or 5 in possible_classes):
        final_class = 3

    # choose the one with higher significance if there are different pathogenic possibilities
    elif 4 in possible_classes and 5 in possible_classes:
        final_class = 5

    # choose the one with higher significance if there are different benign possibilities
    elif 1 in possible_classes and 2 in possible_classes:
        final_class = 1

    # if there is only one possibility choose it
    elif len(possible_classes) == 1:
        final_class = list(possible_classes)[0]

    # uncertain significance if no other criteria match
    elif len(possible_classes) == 0:
        final_class = 3
    
    return final_class