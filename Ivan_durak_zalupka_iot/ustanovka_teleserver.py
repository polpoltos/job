import pyautogui as pg
import pyscreeze
from time import sleep

sleep(2)
print(pg.position())
for i in range(100):
    pg.click(40,402)
    sleep(10)
    pg.click(828, 725)
    sleep(1)
    pg.hotkey('down')
    sleep(0.5)
    pg.hotkey('enter')
    sleep(1)
    pg.click(1188,791)
    sleep(4)