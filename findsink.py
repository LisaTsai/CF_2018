import cv2
from time import sleep
crop_x,crop_y,crop_w,crop_h = 142,265,338,70
x,y=0,0

img = cv2.imread("/home/pi/Desktop/132638.jpg")
cv2.rectangle(img, (x+crop_x, y+crop_y), (x+crop_x + crop_w, y+crop_y + crop_h), (255, 0, 0), 2)
cv2.imshow("Test",img)
#sleep(500)
cv2.waitKey(0)
cv2.destroyAllWindows()
