import io
from os import path
import sys
from flask import Blueprint, abort, current_app, send_from_directory, send_file, request, flash, redirect, url_for, session, jsonify, make_response

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
import common.paths as paths
from ..utils import *
from . import download_functions


download_blueprint = Blueprint(
    'download',
    __name__
)

################################
######### DOWNLOAD VCF ######### 
################################

# listens on get parameter: variant_id
@download_blueprint.route('/download/vcf/one_variant')
@require_permission(['read_resources'])
def variant():
    conn = get_connection()

    variant_id = request.args.get('variant_id')
    require_valid(variant_id, "variant", conn)

    force_url = url_for("download.variant", variant_id = variant_id, force=True)
    redirect_url = url_for('variant.display', variant_id = variant_id)
    download_file_name = "variant_" + str(variant_id) + ".vcf"

    vcf_file_buffer, status, vcf_errors, err_msg = download_functions.get_vcf([variant_id], conn, check_vcf=not request.args.get('force', False))

    if status in ['redirect', 'error']:
        flash({"message": "Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + ". Download it anyway",
               "link": force_url}, "alert-danger")
        current_app.logger.error(get_preferred_username() + " tried to download a vcf which contains errors: " + vcf_errors + ". For variant ids: " + str(variant_id))
        return redirect(redirect_url)

    current_app.logger.info(get_preferred_username() + " downloaded vcf of variant id: " + str(variant_id))

    return send_file(vcf_file_buffer, as_attachment=True, download_name=download_file_name, mimetype="text/vcf")


# listens on get parameter: list_id
@download_blueprint.route('/download/vcf/variant_list')
@require_permission(['read_resources'])
def variant_list():
    conn = get_connection()

    list_id = request.args.get('list_id')
    require_valid(list_id, "user_variant_lists", conn)

    # check that the logged in user is the owner of this list
    require_list_permission(list_id, ['read'], conn)
    variant_ids_oi = conn.get_variant_ids_from_list(list_id)

    force_url = url_for("download.variant_list", list_id = list_id, force = True)
    redirect_url = url_for("user.my_lists", view = list_id)
    download_file_name = "list_" + str(list_id) + ".vcf"

    vcf_file_buffer, status, vcf_errors, err_msg = download_functions.get_vcf(variant_ids_oi, conn)

    if status == "redirect":
        flash({"message": "Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + ". Download it anyway",
               "link": force_url}, "alert-danger")
        current_app.logger.error(get_preferred_username() + " tried to download a vcf which contains errors: " + vcf_errors + ". For variant list " + str(list_id))
        return redirect(redirect_url)

    current_app.logger.info(get_preferred_username() + " downloaded vcf of variant list: " + str(list_id))
    
    return send_file(vcf_file_buffer, as_attachment=True, download_name=download_file_name, mimetype="text/vcf")


from flask import Response, stream_with_context
@download_blueprint.route('/download/test')
@require_permission(["admin_resources"])
def download_test():
    return Response(
        stream_with_context(download_functions.test_large_download()),
        headers={'Content-Disposition': 'attachment; filename=test.txt'}
    )

@download_blueprint.route('/download/test_vcf')
@require_permission(["admin_resources"])
def download_test_vcf():
    conn = get_connection()

    list_id = request.args.get('list_id')
    require_valid(list_id, "user_variant_lists", conn)

    # check that the logged in user is the owner of this list
    require_list_permission(list_id, ['read'], conn)
    variant_ids_oi = conn.get_variant_ids_from_list(list_id)

    return Response(
        stream_with_context(download_functions.get_vcf_stream(variant_ids_oi, conn)),
        headers={'Content-Disposition': 'attachment; filename=test.txt'}
    )


