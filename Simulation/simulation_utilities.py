import random
from datetime import datetime
from paho.mqtt import client as mqtt_client

client_id = f'python-mqtt-{random.randint(0, 100)}'
broker = 'localhost'
port = 1883


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client: mqtt_client, topic: str, msg: str, log_file=None):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        if log_file is not None:
            with open(log_file, 'a') as f:
                f.write(f"At {datetime.now()} sent {msg} to topic {topic}\n")
    else:
        print(status)
        print(f"Failed to send message to topic {topic}")
