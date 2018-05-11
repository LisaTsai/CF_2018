'''

Lisa Tsai

2018/03/23

'''
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


print "--------"
print "current time is " + time.strftime("%Y-%m-%d %H:%M:%S")
print "--------"



### Options

db_enable = 1

inout_flag = 0
old_flag = 0
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
    f = open('/home/pi/count.txt','r')
    count = f.read()
    count = node_out.strip('\n')
    filename = os.listdir(image_dir)[-1]
    if count != old_flag and count > 0:
        sendImage(filename,1)
        old_flag = 1
    elif count !=old_flag and count == 0:
        sendImage(filename,0)
        old_flag = 0
    f.close()
    sleep(15)
        
cv2.destroyAllWindows()
camera.close()
