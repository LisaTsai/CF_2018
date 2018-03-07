
import cv2
import time
start_time = time.time()
w1_min,w1_max,h1_min = 3,640,80
min_areaD,max_areaD = 4000,10000
#node2 sink
crop_x,crop_y,crop_w,crop_h = 142,238,340,70

background = cv2.imread('/home/pi/Desktop/bggray.jpg')
img1=cv2.imread('/home/pi/Desktop/132628.jpg')
img2=cv2.imread('/home/pi/Desktop/132638.jpg')
img3=cv2.imread('/home/pi/Desktop/132649.jpg')
img4=cv2.imread('/home/pi/Desktop/132659.jpg')
img5=cv2.imread('/home/pi/Desktop/132710.jpg')
img6=cv2.imread('/home/pi/Desktop/132720.jpg')
bg_sink = background[crop_y:crop_y+crop_h,crop_x:crop_x+crop_w]
gray1= cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
gray3 = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
gray4 = cv2.cvtColor(img4, cv2.COLOR_BGR2GRAY)
gray5 = cv2.cvtColor(img5, cv2.COLOR_BGR2GRAY)
gray6 = cv2.cvtColor(img6, cv2.COLOR_BGR2GRAY)
bggray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
cv2.imwrite('/home/pi/Desktop/0306/bggray.jpg',bggray)
cv2.imwrite('/home/pi/Desktop/0306/gray.jpg',gray1)
median1 = cv2.medianBlur(gray1,7)
median2 = cv2.medianBlur(gray2,7)
median3 = cv2.medianBlur(gray3,7)
median4 = cv2.medianBlur(gray4,7)
median5 = cv2.medianBlur(gray5,7)
median6 = cv2.medianBlur(gray6,7)
bgmedian = cv2.medianBlur(bggray,7)
cv2.imwrite('/home/pi/Desktop/0306/median.jpg',median1)
cv2.imwrite('/home/pi/Desktop/0306/bgmedian.jpg',bgmedian)
delta1 = cv2.absdiff(bgmedian,median1)
delta2 = cv2.absdiff(bgmedian,median2)
delta3 = cv2.absdiff(bgmedian,median3)
delta4 = cv2.absdiff(bgmedian,median4)
delta5 = cv2.absdiff(bgmedian,median5)
deltasum =cv2.addWeighted(delta1,0.5,delta2,0.5,0)
deltasum =cv2.addWeighted(delta3,0.33,deltasum,0.67,0)
deltasum =cv2.addWeighted(delta4,0.25,deltasum,0.75,0)
deltasum =cv2.addWeighted(delta5,0.2,deltasum,0.8,0)

deltab1 = cv2.absdiff(median1,median2)
deltab2 = cv2.absdiff(median2,median3)
deltab3 = cv2.absdiff(median3,median4)
deltab4 = cv2.absdiff(median4,median5)
deltab5 = cv2.absdiff(median5,median6)

deltasum1 =cv2.addWeighted(deltab1,0.5,deltab2,0.5,0)
deltasum1 =cv2.addWeighted(deltab3,0.33,deltasum,0.67,0)
deltasum1 =cv2.addWeighted(deltab4,0.25,deltasum,0.75,0)
deltasum1 =cv2.addWeighted(deltab5,0.2,deltasum,0.8,0)


cv2.imwrite('/home/pi/Desktop/0306/delta.jpg',deltasum)
cv2.imwrite('/home/pi/Desktop/0306/deltab.jpg',deltasum1)
deltaw= cv2.addWeighted(deltasum,0.5,deltasum1,0.5,0)
cv2.imwrite('/home/pi/Desktop/0306/deltaw.jpg',deltaw)
for i in range(20):
    thre=cv2.threshold(deltasum,i*5,255, cv2.THRESH_BINARY)[1]
    filename = '/home/pi/Desktop/0306/threshold'+str(i)+'.jpg'
    cv2.imwrite(filename,thre)
    dil = cv2.dilate(thre, None, iterations=4)
    ero = cv2.erode(dil,None,iterations=2)
    filename = '/home/pi/Desktop/0306/erode'+str(i)+'.jpg'
    cv2.imwrite(filename,ero)
    #cv2.imwrite('/home/pi/Desktop/0306/dilation.jpg',dil)

    (cnts, _) = cv2.findContours(ero.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        if h < h1_min or cv2.contourArea(c) < min_areaD or w < w1_min or w > w1_max:
            continue
        #if x < 100 or y < 250 or x+w > 480 or y+h > 350:
            #continue
        cv2.rectangle(img1, (x, y), (x + w, y+ h), (0, 255, 0), 2)
    filename = '/home/pi/Desktop/0306/contour'+str(i)+'.jpg'
    cv2.imwrite(filename,img1)
    print " %s secs" % (time.time()-start_time)
