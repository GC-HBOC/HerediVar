from flask import Blueprint, abort, current_app, send_from_directory, send_file, request, flash, redirect, url_for, session, jsonify, Markup, make_response

from os import path
import sys

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import common.paths as paths
import io
import tempfile
import shutil
import re
import os
import uuid
from pathlib import Path
from flask import render_template
from os import listdir
from os.path import isfile, join



def validate_variant_types(variant_types, allowed_variant_types):
    status = 'success'
    message = ""
    for variant_type in variant_types:
        if variant_type not in allowed_variant_types:
            status = "error"
            message = "Variant type " + str(variant_type) + " is unknown."
    return status, message


def get_classified_variants_folder(variant_types):
    classified_variants_folder = path.join(paths.downloads_dir, "classified_variants_" + '_'.join(variant_types))
    Path(classified_variants_folder).mkdir(parents=True, exist_ok=True)
    return classified_variants_folder

def get_all_variants_folder():
    all_variants_folder = path.join(paths.downloads_dir, "all_variants")
    Path(all_variants_folder).mkdir(parents=True, exist_ok=True)
    return all_variants_folder

def get_available_heredivar_versions(folder):
    versions = [f.strip('.vcf') for f in listdir(folder) if isfile(join(folder, f)) and not f.startswith('.')]
    return versions

def generate_consensus_only_vcf(variant_types):
    classified_variants_folder = get_classified_variants_folder(variant_types)

    last_dump_path = classified_variants_folder + "/.last_dump.txt"
    last_dump_date = functions.get_today()
    path_to_download = classified_variants_folder + "/" + last_dump_date + ".vcf"

    functions.remove_oldest_file(classified_variants_folder, maxfiles=10)

    conn = Connection(['read_only'])
    variant_ids_oi = conn.get_variant_ids_with_consensus_classification(variant_types = variant_types)
    vcf_file_buffer, x, xx, xxx = get_vcf(variant_ids_oi, conn, get_variant_vcf_line_only_consensus)
    functions.buffer_to_file_system(vcf_file_buffer, path_to_download)
    conn.close()

    with open(last_dump_path, 'w') as last_dump_file:
        last_dump_file.write(functions.get_today())


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






#def get_vcf(variants_oi, conn, worker=get_variant_vcf_line):
#    status = 'success'
#
#    final_info_headers = {}
#    all_variant_vcf_lines = []
#    for id in variants_oi:
#        info_headers, variant_vcf = worker(id, conn)
#        all_variant_vcf_lines.append(variant_vcf)
#        final_info_headers = merge_info_headers(final_info_headers, info_headers)
#    
#    helper = io.StringIO()
#    printable_info_headers = list(final_info_headers.values())
#    printable_info_headers.sort()
#    functions.write_vcf_header(printable_info_headers, helper.write, tail='\n')
#    for line in all_variant_vcf_lines:
#        helper.write(line + '\n')
#
#    buffer = io.BytesIO()
#    buffer.write(helper.getvalue().encode())
#    buffer.seek(0)
#
#    temp_file_path = tempfile.gettempdir() + "/variant_download_" + str(uuid.uuid4()) + ".vcf"
#    with open(temp_file_path, 'w') as tf:
#        helper.seek(0)
#        copyfileobj(helper, tf)
#    helper.close()
#
#    returncode, err_msg, vcf_errors = functions.check_vcf(temp_file_path)
#
#    os.remove(temp_file_path)
#
#    if returncode != 0:
#        if request.args.get('force') is None:
#            status = "redirect"
#            return None, status, vcf_errors, err_msg
#
#    return buffer, status, "", ""


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

        if returncode != 0:
            status = "error"
            return None, status, vcf_errors, err_msg

        buffer.seek(0)
    return buffer, status, "", ""







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



def get_possible_classes_enigma_atm(class_counts):
    
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


def get_possible_classes_enigma_brca2(class_counts):
    
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



def get_possible_classes_enigma_brca1(class_counts):

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
    result = {'pvs':0, 'ps':0, 'pm':0, 'pp':0, 'bp':0, 'bs':0, 'bm':0, 'ba':0, 'pm2_pp':0, 'bp1_bs': 0} # pm2_pp is special case for ATM scheme and bp1_bs is special case for brca1/2
    data = [x.lower().strip('0123456789') for x in data]
    for key in result:
        key = key.lower()
        result[key] = sum(key == x for x in data)
    return result

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