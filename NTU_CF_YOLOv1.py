
'''
By Lisa Tsai
Latest Update - 2019/01/13

2019/01/13 first trial
'''

### Libraries

from time import sleep
import serial
import socket
import argparse

### Camera libraries

import numpy as np
import requests
#import urllib2
#from urllib import urlencode
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
#import imutils
import cv2
import time

### logfile for img

import csv
import datetime
import MySQLdb

### Record Time

print ("--------")
print ("current time is " + time.strftime("%Y-%m-%d %H:%M:%S"))
print ("--------")

### Options (Not complete)
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


#sink position
#f = open('/home/pi/Adafruit_Python_BME280/sink.txt','r')
f = open('sink.txt','r')
sink = f.read()
sink = sink.strip('/n')
a = sink.split(',')
crop_x,crop_y,crop_w,crop_h =int(a[0]),int(a[1]),int(a[2]),int(a[3])
#bg_sink = bg[crop_y:crop_y+crop_h,crop_x:crop_x+crop_w]
#cv2.imwrite('/home/pi/bg_sink.jpg',bg_sink)

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

### YOLO Options

scale = 0.00392
config = '/home/pi/Desktop/tiny-yolo-cow_head.cfg'
weights = '/home/pi/Desktop/tiny-yolo-cow_head_50000.weights'
classeslist = '/home/pi/Desktop/cowhead.names'
with open(classeslist, 'r') as f:
    classes = [line.strip() for line in f.readlines()]
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
net = cv2.dnn.readNet(weights, config)

class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4

### Camera settings

camera=PiCamera()
camera.resolution=(640,480)
#camera.framerate = FPS
camera.rotation = 0
sleep(0.5)

### Self Define Functions (not complete)

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
        print (e)


### YOLO Functions

def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

### Main 

while True:
    start_time=time.time()
    raw=PiRGBArray(camera,size=(640,480))
    stream = camera.capture_continuous(raw,format="bgr",use_video_port=True)
    for(i,f) in enumerate(stream):
        frame = f.array
        image = frame.copy()
        Width = image.shape[1]
        Height = image.shape[0]
        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(get_output_layers(net))
        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

        #cv2.imshow("Object detection",image)
        if len(indices) > 0 and inout_flag == 0:
            inout_flag,cow_num = 1,1
            time_stamp=time.time()
            start_date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
            text=[start_date_stamp,len(indices)]
            print(text)
            #with open(csv_filename, 'ab') as csv_file:
                #writer = csv.writer(csv_file,delimiter=':')
                #writer.writerow(text)
            mydir = "/home/pi/COW_IMAGES_in/"
            try:
                os.makedirs(mydir)
            except OSError:
                if not os.path.isdir(mydir):
                    raise
            os.chdir(mydir)
            filename = time.strftime("%Y_%m_%d %H_%M_%S")+'.jpg'
            cv2.imwrite(filename,image)
            sendImage(filename,inout_flag)
        
        elif inout_flag == 1 and len(indices) < 1:
            inout_flag,cow_num = 0,0
            time_stamp=time.time()
            end_date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
            text=[start_date_stamp,len(indices)]
            print(text)
            conn = MySQLdb.connect(host="140.112.94.123",port=10000,user="root",passwd="ntubime405",db="dairy_cow405")
            x=conn.cursor()
            s1,s2,s3="0","0","0"
            x.execute('INSERT INTO logfile_image (time_start,time_end,voting_results,voting_total,NODE)' 'VALUES (%s,%s,%s,%s,%s)',(start_date_stamp,end_date_stamp,s1,s2,s3))
            conn.commit()
            conn.close()
            
            print ('INSERT INTO logfile_image (time_start,time_end,voting_results,voting_total,NODE) VALUES (%s,%s,%s,%s,%s)',(start_date_stamp,end_date_stamp,s1,s2,s3))            
            mydir = "/home/pi/COW_IMAGES_out/"
            try:
                os.makedirs(mydir)
            except OSError:
                if not os.path.isdir(mydir):
                    raise
            os.chdir(mydir)
            filename = time.strftime("%Y_%m_%d %H_%M_%S")+'.jpg'
            cv2.imwrite(filename,image)
            sendImage(filename,inout_flag)
        print ("--------")
        print ("current time is " + time.strftime("%Y-%m-%d %H:%M:%S"))
        print ("--------")
        print (inout_flag)
                
        key = cv2.waitKey(1)&0xFF
        raw.truncate(0)

cv2.destroyALLWindows()
stream.close()
raw.close()
camera.close()
