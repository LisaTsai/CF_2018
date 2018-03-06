from picamera import PiCamera
from picamera.array import PiRGBArray
import imutils
import cv2
import time

camera=PiCamera()
camera.resolution=(640,480)
camera.framerate = FPS
camera.rotation = 0
sleep(0.5)

camera.capture('/home/pi/bg.jpg')


