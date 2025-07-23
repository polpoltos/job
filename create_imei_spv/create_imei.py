import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def generate_qrcodes_with_text_from_excel(excel_file, column_name, output_folder, font_path="arial.ttf", font_size=16):
    # 1. Чтение Excel файла
    df = pd.read_excel(excel_file)

    # Проверка, что нужная колонка есть в Excel
    if column_name not in df.columns:
        raise ValueError(f"Колонка '{column_name}' не найдена в файле Excel")

    # 2. Создание папки для QR-кодов, если она не существует
    os.makedirs(output_folder, exist_ok=True)

    for index, value in df[column_name].items():
        # Превращаем значение в строку
        value_str = str(value)

        # Генерация QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(value_str)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # Загрузка шрифта
        try:
            font = ImageFont.truetype(font_path, font_size)  # Используем указанный шрифт
        except IOError:
            font = ImageFont.load_default()
            print("Шрифт не найден. Используется шрифт по умолчанию.")

        # Определяем размер текста
        draw = ImageDraw.Draw(qr_img)
        text_bbox = draw.textbbox((0, 0), value_str, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Определяем нужную ширину итогового изображения
        qr_width, qr_height = qr_img.size
        img_width = max(qr_width, text_width)
        total_height = qr_height + text_height + 20  # Высота с учетом текста

        # Создаем итоговое изображение с учетом текста
        result_img = Image.new("RGB", (img_width, total_height), "white")
        result_img.paste(qr_img, ((img_width - qr_width) // 2, 0))

        # Рисование текста под QR-кодом
        draw = ImageDraw.Draw(result_img)
        text_position = ((img_width - text_width) // 2, qr_height + 5)
        draw.text(text_position, value_str, fill="black", font=font)

        # Сохранение изображения
        output_path = os.path.join(output_folder, f"qrcode_{value_str}.png")
        result_img.save(output_path)

    print(f"QR-коды успешно сохранены в папку: {output_folder}")

# Пример вызова функции:
generate_qrcodes_with_text_from_excel('imei.xlsx', 'imei', 'qrcodes', font_path="arial.ttf", font_size=25)
