
'''
By Lisa Tsai
Latest update - 2018/02/22

2018/02/13 +accumulated difference / vote once / bg
2018/02/14 increase bg update frequency / add conditions of two area overlapped
2018/02/22 MySQL
'''
################# Libraries ###################

#libraries
from time import sleep
import serial
import socket

#cam libraries
import numpy as np
import requests
import urllib2
from urllib import urlencode
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
import imutils
import cv2
import time

#logfile for img
import csv
import datetime
import MySQLdb

### Options

db_enable = 1

textc,sum,counter = 0,0,0
thre_v,thre_max = 20,255
#NTU_CF node2 sink
crop_x,crop_y,crop_w,crop_h = 100,250,380,100
#NTU_CF node1 sink 
#crop_x,crop_y,crop_w,crop_h = 70,268,345,67

#cow position
cow_pos_x = []
cow_pos_y = []
cow_pos_w = []
cow_pos_h = []

#sink only
w1_min_sink,w1_max_sink,h1_min_sink = 3,200,30
min_areaD_sink,max_areaD_sink = 400,8000

#All range
w1_min,w1_max,h1_min = 3,400,30
min_areaD,max_areaD = 1000,100000
vote_cx,vote_cy,vote_count,drink_length = [],[],[],[]
drink_time = 0
drink_total = 10
FPS = 6 # count_max
vote_constant = 10
i_max=FPS*vote_constant-1
#sencond round of vote
vote_max2,vote_count2,vote_num2 = 10,0,0
vote_thre=7
cow_num,vote_num = 0,0
contour_list = []
area_within_thre = 0
x_within_thre = 0
y_within_thre = 0
inout_flag = 0

#background image
bg = cv2.imread('/home/pi/bg.jpg')

#sink position
#f = open('/home/pi/Adafruit_Python_BME280/sink.txt','r')
f = open('sink.txt','r')
sink = f.read()
sink = sink.strip('/n')
a = sink.split(',')
crop_x,crop_y,crop_w,crop_h =int(a[0]),int(a[1]),int(a[2]),int(a[3])
bg_sink = bg[crop_y:crop_y+crop_h,crop_x:crop_x+crop_w]
cv2.imwrite('/home/pi/bg_sink.jpg',bg_sink)

#db number
#f = open('/home/pi/Adafruit_Python_BME280/DB_NUM.txt','r')
f = open('DB_NUM.txt','r')
db = f.read()
db = db.strip('\n')

#node number
#f = open('/home/pi/Adafruit_Python_BME280/NODE_IN.txt','r')
f = open('NODE_IN.txt','r')
node_in = f.read()
node_in = node_in.strip('\n')
#f = open('/home/pi/Adafruit_Python_BME280/NODE_OUT.txt','r')
f = open('NODE_OUT.txt','r')
node_out = f.read()
node_out = node_out.strip('\n')

#location
location = "NTU_CF"
location_cam = location+"_"+db

#db codes:
db_code = "CF"
port_udp = 30001
ip = "140.112.94.123"

try:
    image_dir = "/home/pi/COW_IMAGES/"
    os.mkdir(image_dir,0755);
except:
    pass
# Open UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

url_in='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node_in+'&location='+location_cam
url_out='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node_out+'&location='+location_cam

# time
d=datetime.datetime.now()
dx=d.strftime("%Y%m%d")
csv_filename = "/home/pi/NTU_CF_data.csv"

# Make back-up csv file
fileexist = os.path.isfile(csv_filename)
text=['DATETIME','NUM','COUNT','TOTAL']

if fileexist:      
    print("BACK-UP CSV ALREADY EXISTS!")
else:
    file = open(csv_filename, 'w')
    with open(csv_filename, 'ab') as csv_file:
        writer = csv.writer(csv_file,delimiter=':')
        writer.writerow(text)
	
	
camera=PiCamera()
camera.resolution=(640,480)
camera.framerate = FPS
camera.rotation = 0
sleep(0.5)


### Function

def sendImage(locationx,inout):
    f = open(locationx,'rb')
    files = {'file':f}
    if inout == 1:
        r = requests.post(url_in,files=files)
    else:
        r = requests.post(url_out,files=files)
    print(r.content)
    try:
        if os.path.isfile(locationx):
            os.remove(locationx)
    except Exception as e:
        print e
    
####

