#!/usr/bin/python
# coding=UTF-8

#********************************
#********************************
#  Dairy Cow Farm Sensor System
#    By: Lisa Tsai
#
#   Log:
#   07/23/2018 - Directly insert into SQL
#   04/18/2018 - LineBot
#   01/15/2018 - Use BME280
#********************************
#********************************
sink_tag = "Beta"
Line_on = 0

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import IDs

line_bot_api = LineBotApi(IDs.token)
target = IDs.target

danger,THI_stage,THI_old = 0,0,0
THI_label=['Normal(Lv0)','Mild(Lv1)','Moderate(Lv2)','Severe(Lv3)','Danger(Lv4)']

def push_message(message,target):
	try:
		line_bot_api.push_message(target, TextSendMessage(text=message))
	except LineBotApiError as e:
		print e

mes = "我開始工作啦(" + sink_tag + ")!"
if Line_on:
	push_message(mes,target)


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

#############Options##############

#enable send to db server function
db_enable = 1

#db number
f=open('DB_NUM.txt','r')
db = f.read()
db=db.strip('\n')

#node number
f=open('NODE.txt','r')
node = f.read()
node=node.strip('\n')

#location
f=open('FARM.txt','r')
location = f.read()
location = location.strip('\n')
location_cam = location+"_"+db

#enable sensors
s1 = 1
s2 = 0

db_code = "CF"

#TH value sending delay in seconds
send_delay = 300

#csv backup filename
csv_filename="SENSOR_"+location_cam+"_"+node+".csv"

Hum=[]
Temp=[]

def THI_cal(THI):
	global THI_old
	global THI_stage
	global node
	global danger
	THI_old = THI_stage
	if float(THI) >= 98.00 :
		THI_stage = 4
	elif float(THI) >= 88.00:
		THI_stage = 3
	elif float(THI) >= 78.00:
		THI_stage = 2
	elif float(THI) >= 72.00:
		THI_stage = 1
	elif float(THI) < 72.00:
		THI_stage = 0
	if THI_stage > THI_old and THI_stage > 2:
		mes = "(" + sink_tag + ") THI = "+ THI +" "+ THI_label[THI_stage]
		danger = 1
		push_message(mes,target)
	elif THI_stage < THI_old and THI_stage < 2 and danger == 1:
		mes = "(" + sink_tag + ") THI = "+ THI + " " + THI_label[THI_stage] + "問題已解決"
		danger = 0
	push_message(mes,target)
	#print THI,THI_stage,THI_old
#THI_cal(23.22,80.13)

#################################
# Do not touch the codes below! #
port_udp = 30001
ip = "140.112.94.123" 
 

# Open UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# file transfer url
# url='http://140.112.94.123:30000/DAIRY_COW/IMAGE/RX_IMG.php?node='+node+'&location='+location_cam

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


##################
# Initialization #
##################

# Close and open serial port (resets the module)
print("PROGRAM START")
print("TARGET IP:"+ip+" PORT:"+str(port_udp))
print("Location:"+location+" NODE#"+node)
print("BACK-UP CSV:"+"SENSOR_"+location_cam+"_"+node+".csv")


# Make back-up csv file
fileexist = os.path.isfile(csv_filename)
text=['DATE','NODE','T','H','THI','LOCATION','DB']

if fileexist:      
	print("BACK-UP CSV ALREADY EXISTS!")
else:
	file = open(csv_filename, 'w')
	with open(csv_filename, 'ab') as csv_file:
		writer = csv.writer(csv_file,delimiter=':')
		writer.writerow(text)
  
send_timer=send_delay
time.sleep(1)

##################
#       END      #
##################

while 1:

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
	#print("Sensor: " + str(send_timer) + "  Camera: " + str(hr) + ":" + str(mn) + ":" + str(sec))
	time.sleep(1)

	if send_timer>=send_delay/10: 
		# print("Querying...")
		send_timer=0
		try:
			# read sensor data
			degrees = sensor.read_temperature()
			humidity = sensor.read_humidity()
			h_temp, t_temp= humidity,degrees
			Hum.append(h_temp)
			Temp.append(t_temp)
			print(len(Hum))
			print(Temp)
			if len(Hum)==10:
                                print "Finally inside"
				Temp.sort()
				Hum.sort()
				temp=(Temp[4]+Temp[5])/2
				hum=(Hum[4]+Hum[5])/2
				Hum=[]
				Temp=[]
				print "Do we been here?"
				print (temp)
				print (hum)
				temp="{0:.2f}".format(temp)
				hum= "{0:.2f}".format(hum)
				THI = (1.8*float(temp)+32.0)-(0.55-0.0055*float(hum))*(1.8*float(temp)-26.0)
				THI = "{0:.2f}".format(THI)
				print (float(THI))
				if temp is not None and hum is not None:
					if Line_on:
						THI_cal(THI)
					if db_enable==1:
						try:
							if s1==1:
                                                                print "Thanks"
								conn = MySQLdb.connect(host="140.112.94.123",port=10000,user="root",passwd="ntubime405",db="dairy_cow405")
								x=conn.cursor()
								x.execute('INSERT INTO ntu_cf_thi (DATE,T,H,THI,FARM,EXPT,NODE)' 'VALUES (%s,%s,%s,%s,%s,%s,%s)',(date_stamp,temp,hum,THI,location,"01",node))
								conn.commit()
								conn.close()
								text=[date_stamp,node,temp,hum,THI,location,db]
								with open(csv_filename, 'ab') as csv_file:
									writer = csv.writer(csv_file,delimiter=':')
									writer.writerow(text)
                                                        print "Amazing"
						except:
							pass
		except:
			pass
      


             
            
      
