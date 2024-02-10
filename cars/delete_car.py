import pyautogui as pg
import time

time.sleep(2)
print(pg.position())
for i in range(13):
    pg.click(44, 423)
    time.sleep(0.5)
    pg.click(262, 255)
    time.sleep(1)
    pg.click(1033, 877)
    time.sleep(1)
    pg.click(1046, 589)
    time.sleep(1)
    pg.click(133, 166)
    time.sleep(2)

