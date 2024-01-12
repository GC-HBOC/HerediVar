from flask import flash, abort
import re
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import common.models as models
from functools import cmp_to_key

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

#def bed_ranges_to_heredivar_ranges(ranges):
#    ranges = re.split('[\n]', ranges)
#    result = []
#    for range_entry in ranges:
#        range_entry = range_entry.strip()
#        if '\t' in range_entry: # it is a bed style range
#            new_heredivar_range = convert_bed_line_to_heredivar_range(range_entry)
#            if new_heredivar_range is not None:
#                result.append(new_heredivar_range)
#        else: # it is already a heredivar style range
#            result.append(range_entry)
#    return ';'.join(result)
#
#
#def convert_bed_line_to_heredivar_range(bed_line):
#    parts = bed_line.split('\t')
#    chrom = parts[0]
#    chr_num = functions.validate_chr(chrom)
#    if chr_num is None:
#        return None
#    chrom = 'chr' + str(chr_num)
#    start = parts[1] # bed ranges are zero based at the start position
#    end = int(parts[2]) - 1 # bed ranges are one based at the end position -> need to substract one because mysql has start and end zero based when using BETWEEN operator
#    return chrom + ':' + str(start) + '-' + str(end)

def preprocess_ranges(ranges):
    if ranges is None:
        return None
    seps = get_search_query_separators()
    ranges_split = re.split(seps, ranges)
    ranges_split = [proprocess_range_worker(r) for r in ranges_split]
    ranges_split_filtered = [r for r in ranges_split if r is not None] # filter out erroneous
    if len(ranges_split) != len(ranges_split_filtered):
        flash("At least one of your range query(s) has an error. Please check the syntax. The erroneous range query(s) were removed. You still have " + str(len(ranges_split_filtered)) + " ranges after removing the erroneous ones.", 'alert-danger')
    ranges_split = ';'.join(ranges_split_filtered)
    return ranges_split

def proprocess_range_worker(r):
    r = r.strip()
    r = r.replace(':', '-').replace('\t', '-').replace(' ', '-')
    parts = r.split('-')
    chrom = parts[0]
    chr_num = functions.validate_chr(chrom)
    if chr_num is None:
        return None
    parts[0] = 'chr' + str(chr_num)
    r = '-'.join(parts)
    return r


def extract_ranges(request_obj):
    ranges = request_obj.args.get('ranges', '')
    if ranges != '':
        ranges = preprocess_ranges(ranges)
        ranges = preprocess_query(ranges, pattern= r"(chr)?.+-\d+-\d+")
        if ranges is None:
            flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    else:
        return []
    return ranges


def extract_genes(request_obj):
    genes = request_obj.args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")
    return genes

def extract_variants(request_obj):
    variant_strings = request_obj.args.get('variants', '')
    variant_strings = preprocess_query(variant_strings, pattern=r"(chr)?.+-\d+-.+-.+")
    if variant_strings is None:
        flash("You have an error in your variant query(s). This form is required: chrom-pos-ref-alt OR chrom-start-end-sv_type in case of structural variants. Results are not filtered by genes.", "alert-danger")
    return variant_strings

def extract_external_ids(request_obj):
    external_ids = request_obj.args.get('external_ids', '')
    external_ids = preprocess_query(external_ids)
    if external_ids is None:
        flash("You have an error in your external ID query(s). Results are not filtered by external IDs.", "alert-danger")
    return external_ids

def extract_cdna_ranges(request_obj):
    data = request_obj.args.get('cdna_ranges', '')

    data = preprocess_cdna_ranges(data)
    data = preprocess_query(data, pattern = r"[^:]*:[\*-]?\d+([-+]?\d+)?:[\*-]?\d+([-+]?\d+)?")
    if data is None:
        flash("You have an error in your cDNA range query(s). Results are not filtered by cDNA ranges.", "alert-danger")
    return data

def preprocess_cdna_ranges(ranges):
    if ranges is None:
        return None
    seps = get_search_query_separators()
    ranges_split = re.split(seps, ranges)
    ranges_split = [preprocess_cdna_range_worker(r) for r in ranges_split]
    ranges_split_filtered = [r for r in ranges_split if r is not None] # filter out erroneous
    if len(ranges_split) != len(ranges_split_filtered):
        flash("At least one of your range query(s) has an error. Please check the syntax. The erroneous range query(s) were removed. You still have " + str(len(ranges_split_filtered)) + " ranges after removing the erroneous ones.", 'alert-danger')
    ranges_split = ';'.join(ranges_split_filtered)
    return ranges_split

