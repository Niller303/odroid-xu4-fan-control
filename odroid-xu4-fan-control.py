#!/usr/bin/python

# Loud fan control script to lower speed of fan based on current
# max temperature of any cpu
#
# See README.md for details.

import os
import sys
import time
import subprocess

#set to false to suppress logs
DEBUG=False

if (os.geteuid() != 0):
	sys.exit(1, "This script must be run as root!")

TEMPERATURE_FILE="/sys/devices/virtual/thermal/thermal_zone0/temp"
FAN_MODE_FILE="/sys/devices/platform/pwm-fan/hwmon/hwmon0/automatic"
FAN_SPEED_FILE="/sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1"
TEST_EVERY=1 #seconds

if (not os.path.isfile(TEMPERATURE_FILE)):
	sys.exit(1, "Failed to find temperature file!")
if (not os.path.isfile(FAN_MODE_FILE)):
	sys.exit(1, "Failed to find fan mode file!")
if (not os.path.isfile(FAN_SPEED_FILE)):
	sys.exit(1, "Failed to find fan speed file!")

current_max_temp=subprocess.getoutput("cat %s | cut -d: -f2 | sort -nr | head -1" % (TEMPERATURE_FILE))
print("fan control started. Current max temp: %s" % (current_max_temp))

while (True):
	os.system("echo 0 > %s" % (FAN_MODE_FILE))

	current_max_temp = subprocess.getoutput("cat %s | cut -d: -f2 | sort -nr | head -1" % (TEMPERATURE_FILE))

	if (DEBUG):
		print("event: read_max; temp: %d" % (current_max_temp))

	# 65=b+a^55;255=b+a^75
	new_fan_speed=int(8.194+pow(1.07621,(int(current_max_temp)/1000)))

	if (new_fan_speed > 255):
		new_fan_speed=255
	elif (new_fan_speed < 61): #Note here that around ~60 and under makes it go BEEP
		#note that exactly 60 makes it beep a small amount on fan spinup
		new_fan_speed=61

	if (DEBUG):
		print("event: adjust; speed: %d" % (new_fan_speed))
	
	os.system("echo %d > %s" % (new_fan_speed,FAN_SPEED_FILE))

	time.sleep(TEST_EVERY)
