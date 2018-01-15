
'''
By Lisa Tsai
Latest update - 2018/01/12

'''


from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
#from imutils.video.pivideostream import PiVideoStream
#from imutils.video import FPS
import imutils
import cv2
import time
import os

#logfile for img
import csv
import datetime


textc,sum,counter=0,0,0
thre_v,thre_max=20,255
#lastframe = None
crop_x,crop_y,crop_w,crop_h = 0,0,640,480
min_areaD,max_areaD = 800,10000
w1_min,w1_max,h1_min = 3,640,10
vote_cx,vote_cy,vote_count,drink_length=[],[],[],[]
drink_time=0
drink_total=10
FPS=10 # count_max
cow_num,vote_num=0,0
contour_list=[]
###use append to list

d=datetime.datetime.now()
dx=d.strftime("%Y%m%d")
csv_filname = "NTU_CF_test.csv"

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
	
	
camera=PiCamera()
camera.resolution=(640,480)
camera.framerate=FPS
sleep(0.5)

while True:
	#camera.start_preview()
	raw=PiRGBArray(camera,size=(640,480))
	stream = camera.capture_continuous(raw,format="bgr",use_video_port=True)
	#print("[INFO]sampling frames from picamera module")
	#fps=FPS().start()
	for(i,f) in enumerate(stream):
		frame = f.array
		# Step 1 : grayscale
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# Step 2 : medianBlur
		median = cv2.medianBlur(gray,7) 
		# Step 3 : find lastframe
		if counter == 0:
			lastframe = median
			counter = 1
			break
		
		# Step 4 : absolute diff between lastframe and current frame
		delta = cv2.absdiff(lastframe,median)
		thre=cv2.threshold(delta,thre_v,thre_max, cv2.THRESH_BINARY)[1]
		lastframe = median
		# Step 5 : dilate to fill in holes, then find contours
		thre = cv2.dilate(thre, None, iterations=2)
		(cnts, _) = cv2.findContours(thre.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		count = 0 #accumulated count
		# Step 6 : loop over the contours
		for c in cnts:
			x1,y1,w1,h1 = cv2.boundingRect(c)
			cx,cy = x1+w1/2, y1+h1/2
			#if i <=1:
			#	vote_cx.append(cx)
			#	vote_cy.append(cy)
			#	vote_count.append(0)
			#	drink_length.append(0)
			#elif i == FPS:
			#	for z in range(len(vote_cx)):
			#		flagc = vote_count[z]
			#		vote_count[z]=0
			#		if flagc > FPS/2:
			#			drink_length[z]+=1
			#			drink_time += 1
			#		else:
			#			del vote_cx[z]
			#			del vote_cy[z]
			#			del drink_length[z]
			#			del vote_count[z]
			#else:
			#	for z in range(len(vote_cx)):
			#		if abs(cx-vote_cx[z])<50 and abs(cy-vote_cy[z])<50 :
			#			vote_count[z]+=1
					
			# if the contour is too small, ignore it
			if h1 < h1_min or cv2.contourArea(c) < min_areaD or  cv2.contourArea(c) > max_areaD or w1 < w1_min or w1 > w1_max:
				continue
			sum+=1
			count +=1
			# compute the bounding box for the contour and  draw
			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x+crop_x, y+crop_y), (x+crop_x + w, y+crop_y + h), (0, 255, 0), 2)
		textc=str(count)
		texts = str(sum)
		textd=str(drink_time)
		text=str(i)
		cv2.putText(frame, "FPS : {}".format(text), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
		cv2.putText(frame,"Drink time : {}".format(textd),(10,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)		
		cv2.putText(frame,"Count : {}".format(textc),(10,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
		cv2.putText(frame,"Sum : {}".format(texts),(10,110),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
		
		#frame = imutils.resize(frame,width=400)
		cv2.imshow("Frame",frame)
#		cv2.imshow("Gray",gray)
#		cv2.imshow("Median",median)
#		cv2.imshow("Delta",delta)
		vote_count.append(count)
		if count > 0 :
			currentdate=time.strftime("%Y%m%d")
			mydir = "/home/pi/Desktop/"+currentdate
			try:
				os.makedirs(mydir)
			except OSError:
				if not os.path.isdir(mydir):
					raise
			os.chdir(mydir)
			filename = time.strftime("%H%M%S")+'.jpg' 
			cv2.imwrite(filename,frame)
		key = cv2.waitKey(1)&0xFF
		raw.truncate(0)
		#fps.update()
		if i == FPS:
			# DT format for sensors
			cow_num,vote_num=0,0
			for a in range(len(vote_count)):	
				if a == 0:
					vote_num+=1
			if vote_num < 5 :
				vote_num=0
				for a in range(len(vote_count)):	
					if a >= 1:
						vote_num+=1
				if vote_num < 5 :
					vote_num=0
					for a in range(len(vote_count)):	
						if a >= 2:
							vote_num+=1
					if vote_num >= 5 :
						cow_num = 2
				else:
					cow_num=1
			date_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H-%M-%S')
			text=[date_stamp,cow_num,vote_num,"10"]
			with open(csv_filename, 'ab') as csv_file:
				writer = csv.writer(csv_file,delimiter=':')
				writer.writerow(text)
			vote_count=[]
			break
#fps.stop()
#print("[INFO] elapsed time:{:,2f}".format(fps.elapsed()))
#print("[INFO] approx. FPS: {:,2f}".fomat(fps.fps()))
cv2.destroyAllWindows()
stream.close()
raw.close()
camera.close()
