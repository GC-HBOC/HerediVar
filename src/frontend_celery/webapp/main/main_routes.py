from flask import Blueprint, render_template
from ..utils import *
from ..tasks import send_mail
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import download.download_functions as download_functions

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/webapp/main/static'
)



@main_blueprint.route('/demo_disabled')
def demo_disabled():
    return render_template("main/demo_disabled.html")



# the landing page
@main_blueprint.route('/')
def index():
    conn = get_connection()
    total_num_variants = conn.get_number_of_variants()
    annotation_types = conn.get_annotation_types()
    total_num_classified_variants = conn.get_number_of_classified_variants()
    return render_template('index.html', total_num_variants = total_num_variants, annotation_types = annotation_types, total_num_classified_variants = total_num_classified_variants)


# user access of versioned downloads
@main_blueprint.route('/downloads')
def downloads():
    all_variants_folder = download_functions.get_all_variants_folder()
    last_dump_path = os.path.join(all_variants_folder, ".last_dump.txt")
    if not os.path.isfile(last_dump_path):
        last_dump = None
    else:
        with open(last_dump_path, "r") as last_dump_file:
            last_dump = last_dump_file.read().strip()
    
    return render_template("main/downloads.html", last_dump = last_dump)


# user access of versioned downloads
@main_blueprint.route('/download_previous_versions')
@require_permission(['read_resources'])
def download_previous_versions():
    all_variants_folder = download_functions.get_all_variants_folder()
    all_versions = download_functions.get_available_heredivar_versions(all_variants_folder)
    return render_template("main/download_previous_versions.html", all_versions = all_versions)


@main_blueprint.route('/impressum')
def impressum():
    return render_template('main/impressum.html')


@main_blueprint.route('/about')
def about():
    return render_template('main/about.html')


@main_blueprint.route('/documentation')
def documentation():
    return render_template('main/documentation.html')


@main_blueprint.route('/changelog')
def changelog():
    return render_template('main/changelog.html')


@main_blueprint.route('/contact', methods=['GET', 'POST'])
def contact():
    conn = get_connection()

    core_gene_transcripts = {}
    core_gene_ids = conn.get_gene_ids_with_variants()
    for core_gene_id in core_gene_ids:
        core_gene = conn.get_gene(core_gene_id)
        if core_gene is None:
            continue
        core_gene_symbol = core_gene[2]
        current_transcripts = conn.get_transcripts(core_gene_id)
        core_gene_transcripts[core_gene_symbol] = current_transcripts

    do_redirect = False
    #flash("The contact form is currently under maintenance. Enquiries will not be sent", 'alert-danger')

    if request.method == "POST":
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        institution = request.form.get('institution')
        e_mail = request.form.get('e_mail')
        gene = request.form.get('gene')
        transcript = request.form.get('transcript')
        hgvs_c = request.form.get('c_hgvs')
        hgvs_p = request.form.get('p_hgvs')
        question = request.form.get('question')
        comment = request.form.get('comment')
        if any([x is None for x in [first_name, last_name, institution, e_mail, gene, transcript, question]]):
            flash("You must provide your first and last name, institution, e-mail, gene, transcript and your question", "alert-danger")
        elif hgvs_c is None and hgvs_p is None:
            flash("You must provide either hgvs_c or hgvs_p", "alert-danger")
        else:
            hgvs_for_subject = ' / '.join([x for x in [hgvs_c, hgvs_p] if x is not None])
            sender = "noreply@heredivar.uni-koeln.de"
            text_body = render_template("mail_templates/mail_variant_enquiry.html", 
                                        first_name = first_name, 
                                        last_name = last_name,
                                        institution = institution,
                                        e_mail = e_mail,
                                        gene = gene,
                                        transcript = transcript, 
                                        hgvs_c = hgvs_c,
                                        hgvs_p = hgvs_p,
                                        question = question,
                                        comment = comment)
            recipient = "jan.hauke@uk-koeln.de"
            send_mail(subject = "HerediVar: enquiry for variant " + hgvs_for_subject, sender = sender, recipient = recipient, text_body = text_body)
            flash("Thanks for reaching out to us! You will hear from us soon.", "alert-success")
            do_redirect = True
    
    if do_redirect:
        return redirect(url_for('main.contact'))
    return render_template('main/contact.html', core_gene_transcripts = core_gene_transcripts)