def preprocess_cdna_range_worker(r):
    r = r.strip()
    r = re.sub(pattern = r"\s+", repl = ':', string = r)
    return r


def extract_consensus_classifications(request_obj, allowed_classes):
    classes = allowed_classes + ['-']
    consensus_classifications = request_obj.args.getlist('consensus')
    consensus_classifications = ';'.join(consensus_classifications)
    regex_inner = '|'.join(classes)
    regex_inner = regex_inner.replace('+', '\+')
    consensus_classifications = preprocess_query(consensus_classifications, r'(' + regex_inner + r')?')
    if consensus_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5, 3+, 3- or M. Results are not filtered by consensus classification.", "alert-danger")
    include_heredicare = True if request_obj.args.get('include_heredicare_consensus', 'off') == 'on' else False
    return consensus_classifications, include_heredicare

def extract_user_classifications(request_obj, allowed_classes):
    classes = allowed_classes + ['-']
    user_classifications = request_obj.args.getlist('user')
    user_classifications = ';'.join(user_classifications)
    regex_inner = '|'.join(classes)
    regex_inner = regex_inner.replace('+', '\+')
    user_classifications = preprocess_query(user_classifications, r'(' + regex_inner + r')?')
    if user_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5, 3+, 3- or M. Results are not filtered by consensus classification.", "alert-danger")
    return user_classifications

def extract_automatic_classifications(request_obj, allowed_classes, which):
    classes = allowed_classes + ['-']
    automatic_classifications = request_obj.args.getlist(which)
    automatic_classifications = ';'.join(automatic_classifications)
    regex_inner = '|'.join(classes)
    regex_inner = regex_inner.replace('+', '\+')
    automatic_classifications = preprocess_query(automatic_classifications, r'(' + regex_inner + r')?')
    if automatic_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5, 3+, 3- or M. Results are not filtered by consensus classification.", "alert-danger")
    return automatic_classifications


def extract_hgvs(request_obj):
    hgvs = request_obj.args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = r".*:?c\..+") 
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! c.HGVS should be prefixed by this pattern: 'transcript:c.' Results are not filtered by hgvs.", "alert-danger")
    elif any(not(x.startswith('ENST') or x.startswith('NM') or x.startswith('NR') or x.startswith('XM') or x.startswith('XR')) for x in hgvs):
        flash("You are probably searching for a HGVS c-dot string without knowing its transcript. Be careful with the search results as they might not contain the variant you are looking for!", "alert-warning")
    return hgvs

def extract_annotations(request_obj, conn: Connection):
    annotation_type_ids = request_obj.args.getlist('annotation_type_id')
    annotation_operations = request_obj.args.getlist('annotation_operation')
    annotation_values = request_obj.args.getlist('annotation_value')

    annotation_restrictions = []

    exceptions_dict = get_exception_dict()

    did_flash = False

    for annotation_type_id, operation, value in zip(annotation_type_ids, annotation_operations, annotation_values):
        annotation_type_id = int(annotation_type_id.strip())
        value = value.strip()
        operation = operation.strip()

        # check that all information is there
        if value == "" and operation == "":
            continue
        if value == "" or operation == "":
            if not did_flash:
                flash("Missing some information for annotation search. Skipped some annotation searches.", "alert-danger")
            did_flash = True
            continue
        
        if annotation_type_id > 0: # standard cases
            annotation_type = conn.get_annotation_type(annotation_type_id)
        else:
            annotation_type = exceptions_dict[annotation_type_id]
            annotation_type_id = get_exception_annotation_type_id(annotation_type, conn)

        # set allowed_annotations
        if annotation_type.value_type in ['float', 'int']:
            allowed_operations = ["=", ">", "<", "<=", ">=", "!="]
        else:
            allowed_operations = ["=", "!=", "~"]

        if annotation_type is None: # check that annotation type id is valid
            if not did_flash:
                flash("Unknown annotation type(s) given! Skipping unknown ones.", "alert-danger")
                did_flash = True
            continue
        
        if annotation_type.value_type in ['float', 'int']:
            try:
                value = float(value)
            except:
                flash("The value " + str(value) + " is not numeric, but must be numeric for " + annotation_type.display_title, "alert-danger")
                continue

        table = "variant_annotation"
        if annotation_type.is_transcript_specific:
            table = "variant_transcript_annotation"
        elif annotation_type.title == 'clinvar_interpretation':
            table = "clinvar_variant_annotation"
        elif 'heredicare' in annotation_type.title:
            table = "variant_heredicare_annotation"

        if operation not in allowed_operations:
            flash("The operation " + operation + " is not allowed for " + annotation_type.display_title + ". It must be one of " + str(allowed_operations).replace('\'', ''), "alert-danger")
            continue

        if operation == '~':
            operation = 'LIKE'
            value = functions.enpercent(value)

        new_annotation_restriction = [table, annotation_type_id, operation, value, annotation_type.title]

        annotation_restrictions.append(new_annotation_restriction)


        # cancerhotspots cancertypes
        # maxentscan
        # maxentscan_swa
    
    return annotation_restrictions

