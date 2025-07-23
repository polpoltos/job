from docx import Document
import openpyxl


def read_excel(file_path, start):
    # Открываем файл Excel
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    # Проходим по строкам начиная с 500-й и выводим значения из столбцов A, C и D
    counter = nach - 1
    for row in sheet.iter_rows(min_row=start, values_only=True):
        if row[0] == None:
            break
        a_value = row[0]  # Столбец A
        c_value = row[2]  # Столбец C
        d_value = row[3]  # Столбец D
        counter+=1
        # print(f"A: {a_value}, C: {c_value}, D: {d_value}")
        replace_text_in_docx('102.docx', counter, c_value, d_value, a_value)
        if counter > zack-1:
            break
def replace_text_in_docx(file_path, num, login, password, inventory_number):
    # Открываем документ
    doc = Document(file_path)

    # Проходим через каждый параграф документа
    for paragraph in doc.paragraphs:
        if 'Логин:' in paragraph.text:
            inline = paragraph.runs
            for i in range(len(inline)):
                if 'PTZ00102' in inline[i].text:
                    inline[i].text = inline[i].text.replace('PTZ00102', f"{login}")
        if 'Пароль:' in paragraph.text:
            inline = paragraph.runs
            for i in range(len(inline)):
                if '7L4raE7N' in inline[i].text:
                    inline[i].text = inline[i].text.replace('7L4raE7N', f"{password}")
        if '№' in paragraph.text:
            inline = paragraph.runs
            for i in range(len(inline)):
                if '00102' in inline[i].text:
                    inline[i].text = inline[i].text.replace('00102', f"{inventory_number}")

    # Сохраняем изменения в новом файле
    doc.save(f"txt/{num}.docx")


# Пример использования функции
# replace_text_in_docx('102.docx', '102', 'pisya_popa', 'pisya_popa', 'popa')
nach = 1601 #Начать с комплекта
zack = 1700 #Закончить комплектом
read_excel('login_2.xlsx', nach+1)