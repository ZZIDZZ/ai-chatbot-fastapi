# read pdf and print its content
from pypdf import PdfReader
import io

file = open("testing.pdf", "rb")

contents = file.read()
pdf_reader = PdfReader(io.BytesIO(contents))

for page in pdf_reader.pages:
    print(page.extract_text())
file.close()