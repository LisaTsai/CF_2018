#!/usr/bin/env python3
# coding=UTF-8

#********************************
#********************************
#  Dairy Cow Farm Sensor System
#    By: Lisa Tsai
#
#   Log:
#   03/14/2019 - Replace BME280 with SHT20
#   07/23/2018 - Directly insert into SQL
#   04/18/2018 - LineBot
#   01/15/2018 - Use BME280
#********************************
#********************************

#import libraries and get settings
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import settings

line_bot_api = LineBotApi(settings.token)
target = settings.target

#Define a fcn for push message to the target Line group
def push_message(message,target):
	try:
		line_bot_api.push_message(target, TextSendMessage(text=message))
	except LineBotApiError as e:
		print (e)

#Testing on pushing message and announce that the program starts to work
mes = "我開始工作啦(" + settings.sink_tag + ")!"
if settings.Line_on:
	push_message(mes,target)

#Define the THI related variables and labels
danger,THI_stage,THI_old = 0,0,0
THI_label=['Normal(Lv0)','Mild(Lv1)','Moderate(Lv2)','Severe(Lv3)','Danger(Lv4)']


#libraries
import time
import datetime
import os
import csv
import MySQLdb
from sensor.SHT20 import SHT20
import requests

#############Options##############

db=settings.db_num
node=settings.node
location = settings.farm
send_delay = settings.time_delay

#csv backup filename
csv_filename="SENSOR_"+location+"_"+db+"_"+node+".csv"


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

##################
# Initialization #
##################

# Close and open serial port (resets the module)
print("PROGRAM START")
print("Location:"+location+" NODE#"+node)
print("BACK-UP CSV:"+csv_filename)


# Make back-up csv file
fileexist = os.path.isfile(csv_filename)
text=['DATE','NODE','T','H','THI','LOCATION','DB']

if fileexist:      
	print("BACK-UP CSV ALREADY EXISTS!")
else:
	file = open(csv_filename, 'w')
	with open(csv_filename, 'a') as csv_file:
		writer = csv.writer(csv_file,delimiter=':')
		writer.writerow(text)
  

#Initialize the empty array for humidity record and temperature record
Hum,Temp=[],[]
#initialize the send_timer and rest for 1 second
send_timer=0
time.sleep(1)
#SHT20 settings
sht = SHT20(1,0x40)


##################
#       END      #
##################

while True:
        # DT format for sensors
        time_stamp = time.time()
        date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H-%M-%S')

        send_timer=send_timer+1
	#print("Sensor: " + str(send_timer) + "  Camera: " + str(hr) + ":" + str(mn) + ":" + str(sec))
        #wait for 1 second
        time.sleep(1)
        if send_timer>=send_delay/10: 
		#print("Querying...")
                send_timer=0
                try:
                        # read sensor data
                        h,t = sht.all()
                        Hum.append(h.RH)
                        Temp.append(t.C)
                        print(Hum)
                        print(Temp)
                        #Apply median filter on the humidity and temperature data arrays
                        if len(Hum)==10:
                                Temp.sort()
                                Hum.sort()
                                temp=(Temp[4]+Temp[5])/2
                                hum=(Hum[4]+Hum[5])/2
                                Hum,Temp=[],[]
                                temp="{0:.2f}".format(temp)
                                hum= "{0:.2f}".format(hum)
                                THI = (1.8*float(temp)+32.0)-(0.55-0.0055*float(hum))*(1.8*float(temp)-26.0)
                                print (temp)
                                print (hum)
                                THI = "{0:.2f}".format(THI)
                                print (float(THI))
                                if temp is not None and hum is not None:
                                        if settings.Line_on:
                                                THI_cal(THI)
                                        if settings.db_enable==1:
                                                try:
                                                        #connect to the MySQL server and insert data
                                                        conn = MySQLdb.connect(host=settings.lab_host,port=settings.lab_port,user=settings.lab_user,passwd=settings.lab_passwd,db=settings.lab_db)
                                                        x = conn.cursor()
                                                        action = 'INSERT INTO '+ settings.lab_table +' (DATE,T,H,THI,FARM,EXPT,NODE) VALUES (%s,%s,%s,%s,%s,%s,%s)'
                                                        data_value = (date_stamp,temp,hum,THI,location,settings.exp,node)
                                                        x.execute(action ,data_value)
                                                        conn.commit()
                                                        conn.close()
                                                        print("Insert data into MySQL successfully")
                                                        text=[date_stamp,node,temp,hum,THI,location,db]
                                                        with open(csv_filename, 'a') as csv_file:
                                                                writer = csv.writer(csv_file,delimiter=':')
                                                                writer.writerow(text)
                                                except:
                                                        pass
                                                try:
                                                        #connect to the database of III and insert data
                                                        record_dt = ('?record_dt='+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                                        THI_str = ('&temperature='+str(temp)+'&humidity='+str(hum)+'&thi='+str(THI))
                                                        info = ('&ranch_no='+node+'&ranch_name='+location)
                                                        print(record_dt+THI_str+info)
                                                        data_post = requests.post("http://140.92.88.118/CMS/api/sensor/saveRanchTah"+record_dt+THI_str+info)
                                                        print(data_post.text)
                                                except:
                                                        pass
                except:
                        pass
      


             
            
      
