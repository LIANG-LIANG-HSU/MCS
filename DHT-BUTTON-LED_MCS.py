#!/usr/bin/python3
import sys
import Adafruit_DHT
import time
import sys
import http.client as http
import urllib
import json
import RPi.GPIO as GPIO
import requests

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17,GPIO.OUT)

# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
    print('Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
    sys.exit(1)

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

deviceId = "DQKt4PnX"
deviceKey = "w4udKAwnBiuY4030"
def post_to_mcs(payload):
	headers = {"Content-type": "application/json", "deviceKey": deviceKey}
	not_connected = 1
	while (not_connected):
            try:
                conn = http.HTTPConnection("api.mediatek.com:80")
                conn.connect()
                not_connected = 0
            except (http.HTTPException, socket.error) as ex:
                print ("Error: %s" % ex)
                time.sleep(10)
	conn.request("POST", "/mcs/v2/devices/" + deviceId + "/datapoints", json.dumps(payload), headers)
	response = conn.getresponse()
	#print( response.status, response.reason, json.dumps(payload), time.strftime("%c"))
	data = response.read()
	conn.close()

def get_to_mcs():
	host = "http://api.mediatek.com"
	endpoint = "/mcs/v2/devices/" + deviceId + "/datachannels/LEDControl/datapoints"
	url = host + endpoint
	headers = {"Content-type": "application/json", "deviceKey": deviceKey}
	r = requests.get(url,headers=headers)
	value = (r.json()["dataChannels"][0]["dataPoints"][0]["values"]["value"])
	return value

while True:
    SwitchStatus = GPIO.input(24)
    h0, t0= Adafruit_DHT.read_retry(sensor, pin)

    if(get_to_mcs()==1):
        print("LED turning on.")
        LEDon = GPIO.output(17,1)
        time.sleep(0.5)
    if(get_to_mcs()==0):
        print("LED turning off.")
        LEDoff = GPIO.output(17,0)
        time.sleep(0.5)

    if h0 is not None and t0 is not None:
        if(SwitchStatus == 0):
            print('Button pressed')
        else:
            print('Button repressed')

        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(t0, h0))
        print("")

        payload = {"datapoints":[{"dataChnId":"Humidity","values":{"value":h0}},
            {"dataChnId":"Temperature","values":{"value":t0}},
            {"dataChnId":"SwitchStatus","values":{"value":SwitchStatus}}]}
        post_to_mcs(payload)
        time.sleep(3)

    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)