import cv2
from time import sleep
crop_x,crop_y,crop_w,crop_h = 70,268,345,67
x,y=0,0

img = cv2.imread("/home/pi/Desktop/NODE11_2018_02_06 14_54_03.jpg")
cv2.rectangle(img, (x+crop_x, y+crop_y), (x+crop_x + crop_w, y+crop_y + crop_h), (255, 0, 0), 2)
cv2.imshow("Test",img)
#sleep(500)
cv2.waitKey(0)
cv2.destroyAllWindows()