while True:
    start_time=time.time()
    raw=PiRGBArray(camera,size=(640,480))
    stream = camera.capture_continuous(raw,format="bgr",use_video_port=True)
    for(i,f) in enumerate(stream):
        frame = f.array
        img=frame.copy()
        frame_sink = frame[crop_y:crop_y+crop_h,crop_x:crop_x+crop_w]
        img_sink = frame_sink.copy()
        # Step 1 : grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_sink = cv2.cvtColor(frame_sink, cv2.COLOR_BGR2GRAY)
        graybg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        graybg_sink = cv2.cvtColor(bg_sink, cv2.COLOR_BGR2GRAY)
        # Step 2 : medianBlur
        median = cv2.medianBlur(gray,7)
        median_sink = cv2.medianBlur(gray_sink,7)
        medianbg = cv2.medianBlur(graybg,7)
        medianbg_sink = cv2.medianBlur(graybg_sink,7)
        # Step 3 : find lastframe
        if i%6 == 0:
            lastframe = median
            lastframe_sink=median_sink
            #print "lastframe dealed"
            raw.truncate(0)
            continue
	    # Step 4 : absolute diff between lastframe and current frame
        deltab = cv2.absdiff(medianbg,median)
        delta = cv2.absdiff(lastframe,median)
        deltab_sink = cv2.absdiff(medianbg_sink,median_sink)
        delta_sink = cv2.absdiff(lastframe_sink,median_sink)
        # 5 sets of accumulation between frames
        if i%6 == 1:
            accu_img = delta
            accu_imgb = deltab
            accu_img_sink = delta_sink
            accu_imgb_sink = deltab_sink
        elif i%6 == 2:
            accu_img = cv2.addWeighted(delta,0.5,accu_img,0.5,0)
            accu_imgb = cv2.addWeighted(deltab,0.5,accu_imgb,0.5,0)
            accu_img_sink = cv2.addWeighted(delta_sink,0.5,accu_img_sink,0.5,0)
            accu_imgb_sink = cv2.addWeighted(deltab_sink,0.5,accu_imgb_sink,0.5,0)
        elif i%6 == 3:
            accu_img = cv2.addWeighted(delta,0.33,accu_img,0.67,0)
            accu_imgb = cv2.addWeighted(deltab,0.33,accu_imgb,0.67,0)
            accu_img_sink = cv2.addWeighted(delta_sink,0.33,accu_img_sink,0.67,0)
            accu_imgb_sink = cv2.addWeighted(deltab_sink,0.33,accu_imgb_sink,0.67,0)
        elif i%6 == 4:
            accu_img = cv2.addWeighted(delta,0.25,accu_img,0.75,0)
            accu_imgb = cv2.addWeighted(deltab,0.25,accu_imgb,0.75,0)
            accu_img_sink = cv2.addWeighted(delta_sink,0.25,accu_img_sink,0.75,0)
            accu_imgb_sink = cv2.addWeighted(deltab_sink,0.25,accu_imgb_sink,0.75,0)
        else:
            accu_img_sink = cv2.addWeighted(delta_sink,0.2,accu_img_sink,0.8,0)
            accu_imgb_sink = cv2.addWeighted(deltab_sink,0.2,accu_imgb_sink,0.8,0)
            accu_re_sink = cv2.addWeighted(accu_img_sink,0.8,accu_imgb_sink,0.2,0)
            thre_sink=cv2.threshold(accu_re_sink,thre_v,thre_max, cv2.THRESH_BINARY)[1]
            #print "THRESHOLD DONE"
	    # Step 5 : dilate to fill in holes, then find contours
            dil_sink = cv2.dilate(thre_sink, None, iterations=4)
            ero_sink = cv2.erode(dil_sink,None,iterations=2)
            (cnts, _) = cv2.findContours(ero_sink.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            count = 0 #accumulated count number of cow
	    # Step 6 : loop over the contours
            img_sink_copy = img_sink.copy()
            img_sink_copy[ero_sink>0]=(0,255,255)
            for c in cnts:
                x1,y1,w1,h1 = cv2.boundingRect(c)
                cx,cy = x1+w1/2, y1+h1/2			
                if h1 < h1_min_sink or cv2.contourArea(c) < min_areaD_sink or w1 < w1_min_sink or w1 > w1_max_sink:
                    continue
                sum+=1
                count +=1
                
                cow_pos_x.append(crop_x+x1)
                cow_pos_y.append(crop_y+y1)
                cow_pos_h.append(h1)
                cow_pos_w.append(w1)
                
                img_sink_crop = img_sink_copy[y1:y1+h1,x1:x1+w1]
                img[crop_y+y1:crop_y+y1+h1,crop_x+x1:crop_x+x1+w1]=img_sink_crop
                cv2.rectangle(img, (x1+crop_x, y1+crop_y), (x1 + w1+crop_x, y1 + h1+crop_y), (255, 0, 0), 2)
                #cv2.rectangle(img, (crop_x, crop_y), (crop_x + crop_w, crop_y + crop_h), (0, 0, 255), 2)
                #img_sink[thre_sink>0]=(0,255,255)
                
            #cv2.imshow("Frame",frame)
            #cv2.imshow("Img",img)
            #cv2.imshow("accuimg",accu_img)
            #cv2.imshow("dil",dil)
            #cv2.imshow("ero",ero)
            #cv2.imshow("thre",thre)
            #print i
            ########
            '''filename = time.strftime("%Y_%m_%d %H_%M_%S")+'.jpg'
            cv2.imwrite(filename,img)'''
            #########
            vote_count.append(count)
            if count > 0 :
                accu_img = cv2.addWeighted(delta,0.2,accu_img,0.8,0)
                accu_imgb = cv2.addWeighted(deltab,0.2,accu_imgb,0.8,0)
                accu_re = cv2.addWeighted(accu_img,0.8,accu_imgb,0.2,0)
                thre=cv2.threshold(accu_re,thre_v,thre_max, cv2.THRESH_BINARY)[1]
                dil = cv2.dilate(thre, None, iterations=4)
                ero = cv2.erode(dil,None,iterations=2)
                (cnts, _) = cv2.findContours(ero.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                for c in cnts:
                    x1,y1,w1,h1 = cv2.boundingRect(c)		
                    if h1 < h1_min or cv2.contourArea(c) < min_areaD or w1 < w1_min or w1 > w1_max:
                        continue
                    if (crop_y+crop_h) < y1 or crop_y > (y1+h1) or (crop_x+crop_w) < x1 or crop_x > (x1+w1):
                        continue
                    for a in range(len(cow_pos_x)):
                        if x1 <= cow_pos_x[a]+5 and y1 <= cow_pos_y[a]+5 and x1+w1 >=cow_pos_x[a]+cow_pos_w[a]-5 and y1+h1 >= cow_pos_y[a]+cow_pos_h[a]-5:
                            cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                    #img[thre>0]=(0,255,255)
                cv2.imwrite('/home/pi/in.jpg',img)
            else :
                cv2.imwrite('/home/pi/out.jpg',img)
            key = cv2.waitKey(1)&0xFF
            raw.truncate(0)

            if i == i_max:
                #print "%s secs" % (time.time()-start_time)
                cow_num,vote_num=0,0
                if inout_flag == 0:
                    for a in range(len(vote_count)):
                        if vote_count[a] != 0:
                            vote_num+=1
                    if vote_num >= vote_thre :
                        inout_flag,cow_num = 1,1
                        time_stamp=time.time()
                        start_date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
                        text=[start_date_stamp,cow_num,vote_num,len(vote_count)]
                        print(text)
                        with open(csv_filename, 'ab') as csv_file:
                            writer = csv.writer(csv_file,delimiter=':')
                            writer.writerow(text)
                        mydir = "/home/pi/COW_IMAGES_in/"
                        try:
                            os.makedirs(mydir)
                        except OSError:
                            if not os.path.isdir(mydir):
                                raise
                        os.chdir(mydir)
                        filename = time.strftime("%Y_%m_%d %H_%M_%S")+'.jpg'
                        img = cv2.imread('/home/pi/in.jpg')
                        cv2.imwrite(filename,img)
                        sendImage(filename,inout_flag)
                    else:
                        bg = cv2.addWeighted(bg,0.7,frame,0.3,0)
                        cv2.imwrite('/home/pi/bg.jpg',bg)
                        bg_sink = bg[crop_y:crop_y+crop_h,crop_x:crop_x+crop_w]
                        cv2.imwrite('/home/pi/bg_sink.jpg',bg_sink)
                    vote_count=[]
                elif inout_flag == 1:
                    for a in range(len(vote_count)-1):
                        if vote_count[a] == 0:
                            vote_num+=1
                    if vote_num >= vote_thre :
                        inout_flag,cow_num = 0,0
                        time_stamp=time.time()
                        end_date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
                        
                        text=[end_date_stamp,cow_num,vote_num,len(vote_count)]
                        print(text)
                        #send_text=[start_date_stamp,end_date_stamp,vote_num,len(vote_count),node_in/10]
                        conn = MySQLdb.connect(host="140.112.94.123",port=10000,user="root",passwd="ntubime405",db="dairy_cow405")
                        x=conn.cursor()
                        s1=str(vote_num)
                        s2=str(len(vote_count))
                        s3=str(int(node_in)/10)

                        x.execute('INSERT INTO logfile_image (time_start,time_end,voting_results,voting_total,NODE)' 'VALUES (%s,%s,%s,%s,%s)',(start_date_stamp,end_date_stamp,s1,s2,s3))
                        conn.commit()
                        conn.close()
                        print 'INSERT INTO logfile_image (time_start,time_end,voting_results,voting_total,NODE) VALUES (%s,%s,%s,%s,%s)',(start_date_stamp,end_date_stamp,s1,s2,s3)
                        with open(csv_filename, 'ab') as csv_file:
                            writer = csv.writer(csv_file,delimiter=':')
                            writer.writerow(text)
                        mydir = "/home/pi/COW_IMAGES_out/"
                        try:
                            os.makedirs(mydir)
                        except OSError:
                            if not os.path.isdir(mydir):
                                raise
                        os.chdir(mydir)
                        filename = time.strftime("%Y_%m_%d %H_%M_%S")+'.jpg'
                        img = cv2.imread('/home/pi/out.jpg')
                        cv2.imwrite(filename,img)
                        bg = cv2.addWeighted(bg,0.7,frame,0.3,0)
                        cv2.imwrite('/home/pi/bg.jpg',bg)
                        bg_sink = bg[crop_y:crop_y+crop_h,crop_x:crop_x+crop_w]
                        cv2.imwrite('/home/pi/bg_sink.jpg',bg_sink)
                        sendImage(filename,inout_flag)
                    vote_count=[]
                break
        raw.truncate(0)
        
cv2.destroyAllWindows()
stream.close()
raw.close()
camera.close()
