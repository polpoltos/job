import pyautogui as pg
from time import sleep
import numpy as np
import openpyxl
import keyboard

def read_excel(file_path):

    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        wia_id = str(row[0])
        print(wia_id)
        sleep(2)
        pg.click(pg.locateCenterOnScreen('img.png'))
        sleep(1)
        pg.click(771, 398)
        sleep(0.5)
        keyboard.send('ctrl+a')
        sleep(1)
        keyboard.write(wia_id)
        sleep(0.5)
        pg.click(771, 398)
        sleep(1)
        pg.click(pg.locateCenterOnScreen('img_1.png'))
        sleep(3)
        pg.click(357, 344)
        sleep(2)
        pg.click(1762, 358)
        sleep(0.5)
        keyboard.send('ctrl+a')
        sleep(1)
        keyboard.write('31.07.2025 00:00:00')
        sleep(0.5)
        try:
            pg.click(pg.locateCenterOnScreen('img_2.png'))
        except:
            pg.click(902, 194)
        sleep(1)
        pg.click(233, 284)
        sleep(0.5)
        keyboard.send('g')
        sleep(0.5)
        keyboard.send('enter')
        sleep(0.5)
        pg.click(233, 437)
        sleep(0.5)
        keyboard.send('ctrl+a')
        sleep(1)
        keyboard.write('((x < 18) && (x > 13.2)) || (x > 26.8)')
        sleep(0.5)
        pg.click(233, 567)
        sleep(0.5)
        keyboard.send('down')
        sleep(0.5)
        keyboard.send('enter')
        sleep(1)
        pg.click(233, 713)
        sleep(0.5)
        keyboard.send('ctrl+a')
        sleep(1)
        keyboard.write('0')
        sleep(0.5)
        pg.click(233, 855)
        sleep(0.5)
        keyboard.send('ctrl+a')
        sleep(1)
        keyboard.write('2')
        sleep(1)
        pg.click(pg.locateCenterOnScreen('img_3.png'))
        sleep(2)



sleep(2)
print(pg.position())
read_excel('Object_list.xlsx')
