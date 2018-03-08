#!/bin/sh

sudo pip install imutils
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install python-opencv
sudo apt-get -y install python-mysqldb
python NTU_CF_ver4.py
