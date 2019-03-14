#!/bin/sh

sudo pip install imutils
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install python3-dev libmysqlclient-dev
sudo pip3 install mysqlclient
sudo pip3 install sensor
python3 bgget.py
python3 NTU_CF_YOLOv1.py
