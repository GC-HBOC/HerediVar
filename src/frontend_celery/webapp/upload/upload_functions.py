from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common import functions
from common.heredicare_interface import Heredicare
from common.db_IO import Connection
from ..utils import *


def extract_variant_ids(request_args, conn: Connection):
    variant_ids_strs = request_args.getlist('variant_ids')
    if 'heredicare' in variant_ids_strs:
        check_update_all_progressing_heredicare(conn)
        result = conn.get_variant_ids_which_need_heredicare_upload()
    else:
        result = []
        for variant_ids_str in variant_ids_strs:
            result.extend(variant_ids_str.split(','))
    return result

def extract_clinvar_selected_genes(variant_ids, request_form):
    result = {}
    for variant_id in variant_ids:
        selected_gene_id = request_form.get("clinvar_gene_" + str(variant_id))
        if selected_gene_id is not None:
            result[variant_id] = selected_gene_id
    return result


