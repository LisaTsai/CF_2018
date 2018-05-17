import MySQLdb
import csv
import datetime
import os

csv_filename1 ="C:/Users/Lisa/Desktop/re_ntu_cf_2018-04.csv"

with open('C:/Users/Lisa/Desktop/ntu_cf_2018-04.csv') as csvfile:

  rows = csv.reader(csvfile)
  old_mon = 0
  old_date = 0
  old_hour = -1
  # 11 outdoor and 12 indoor
  T_val_11 = [[0.0 for col in range(24)] for row in range(31)] #Tval[date-1][hour]
  H_val_11 = [[0.0 for col in range(24)] for row in range(31)]
  count_11 = [[0 for col in range(24)] for row in range(31)]
  T_val_12 = [[0.0 for col in range(24)] for row in range(31)]
  H_val_12 = [[0.0 for col in range(24)] for row in range(31)]
  count_12 = [[0 for col in range(24)] for row in range(31)]
  THI_11 = [[0.0 for col in range(24)] for row in range(31)]
  THI_12 = [[0.0 for col in range(24)] for row in range(31)]
  #T_val[1][2] = T_val[1][2]+ 23
  #print T_val
  for row in rows:
    a=row[1]
    s1=a.split(' ')
    s2=s1[0].split('-') #date
    s3=s1[1].split(':') #time
    #print(s2)
    #print(s3)
    date = int(s2[2])
    hour = int(s3[0])
    if row[6] == "11":
        if row[2] == "T":
            count_11[date-1][hour] = count_11[date-1][hour] + 1
            T_val_11[date - 1][hour] = T_val_11[date - 1][hour] + float(row[3])
        elif row[2] == "H":
            H_val_11[date - 1][hour] = H_val_11[date - 1][hour] + float(row[3])
    elif row[6] == "1" or row[6] == "2":
        if row[2] == "T":
            count_12[date-1][hour] = count_12[date-1][hour] + 1
            T_val_12[date - 1][hour] = T_val_12[date - 1][hour] + float(row[3])
        elif row[2] == "H":
            H_val_12[date - 1][hour] = H_val_12[date - 1][hour] + float(row[3])

for i in range(0,31):
    for j in range(0,24):
        if T_val_11[i][j] != 0.0 and count_11[i][j] != 0 and  H_val_11[i][j] != 0.0 :
            T_val_11[i][j] = round((T_val_11[i][j] / float(count_11[i][j])),2)
            H_val_11[i][j] = round((H_val_11[i][j] / float(count_11[i][j])),2)
            THI_11[i][j] = round(((1.8 * T_val_11[i][j]  + 32.0) - (0.55-0.0055 * H_val_11[i][j])*(1.8*T_val_11[i][j] - 26.0)),2)
        if T_val_12[i][j] != 0.0 and count_12[i][j] != 0 and  H_val_12[i][j] != 0.0:
            T_val_12[i][j] =round(( T_val_12[i][j] / float(count_12[i][j])),2)
            H_val_12[i][j] = round((H_val_12[i][j] / float(count_12[i][j])),2)
            THI_12[i][j] = round(((1.8 * T_val_12[i][j] + 32.0) - (0.55 - 0.0055 * H_val_12[i][j]) * (1.8 * T_val_12[i][j] - 26.0)),2)

text =['DATE','HOUR','Indoor','T','H','THI','Outdoor','T','H','THI']
if os.path.isfile(csv_filename1):
    print(" file already exists")
else:
    #file = open(csv_filename1,'wb')
    with open(csv_filename1,'wb') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(text)
        for i in range(0, 31):
            for j in range(0, 24):
                text1 = [str(i+1),str(j),' ',str(T_val_11[i][j]), str(H_val_11[i][j]),str(THI_11[i][j]),' ', str(T_val_12[i][j]), str(H_val_12[i][j]),str(THI_12[i][j])]
                writer = csv.writer(f, delimiter=',')
                writer.writerow(text1)