def get_exception_annotation_type_id(annotation_type, conn: Connection):
    if annotation_type.id in [-1, -2]:
        return conn.get_most_recent_annotation_type_id("maxentscan")
    if annotation_type.id in [-3, -4, -5, -6]:
        return conn.get_most_recent_annotation_type_id("maxentscan_swa")

def get_exception_dict():
    result = {}
    result[-1] = models.Annotation_type(
        id = -1,
        title = "maxentscan_ref",
        display_title = "MaxEntScan ref",
        description = "",
        value_type = "float",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = True
        )
    result[-2] = models.Annotation_type(
        id = -2,
        title = "maxentscan_alt",
        display_title = "MaxEntScan alt",
        description = "",
        value_type = "float",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = True
        )
    result[-3] = models.Annotation_type(
        id = -3,
        title = "maxentscan_swa_donor_ref",
        display_title = "MaxEnt SWA donor ref",
        description = "",
        value_type = "float",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = True
        )
    result[-4] = models.Annotation_type(
        id = -4,
        title = "maxentscan_swa_donor_alt",
        display_title = "MaxEnt SWA donor alt",
        description = "",
        value_type = "float",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = True
        )
    result[-5] = models.Annotation_type(
        id = -5,
        title = "maxentscan_swa_acceptor_ref",
        display_title = "MaxEnt SWA acceptor ref",
        description = "",
        value_type = "float",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = True
        )
    result[-6] = models.Annotation_type(
        id = -6,
        title = "maxentscan_swa_acceptor_alt",
        display_title = "MaxEnt SWA acceptor alt",
        description = "",
        value_type = "float",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = True
        )
    result[-7] = models.Annotation_type(
        id = -7,
        title = "clinvar_interpretation",
        display_title = "ClinVar interpretation",
        description = "",
        value_type = "text",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = False
        )
    result[-8] = models.Annotation_type(
        id = -8,
        title = "heredicare_n_fam",
        display_title = "HerediCare nfam",
        description = "",
        value_type = "int",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = False
        )
    result[-9] = models.Annotation_type(
        id = -9,
        title = "heredicare_n_pat",
        display_title = "HerediCare npat",
        description = "",
        value_type = "int",
        version = "",
        version_date = "",
        group_name = "",
        is_transcript_specific = False
        )
    return result

def preprocess_annotation_types_for_search(annotation_types):
    result = []
    for annotation_type in annotation_types:
        if "gnomad" in annotation_type.title:
            annotation_type.display_title = "GnomAD " + annotation_type.display_title
        if "cancerhotspots" in annotation_type.title:
            annotation_type.display_title = "Cancerhotspots " + annotation_type.display_title
        if "flossies" in annotation_type.title:
            annotation_type.display_title = "FLOSSIES " + annotation_type.display_title
        if "tp53db" in annotation_type.title:
            annotation_type.display_title = "TP53db " + annotation_type.display_title
        if "task_force_protein_domain" in annotation_type.title:
            annotation_type.display_title = "task force protein " + annotation_type.display_title
        
        annotation_type.display_title = annotation_type.display_title[0].upper() + annotation_type.display_title[1:]

        if annotation_type.title not in ["spliceai_details", "task_force_protein_domain_source", "maxentscan_ref", "maxentscan_alt", "maxentscan", "maxentscan_swa"]:
            result.append(annotation_type)

    exception_dict = get_exception_dict()
    for exception_id in exception_dict:
        result.append(exception_dict[exception_id])

    result = order_annotation_types(result)
    return result



