import fitz


class PDFToText:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.text = ""

    def extract_text(self, pdf_file):
        """
        Extracts text from all pages of a PDF file.

        Args:
            pdf_file (str): The path to the PDF file.

        Returns:
            str: The extracted text from all pages.
        """
        doc = fitz.open(pdf_file)

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            self.text += page.get_text()

        doc.close()
        return self.text
    


if __name__ == "__main__":
    pdf_file = "/home/balk/Downloads/MDFDS.pdf"
    pdf_to_text = PDFToText(pdf_file)
    extracted_text = pdf_to_text.extract_text(pdf_file)
    print(extracted_text)