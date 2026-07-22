from pypdf import PdfReader

def extract_pdf_text(pdf_path):
    reader=PdfReader(pdf_path)
    pages=[]
    for page in reader.pages:
        page_text=page.extract_text()
        if page_text:
            pages.append(page_text)
    return "\n".join(pages)
