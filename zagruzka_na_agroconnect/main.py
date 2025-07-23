import openpyxl

import pyautogui as pg
from time import sleep
import cv2
import numpy as np
import pyscreenshot as ImageGrab
import keyboard

def read_excel(file_path):
    # Открываем файл Excel
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        imei = str(row[0])
        pg.click(2494, 1316)
        sleep(0.5)
        keyboard.write(imei)
        sleep(0.5)
        keyboard.press('tab')
        keyboard.write(imei)
        pg.click(1436, 818)

def find_patt(img, thres=0.60):
    screenshot = ImageGrab.grab()
    image = np.array(screenshot.getdata(), dtype='uint8').reshape((screenshot.size[1], screenshot.size[0], 3))
    patt = cv2.imread(img, 0)
    img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (patt_H, patt_W) = patt.shape[:2]
    res = cv2.matchTemplate(img_grey, patt, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > thres)
    points = list(zip(*loc[::-1]))
    return patt_H, patt_W, points

sleep(2)
print(pg.position())


read_excel('imei.xlsx')