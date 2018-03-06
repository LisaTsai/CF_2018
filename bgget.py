from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep

camera=PiCamera()
camera.resolution=(640,480)
sleep(0.5)

camera.capture('/home/pi/bg.jpg')


