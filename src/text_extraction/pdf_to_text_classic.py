import fitz


class PDFToText:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file

    def extract_text(self) -> str:
        doc = fitz.open(self.pdf_file)

        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()

        doc.close()
        return text