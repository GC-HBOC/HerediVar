from flask import flash, abort
import re
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import common.models as models
from functools import cmp_to_key

def get_search_query_separators():
    return '[;,\n]'

def preprocess_query(query, pattern = '.*', seps = get_search_query_separators(), remove_whitespace = True):
    query = query.strip()
    if remove_whitespace:
        query = ''.join(re.split('[ \r\f\v\t]', query)) # remove whitespace except for newline
    reg = "^(%s" + seps + "*)*$"
    pattern = re.compile(reg % (pattern, ))
    result = pattern.match(query)
    if result is None:
        return None # means that there is an error!
    # split into list
    query = re.split(seps, query)
    query = [x for x in query if x != '']
    return query



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
    ranges_split = [preprocess_range_worker(r) for r in ranges_split]
    ranges_split_filtered = [r for r in ranges_split if r is not None] # filter out erroneous
    if len(ranges_split) != len(ranges_split_filtered):
        flash("At least one of your range query(s) has an error. Please check the syntax. The erroneous range query(s) were removed. You still have " + str(len(ranges_split_filtered)) + " ranges after removing the erroneous ones.", 'alert-warning')
    ranges_split = ';'.join(ranges_split_filtered)
    return ranges_split

def preprocess_range_worker(r):
    r = r.strip()
    r = re.sub(r"\s+", " ", r)
    r = r.replace(':', '-').replace(' ', '-')
    parts = r.split('-')
    if len(parts) != 3:
        return None
    chrom = parts[0]
    chr_num = functions.validate_chr(chrom)
    if chr_num is None:
        return None
    parts[0] = 'chr' + str(chr_num)
    r = '-'.join(parts)
    return r


def extract_ranges(request_args):
    ranges = request_args.get('ranges', '')
    if ranges != '':
        print(ranges)
        ranges = preprocess_ranges(ranges)
        print(ranges)
        ranges = preprocess_query(ranges, pattern= r"(chr)?.+-\d+-\d+")
        print(ranges)
        if ranges is None:
            flash("You have an error in your range query(s). Please check the syntax! Results are not filtered by ranges.", "alert-danger")
    else:
        return []
    return ranges


def extract_variant_ids(request_args):
    variant_ids = request_args.get('variant_ids', '')
    variant_ids = preprocess_query(variant_ids, pattern=r"\d+")
    if variant_ids is None:
        flash("You have an error in your variant_ids query(s). Results are not filtered by variant_ids.", "alert-danger")
    return variant_ids

def extract_selected_variants(request_args):
    variant_ids = request_args.get('selected_variants', '')
    variant_ids = preprocess_query(variant_ids, pattern=r"\d+")
    if variant_ids is None:
        flash("You have an error in your variant_ids query(s). Results are not filtered by variant_ids.", "alert-danger")
    return variant_ids

def extract_genes(request_args):
    genes = request_args.get('genes', '')
    genes = preprocess_query(genes)
    if genes is None:
        flash("You have an error in your genes query(s). Results are not filtered by genes.", "alert-danger")
    return genes

def extract_variants(request_args):
    variant_strings = request_args.get('variants', '')
    variant_strings = preprocess_query(variant_strings, pattern=r"(chr)?.+-\d+-[a-zA-Z]+-[a-zA-Z]+")
    if variant_strings is None:
        flash("You have an error in your variant query(s). This form is required: chrom-pos-ref-alt OR chrom-start-end-sv_type in case of structural variants. Results are not filtered by variant strings.", "alert-danger flash_id:search_error_variants")
    return variant_strings

def extract_variant_types(request_args, allowed_variant_types):
    variant_types = request_args.get('variant_type', '')
    #variant_types = ';'.join(variant_types)
    regex_inner = '|'.join(allowed_variant_types)
    variant_types = preprocess_query(variant_types, r'(' + regex_inner + r')?')
    if variant_types is None:
        flash("You have an error in your variant type query. Results are not filtered by variant types.", "alert-danger")
    return variant_types


def extract_external_ids(request_args):
    external_ids = request_args.get('external_ids', '')
    external_ids = preprocess_query(external_ids)
    if external_ids is None:
        flash("You have an error in your external ID query(s). Results are not filtered by external IDs.", "alert-danger")
    return external_ids

