import pandas as pd
import os


def convert_xlsx_to_csv(xlsx_file, csv_file):
    try:
        # Чтение данных из XLSX файла
        data = pd.read_excel(xlsx_file)

        # Запись данных в CSV файл с указанием разделителя
        data.to_csv(csv_file, index=False, sep=';')
        print(f'Файл {xlsx_file} успешно преобразован в {csv_file}')
    except Exception as e:
        print(f'Ошибка при преобразовании файла {xlsx_file}: {e}')


def convert_all_xlsx_in_folder(folder_path):
    # Получение списка всех файлов в папке
    for filename in os.listdir(folder_path):
        # Проверка, является ли файл XLSX файлом
        if filename.endswith('.xlsx'):
            xlsx_file = os.path.join(folder_path, filename)
            csv_file = os.path.join(folder_path, filename.replace('.xlsx', '.csv'))
            print(f'Преобразование файла: {xlsx_file}')
            convert_xlsx_to_csv(xlsx_file, csv_file)
        else:
            print(f'Файл {filename} не является XLSX файлом и будет пропущен.')

folder_path = 'C:/Users/kurba/OneDrive/Desktop/Тарировка'
convert_all_xlsx_in_folder(folder_path)
