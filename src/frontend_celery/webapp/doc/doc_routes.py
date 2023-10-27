from flask import Blueprint, render_template, request
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection
from ..utils import require_permission
from ..utils import *
from ..tasks import send_mail

doc_blueprint = Blueprint(
    'doc',
    __name__
)

# static info pages
@doc_blueprint.route('/help/search')
@require_permission(['read_resources'])
def search_help():
    return render_template('doc/search_help.html')


@doc_blueprint.route('/deleted_variant_info')
@require_permission(['read_resources'])
def deleted_variant():
    return render_template('doc/deleted_variant.html')

@doc_blueprint.route('/impressum')
def impressum():
    return render_template('doc/impressum.html')


@doc_blueprint.route('/about')
def about():
    return render_template('doc/about.html')


@doc_blueprint.route('/documentation')
def documentation():
    return render_template('doc/documentation.html')

@doc_blueprint.route('/changelog')
def changelog():
    return render_template('doc/changelog.html')


@doc_blueprint.route('/contact', methods=['GET', 'POST'])
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

    flash("The contact form is currently under maintenance. Enquiries will not be sent", 'alert-danger')

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
            #return render_template('doc/contact.html', core_gene_transcripts = core_gene_transcripts)
        elif hgvs_c is None and hgvs_p is None:
            flash("You must provide either hgvs_c or hgvs_p", "alert-danger")
            #return render_template('doc/contact.html', core_gene_transcripts = core_gene_transcripts)
        else:
            hgvs_for_subject = ' / '.join([x for x in [hgvs_c, hgvs_p] if x is not None])
            sender = "noreply@heredivar.uni-koeln.de"
            text_body = render_template("doc/mail_variant_enquiry.html", 
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
            #send_mail(subject = "HerediVar: enquiry for variant " + hgvs_for_subject, sender = sender, recipient = "marvin.doebel@med.uni-tuebingen.de", text_body = text_body)
            #flash("Success! Thanks for reaching out to us! You will hear from us soon.", "alert-success")
            do_redirect = True
    
    if do_redirect:
        return redirect(url_for('doc.contact'))
    return render_template('doc/contact.html', core_gene_transcripts = core_gene_transcripts)