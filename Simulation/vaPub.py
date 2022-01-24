# python 3.6

import random
import time
from datetime import datetime

from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 1883
topic = "sim1/voice"
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

def publishSensor(client):
    level = 20
    while True:
        #msg = f"{{req: {random.choice(['turnon', 'turnoff'])}, time: {datetime.now()}}}"
        msg = f"{random.choice(['ON', 'OFF'])}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

        change = random.randint(-5, 5)
        level += change

        time.sleep(60)


def run():
    client = connect_mqtt()
    client.loop_start()
    publishSensor(client)


if __name__ == '__main__':
    run()
