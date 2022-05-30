from reportlab.pdfgen import canvas
import base64
import os

class pdf_gen:
    def __init__(self, file_name):
        root = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(root, 'latest_reports', file_name)
        self.canvas = canvas.Canvas(self.path)
        #c.drawString(100,750,"TESTTEST1234äöüß!")
        #c.save()

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
        self.canvas.save()

    def get_base64_encoding(self, path = ''):
        if path == '':
            path = self.path
        with open(path, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())
            return encoded_string
    
    def base64_to_pdf(self, base64_pdf, path = ''):
        if path == '':
            path = self.path
        
        file_64_decode = base64.b64decode(base64_pdf) 
        file_result = open(path, 'wb') 
        file_result.write(file_64_decode)

