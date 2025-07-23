import time

import pyautogui as pg
import pyscreeze
from time import sleep


sleep(2)
print(pg.position())
for i in range(153, 250):
    pg.click(2408, 196)
    sleep(2)
    pg.click(1307, 298)
    sleep(1)
    pg.hotkey('ctrl', 'a')
    sleep(0.3)
    pg.hotkey('ctrl', 'v')
    sleep(0.3)
    pg.write(f'_00{i}')
    sleep(0.3)
    pg.hotkey('enter')
    sleep(0.3)
    pg.hotkey('down')
    pg.hotkey('enter')
    pg.click(1307, 334)
    sleep(0.3)
    pg.hotkey('down')
    pg.hotkey('enter')
    pg.click(2464, 514)
    pg.click(2467, 102)
    sleep(2)