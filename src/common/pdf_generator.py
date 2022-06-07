from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table

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
        self.linewidth = 1 * cm
        self.width = self.width - self.margin_left - self.margin_right
        self.height = self.height - self.margin_top - self.margin_bottom
        self.font = "Times-Roman"
        self.col1width = 5 * cm
        self.col2width = self.width - self.col1width
        self.cursor = self.Point(0 + self.margin_left, 0 + self.margin_top)


    def add_title(self, title):
        self.canvas.setFont(self.font, 20)
        self.canvas.drawString(self.cursor.x, self.cursor.y, title)
        self.nextLine()

    def add_variant_info(self, classification, date, comment):
        comment = self.prepare_text(comment)
        self.canvas.setFont(self.font, 12)
        tab = Table([("comment", comment), ("date", date), ("class", classification)])
        tab_width, tab_height = tab.wrapOn(self.canvas, 0, 0)
        tab.drawOn(self.canvas, self.cursor.x, self.cursor.y)
        self.skip(0, tab_height)
    
    def add_spacer(self):
        self.canvas.line(self.cursor.x, self.cursor.y, self.cursor.x + self.width, self.cursor.y)
        self.nextLine()
    
    def add_relevant_information(self, title, value):
        value = self.prepare_text(str(value))
        self.canvas.setFont(self.font, 12)
        tab = Table([(title, value)], colWidths=[self.col1width, self.col2width])
        tab_width, tab_height = tab.wrapOn(self.canvas, 0, 0)
        tab.drawOn(self.canvas, self.cursor.x, self.cursor.y)
        self.skip(0, tab_height)

    def nextLine(self, multiplier = 1):
        self.cursor.y = self.cursor.y + self.linewidth * multiplier
    
    def skip(self, x, y):
        self.cursor.x = self.cursor.x + x
        self.cursor.y = self.cursor.y + y

    def prepare_text(self, text):
        n = 75
        chunks = [text[i:i+n] for i in range(0, len(text), n)]
        chunks.reverse()
        result = '\n'.join(chunks)
        return result


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