def order_annotation_types(annotation_types):
    keyfunc = cmp_to_key(mycmp = sort_annotation_types)
    annotation_types.sort(key = keyfunc) # sort by preferred transcript
    return annotation_types
 
def sort_annotation_types(a, b):
    a_title = a.display_title
    b_title = b.display_title

    if a_title > b_title:
        return 1
    elif a_title < b_title:
        return -1
    return 0


def extract_lookup_list(request_obj, user_id, conn):
    lookup_list_names = request_obj.args.getlist('lookup_list_name')
    lookup_list_ids = request_obj.args.getlist('lookup_list_id')
    variant_ids_oi = []
    num_valid_lists = 0
    for list_name, list_id in zip(lookup_list_names, lookup_list_ids):
        list_name = list_name.strip()
        list_id = list_id.strip()
        if list_name == '' and list_id == '':
            continue
        if (list_name != '' and list_id == ''):
            flash("The list you are trying to access does not exist. Results are not filtered by list.", 'alert-danger')
        else:
            list_ids = preprocess_query(list_id, r'\d*') # either none if there was an error or a list_id
            if list_id is None:
                flash("You have an error in your list search.", "alert-danger")
            elif len(list_ids) >= 1:
                num_valid_lists += 1
                list_id = list_ids[0]
                list_permissions = conn.check_list_permission(user_id, list_id)
                if list_permissions is not None:
                    if not list_permissions['owner'] and not list_permissions['read']:
                        flash("You are not allowed to access this list", 'alert-danger')
                        return abort(403)
                    else:
                        variant_ids_oi.extend(conn.get_variant_ids_from_list(list_id))
                else:
                    flash("The list which you are trying to access does not exist.", "alert-danger")
    
    if num_valid_lists > 0 and len(variant_ids_oi) == 0:
        flash("All lists you are trying to access are empty.", "alert-warning")
        variant_ids_oi = [-1]

    #if (lookup_list_name.strip() != '' and lookup_list_id.strip() == ''):
    #    flash("The list you are trying to access does not exist. Results are not filtered by list.", 'alert-danger')
    #else:
    #    lookup_list_ids = preprocess_query(lookup_list_id, r'\d*') # either none if there was an error or a list_id
    #    #if len(lookup_list_id) > 1: # only one list_id can be searched at a time
    #    #    flash("You have submitted multiple lists which is not allowed. Defaulting to the first one given: " + lookup_list_id[0], "alert-warning")
    #    if lookup_list_ids is None:
    #        flash("You have an error in your list search.", "alert-danger")
    #    elif len(lookup_list_ids) >= 1:
    #        for lookup_list_id in lookup_list_ids:
    #            list_permissions = conn.check_list_permission(user_id, lookup_list_id)
    #            if list_permissions is not None:
    #                if not list_permissions['owner'] and not list_permissions['read']:
    #                    flash("You are not allowed to access this list", 'alert-danger')
    #                else:
    #                    variant_ids_oi.extend(conn.get_variant_ids_from_list(lookup_list_id))
    #            else:
    #                flash("The list which you are trying to access does not exist.", "alert-danger")
    
    #if len(variant_ids_oi) == 0:
    #    flash("All lists you are trying to access are empty.", "alert-warning")
    #    variant_ids_oi = [-1]
    variant_ids_oi = list(set(variant_ids_oi)) # make variant ids them unique
    return variant_ids_oi


def extract_search_settings(request_obj):
    sort_bys = ["genomic position", "recent"]
    page_sizes = ["5", "20", "50", "100"]

    selected_page_size = request_obj.args.get('page_size', page_sizes[1])
    selected_sort_by = request_obj.args.get('sort_by', sort_bys[0])
    include_hidden = True if request_obj.args.get('include_hidden', 'off') == 'on' else False


    if selected_page_size not in page_sizes:
        flash("This page size is not supported. Defaulting to 20.", "alert-warning")
        selected_page_size = "20"
    if selected_sort_by not in sort_bys:
        flash("The variant table can not be sorted by " + str(selected_sort_by) + ". Defaulting to genomic position sort.", "alert-warning")
        selected_sort_by = "genomic position"

    return sort_bys, page_sizes, selected_page_size, selected_sort_by, include_hidden

    