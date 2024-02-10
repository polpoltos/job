import pyautogui as pg
import time

# Получение позиции мыши и вывод в консоль
# print(pg.position())
for i in range(1200):
    time.sleep(3)
    pg.moveTo(147, 500, 0.5)
    pg.click()
    pg.moveTo(1100, 960, 1)
    pg.click()
    pg.moveTo(1110, 614, 1)
    pg.click()