#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import requests
# Set the LED PIN
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)

deviceId = "DQKt4PnX"
deviceKey = "w4udKAwnBiuY4030"

# Set MediaTek Cloud Sandbox (MCS) Connection
def get_to_mcs():
	host = "http://api.mediatek.com"
	endpoint = "/mcs/v2/devices/" + deviceId + "/datachannels/LEDControl/datapoints"
	url = host + endpoint
	headers = {"Content-type": "application/json", "deviceKey": deviceKey}
	r = requests.get(url,headers=headers)
	value = (r.json()["dataChannels"][0]["dataPoints"][0]["values"]["value"])
	return value

# Receive the Data from MCS
while(True):
	if(get_to_mcs()==1):
		print("LED turning on.")
		LEDon = GPIO.output(17,1)
		time.sleep(0.5)
	if(get_to_mcs()==0):
		print("LED turning off.")
		LEDoff = GPIO.output(17,0)
		time.sleep(0.5)