import fitz  # PyMuPDF
from PIL import Image
import io

nach = 1601
zack = 1700
for i in range(nach, zack+1):
    pdf = fitz.open(f'pdfs/{i}.pdf')

    # Iterate over each page and convert it to TIFF
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        output = f'tiffs/{i}.tiff'
        img.save(output, format='TIFF')

    pdf.close()
