import random

from paho.mqtt import client as mqtt_client

light = "openhab/sim2/Light"
blind = "openhab/sim2/Blind"
ol_sensor = "openhab/sim2/OutsideLight"
il_sensor = "openhab/sim2/InsideLight"

broker = 'localhost'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

ol_level = 0
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


def subscribe_il(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        print(msg.payload.decode())
        if msg.payload.decode() == "REQUEST":
            print("Hi")
            publish_il(client)

    client.subscribe(il_sensor)
    client.on_message = on_message


def publish_il(client):
    il_level = random.choice([0, 10])
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


def run():
    client_il = connect_mqtt()
    subscribe_il(client_il)
    client_il.loop_forever()


if __name__ == '__main__':
    run()