def extract_cdna_ranges(request_args):
    data = request_args.get('cdna_ranges', '')

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


def extract_consensus_classifications(request_args, allowed_classes):
    classes = allowed_classes + ['-']
    consensus_classifications = request_args.get('consensus', '')
    #consensus_classifications = ';'.join(consensus_classifications)
    regex_inner = '|'.join(classes)
    regex_inner = regex_inner.replace('+', '\+')
    consensus_classifications = preprocess_query(consensus_classifications, r'(' + regex_inner + r')?')
    if consensus_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5, 3+, 3- or M. Results are not filtered by consensus classification.", "alert-danger")
    include_heredicare = True if request_args.get('include_heredicare_consensus', 'off') == 'on' else False
    return consensus_classifications, include_heredicare

def extract_user_classifications(request_args, allowed_classes):
    classes = allowed_classes + ['-']
    user_classifications = request_args.get('user', '')
    #user_classifications = ';'.join(user_classifications)
    regex_inner = '|'.join(classes)
    regex_inner = regex_inner.replace('+', '\+')
    user_classifications = preprocess_query(user_classifications, r'(' + regex_inner + r')?')
    if user_classifications is None:
        flash("You have an error in your user class query(s). It must consist of a number between 1-5, 3+, 3- or M. Results are not filtered by consensus classification.", "alert-danger")
    return user_classifications

def extract_automatic_classifications(request_args, allowed_classes, which):
    classes = allowed_classes + ['-']
    automatic_classifications = request_args.get(which, '')
    #automatic_classifications = ';'.join(automatic_classifications)
    regex_inner = '|'.join(classes)
    regex_inner = regex_inner.replace('+', '\+')
    automatic_classifications = preprocess_query(automatic_classifications, r'(' + regex_inner + r')?')
    if automatic_classifications is None:
        flash("You have an error in your consensus class query(s). It must consist of a number between 1-5, 3+, 3- or M. Results are not filtered by consensus classification.", "alert-danger")
    return automatic_classifications


def extract_clinvar_upload_states(request_args, allowed_upload_states):
    regex_inner = '|'.join(allowed_upload_states)
    clinvar_upload_states = request_args.get('clinvar_upload_state', '')
    clinvar_upload_states = preprocess_query(clinvar_upload_states, r'(' + regex_inner + r')?')
    if clinvar_upload_states is None:
        flash("You have an error in your clinvar upload state query(s). Must be one of " + str(allowed_upload_states) + " Results are not filtered by clinvar upload states.", "alert-danger")
    return clinvar_upload_states


def extract_needs_upload(request_args, allowed_needs_request):
    regex_inner = '|'.join(allowed_needs_request)
    clinvar_upload_states = request_args.get('needs_upload', '')
    clinvar_upload_states = preprocess_query(clinvar_upload_states, r'(' + regex_inner + r')?')
    if clinvar_upload_states is None:
        flash("You have an error in your needs upload query(s). Must be one of " + str(allowed_needs_request) + " Results are not filtered by needs upload.", "alert-danger")
    return clinvar_upload_states

def extract_heredicare_upload_states(request_args, allowed_upload_states):
    regex_inner = '|'.join(allowed_upload_states)
    heredicare_upload_states = request_args.get('heredicare_upload_state', '')
    heredicare_upload_states = preprocess_query(heredicare_upload_states, r'(' + regex_inner + r')?')
    if heredicare_upload_states is None:
        flash("You have an error in your heredicare upload state query(s). Must be one of " + str(allowed_upload_states) + " Results are not filtered by heredicare upload states.", "alert-danger")
    return heredicare_upload_states


def extract_hgvs(request_args):
    hgvs = request_args.get('hgvs', '')
    hgvs = preprocess_query(hgvs, pattern = r".*:?c\..+") 
    if hgvs is None:
        flash("You have an error in your hgvs query(s). Please check the syntax! c.HGVS should be prefixed by this pattern: 'transcript:c.' Results are not filtered by hgvs.", "alert-danger")
    elif any(not(x.startswith('ENST') or x.startswith('NM') or x.startswith('NR') or x.startswith('XM') or x.startswith('XR')) for x in hgvs):
        flash("You are probably searching for a HGVS c-dot string without knowing its transcript. Be careful with the search results as they might not contain the variant you are looking for!", "alert-warning")
    return hgvs

