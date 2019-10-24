# CF_2018

Latest update - 20180307

Windows install MySQLdb for python
1. install git bash
2. download python2.7.14
3. add python th environmental path
4. install pip through get-pip.py
5. pip install mysqlclient==1.3.4

Mac install MySQLdb for python
1. install xcode
2. sudo pip install MySQL-python

After Node Installation
1. cd Adafruit_Python_BME280
2. git clone https://github.com/LisaTsai/CF_2018.git
3. cd CF_2018
4. sh setup.sh

Stop Autostart Programs
1. sudo nano /etc/rc.local
2. comment the python ~ line with #
3. sudo reboot
=> remember to uncomment after finished

Check SHT20
1. $i2cdetect -y 1
2. Remember to turn on I2C and turn off SPI in the preferences


[Notes]

rc.local can run script as unseenable background program
use $ps axOT to find the exact file and $kill code_of_program
