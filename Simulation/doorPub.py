# python 3.6

import random
import time
from datetime import datetime

from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 1883
topic = "sim1/door"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publishDoor(client):
    position = "OPEN"
    while True:
        #msg = f"{{position: {position}, time: {datetime.now()}}}"
        msg = f"{random.choice(['OPEN', 'CLOSED'])}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

        if random.random() < 0.5:
            position = "CLOSED"
        else:
            position = "CLOSED"

        time.sleep(15)

def run():
    client = connect_mqtt()
    client.loop_start()
    publishDoor(client)


if __name__ == '__main__':
    run()
