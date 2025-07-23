from docx2pdf import convert

def convert_docx_to_pdf(docx_file_path, pdf_file_path):
    # Конвертируем DOCX в PDF
    convert(docx_file_path, pdf_file_path)
nach = 1601
zack = 1700
# Укажите путь к вашему DOCX файлу и путь для сохранения PDF файла
for i in range(nach,zack+1):
    docx_file_path = f"txt/{i}.docx"
    pdf_file_path = f"pdfs/{i}.pdf"
    convert_docx_to_pdf(docx_file_path, pdf_file_path)