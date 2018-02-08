
import cv2

w1_min,w1_max,h1_min = 3,640,10
min_areaD,max_areaD = 800,10000
#node2 sink
crop_x,crop_y,crop_w,crop_h = 100,250,380,100

background = cv2.imread('/home/pi/Desktop/NODE22_2018_02_04 00_24_57.jpg')
img =cv2.imread('/home/pi/Desktop/NODE21_2018_02_04 10_46_04.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
bggray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
cv2.imwrite('/home/pi/Desktop/bggray.jpg',bggray)
cv2.imwrite('/home/pi/Desktop/gray.jpg',gray)
median = cv2.medianBlur(gray,7)
bgmedian = cv2.medianBlur(bggray,7)
cv2.imwrite('/home/pi/Desktop/median.jpg',median)
cv2.imwrite('/home/pi/Desktop/bgmedian.jpg',bgmedian)
delta = cv2.absdiff(bgmedian,median)
cv2.imwrite('/home/pi/Desktop/delta.jpg',delta)
thre=cv2.threshold(delta,25,255, cv2.THRESH_BINARY)[1]
cv2.imwrite('/home/pi/Desktop/threshold.jpg',thre)
ero = cv2.erode(thre,None,iterations=4)
dil = cv2.dilate(ero, None, iterations=4)
cv2.imwrite('/home/pi/Desktop/erode.jpg',ero)
cv2.imwrite('/home/pi/Desktop/dilation.jpg',dil)
(cnts, _) = cv2.findContours(dil.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    if h < h1_min or cv2.contourArea(c) < min_areaD or  cv2.contourArea(c) > max_areaD or w < w1_min or w > w1_max:
        continue
    if x < 100 or y < 250 or x+w > 480 or y+h > 350:
        continue
    cv2.rectangle(img, (x, y), (x + w, y+ h), (0, 255, 0), 2)
cv2.imwrite('/home/pi/Desktop/contour.jpg',img)
