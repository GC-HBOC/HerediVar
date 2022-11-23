from flask import flash, abort
import re
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions

def preprocess_query(query, pattern = '.*'):
    seps = get_search_query_separators()
    query = query.strip()
    query = ''.join(re.split('[ \r\f\v\t]', query)) # remove whitespace except for newline
    reg = "^(%s" + seps + "*)*$"
    pattern = re.compile(reg % (pattern, ))
    result = pattern.match(query)
    #print(result.group(0))
    if result is None:
        return None # means that there is an error!
    # split into list
    query = re.split(seps, query)
    query = [x for x in query if x != '']
    return query

def get_search_query_separators():
    return '[;,\n]'

def bed_ranges_to_heredivar_ranges(ranges):
    ranges = re.split('[\n]', ranges)
    result = []
    for range_entry in ranges:
        range_entry = range_entry.strip()
        if '\t' in range_entry: # it is a bed style range
            new_heredivar_range = convert_bed_line_to_heredivar_range(range_entry)
            if new_heredivar_range is not None:
                result.append(new_heredivar_range)
        else: # it is already a heredivar style range
            result.append(range_entry)
    return ';'.join(result)


def convert_bed_line_to_heredivar_range(bed_line):
    parts = bed_line.split('\t')
    chrom = parts[0]
    chr_num = functions.validate_chr(chrom)
    if chr_num is None:
        return None
    chrom = 'chr' + str(chr_num)
    start = parts[1] # bed ranges are zero based at the start position
    end = int(parts[2]) - 1 # bed ranges are one based at the end position -> need to substract one because mysql has start and end zero based when using BETWEEN operator
    return chrom + ':' + str(start) + '-' + str(end)


def extract_genes(request_obj):
    genes = request_obj.args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")
    return genes

def extract_ranges(request_obj):
    ranges = request_obj.args.get('ranges', '')
    if '\t' in ranges:
        ranges = bed_ranges_to_heredivar_ranges(ranges)
    ranges = preprocess_query(ranges, pattern= r"chr.+:\d+-\d+")
    if ranges is None:
        flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    return ranges

def extract_consensus_classifications(request_obj):
    consensus_classifications = request_obj.args.getlist('consensus')
    consensus_classifications = ';'.join(consensus_classifications)
    consensus_classifications = preprocess_query(consensus_classifications, r'[12345-]?')
    if consensus_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")
    return consensus_classifications

def extract_user_classifications(request_obj):
    user_classifications = request_obj.args.getlist('user')
    user_classifications = ';'.join(user_classifications)
    user_classifications = preprocess_query(user_classifications, r'[12345-]?')
    if user_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5. Results are not filtered by consensus classification.", "alert-danger")
    return user_classifications

def extract_hgvs(request_obj):
    hgvs = request_obj.args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = r".*:?c\..+")
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! c.HGVS should be prefixed by this pattern: 'transcript:c.' Results are not filtered by hgvs.", "alert-danger")
    if any(not(x.startswith('ENST') or x.startswith('NM') or x.startswith('NR') or x.startswith('XM') or x.startswith('XR')) for x in hgvs):
        flash("You are probably searching for a HGVS c-dot string without knowing its transcript. Be careful with the search results as they might not contain the variant you are looking for!", "alert-warning")
    return hgvs

def extract_lookup_list(request_obj, user_id, conn):
    lookup_list_name = request_obj.args.get('lookup_list_name', '')
    lookup_list_id = request_obj.args.get('lookup_list_id', '')
    variant_ids_oi = []
    if (lookup_list_name.strip() != '' and lookup_list_id.strip() == ''):
        flash("The list you are trying to access does not exist. Results are not filtered by list.", 'alert-danger')
    else:
        lookup_list_id = preprocess_query(lookup_list_id, r'\d*') # either none if there was an error or a list_id
        if len(lookup_list_id) > 1: # only one list_id can be searched at a time
            flash("You have submitted multiple lists which is not allowed. Defaulting to the first one given: " + lookup_list_id[0], "alert-warning")
        if lookup_list_id is None:
            flash("You have an error in your variant id query(s). It must contain only numbers. Results are not filtered by variants.", "alert-danger")
        elif len(lookup_list_id) >= 1:
            lookup_list_id = lookup_list_id[0] # unpack list & set default if there are multiple list_ids
            list_permissions = conn.check_list_permission(user_id, lookup_list_id)
            if list_permissions is not None:
                if not list_permissions['owner'] and not list_permissions['read']:
                    return abort(403)
                else:
                    variant_ids_oi = conn.get_variant_ids_from_list(lookup_list_id)
                    if len(variant_ids_oi) == 0:
                        flash("The list you are trying to access is empty.", "alert-warning")
                        variant_ids_oi = [-1]
            else:
                flash("The list which you are trying to access does not exist.", "alert-danger")
    return variant_ids_oi