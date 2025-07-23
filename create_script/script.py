import pyautogui as pg  # Используем сокращение 'pg'
from pynput import mouse, keyboard
import time

# Файл для записи действий в формате pyautogui
RECORD_FILE = "recorded_actions_pg.py"

# Глобальные переменные для хранения состояния
pressed_keys = set()
TRIGGER_COMBINATION = {'F2'}  # Триггерная комбинация для keyboard.write
EXIT_COMBINATION = {"space"}  # Комбинация выхода (Right + Left)


# Нормализация имени клавиши
def normalize_key(key):
    try:
        # Обычные буквы, цифры и символы
        key_name = key.char.lower() if key.char else None
        if key_name and key_name.isprintable():  # Проверяем, является ли клавиша печатаемым символом
            return key_name
    except AttributeError:
        # Специальные клавиши (F1, Enter, Space, Tab и т.д.)
        key_name = str(key).replace("Key.", "").lower()

    # Замена специальных кодов на читаемые имена
    if key_name == "ctrl_l":  # Ctrl
        return "ctrl"
    elif key_name == "shift":  # Shift
        return "shift"
    elif key_name == "alt_l":  # Alt
        return "alt"
    elif key_name == "space":  # Пробел
        return "space"
    elif key_name == "enter":  # Enter
        return "enter"
    elif key_name == "backspace":  # Backspace
        return "backspace"
    elif key_name.startswith("f"):  # Функциональные клавиши F1-F12
        return key_name.upper()  # Например, f1 -> F1
    elif key_name == "tab":  # Tab
        return "tab"
    elif key_name == "esc":  # Esc
        return "esc"
    elif key_name in ["up", "down", "left", "right"]:  # Стрелки
        return key_name
    elif key_name == "cmd" or key_name == "super_l":  # Windows/Super клавиша
        return "win"

    # Возвращаем имя клавиши без изменений, если оно уже нормализовано
    return key_name


# Запись событий кликов мыши
def on_mouse_click(x, y, button, pressed):
    if pressed:
        button_name = str(button).replace("Button.", "")
        with open(RECORD_FILE, 'a') as log:
            log.write(f"pg.click(x={x}, y={y}, button='{button_name}')\n")
            log.write(f"time.sleep(0.5)\n")


# Запись событий клавиатуры
def on_key_press(key):
    normalized_key = normalize_key(key)
    if normalized_key:  # Убедимся, что клавиша успешно нормализована
        pressed_keys.add(normalized_key)

    # Проверка триггерной комбинации для keyboard.write
    if TRIGGER_COMBINATION.issubset(pressed_keys):
        text_to_write = input("Введите текст для записи через keyboard.write: ")
        with open(RECORD_FILE, 'a') as log:
            log.write(f"keyboard.write('{text_to_write}')\n")
            log.write(f"time.sleep(0.5)\n")

    # Проверка комбинации выхода (Right + Left)
    if EXIT_COMBINATION.issubset(pressed_keys):
        return False  # Остановка записи

    # Запись обычных нажатий клавиш или комбинаций
    key_combination = "+".join(sorted(pressed_keys))
    with open(RECORD_FILE, 'a') as log:
        if len(pressed_keys) > 1 and not TRIGGER_COMBINATION.issubset(pressed_keys):
            log.write(f"pg.hotkey({', '.join(map(repr, sorted(pressed_keys)))})\n")
        else:
            # Если это пробел, записываем его как строку
            if normalized_key == " ":
                normalized_key = "' '"
            log.write(f"pg.press({repr(normalized_key)})\n")
        log.write(f"time.sleep(0.5)\n")


def on_key_release(key):
    normalized_key = normalize_key(key)
    if normalized_key in pressed_keys:
        pressed_keys.remove(normalized_key)


# Главная функция
def main():
    # Создание файла для записи действий
    with open(RECORD_FILE, 'w') as log:
        log.write("import pyautogui as pg\n")  # Используем сокращение 'pg'
        log.write("import time\n")
        log.write("import keyboard\n\n")  # Добавляем импорт библиотеки keyboard

    print("Запись действий началась.")
    print("Нажмите Right + Left для остановки записи.")

    # Начало прослушивания событий мыши
    with mouse.Listener(on_click=on_mouse_click) as mouse_listener:
        # Начало прослушивания событий клавиатуры
        with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as keyboard_listener:
            mouse_listener.join()
            keyboard_listener.join()


if __name__ == "__main__":
    main()