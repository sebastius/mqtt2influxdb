#!/usr/bin/env python3
# based on https://gist.github.com/LarsBergqvist/5f3d5a738220a242d35f1113dbc6a277
import paho.mqtt.client as mqtt
import datetime
import time
from influxdb import InfluxDBClient

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("#")
    
def on_message(client, userdata, msg):
    print("Received a message on topic: " + msg.topic)
    # Use utc as timestamp
    receiveTime=datetime.datetime.utcnow()
    message=msg.payload.decode("utf-8")
    isfloatValue=False

    # Hack to convert open/closed state to 1/0
    if msg.topic == "hackalot/state":
        message = 1 if message == "open" else 0

    try:
        # Convert the string to a float so that it is stored as a number and not a string in the database
        gespleten = message.split(' ')
        
        val = float(gespleten[0])
        
        isfloatValue=True
    except:
        isfloatValue=False

    if isfloatValue:
        print(str(receiveTime) + ": " + msg.topic + " " + str(val))

        json_body = [
            {
                "measurement": msg.topic,
                "time": receiveTime,
                "fields": {
                    "value": val
                }
            }
        ]

        dbclient.write_points(json_body)
        print("Finished writing to InfluxDB")
    else:
        json_body = [
            {
                "measurement": msg.topic,
                "time": receiveTime,
                "fields": {
                    "value": message
                },
                "tags": {
                   "MQTTtext": message
                }
            }
        ]
        
        dbclient.write_points(json_body)
        print("Finished writing non float data to InfluxDB")

        
# Set up a client for InfluxDB
dbclient = InfluxDBClient('localhost', 8086, 'telegrafuser', 'wachtwoord', 'telegraf')

# Initialize the MQTT client that should connect to the Mosquitto broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
connOK=False
while(connOK == False):
    try:
        client.connect("localhost", 1883, 60)
        connOK = True
    except:
        connOK = False
        print("Not connected to MQTT")
    time.sleep(2)

# Blocking loop to the Mosquitto broker
client.loop_forever()
