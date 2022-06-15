


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, Paragraph
from reportlab.lib.styles import ParagraphStyle
import textwrap
import math
import os

class pdf_gen:

    class Point(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    def __init__(self, buffer):
        self.canvas = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
        self.width, self.height = A4
        self.margin_left = 2 * cm
        self.margin_right = 2 * cm
        self.margin_top = 2 * cm
        self.margin_bottom = 2 * cm
        self.linewidth = 0.5 * cm
        self.width = self.width - self.margin_left - self.margin_right
        self.height = self.height - self.margin_top - self.margin_bottom
        self.font = "Times-Roman"
        self.col1width = 5 * cm
        self.col2width = self.width - self.col1width
        self.cursor = self.Point(0 + self.margin_left, 0 + self.margin_top)


    def add_title(self, title):
        title, nlines = self.prepare_text(title, 55)
        self.canvas.setFont(self.font, 20)
        self.draw_wrapped_text(title)
        #self.canvas.drawString(self.cursor.x, self.cursor.y, title)
        #self.skip(0, height)
    
    def add_subtitle(self, subtitle):
        self.nextLine()
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.cursor.x, self.cursor.y, subtitle)
        self.nextLine(0.3)
        self.add_spacer()

    def add_variant_info(self, variant, classification, date, comment):
        comment, nlines = self.prepare_text(comment)
        variant, nlines = self.prepare_text(variant, 64)
        self.canvas.setFont(self.font, 12)
        tab = Table([("comment", comment), ("date", date), ("class", classification), ("variant", variant)])
        self.draw_table(tab)
    
    def add_spacer(self):
        self.canvas.line(self.cursor.x, self.cursor.y, self.cursor.x + self.width, self.cursor.y)
        self.nextLine()
    
    def add_relevant_information(self, title, value):
        value, nlines = self.prepare_text(str(value))
        self.canvas.setFont(self.font, 12)
        tab = Table([(title, value)], colWidths=[self.col1width, self.col2width])
        self.draw_table(tab)
    
    def add_relevant_literature(self, literature_oi):
        self.canvas.setFont(self.font, 12)
        pmids = ', '.join(literature_oi)
        pmids, nlines = self.prepare_text(pmids)
        #self.canvas.drawString(self.cursor.x, self.cursor.y, pmids)
        #self.nextLine(multiplier = nlines)
        tab = Table([(pmids,)])
        self.draw_table(tab)
    
    def add_relevant_classifications(self, classifications, headers, colwidths): # colwidths in number of chars it is more like a maximal colwidth
        classifications = [[self.prepare_text(str(y), colwidth)[0] for y, colwidth in zip(x, colwidths)] for x in classifications]
        classifications.append(list(headers))
        self.canvas.setFont(self.font, 12)
        tab = Table(classifications)
        self.draw_table(tab)

    
    def draw_table(self, tab):
        tab_width, tab_height = tab.wrapOn(self.canvas, 0, 0)
        tab.drawOn(self.canvas, self.cursor.x, self.cursor.y)
        self.skip(0, tab_height)
    
    def draw_wrapped_text(self, text):
        textobject = self.canvas.beginText(self.cursor.x, self.cursor.y)
        text = text.splitlines(False)
        text.reverse()
        for line in text:
            textobject.textLine(line.rstrip())
            self.nextLine(1.5)
        self.canvas.drawText(textobject)


    def nextLine(self, multiplier = 1):
        self.cursor.y = self.cursor.y + self.linewidth * multiplier
    
    def skip(self, x, y):
        self.cursor.x = self.cursor.x + x
        self.cursor.y = self.cursor.y + y

    def prepare_text(self, text, n=75):
        chunks = textwrap.wrap(text, n)
        #chunks = [text[i:i+n] for i in range(0, len(text), n)]
        chunks.reverse()
        nlines = len(chunks)
        result = '\n'.join(chunks)
        return result, nlines


    def generate_default_report(self, reason):
        #self.canvas.drawString(100, 750, "This variant classification does not have a report. <br />")
        #self.canvas.drawString(100, 750, "Reason: " + reason + ".")

        textobject = self.canvas.beginText(0, 650)
        lines = ["This variant classification does not have a report.", "Reason: " + reason + "."]
        for line in lines:
            textobject.textLine(line)
        self.canvas.drawText(textobject)

        self.save_pdf()


    def save_pdf(self):
        self.canvas.showPage()
        self.canvas.save()