#!/usr/bin/python3
#pyinstaller.exe --clean --onefile --add-data "devcon.exe;." ser2osc.py
import json
import os
import sys
import serial
import time
import serial.tools.list_ports
from pynput.keyboard import Key, Controller
from pythonosc import udp_client
import subprocess

keyboard = Controller()
VERSION = "2050.05.21"
print(f"Version: {VERSION}")

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
            "useTimer" : False,
            "timer" : 120,
            "useOsc" : False,
            "oscServer" : "127.0.0.1",
            "oscPort" : 8010,
            "oscAddress" : "/serial",
            "arduinoDriver" : "USB\\VID_1A86&PID_7523"
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
    bundle_dir = sys._MEIPASS
else:
    cwd = os.path.dirname(this_file)
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

print("Current working directory:", cwd)

# Read Config File
settingsFile = os.path.join(cwd, "config.json")
config = readConfig(settingsFile)
baudrate = config["baudrate"]
uart = config["uart"]
keyPress = config["keyPress"]
useTimer = bool(config["useTimer"])
timer = config["timer"]
numBtns = config["numBtns"]
oscServer = config["oscServer"]
oscPort = config["oscPort"]
oscAddress = config["oscAddress"]
useOsc = bool(config["useOsc"])
arduinoDriver = config["arduinoDriver"]

if useOsc:
    # Set up the OSC client
    oscClient = udp_client.SimpleUDPClient(oscServer, oscPort)

# setup Seiral
noSerial = True
while noSerial:
    try:
        if uart == "auto":
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if "USB" in p.description:
                    uart = p.device
        print(f"Using port: {uart}")
        
        ser = serial.Serial(
            port=uart,
            baudrate=baudrate,
            timeout=1
        )
        noSerial = False
        uartOn = True
        ser.flush()
    except serial.SerialException as e:
        #print("An exception occurred:", e)
        if "PermissionError" in str(e):
            print("PermissionError")
            print("Restart arduino driver")
            print(f"Using driver: {arduinoDriver}")
            devconFile = os.path.join(bundle_dir, "devcon.exe")
            subprocess.run([devconFile, "disable", arduinoDriver])
            subprocess.run([devconFile, "enable", arduinoDriver])
        else:
            print("An unexpected serial error occurred.")
    except Exception as error:
        print("An unexpected error occurred:", error)

#Setup list to hold LED states
try:
    while uartOn:
        x=ser.readline().strip().decode()
        #print(x)
        if x.isnumeric():
            xInt = int(x)
            print(keyPress[xInt])
            keyboard.press(keyPress[xInt])
            keyboard.release(keyPress[xInt])
            if useOsc:
                oscClient.send_message(oscAddress, keyPress[xInt])

except KeyboardInterrupt:
    ser.close()