# listens on get parameter: raw
@download_blueprint.route('/download/vcf/classified')
@require_permission(['read_resources'])
def classified_variants():
    return_raw = request.args.get('raw')
    
    classified_variants_folder = download_functions.get_classified_variants_folder() #current_app.static_folder + "/files/classified_variants"
    last_dump_path = classified_variants_folder + "/.last_dump.txt"
    force_url = url_for("download.classified_variants", raw=return_raw, force = True)
    redirect_url = url_for("main.downloads")

    if not os.path.isfile(last_dump_path): # generate a new file if it is missing...
        conn = get_connection()
        variant_types = conn.get_enumtypes("variant", "variant_type")
        download_functions.generate_consensus_only_vcf(variant_types, dummy = True)
    
    with open(last_dump_path, 'r') as last_dump_file:
        last_dump_date = last_dump_file.read()
    path_to_download = classified_variants_folder + "/" + last_dump_date + ".vcf"
    returncode, err_msg, vcf_errors = functions.check_vcf(path_to_download)

    if returncode != 0:
        if request.args.get('force') is None:
            flash({"message": "Error during VCF Check: " + vcf_errors + " with error message: " + err_msg + ". Download it anyway",
                   "link": force_url}, "alert-danger")
            current_app.logger.error(get_preferred_username() + " tried to download all classified variants as vcf, but it contains errors: " + vcf_errors)
            return redirect(redirect_url)

    if return_raw is not None:
        with open(path_to_download, "r") as file_to_download:
            download_text = file_to_download.read()
            resp = make_response(download_text, 200)
            resp.mimetype = "text/plain"
            return resp
    else:
        return send_file(path_to_download, download_name="HerediVar-classified" + "-" + last_dump_date + ".vcf", as_attachment=True, mimetype="text/vcf")


@download_blueprint.route('/download/vcf/heredivar/current')
@require_permission(['read_resources'])
def heredivar_current():
    all_variants_folder = download_functions.get_all_variants_folder()
    last_dump_path = path.join(all_variants_folder, ".last_dump.txt")

    if not path.exists(last_dump_path):
        return abort(404)
    
    with open(last_dump_path, "r") as last_dump_file:
        last_dump = last_dump_file.read().strip()

    path_to_download = path.join(all_variants_folder, last_dump+".vcf.gz")

    if not path.exists(path_to_download):
        return abort(404)
    
    return send_file(path_to_download, download_name="HerediVar-"+last_dump+".vcf.gz", as_attachment=True, mimetype="application/gzip")


@download_blueprint.route('/download/vcf/heredivar/<string:version>')
@require_permission(['read_resources'])
def heredivar_version(version): # version is a date
    all_variants_folder = download_functions.get_all_variants_folder()

    available_versions = download_functions.get_available_heredivar_versions(all_variants_folder)
    if version not in available_versions:
        return abort(404)

    path_to_download = path.join(all_variants_folder, version+".vcf.gz")

    if not path.exists(path_to_download):
        return abort(404)
    
    return send_file(path_to_download, download_name="HerediVar-"+version+".vcf.gz", as_attachment=True, mimetype="application/gzip")


##################################
######### DOWNLOAD CLASS #########
##################################

