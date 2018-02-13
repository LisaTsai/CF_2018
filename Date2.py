import time 
import os 
import errno
from picamera import PiCamera

day = 100
interval = 10
RecordTime = 86400/interval*day
getthedate = "20170801"

camera = PiCamera()
camera.resolution = (640,480)

for i in range(int(RecordTime)):
    getcurrentdate = time.strftime("%Y%m%d")
    if getthedate != getcurrentdate:
        getthedate = getcurrentdate
        mydir = "/home/pi/Desktop/"+getthedate
        try:
            os.makedirs(mydir)
        except OSError:
            if not os.path.isdir(mydir):
                raise
        os.chdir(mydir)
    filename = time.strftime("%H%M%S")+'.jpg'
    camera.capture(filename)
    time.sleep(interval)

#runstill = ("raspistill -w 1280 -h 720 -tl 10 -t 50 -o "+mydir+"/pic%03d.jpg")
#os.system(runstill)