def extract_annotations(request_args, conn: Connection):
    annotation_type_ids = request_args.get('annotation_type_id', '')
    annotation_operations = request_args.get('annotation_operation', '')
    annotation_values = request_args.get('annotation_value', '')

    annotation_type_ids = [x for x in annotation_type_ids.split(';') if x.strip() != '']
    annotation_operations = [x for x in annotation_operations.split(';') if x.strip() != '']
    annotation_values = [x for x in annotation_values.split(';') if x.strip() != '']

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


def extract_point_score(request_args, point_score_types):
    type_ids = request_args.get('point_score_type_id', '')
    operations = request_args.get('point_score_operation', '')
    values = request_args.get('point_score_value', '')

    restrictions = []

    if type_ids == "":
        return restrictions

    type_ids = [int(x.strip()) for x in type_ids.split(';')]
    operations = [x.strip() for x in operations.split(';')]
    values = [x.strip() for x in values.split(';')]

    valid_point_score_types = [x["id"] for x in point_score_types]
    

    did_flash = False
    for type_id, operation, value in zip(type_ids, operations, values):

        # check that all information is there
        if value == "" and operation == "":
            continue
        if value == "" or operation == "":
            if not did_flash:
                flash("Missing some information for point score search value and operation must be present. Skipped some point score searches.", "alert-danger")
            did_flash = True
            continue

        if type_id not in valid_point_score_types: # check that type id is valid
            if not did_flash:
                flash("Unknown point score type(s) given! Skipping unknown ones.", "alert-danger")
                did_flash = True
            continue

        # set allowed_operations
        allowed_operations = ["=", ">", "<", "<=", ">=", "!="]
        if operation not in allowed_operations:
            flash("The operation " + operation + " is not allowed for " + point_score_types[type_id]["display_title"] + ". It must be one of " + str(allowed_operations).replace('\'', ''), "alert-danger")
            continue

        try:
            value = float(value)
        except:
            flash("The value " + str(value) + " is not numeric, but must be numeric for " + point_score_types[type_id]["display_title"], "alert-danger")
            continue

        new_restriction = [point_score_types[type_id]["table"], type_id, operation, value]

        restrictions.append(new_restriction)
    
    return restrictions



def extract_lookup_list(request_args, user_id, conn: Connection):
    lookup_list_names = request_args.get('lookup_list_name', "").split(';')
    lookup_list_ids = request_args.get('lookup_list_id', "").split(';')
    variant_ids_oi = []
    num_valid_lists = 0
    for list_name, list_id in zip(lookup_list_names, lookup_list_ids):
        list_name = list_name.strip()
        list_id = list_id.strip()
        if list_name == '' and list_id == '':
            continue
        if (list_name != '' and list_id == ''):
            flash("The list " + list_name + " does not exist. Results are not filtered by this list.", 'alert-danger flash_id:unknown_list_search')
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
                        return abort(403)
                    else:
                        variant_ids_oi.extend(conn.get_variant_ids_from_list(list_id))
                else:
                    flash("The list which you are trying to access does not exist.", "alert-danger flash_id:unknown_list_search")
    
    if num_valid_lists > 0 and len(variant_ids_oi) == 0:
        flash("All lists you are trying to access are empty.", "alert-warning")
        variant_ids_oi = [-1]

    variant_ids_oi = list(set(variant_ids_oi)) # make variant ids them unique
    return variant_ids_oi


