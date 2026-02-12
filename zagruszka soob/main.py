import pyautogui as pg
from time import sleep
import openpyxl
import keyboard

sleep(2)
print(pg.position())


def read_excel(file_path):
    # Открываем файл Excel
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        wia_id = str(row[0])
        print(wia_id)
        sleep(1)
        pg.click(pg.locateCenterOnScreen('img_1.png'))
        sleep(1)
        pg.click(853, 741)
        sleep(0.5)
        keyboard.send('ctrl+a')
        sleep(1)
        keyboard.write(wia_id)
        sleep(0.5)
        pg.click(130, 621)
        sleep(1)
        pg.click(pg.locateCenterOnScreen('img_2.png'))
        sleep(1)
        try:
            pg.click(130, 621)
            sleep(7)
            try:
                pg.click(pg.locateCenterOnScreen("img_3.png"))  # для остальной техники
            except:
                try:
                    pg.click(pg.locateCenterOnScreen("img_4.png"))  # для УСС
                except:
                    pg.click(pg.locateCenterOnScreen("img_8.png"))
            sleep(1)
            keyboard.press('down')
            sleep(0.2)
            keyboard.press('down')
            sleep(0.2)
            keyboard.press('down')
            sleep(0.2)
            keyboard.press('down')
            sleep(0.2)
            keyboard.press('down')
            sleep(0.2)
            pg.click(pg.locateCenterOnScreen("img_5.png"))
            sleep(1)
            pg.click(1514, 624)
            pg.write("11.09.2025 00:00:00", interval=0.01)
            pg.click(1514, 800)
            pg.write("13.09.2025 00:00:00", interval=0.01)
            sleep(1)
            pg.click(pg.locateCenterOnScreen("img_6.png"))
            sleep(10)
            pg.click(pg.locateCenterOnScreen("img_7.png"))
            sleep(2)
        except:
            continue

read_excel('Object_list.xlsx')