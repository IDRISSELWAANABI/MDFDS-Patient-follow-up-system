import fitz


class PDFToText:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.text = ""

    def extract_text(self) -> str:
        doc = fitz.open(self.pdf_file)

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            self.text += page.get_text()

        doc.close()
        return self.text