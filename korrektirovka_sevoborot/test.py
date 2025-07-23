import cv2
import time
import numpy as np
import pyscreenshot as ImageGrab
import pyautogui


def find_patt(thres=0.60):
	screenshot = ImageGrab.grab()
	image = np.array(screenshot.getdata(), dtype='uint8').reshape((screenshot.size[1], screenshot.size[0], 3))
	patt = cv2.imread('butt01.png', 0)
	img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	(patt_H, patt_W) = patt.shape[:2]
	res = cv2.matchTemplate(img_grey, patt, cv2.TM_CCOEFF_NORMED)
	loc = np.where(res>thres)
	points = list(zip(*loc[::-1]))
	if len(points)!=0:
		pyautogui.moveTo(points[0][0]+patt_H/2, points[0][1]+patt_W/2)
		pyautogui.click()
	return (bool(points))




if __name__ == '__main__':
	print(find_patt())