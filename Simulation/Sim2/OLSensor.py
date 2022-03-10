# python3.6

import random

from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 8080
topic = "openhab/sim2/OutsideLight"
topic2 = "openhab/sim2/SecretLight"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'oh.Prov.WLfzbVdEwCFyoFHPnTJzJTBSeZbaqNfOrsov28o8sutbUrcdzMe2Zq8WNgYOmG18aJmj8bOjeppfFi49NvnppA'
password = ''


def connect_mqtt() -> mqtt_client:
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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg == "REQUEST":
            publish(client, topic)

    client.subscribe(topic)
    client.on_message = on_message


def publish(client, topic):
    level = random.choice([0, 20])
    msg = f"{level}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()