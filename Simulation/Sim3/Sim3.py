import random
from time import sleep

from paho.mqtt import client as mqtt_client
from threading import Thread

light = "openhab/sim2/Light"
blind = "openhab/sim2/Blind"
ol_sensor = "openhab/sim2/OutsideLight"
il_sensor = "openhab/sim2/InsideLight"

client_id = f'python-mqtt-{random.randint(0, 100)}'
broker = 'localhost'
port = 1883
# generate client ID with pub prefix randomly
username = 'emqx'
password = 'public'

ol_level = 20
il_level = 0
blind_status = "CLOSED"


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


def subscribe_light(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(light)
    client.on_message = on_message


def subscribe_blind(client: mqtt_client):
    def on_message(client, userdata, msg):
        global blind_status
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        blind_status = msg
        publish_il()

    client.subscribe(light)
    client.on_message = on_message


def subscribe_ol(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg == "REQUEST":
            publish_ol(client)

    client.subscribe(ol_sensor)
    client.on_message = on_message


def publish_ol(client):
    msg = f"{ol_level}"
    result = client.publish(ol_sensor, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{ol_sensor}`")
    else:
        print(f"Failed to send message to topic {ol_sensor}")


def subscribe_il(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg == "REQUEST":
            publish_il(client)

    client.subscribe(il_sensor)
    client.on_message = on_message


def publish_il(client):
    print(blind_status)
    print(il_level)
    print(ol_level)
    if blind_status == "CLOSED":
        level = il_level
    else:
        level = ol_level + il_level

    msg = f"{level}"
    result = client.publish(il_sensor, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{il_sensor}`")
    else:
        print(f"Failed to send message to topic {il_sensor}")


def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.payload.decode() == "REQUEST":
            if msg.topic == il_sensor:
                print("Publishing inside light")
                publish_il(client)
            else:
                print("Publishing outside light")
                publish_ol(client)
        elif msg.topic == blind:
            global blind_status
            blind_status = msg.payload.decode()
            publish_il(client)
            print(f"Updating blind status to {blind_status}")
        elif msg.topic == light:
            global il_level
            if msg.payload.decode() == "ON":
                il_level = 10
            else:
                il_level = 0

            print(f"Updating inside light level to {il_level}")

    client.subscribe(il_sensor)
    client.subscribe(ol_sensor)
    client.subscribe(light)
    client.subscribe(blind)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

    global ol_level
    while True:
        ol_level = random.choice([0, 20])
        publish_ol(client)
        sleep(1)
        print(ol_level)

if __name__ == '__main__':
    run()
