import pyautogui as pg
from time import sleep

sleep(2)
print(pg.position())
for i in range(102, 152):
    num = 0
    stroka = f'_00{i}'
    pg.click(771, 505)
    sleep(0.5)
    pg.click(880, 623)
    sleep(2)
    pg.hotkey('ctrl', 'a')
    sleep(0.2)
    pg.hotkey('ctrl', 'v')
    pg.typewrite(stroka, 0.2)
    sleep(0.5)
    pg.click(1088, 693)
    sleep(2)
    for _ in range(6):
        num += 1
        pg.click(470, 634)
        sleep(3)
        pg.click(973, 208)
        sleep(0.5)
        pg.click(1172, 272)
        sleep(1)
        pg.click(857, 543)
        for i in range(num):
            sleep(0.2)
            pg.hotkey('down')
        sleep(0.5)
        pg.hotkey('enter')
        pg.click(1230, 667)
        sleep(2)
        pg.click(1227, 470)
        sleep(0.5)
        pg.click(1227, 470)
        sleep(0.5)
        pg.click(1000, 433)
        pg.hotkey('ctrl', 'a')
        sleep(1)
        pg.hotkey('ctrl', 'v')
        pg.typewrite(stroka, 0.05)
        pg.hotkey('enter')
        sleep(1.5)
        pg.click(871, 487)
    pg.click(1248, 409)
    pg.click(1250, 166)

