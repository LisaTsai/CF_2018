#!/usr/bin/python
# coding=UTF-8

#********************************#
#********************************#
#   Common platform WiSN program #
#    By: Lisa Tsai               # 
#        Dan Jeric Arcega Rustia #
#                                #
#   Log:
#   12/19/2018 - Local Server
#   4/18/2018 - LineBot          #
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
import numpy as np
import requests
import urllib2
from urllib import urlencode
import os

#sensor libraries
from Adafruit_BME280 import *
import smbus
import csv
import MySQLdb
import pyodbc
import pymssql

#############Options##############

#enable send to db server function
db_enable = 1

#db number
f=open('/home/pi/Adafruit_Python_BME280/DB_NUM.txt','r')
db = f.read()
db=db.strip('\n')

#node number
f=open('/home/pi/Adafruit_Python_BME280/NODE.txt','r')
node = f.read()
node=node.strip('\n')

#location
location = "SF_CF"
location_cam = "SF_CF"+"_"+db

#enable sensors
s1 = 1
s2 = 0

#db codes where:
db_code = "CF"


#TH value sending delay in seconds
send_delay=300

#csv backup filename
csv_filename="SENSOR_"+location_cam+"_"+node+".csv"

Hum=[]
Temp=[]

#################################
# Do not touch the codes below! #
port_udp = 30001
ip = "140.112.94.123" 
 

# Open UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# file transfer u
url='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node+'&location='+location_cam

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


##################
# Initialization #
##################

# Close and open serial port (resets the module)
print("PROGRAM START")
  
send_timer=send_delay
time.sleep(1)

##################
#       END      #
##################

while 1:
        time_stamp = time.time()
        date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

        d=datetime.datetime.now()
        dx=d.strftime("%Y,%m,%d %H,%M,%S")

        hr=d.strftime("%H")
        mn=d.strftime("%M")
        sec=d.strftime("%S")

        hr=int(hr)
        mn = int (mn)
        sec = int (sec)

        send_timer=send_timer+1
        time.sleep(1)

        if send_timer>=send_delay/10: 
                send_timer=0
                try:
                        degrees = sensor.read_temperature()
                        humidity = sensor.read_humidity()
                        h_temp, t_temp= humidity,degrees
                        Hum.append(h_temp)
                        Temp.append(t_temp)
                        print Temp
                        if len(Hum)==10:
                                Temp.sort()
                                Hum.sort()
                                temp=(Temp[4]+Temp[5])/2
                                hum=(Hum[4]+Hum[5])/2
                                Hum=[]
                                Temp=[]
                                temp="{0:.2f}".format(temp)
                                hum= "{0:.2f}".format(hum)
                                THI = (1.8*float(temp)+32.0)-(0.55-0.0055*float(hum))*(1.8*float(temp)-26.0)
                                THI="{0:.2f}".format(THI)
                                time_stamp = time.time()
                                date_stamp2 = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
                                if temp is not None and hum is not None:
                                        print THI
                                        try:
                                                print "0"
                                                server = '114.35.39.4:2345'
                                                db = 'Ranch_NTU'
                                                user = 'sa'
                                                pswd = '0988656892@0972195120'
                                                #conn = pyodbc.connect('DRIVER={FreeTDS};SERVER='+server+';DATABASE='+db+';UID='+user+';PWD='+pswd)
                                                conn = pymssql.connect(host=server, user=user, password=pswd, database=db)
                                                

                                                print "1"
                                                x = conn.cursor()
                                                print "2"
                                                print date_stamp + ", " + temp + ", " + hum + ", " +THI
                                                x.execute('INSERT INTO dbo.Ranch_THI(DATE,T,H,THI,FARM,NODE,EXPT,CREATE_DATE,CREATE_USER,UPDATE_DATE,UPDATE_USER,IS_ACTIVE)''VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(date_stamp,temp,hum,THI,"Fourways","01","00",date_stamp,"NTU",date_stamp2,"NTU","Y"))
                                                #x.execute("INSERT INTO dbo.Ranch_THI (DATE, T,H,THI) VALUES (%s, %s, %s, %s)", (date_stamp, temp, hum, THI))
                                                
                                                
                                                print "3"
                                                conn.commit()
                                                print "4"
                                                conn.close()
                                                print "5"
                                        except:
                                                pass
                except:
                        pass

      


             
            
      
