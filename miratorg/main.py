import pyautogui as pg
from time import sleep
import cv2
import numpy as np
import pyscreenshot as ImageGrab
import keyboard

sleep(2)
for _ in range(781):
    pg.click(179, 826)
    sleep(4)
    pg.click(1185, 510)
    sleep(0.5)
    keyboard.write('0')
    sleep(0.5)
    pg.click(1431, 977)
    sleep(0.5)
    keyboard.write('01.05.2025 00:00:00')
    sleep(1)
    pg.click(3701,2021)
    sleep(5)
print(pg.position())