def extract_lookup_list_ids(request_args, user_id, conn: Connection):
    lookup_list_names = request_args.get('lookup_list_name', "").split(';')
    lookup_list_ids = request_args.get('lookup_list_id', "").split(';')
    all_list_ids = []
    for list_name, list_id in zip(lookup_list_names, lookup_list_ids):
        list_name = list_name.strip()
        list_id = list_id.strip()
        if list_name == '' and list_id == '':
            continue
        if (list_name != '' and list_id == ''):
            flash("The list " + list_name + " does not exist. Results are not filtered by this list.", 'alert-danger flash_id:unknown_list_search')
        else:
            list_ids = preprocess_query(list_id, r'\d*') # either none if there was an error or a list_id
            if list_id is None:
                flash("You have an error in your list search.", "alert-danger")
            elif len(list_ids) >= 1:
                list_id = list_ids[0]
                list_permissions = conn.check_list_permission(user_id, list_id)
                if list_permissions is not None:
                    if not list_permissions['owner'] and not list_permissions['read']:
                        return abort(403)
                    else:
                        all_list_ids.append(list_id)
                else:
                    flash("The list " + list_name + " which you are trying to access does not exist.", "alert-danger flash_id:unknown_list_search") # this should not happen

    return all_list_ids


def get_static_search_information(user_id, conn: Connection):
    sort_bys = ["genomic position", "recent"]
    page_sizes = ["5", "20", "50", "100"]
    default_page_size = "20"
    default_sort_by = "genomic position"
    default_page = 1
    allowed_user_classes = functions.order_classes(conn.get_enumtypes('user_classification', 'classification'))
    allowed_consensus_classes = functions.order_classes(conn.get_enumtypes('consensus_classification', 'classification'))
    allowed_automatic_classes = functions.order_classes(conn.get_enumtypes('automatic_classification', 'classification_splicing'))
    allowed_variant_types = ['small_variants', 'insertions', 'deletions', 'delins', 'structural_variant']
    annotation_types = conn.get_annotation_types(exclude_groups = ['ID'])
    annotation_types = preprocess_annotation_types_for_search(annotation_types)
    point_score_types = [
        {"id": 0, "display_title": "consensus classification", "table": "consensus_classification"},
        {"id": 1, "display_title": "automatic classification", "table": "automatic_classification"}
    ]
    lists = conn.get_lists_for_user(user_id)
    allowed_clinvar_upload_states = conn.get_unique_publish_clinvar_queue_status()
    allowed_heredicare_upload_states = conn.get_unique_publish_heredicare_queue_status()
    allowed_needs_upload = ["clinvar", "heredicare"]
    if 'skipped' in allowed_heredicare_upload_states:
        allowed_heredicare_upload_states.remove('skipped')
    return {'sort_bys': sort_bys, 'page_sizes': page_sizes, 'allowed_user_classes': allowed_user_classes, 'allowed_consensus_classes': allowed_consensus_classes, 'allowed_automatic_classes': allowed_automatic_classes,
            'annotation_types': annotation_types, 'allowed_variant_types': allowed_variant_types, 'default_page_size': default_page_size, 'default_sort_by': default_sort_by, 'default_page': default_page, 'lists': lists,
            'allowed_clinvar_upload_states': allowed_clinvar_upload_states, "allowed_heredicare_upload_states": allowed_heredicare_upload_states, 'allowed_needs_upload': allowed_needs_upload, 'point_score_types': point_score_types}



