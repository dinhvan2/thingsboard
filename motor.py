import serial.tools.list_ports
import paho.mqtt.client as mqttclient
import time
import json
import random

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "qmxrjQH0sbbjF9fdLUWb"



def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

autoMode = 0
def recv_message(client, userdata, message):
    # print("Received: ", message.payload.decode("utf-8"))
    print("Received: ", json.loads(message.payload)['shared'])
    cmd = 0
    try:
        jsonobj = json.loads(message.payload)['shared']
        if jsonobj['Fan_1'] == "1" :
            cmd = 0
            print(cmd)
            print(ser.write((str(cmd)).encode()))
        elif jsonobj['Fan_1'] == "0" :
            cmd = 1
            print(cmd)
            print(ser.write((str(cmd)).encode()))
        if jsonobj['Fan_2'] == "1":
            cmd = 2
            print(cmd)
            print(ser.write((str(cmd)).encode()))
        elif jsonobj['Fan_2'] == "0":
            cmd = 3
            print(cmd)
            ser.write((str(cmd)).encode())
        elif jsonobj['Led_1'] == "1":
            cmd = 4
            print(cmd)
            ser.write((str(cmd)).encode())
        elif jsonobj['Led_1'] == "0":
            cmd = 5
            print(cmd)
            ser.write((str(cmd)).encode())
        elif jsonobj['Led_2'] == "1":
            cmd = 6
            print(cmd)
            ser.write((str(cmd)).encode())
        elif jsonobj['Led_2'] == "0":
            cmd = 7
            print(cmd)
            ser.write((str(cmd)).encode())
            
    except:
        pass
    if isMicrobitConnected:
         ser.write((str(cmd)).encode())


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        # client.subscribe("v1/devices/me/rpc/request/+")
        client.subscribe("v1/devices/me/rpc/response/1")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message


def getPort():
    ports = serial.tools.list_ports.comports()
    print(ports)
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print(strPort)
        if "USB-SERIAL CH340" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
            print(commPort)
    return commPort


isMicrobitConnected = False
if getPort() != "None":
    ser = serial.Serial( port=getPort(), baudrate=115200)
    isMicrobitConnected = True

# mess = ""
entry_dict = {
    "temperature": "",
    "humidity": "",
}
methodSensor = {
    "Fan_1": "",
    "Fan_2": "",
    "Led_1":"",
    "Led_2":""
}


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    entry_dict["temperature"] = splitData[0]
    entry_dict["humidity"] = splitData[1]
    print(type(entry_dict["humidity"]))
    print(json.dumps(entry_dict))
    # Automatic in gateway
    client.publish("v1/devices/me/telemetry", json.dumps(entry_dict))
    if autoMode == 1:
        if  float(entry_dict["humidity"]) < 60:
            methodSensor["method"] = "setFan"
            methodSensor["params"] = "On"
            client.publish("v1/devices/me/attributes", json.dumps(methodSensor),1)
        if  float(entry_dict["humidity"]) > 80:
            methodSensor["method"] = "setFan"
            methodSensor["params"] = "Off"
            client.publish("v1/devices/me/attributes", json.dumps(methodSensor),1)
        if  float(entry_dict["temperature"]) > 30:
            methodSensor["method"] = "setAir"
            methodSensor["params"] = "On"
            client.publish("v1/devices/me/attributes", json.dumps(methodSensor),1)
        if  float(entry_dict["temperature"]) < 20:
            methodSensor["method"] = "setAir"
            methodSensor["params"] = "Off"
            client.publish("v1/devices/me/attributes", json.dumps(methodSensor),1)
        

mess = ""
def readSerial():
    print("hello")
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""   
            else:
                mess = mess[end+1:]


while True:
    if isMicrobitConnected:
        print("Yolobit access is accepted!")
        readSerial()
    client.publish('v1/devices/me/attributes/request/1', '{"sharedKeys":"Fan_1,Fan_2,Led_1,Led_2"}')
    time.sleep(1)
    
