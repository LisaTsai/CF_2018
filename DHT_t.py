#!/usr/bin/python

'''
BME280 Sensor TH value
Made by Lisa
'''

################# Libraries ###################

#libraries
import time
import serial
import datetime
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

#sensor libraries
from Adafruit_BME280 import *
import smbus
import csv

################### Options ######################

#enable send to db server function
db_enable = 1

#db number
db = "10"

#node number
node_in = "1"
node_out = "2"
#location
location = "Lab405"
location_cam = "Lab405"+"_"+db

#enable sensors
#s1 = 1
#s2 = 0

#db codes where:
#CF=Cow farm
db_code = "CF"

#TH value sending delay in seconds
send_delay=300

#csv backup filename
csv_filename="SENSOR_"+location_cam+".csv"

##################################################

################ Parameters ######################

textc = 0
sum=0
counter=0
thre_v=20
thre_max=255
#lastframe = None
crop_x = 0
crop_y = 0
crop_w = 640
crop_h = 480
min_areaD = 800
max_areaD = 10000
w1_min=3
w1_max=640
h1_min=10
vote_cx=[]
vote_cy=[]
vote_count=[]
drink_length=[]
drink_time=0
#FPS=10




 ##################################################
############### Previous Settings ################

camera=PiCamera()
camera.resolution=(3280,2464)
camera.rotation = 0
camera.awb_mode = 'auto'
camera.drc_strength = 'high'


sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
send_delay=1
ip = "140.112.94.123"

if db_code=="CF":
  try:
    image_dir = "/home/pi/COW_IMAGES/"
    os.mkdir(image_dir,0755);
  except:
    pass
  port_udp = 30001

# Open UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

url_in='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node_in+'&location='+location_cam
url_out='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node_out+'&location='+location_cam

###################################################

####################
# Function Listing #
####################


def getImage():
    d=datetime.datetime.now()
    dx=d.strftime("%Y,%m,%d %H,%M,%S")
    
    print("Image captured!")
    locationx = image_dir+str(dx)+".jpg"
    print(locationx)
    filename=dx+".jpg"
    print(filename)
    camera.capture(locationx)

    ##open img file of in&out
    f = open(locationx,'rb')
    files = {'file':f}
    r_in=requests.post(url_in,files=files)
    r_out=requests.post(url_out,files=files)
    print(r_in.content)
    print(r_out.content)
    
##################
# Initialization #
##################

# Close and open serial port (resets the module)
print("PROGRAM START")
print("TARGET IP:"+ip+" PORT:"+str(port_udp))
print("DB CODE:"+db_code)
print("BACK-UP CSV:"+"SENSOR_"+location_cam+".csv")


# Make back-up csv file
fileexist = os.path.isfile(csv_filename)
text=['DB_CODE','DATE','NODE','TYPE','VALUE','LOCATION','DB']

if fileexist:      
  print("BACK-UP CSV ALREADY EXISTS!")
else:
  file = open(csv_filename, 'w')
  with open(csv_filename, 'ab') as csv_file:
    writer = csv.writer(csv_file,delimiter=':')
    writer.writerow(text)
  
send_timer=send_delay
time.sleep(1)

#getImage()

##################
#       END      #
##################

while True:
    
    # DT format for sensors
    time_stamp = time.time()
    date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H-%M-%S')
    
    # DT format for camera
    d=datetime.datetime.now()
    dx=d.strftime("%Y,%m,%d %H,%M,%S")

    hr=d.strftime("%H")
    mn=d.strftime("%M")
    sec=d.strftime("%S")

    hr=int(hr)
    mn = int (mn)
    sec = int (sec)
  #########################
    
    send_timer=send_timer+1
    time.sleep(1)
    Hum=[]
    Temp=[]
''' if(sec%5 == 0):
        try:
            getImage()
        except:
            pass
'''
    if send_timer>=send_delay:
       print("Querying...")
       
       degrees = sensor.read_temperature()
       pascals = sensor.read_pressure()
       hectopascals = pascals / 100
       humidity = sensor.read_humidity()
       
       print (humidity)
       print (degrees)
       h_temp, t_temp= humidity,degrees
       Hum.append(h_temp)
       Temp.append(t_temp)
       if len(Hum)==10:
           Temp.sort()
           Hum.sort()
           temp=(Temp[4]+Temp[5])/2
           hum=(Hum[4]+Hum[5])/2
           Hum=[]
           Temp=[]
           # round off to two decimal places
           temp="{0:.2f}".format(temp)
           hum= "{0:.2f}".format(hum)
           if temp is not None and hum is not None:
               #THI=(1.8*temp+32.0)-(0.55-0.0055*hum)*(1.8*temp-26.0)
               _packet1a=db_code+":"+date_stamp+":"+node+":T:"+temp+":"+location+":"+db
               _packet1b=db_code+":"+date_stamp+":"+node+":H:"+hum+":"+location+":"+db
               #_packet1c=db_code+":"+date_stamp+":"+node+":I:"+THI+":"+location+":"+db
               print(_packet1a)
               print(_packet1b)
               #print(_packet1c)
               text=[db_code,date_stamp,node,"T",temp,location,db]
               text2=[db_code,date_stamp,node,"H",hum,location,db]
               #text3=[db_code,date_stamp,node,"I",THI,location,db]
           
               with open(csv_filename, 'ab') as csv_file:
                   writer = csv.writer(csv_file,delimiter=':')
                   writer.writerow(text)
                   writer.writerow(text2)
                   #writer.writerow(text3)
               
    send_timer=0
       
    if db_enable==1:
            try:
                sock.sendto(_packet1a, (ip,port_udp))
                time.sleep(0.2)
                sock.sendto(_packet1b, (ip,port_udp))
                time.sleep(0.2)
                #sock.sendto(_packet1c, (ip,port_udp))
                #time.sleep(0.2)
                port.reset_input_buffer()                        
            except:
                pass
