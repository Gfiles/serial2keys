#!/usr/bin/python3
import json
import os
import sys
import serial
import time
import serial.tools.list_ports
from pynput.keyboard import Key, Controller

keyboard = Controller()

def readConfig(settingsFile):
    if os.path.isfile(settingsFile):
        with open(settingsFile) as json_file:
            data = json.load(json_file)
    else:
        data = {
            "uart" : "auto",
	        "baudrate" : 9600,
	        "keyPress" : "abcdefghijklmnopqrstuvwxyz",
            "numBtns" : 1,
            "useTimer" : 1,
            "timer" : 120
        }
        # Serializing json
        json_object = json.dumps(data, indent=4)
 
        # Writing to config.json
        with open(settingsFile, "w") as outfile:
            outfile.write(json_object)
    return data

# Get the current working
# directory (CWD)
try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
if getattr(sys, 'frozen', False):
    cwd = os.path.dirname(sys.executable)
else:
    cwd = os.path.dirname(this_file)

print("Current working directory:", cwd)

# Read Config File
settingsFile = os.path.join(cwd, "config.json")
config = readConfig()
baudrate = config["baudrate"]
uart = config["uart"]
keyPress = config["keyPress"]
useTimer = config["useTimer"]
timer = config["timer"]
numBtns = config["numBtns"]

# setup Seiral
if uart == "auto":
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB" in p.description:
            uart = p.device

ser = serial.Serial(
        # Serial Port to read the data from
        port = uart,
        #Rate at which the information is shared to the communication channel
        baudrate = baudrate,
        # Number of serial commands to accept before timing out
        timeout=1
)
#Setup list to hold LED states
ledState = []
timers = []
for i in range(numBtns):
    ledState.append(1)
    timers.append(0)

btnOn = "1"
btnOff = "0"

try:
    while 1:
        x=ser.readline().strip().decode()
        #print(x)
        if x.isnumeric():
            xInt = int(x)
            keyboard.press(keyPress[xInt])
            keyboard.release(keyPress[xInt])
            if useTimer:
                ledState[xInt] = 0
                msg = f"{xInt}{btnOff}"
                ser.write(msg.encode('utf-8'))
                timers[xInt] = time.time()
        if useTimer:
            for i in range(numBtns):
                if ledState[i] == 0:
                    if time.time() - timers[i] > timer:
                        ledState[i] = 1
                        msg = f"{i}{btnOn}"
                        ser.write(msg.encode('utf-8'))

except KeyboardInterrupt:
    pass
