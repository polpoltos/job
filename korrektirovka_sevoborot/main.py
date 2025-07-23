import pyautogui as pg
from time import sleep
import cv2
import numpy as np
import pyscreenshot as ImageGrab
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
# patt_H_1, patt_W_2, points_1 = find_patt('butt01.png')
# if bool(points_1):
#     pg.click(1171, 444)
#     sleep(0.5)
#     pg.click(1211, 550)
#     sleep(0.5)
#     pg.click(1211, 575)
#     sleep(0.5)
#     pg.click(1211, 603)
for i in range(1010):
    patt_H, patt_W, points = find_patt('kar.png')
    if points:
        pg.moveTo(points[0][0] + patt_H / 2, points[0][1] + patt_W / 2)
        pg.click()
        sleep(0.5)
        pg.click(1073, 573)
        sleep(0.5)
        pg.hotkey('ctrl', 'a')
        sleep(0.5)
        pg.typewrite("30.10.2024")
        sleep(1)
        pg.click(1211, 811)
        sleep(8)
        patt_H_1, patt_W_2, points_1 = find_patt('butt01.png')
        if bool(points_1):
            pg.click(1211, 500)
            sleep(0.5)
            pg.click(1211, 545)
            sleep(0.5)
            pg.click(1211, 587)
            sleep(0.5)
            pg.click(1211, 645)
            sleep(0.5)
            pg.click(1211, 695)
            sleep(0.5)
            pg.click(1175, 500)
            sleep(0.5)
            pg.click(1175, 545)
            sleep(0.5)
            pg.click(1175, 588)
            sleep(0.5)
            pg.click(1175, 645)
            sleep(0.5)
            pg.click(1175, 695)
            sleep(2)
            pg.click(1732, 212)
        sleep(3)
        points_1 = []