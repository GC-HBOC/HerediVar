
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.graphics.shapes import Line, Drawing
import textwrap
import math
import os
from reportlab.lib import colors

class pdf_gen:

    class Point(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    def __init__(self, buffer):
        self.doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
        self.font = "Times-Roman"
        self.story = []
        self.width = self.doc.width
        self.height = self.doc.height
        self.col1width = 6 * cm
        self.col2width = self.width - self.col1width
        self.subtitle_style = ParagraphStyle("subtitle", fontName=self.font, fontSize=15, spaceAfter=5, spaceBefore=15)
        self.title_style = ParagraphStyle("title", fontName=self.font, fontSize=17, spaceAfter=30)
        self.table_text_style = ParagraphStyle("table_text", fontName=self.font, fontSize=8)
        self.table_style = [('NOSPLIT', (0,1), (1,2)), ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray), ('VALIGN', (0, 0), (-1, -1), 'TOP')]
        self.table_text_head_style = ParagraphStyle("table_head", fontName=self.font, fontSize = 10)


    def add_title(self, title):
        self.story.append(Paragraph(title, self.title_style))
        #self.draw_wrapped_text(title)
        #self.canvas.drawString(self.cursor.x, self.cursor.y, title)
        #self.skip(0, height)
    
    def add_subtitle(self, subtitle):
        self.story.append(Paragraph(subtitle, self.subtitle_style))
        self.add_spacer()

    def add_variant_info(self, variant, classification, date, comment, rsid):
        tablevalues = [("variant", Paragraph(variant)), ("class", Paragraph(classification)), ("date", Paragraph(date)), ("comment", Paragraph(comment))]
        if rsid is not None:
            rsid = 'rs' + str(rsid)
            tablevalues.append(("rsid", Paragraph(rsid)))
        tab = Table(tablevalues, style=[('VALIGN', (0, 0), (-1, -1), 'TOP')], hAlign='LEFT', colWidths=[3*cm, self.width-3*cm])
        self.story.append(tab)
    
    def add_spacer(self):
        d = Drawing(self.width, 1)
        d.add(Line(0, 0, self.width, 0))
        self.story.append(d)
        self.story.append(Spacer(self.width, 0.3*cm))
    
    def add_relevant_information(self, title, value):
        tab = Table([(title, Paragraph(value))], colWidths=[self.col1width, self.col2width], hAlign='LEFT')
        self.story.append(tab)
    
    def add_relevant_literature(self, literature_oi):
        pmids = ', '.join(literature_oi)
        self.story.append(Paragraph(pmids))
    
    def add_relevant_classifications(self, classifications, headers, colwidths): # colwidths in number of chars it is more like a maximal colwidth
        #classifications = [[self.prepare_text(str(y), colwidth)[0] for y, colwidth in zip(x, colwidths)] for x in classifications]
        classifications = [[Paragraph(str(y), self.table_text_style) for y in x] for x in classifications]
        colwidths = [x*cm for x in colwidths]

        classifications.insert(0,[Paragraph(str(x), self.table_text_head_style) for x in headers])
        tab = Table(classifications, hAlign='LEFT', style=self.table_style, repeatRows=1, colWidths=colwidths)
        self.story.append(tab)

    
    def add_text(self, text):
        self.story.append(Paragraph(text, ParagraphStyle("basic", spaceBefore=0.2*cm, spaceAfter=0.2*cm)))
    
    
    def prepare_text(self, text, n=75):
        chunks = textwrap.wrap(text, n)
        #chunks = [text[i:i+n] for i in range(0, len(text), n)]
        #chunks.reverse()
        nlines = len(chunks)
        result = '\n'.join(chunks)
        return result, nlines


    def generate_default_report(self, reason):
        self.story.append(Paragraph("This variant classification does not have a report. Reason: " + reason + "."))
        self.save_pdf()
        

    def save_pdf(self):
        self.doc.build(self.story)