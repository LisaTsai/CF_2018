'''
By Lisa Tsai
Latest Update - 2019/01/13

2019/01/13 first trial

'''

### Libraries

from time import sleep
import serial
import socket
import argparse

### Camera libraries

import numpy as np
import requests
#import urllib2
#from urllib import urlencode
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
#import imutils
import cv2
import time

### logfile for img

import csv
import datetime
#import MySQLdb

### Record Time

print ("--------")
print ("current time is " + time.strftime("%Y-%m-%d %H:%M:%S"))
print ("--------")

### Options (Not complete)

#FPS=6

### YOLO Options

scale = 0.00392
config = '/home/pi/Desktop/tiny-yolo-cow_head.cfg'
weights = '/home/pi/Desktop/tiny-yolo-cow_head_50000.weights'
classeslist = '/home/pi/Desktop/cowhead.names'
with open(classeslist, 'r') as f:
    classes = [line.strip() for line in f.readlines()]
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
net = cv2.dnn.readNet(weights, config)

class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4

### Camera settings

camera=PiCamera()
camera.resolution=(640,480)
#camera.framerate = FPS
camera.rotation = 0
sleep(0.5)

### Self Define Functions (not complete)

### YOLO Functions

def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

### Main 

while True:
    start_time=time.time()
    raw=PiRGBArray(camera,size=(640,480))
    stream = camera.capture_continuous(raw,format="bgr",use_video_port=True)
    for(i,f) in enumerate(stream):
        frame = f.array
        image = frame.copy()
        Width = image.shape[1]
        Height = image.shape[0]
        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(get_output_layers(net))
        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
        cv2.imshow("Object detection",image)
        key = cv2.waitKey(1)&0xFF
        raw.truncate(0)

cv2.destroyALLWindows()
stream.close()
raw.close()
camera.close()
