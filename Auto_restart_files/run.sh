#!/bin/bash
cd /home/pi/CF_2018
lxterminal -e "./SHT20_sensor.py" &
lxterminal -e "./NTU_CF_YOLOv2.py" &