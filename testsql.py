
import MySQLdb
import csv
import datetime
import os


d = datetime.datetime.now()
dx = d.strftime("%Y%m%d")
date = d.strftime("%Y-%m-%d")
print type(date)
print date
print "today is " + date
ans=raw_input( "Do you want today's data? (y/n)")
if ans == "n":
    date = raw_input("Please type the date in the form like 2018-02-24 to get data")
csv_filename = date+".csv"

text =['DATE','TYPE','VALUE','THI','NODE']
if os.path.isfile(csv_filename):
    print("today's file already exists")
else:
    file = open(csv_filename,'w')
    with open(csv_filename,'ab') as csv_file:
        writer= csv.writer(csv_file,delimiter=',')
        writer.writerow(text)
#hour_ave = [[0 for y in range(61)]for x in range(13)]
conn = MySQLdb.connect(host="140.112.94.123",port=10000,user="root",passwd="ntubime405",db="dairy_cow405")

x=conn.cursor()

sqltxt="SELECT * FROM ntu_cf_02 WHERE `DATE` LIKE \"%" + date + "%\""
print sqltxt
try :
    x.execute(sqltxt)
    results = x.fetchall()
    for row in results:
        DATE=row[1]
	h = DATE.hour
        #print h
        m = DATE.minute
        #print m
        #print type(m)
        TYPE=row[2]
        VALUE=row[3]
        NODE=row[6]
        if TYPE == "T" :
            T=float(VALUE)
            text=[DATE,TYPE,VALUE,NODE]
        else: 
            H=float(VALUE)
            THI = (1.8*T+32)-(0.55-0.0055*H)*(1.8*T-26)	
            #hour_ave[h][m]=THI
            #print hour_ave[h][m]		
            text=[DATE,TYPE,VALUE,THI,NODE]
        with open(csv_filename,'ab') as csv_file:
            writer= csv.writer(csv_file,delimiter=',')
            writer.writerow(text)
except:
    print "ERROR : unable to fetch data"

conn.close()

'''
THI_hour = [0 for x in range(12)]
for x in range(12):
    sum = 0.0
    counter = 0
    for y in range(60):
        if hour_ave[x][y] != 0:
            sum+=hour_ave[x][y]
            counter+=1
    if counter != 0:
        THI_hour[x]=float(sum)/float(counter)
        text=[x,THI_hour[x]]
        with open(csv_filename,'ab') as csv_file:
            writer = csv.writer(csv_file,delimiter=',')
            writer.writerow(text)
'''   
