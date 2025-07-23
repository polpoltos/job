import pandas as pd
from pdf2docx import Converter
from docx import Document
from docx2pdf import convert

# Read the Excel file
excel_file = 'login.xlsx'
data = pd.read_excel(excel_file)

# Get login, password, and inventory number from the Excel file
inventory_number = data.iloc[0, 0]  # Column A
login = data.iloc[0, 2]  # Column C
password = data.iloc[0, 3]  # Column D

# Paths
template_pdf_path = '102.pdf'
intermediate_docx_path = '102.docx'
output_pdf_path = 'updated_102.pdf'

# Step 1: Convert PDF to DOCX
cv = Converter(template_pdf_path)
cv.convert(intermediate_docx_path, start=0, end=None)
cv.close()

# Step 2: Update the DOCX file
doc = Document(intermediate_docx_path)

# Iterate through paragraphs to find and replace the text
for paragraph in doc.paragraphs:
    if 'Логин:' in paragraph.text:
        paragraph.text = f"Логин: {'login'}"
    if 'Пароль:' in paragraph.text:
        paragraph.text = f"Пароль: {password}"
    if 'Инвентарный номер:' in paragraph.text:
        paragraph.text = f"Инвентарный номер: {inventory_number}"

# Save the updated DOCX file
doc.save(intermediate_docx_path)

# Step 3: Convert DOCX back to PDF
convert(intermediate_docx_path, output_pdf_path)

print(f"Updated PDF saved to {output_pdf_path}")