def get_merged_variant_page(request_args, user_id, static_information, conn:Connection, flash_messages = True, select_all = False, empty_if_no_variants_oi = False, respect_selected_variants = False):
    static_information = get_static_search_information(user_id, conn)

    variant_strings = extract_variants(request_args)
    variant_types = extract_variant_types(request_args, static_information['allowed_variant_types'])

    genes = extract_genes(request_args)
    ranges = extract_ranges(request_args)
    consensus_classifications, include_heredicare_consensus = extract_consensus_classifications(request_args, static_information['allowed_consensus_classes'])
    user_classifications = extract_user_classifications(request_args, static_information['allowed_user_classes'])
    automatic_classifications_splicing = extract_automatic_classifications(request_args, static_information['allowed_automatic_classes'], which="automatic_splicing")
    automatic_classifications_protein = extract_automatic_classifications(request_args, static_information['allowed_automatic_classes'], which="automatic_protein")
    point_score_restrictions = extract_point_score(request_args, static_information["point_score_types"])
    hgvs = extract_hgvs(request_args)
    #variant_ids_oi = extract_lookup_list(request_args, user_id, conn)
    external_ids = extract_external_ids(request_args)
    cdna_ranges = extract_cdna_ranges(request_args)
    annotation_restrictions = extract_annotations(request_args, conn)
    clinvar_upload_states = extract_clinvar_upload_states(request_args, static_information['allowed_clinvar_upload_states'])
    heredicare_upload_states = extract_heredicare_upload_states(request_args, static_information['allowed_heredicare_upload_states'])

    #variant_ids_oi = extract_lookup_list(request_args, user_id, conn)
    variant_ids_oi = extract_variant_ids(request_args)
    lookup_list_ids = extract_lookup_list_ids(request_args, user_id, conn)
    view_list_id = request_args.get('view', "")
    if view_list_id != "" and view_list_id not in lookup_list_ids:
        lookup_list_ids.append(view_list_id)
    #if view_list_id == '':
    #    return abort(404)
    #if view_list_id is not None: # the user wants to see the list
    #    list_permissions = conn.check_list_permission(user_id, view_list_id)
    #    if not list_permissions['read'] and flash_messages:
    #        return abort(403)
    #variant_ids_from_list = conn.get_variant_ids_from_list(view_list_id)
    #if variant_ids_from_list is not None and len(variant_ids_from_list) > 0 and (variant_ids_oi is None or len(variant_ids_oi) == 0):
    #    variant_ids_oi = variant_ids_from_list
    #elif variant_ids_from_list is not None and len(variant_ids_from_list) > 0 and variant_ids_oi is not None and len(variant_ids_oi) > 0:
    #    variant_ids_oi = list(set(functions.none_to_empty_list(variant_ids_from_list)) & set(functions.none_to_empty_list(variant_ids_oi))) # take the intersection of the two lists
    #if empty_if_no_variants_oi and len(variant_ids_oi) == 0:
    #if view_list_id is not None and view_list_id not in lookup_list_ids:
    #    return [], 0, static_information['default_page'], static_information['default_page_size']

    selected_page_size = request_args.get('page_size', static_information['default_page_size'])
    selected_sort_by = request_args.get('sort_by', static_information['default_sort_by'])
    include_hidden = request_args.get('include_hidden', 'off') == 'on'

    if selected_sort_by not in static_information['sort_bys']:
        if flash_messages:
            flash("The variant table can not be sorted by " + str(selected_sort_by) + ". Defaulting to genomic position sort.", "alert-danger")
        selected_sort_by = static_information['default_sort_by']

    if select_all:
        page = 1
        selected_page_size = "unlimited"
    else:
        if selected_page_size not in static_information['page_sizes']:
            if flash_messages:
                flash("This page size is not supported. Defaulting to " + str(static_information['default_page_size']) + ".", "alert-danger")
            selected_page_size = static_information['default_page_size']
        selected_page_size = int(selected_page_size)
        page = int(request_args.get('page', 1))

    selected_variants = extract_selected_variants(request_args)
    select_all_variants = request_args.get('select_all_variants', "false") == "true"

    needs_upload = extract_needs_upload(request_args, static_information['allowed_needs_upload'])
    
    variants, total = conn.get_variants_page_merged(
        page=page, 
        page_size=selected_page_size, 
        sort_by=selected_sort_by, 
        include_hidden=include_hidden, 
        user_id=user_id, 
        ranges=ranges, 
        genes = genes, 
        consensus=consensus_classifications, 
        user=user_classifications, 
        automatic_splicing=automatic_classifications_splicing,
        automatic_protein=automatic_classifications_protein,
        point_score=point_score_restrictions,
        hgvs=hgvs, 
        variant_ids_oi=variant_ids_oi,
        include_heredicare_consensus = include_heredicare_consensus,
        external_ids = external_ids,
        cdna_ranges = cdna_ranges,
        annotation_restrictions = annotation_restrictions,
        variant_strings = variant_strings,
        variant_types = variant_types,
        clinvar_upload_states = clinvar_upload_states,
        heredicare_upload_states = heredicare_upload_states,
        lookup_list_ids = lookup_list_ids,
        respect_selected_variants = respect_selected_variants,
        selected_variants = selected_variants,
        select_all_variants = select_all_variants,
        needs_upload = needs_upload
    )

    return variants, total, page, selected_page_size
