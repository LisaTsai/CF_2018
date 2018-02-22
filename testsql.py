
import MySQLdb
import csv
import datetime
import os

d = datetime.datetime.now()
dx = d.strftime("%Y%m%d")
date = d.strftime("%Y-%m-%d")

csv_filename = dx+".csv"
text =['ID','DATE','TYPE','VALUE','FARM','EXPT','NODE']
if os.path.isfile(csv_filename):
    print("today's file already exists")
else:
    file = open(csv_filename,'w')
    with open(csv_filename,'ab') as csv_file:
        writer= csv.writer(csv_file,delimiter=',')
        writer.writerow(text)

conn = MySQLdb.connect(host="140.112.94.123",port=10000,user="root",passwd="ntubime405",db="dairy_cow405")
#print "a"
x=conn.cursor()
sqltxt="SELECT * FROM ntu_cf_02 WHERE `DATE` LIKE \"%" + date + "%\""

print sqltxt
try :
    x.execute(sqltxt)
    results = x.fetchall()
    for row in results:
        #print row
        ID = row[0]
        DATE=row[1]
        TYPE=row[2]
        VALUE=row[3]
        FARM=row[4]
        EXPT=row[5]
        NODE=row[6]
        print ID,DATE,TYPE,VALUE,FARM,EXPT,NODE
        text=[ID,DATE,TYPE,VALUE,FARM,EXPT,NODE]
        with open(csv_filename,'ab') as csv_file:
            writer= csv.writer(csv_file,delimiter=',')
            writer.writerow(text)
except:
    print "ERROR : unable to fetch data"
'''start_time="2018-01-02 18:18:18"
end_time="2018-01-02 18:20:20"#
vs=9

v=str(vs)
n="10"
node="10"


x.execute('INSERT INTO logfile_image (time_start,time_end,voting_results,voting_total,NODE)' 'VALUES (%s,%s,%s,%s,%s)',(start_time,end_time,v,n,node))
'''

#conn.commit()
#print 'INSERT INTO logfile_image (time_start,time_end,voting_results,voting_total,NODE) VALUES (%s,%s,%s,%s,%s)',(start_time,end_time,v,n,node)
conn.close()

