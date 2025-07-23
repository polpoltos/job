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
    if len(points) != 0:
        pg.moveTo(points[0][0] + patt_H / 2, points[0][1] + patt_W / 2)
        pg.click()
    # return patt_H, patt_W, points

sleep(2)
print(pg.position())
for i in range(200):
    find_patt('karan.png')
    sleep(1)
    pg.click(1158, 832)
    sleep(0.5)
    pg.hotkey('backspace')
    sleep(0.2)
    pg.hotkey('7')
    sleep(0.5)
    pg.click(1006, 873)
    sleep(0.5)
    pg.hotkey('down')
    sleep(0.2)
    pg.hotkey('enter')
    sleep(0.5)
    pg.click(1223, 938)
    sleep(3)