# GET VARIANT CLASS BY SCHEME
@download_blueprint.route('/calculate_class/<string:scheme_type>/<string:version>/<string:selected_classes>')
@download_blueprint.route('/calculate_class/<string:scheme_type>/<string:version>/')
@download_blueprint.route('/calculate_class/<string:scheme_type>/<string:version>')
@download_blueprint.route('/calculate_class')
def calculate_class(scheme_type = None, version = None, selected_classes = ''):

    if scheme_type is None:
        scheme_type = request.args.get("scheme_type")
    if version is None:
        version = request.args.get("version")
    if selected_classes == '':
        selected_classes = request.args.get('selected_classes', '')

    if scheme_type is None or version is None:
        raise ValueError("The scheme type or version is missing.")

    scheme_type = scheme_type.lower()

    if scheme_type == "none":
        return jsonify({'final_class': '-'})

    selected_classes = selected_classes.split('+')

    #print(scheme_type)
    #print(version)
    #print(selected_classes)

    final_class = None
    if scheme_type == 'acmg':
        class_counts = download_functions.get_class_counts(selected_classes) # count how often we have each strength
        possible_classes = download_functions.get_possible_classes_acmg(class_counts) # get a set of possible classes depending on selected criteria following PMC4544753
        final_class = download_functions.decide_for_class_acmg(possible_classes) # decide for class follwing the original publicatoin of ACMG (PMC4544753)
    
    elif scheme_type == 'task-force':
        final_class = download_functions.decide_for_class_task_force(selected_classes)

    elif scheme_type == 'acmg-svi':
        class_counts = download_functions.get_class_counts(selected_classes)
        possible_classes = download_functions.get_possible_classes_acmg_svi(class_counts)
        final_class = download_functions.decide_for_class_acmg(possible_classes)

    elif 'acmg' in scheme_type:
        class_counts = download_functions.get_class_counts(selected_classes) # count how often we have each strength

        # get a set of possible classes depending on selected criteria depending on the gene and version
        if 'brca1' in scheme_type and version == "v1.0.0":
            possible_classes = download_functions.get_possible_classes_enigma_brca1_1_0_0(class_counts) 
        elif 'brca1' in scheme_type and version == "v1.1.0":
            possible_classes = download_functions.get_possible_classes_enigma_brca12_1_1_0(class_counts) 
        elif 'brca2' in scheme_type and version == "v1.0.0":
            possible_classes = download_functions.get_possible_classes_enigma_brca2_1_0_0(class_counts) 
        elif 'brca2' in scheme_type and version == "v1.1.0":
            possible_classes = download_functions.get_possible_classes_enigma_brca12_1_1_0(class_counts) 
        elif 'palb2' in scheme_type and (version == "v1.0.0" or version == "v1.1.0"):
            possible_classes = download_functions.get_possible_classes_enigma_palb2(class_counts) 
        elif 'tp53' in scheme_type and version == "v1.4.0":
            possible_classes = download_functions.get_possible_classes_enigma_tp53(class_counts) 
        elif 'atm' in scheme_type and version == "v1.1.0":
            possible_classes = download_functions.get_possible_classes_enigma_atm_1_1_0(class_counts) 
        elif 'atm' in scheme_type and version == "v1.3.0":
            possible_classes = download_functions.get_possible_classes_enigma_atm_1_3_0(class_counts) 
        elif 'pten' in scheme_type and version == "v3.0.0":
            possible_classes = download_functions.get_possible_classes_enigma_pten(class_counts) 
        elif 'pten' in scheme_type and version == "v3.1.0":
            possible_classes = download_functions.get_possible_classes_enigma_pten_310(class_counts) 
        elif any([gene_symbol in scheme_type for gene_symbol in ['pms2', 'mlh1', 'msh2', 'msh6']]) and version == "v1.0.0": # MMR genes
            possible_classes = download_functions.get_possible_classes_enigma_insight_mmr_100(class_counts) 
        else:
            raise RuntimeError('The class could not be calculated with given parameters. Did you specify a supported scheme and version? (either "acmg" or VUS "task-force" based)')

        final_class = download_functions.decide_for_class_acmg(possible_classes) # decide for class

    if final_class is None:
        raise RuntimeError('The class could not be calculated with given parameters. Did you specify a supported scheme and version? (either "acmg" or VUS "task-force" based)')

    result = {'final_class': final_class}
    return jsonify(result)



###############################
######## FILES FOR IGV ########
###############################

@download_blueprint.route('/download/refgene_ngsd.gff3.gz')
def refgene_ngsd():
    filename = "refgene_ngsd.gff3.gz"
    return send_from_directory(directory=paths.igv_data_path, path=filename, download_name="refgene_ngsd.gff3.gz", as_attachment=True, mimetype="text")

@download_blueprint.route('/download/refgene_ngsd.gff3.gz.tbi')
def refgene_ngsd_tabix():
    filename = "refgene_ngsd.gff3.gz.tbi"
    return send_from_directory(directory=paths.igv_data_path, path=filename, download_name="refgene_ngsd.gff3.gz.tbi", as_attachment=True, mimetype="text")

@download_blueprint.route('/download/hg38.fa')
def ref_genome():
    filename = "GRCh38.fa"
    return send_from_directory(directory=paths.ref_genome_dir, path=filename, download_name="GRCh38.fa", as_attachment=True, mimetype="text")

