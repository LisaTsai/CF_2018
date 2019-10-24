#!/usr/bin/python

#********************************#
#********************************#
#   Common platform WiSN program #
#    By: Lisa Tsai				 # 
#		 Dan Jeric Arcega Rustia #
#                                #
#   Log:                         #
#   1/15/2018 - use BME280       #
#   9/28/2017 - universal code   #
#   7/5/2017 - added CSV backup  #
#   6/26/2017 - new program for  #
#               waterproof design#
#   5/22/2017 - removed com check#
#   5/12/2017 - added camera     #
#   5/5/2017 - added com check   #
#   3/30/2017 - finished up to   #
#               temp,hum and lux #
#             - udp sending      #
#********************************#
#********************************#

import subprocess
try:
  subprocess.call(['/home/pi/RPi_Cam_Web_Interface/stop.sh'])
except:
  pass

#libraries
import time
import serial
import datetime
import socket

#cam libraries
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import requests
import urllib2
from urllib import urlencode
import os

#sensor libraries
from Adafruit_BME280 import *
import smbus
import csv

#############Options##############

#enable send to db server function
db_enable = 1

#db number
db = "2"

#node number
node = "45"

#location
location = "NTU_CF"
location_cam = "NTU_CF"+"_"+db

#enable sensors
s1 = 1
s2 = 0

#db codes where:
#PD=Pest detect
#BD=Bee detect
#PF=Plant factory
#CF=Cow farm
#H=Home envi
db_code = "CF"


# dht sensor constants
#dhtg = Adafruit_DHT.AM2302
#dht_pin = 17

#TH value sending delay in seconds
send_delay=60

#csv backup filename
csv_filename="SENSOR_"+location_cam+"_"+node+".csv"

Hum=[]
Temp=[]

#################################
# Do not touch the codes below! #


#image directory
if db_code=="CF":
  try:
    image_dir = "/home/pi/COW_IMAGES/"
    os.mkdir(image_dir, 0755);
  except:
    pass
  port_udp = 30001
if db_code=="PD":
  try:
    image_dir = "/home/pi/PEST_IMAGES/"
    os.mkdir(image_dir, 0755);
  except:
    pass
  port_udp = 20001
 
ip = "140.112.94.123" 
 

# Open UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# file transfer url
#url='http://140.112.94.123:20000/PEST_DETECT/PEST_IMAGES/RX_IMG.php?node='+node+'&location='+location_cam
url='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node+'&location='+location_cam

# camera settings
camera = PiCamera()
camera.resolution = (3280,2464)
camera.framerate = 15
camera.rotation = 0
camera.awb_mode = 'auto'
camera.drc_strength = 'high'

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

#bh1750 constants
DEVICE     = 0x23 # Default device I2C address
 
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
 
# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13
# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10
# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20
# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23
 
#bus = smbus.SMBus(0) # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
  return convertToNumber(data)



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

    f = open(locationx,'rb')
    files = {'file':f}
    r=requests.post(url,files=files)
    print(r.content)
	for the_file in os.listdir(image_dir):
	    file_path = os.path.join(image_dir,the_file)
		try:
		    if os.path.isfile(file_path):
			    os.remove(file_path)
				print("delete sucess")
		except Expection as e:
		    print e


##################
# Initialization #
##################

# Close and open serial port (resets the module)
print("PROGRAM START")
print("TARGET IP:"+ip+" PORT:"+str(port_udp))
print("DB CODE:"+db_code+" NODE#"+node)
print("BACK-UP CSV:"+"SENSOR_"+location_cam+"_"+node+".csv")


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


getImage()

##################
#       END      #
##################

while 1:

    ##########################
    #### GET TIME AND DATE ###

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
    ###########################

    send_timer=send_timer+1
    print("Sensor: " + str(send_timer) + "  Camera: " + str(hr) + ":" + str(mn) + ":" + str(sec))
    time.sleep(1)

    if (mn%1 == 0 and sec == 0):
        #if hr>6 and hr <=18:
        try:
            getImage()
        except:
            pass

    if send_timer>=send_delay/10: 
        print("Querying...")
        send_timer=0
        # get sensor 1 data
        try:
            # read sensor data
            degrees = sensor.read_temperature()
	    humidity = sensor.read_humidity()
			
            h_temp, t_temp= humidity,degrees
            Hum.append(h_temp)
            Temp.append(t_temp)
            #print(h_temp)
            #print(t_temp)
            #print(Hum)
            #print(Temp)
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
                if db_enable==1:
                    try:
                        if s1==1:
                            sock.sendto(_packet1a, (ip,port_udp))
                            time.sleep(0.2)
                            sock.sendto(_packet1b, (ip,port_udp))
                            time.sleep(0.2)
                            port.reset_input_buffer()                        
                    except:
                        pass
                #print(_packet1c)
                text=[db_code,date_stamp,node,"T",temp,location,db]
                text2=[db_code,date_stamp,node,"H",hum,location,db]
                #text3=[db_code,date_stamp,node,"I",THI,location,db]
                with open(csv_filename, 'ab') as csv_file:
                  writer = csv.writer(csv_file,delimiter=':')
                  writer.writerow(text)
                  writer.writerow(text2)
                  #writer.writerow(text3)
        except:
            pass

      


             
            
      
