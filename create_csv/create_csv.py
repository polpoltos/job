import pytesseract
from PIL import ImageGrab, Image
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import io

# Убедитесь, что Tesseract установлен и путь настроен
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\kurba\PycharmProjects\read_symbols\tesseract.exe'


def process_image(image):
    """Извлечение текста из изображения и преобразование в данные"""
    # Распознаём текст
    text = pytesseract.image_to_string(image)
    lines = text.strip().split("\n")
    flat_data = []

    # Преобразуем текст в список чисел
    for line in lines:
        items = line.split()
        for item in items:
            flat_data.append((item))


    # Распределяем данные по двум колонкам
    data = [[flat_data[i], flat_data[i + 1] if i + 1 < len(flat_data) else ''] for i in range(0, len(flat_data), 2)]
    return data


def from_file():
    """Обработка изображения, загруженного из файла"""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if not file_path:
        return
    try:
        image = Image.open(file_path)
        data = process_image(image)
        if data:
            save_csv(data)
        else:
            messagebox.showerror("Ошибка", "Не удалось распознать данные.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при обработке: {e}")


def from_clipboard():
    """Обработка изображения из буфера обмена"""
    try:
        # Извлекаем изображение из буфера обмена
        clipboard_content = ImageGrab.grabclipboard()

        if isinstance(clipboard_content, Image.Image):
            image = clipboard_content
        elif isinstance(clipboard_content, list) and clipboard_content:
            # ShareX может помещать пути файлов
            file_path = clipboard_content[0]
            image = Image.open(file_path)
        elif isinstance(clipboard_content, bytes):
            image = Image.open(io.BytesIO(clipboard_content))
        else:
            raise ValueError("Буфер обмена не содержит изображения или допустимых файлов.")

        data = process_image(image)
        if data:
            save_csv(data)
        else:
            messagebox.showerror("Ошибка", "Не удалось распознать данные.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при обработке: {e}")


def save_csv(data):
    """Сохранение данных в файл CSV"""
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        # Создаём DataFrame с данными
        df = pd.DataFrame(data)
        # Сохраняем данные в CSV с разделителем ";"
        df.to_csv(file_path, index=False, encoding="utf-8", sep=";")
        messagebox.showinfo("Успех", "Данные успешно сохранены в CSV!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")


# Создание интерфейса
root = tk.Tk()
root.title("Image to CSV")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label = tk.Label(frame, text="Выберите способ загрузки изображения:")
label.pack()

button_file = tk.Button(frame, text="Загрузить изображение из файла", command=from_file)
button_file.pack(pady=5)

button_clipboard = tk.Button(frame, text="Загрузить изображение из буфера обмена", command=from_clipboard)
button_clipboard.pack(pady=5)

root.mainloop()