@download_blueprint.route('/download/hg38.fa.fai')
def ref_genome_index():
    filename = "GRCh38.fa.fai"
    return send_from_directory(directory=paths.ref_genome_dir, path=filename, download_name="GRCh38.fa.fai", as_attachment=True, mimetype="text")


#####################################
######### EVIDENCE DOWNLOAD #########
#####################################

@download_blueprint.route('/download/evidence_document/<int:consensus_classification_id>')
@require_permission(['read_resources'])
def evidence_document(consensus_classification_id):
    conn = get_connection()
    
    require_valid(consensus_classification_id, "consensus_classification", conn)

    consensus_classification = conn.get_evidence_document(consensus_classification_id)
    binary_report = consensus_classification[0] # file in base 64 format -> use functions.base64_to_file to write to file
    report_filename = 'consensus_classification_report_' + str(consensus_classification_id) + '.html'

    buffer = io.BytesIO()
    buffer.write(binary_report)
    buffer.seek(0)

    current_app.logger.info(get_preferred_username() + " downloaded consensus classification evidence document for consensus classification " + str(consensus_classification_id))
    
    return send_file(buffer, as_attachment=True, download_name=report_filename, mimetype='text/html')

@download_blueprint.route('/download/assay_report/<int:assay_id>')
@require_permission(['read_resources'])
def assay_report(assay_id):
    conn = get_connection()

    require_valid(assay_id, "assay", conn)

    # the assay report is not part of the assay object [defined in models.py] 
    # -> this way we do not have to transmit it every time we access a variant
    b_64_assay, filename = conn.get_assay_report(assay_id) 

    buffer = io.BytesIO()
    buffer.write(b_64_assay) # decode_b64 is not required because bytes are converted automatically by send_file
    buffer.seek(0)

    current_app.logger.info(get_preferred_username() + " downloaded assay " + str(assay_id))
    
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application')


########################################
######### INOFFICIAL DOWNLOADS #########
########################################
# these can be used for debugging

#@download_blueprint.route('/download/annotation_errors')
#@require_permission(['admin_resources'])
#def annotation_errors():
#    conn = get_connection()
#
#    download_file_name = "annotation_errors_" + functions.get_today() + ".tsv"
#
#    annotation_stati, errors, warnings, total_num_variants = conn.get_annotation_statistics(exclude_sv=True)
#
#    helper = io.StringIO()
#    helper.write("#" + "\t".join(["chrom", "pos", "ref", "alt", "error_msg"]) + '\n')
#    for variant_id in errors:
#        variant = conn.get_variant(variant_id)
#        new_line = "\t".join([variant.chrom, str(variant.pos), variant.ref, variant.alt, errors[variant_id]])
#        helper.write(new_line + "\n")
#    
#    buffer = io.BytesIO()
#    buffer.write(helper.getvalue().encode())
#    buffer.seek(0)
#    
#    return send_file(buffer, as_attachment=True, download_name=download_file_name, mimetype="text")


#@download_blueprint.route('/recalculate_automatic_classes')
#def recalculate_automatic_classes():
#    conn = get_connection()
#
#    automatic_classification_ids = conn.get_automatic_classification_ids()
#
#    for automatic_classification_id in automatic_classification_ids:
#        criteria = conn.get_automatic_classification_criteria_applied(automatic_classification_id)
#
#        selected_splicing = []
#        selected_protein = []
#        for criterium in criteria:
#            rule_type = criterium[2]
#            evidence_type = criterium[6]
#            is_selected = criterium[4] == 1
#
#            if is_selected:
#                if rule_type == 'splicing':
#                    selected_splicing.append(evidence_type)
#                elif rule_type == 'protein':
#                    selected_protein.append(evidence_type)
#                else:
#                    selected_splicing.append(evidence_type)
#                    selected_protein.append(evidence_type)
#
#        classification_splicing = calculate_class('acmg-svi', '+'.join(selected_splicing)).json['final_class']
#        classification_protein = calculate_class('acmg-svi', '+'.join(selected_protein)).json['final_class']
#
#        conn.update_automatic_classification(automatic_classification_id, classification_splicing, classification_protein)

