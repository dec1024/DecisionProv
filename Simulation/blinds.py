import random
import threading
from time import sleep
from enum import Enum

from simulation_utilities import connect_mqtt, publish
from paho.mqtt import client as mqtt_client
from threading import Thread


class Switch(Enum):
    OFF = 0
    ON = 1
    NEUTRAL = 2


OLL = "sim1/OLL"
BS = "sim1/BS"
ILL = "sim1/ILL"
LS = "sim1/LS"
LSS = "sim1/LSS"

ol_level = random.randint(0, 20)
blind_state = 0
bulb_brightness = 10
light_state = 1

log_file = "./Data/blinds.log"
with open(log_file, "w"):
    pass


def inside_light_level():
    return blind_state * ol_level + light_state * bulb_brightness


def subscribe_light(client: mqtt_client, msg):
    global light_state
    # Adjust light state and il_level (but not yet published!)
    if msg == "ON":
        light_state = 1
    else:
        light_state = 0

    if inside_light_level() < 18 and light_state == 0:
        publish(client, LSS, "ON", log_file=log_file)
        # After 5 secs reset light to neutral
        timer = threading.Timer(3.0, publish, args=(client, LSS, "NEUTRAL"), kwargs={"log_file": log_file})
        timer.start()


def subscribe_blind(client: mqtt_client, msg):
    global blind_state
    # Adjust light state and il_level (but not yet published!)
    if msg == "OPEN":
        blind_state = 1
    else:
        blind_state = 0


def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == LS:
            subscribe_light(client, msg.payload.decode())
        elif msg.topic == BS:
            subscribe_blind(client, msg.payload.decode())

    client.subscribe(LS)
    client.subscribe(BS)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
    publish(client, LSS, "NEUTRAL", log_file=log_file)

    global ol_level
    while True:
        change_ol_level = random.choice([True, False])
        if change_ol_level:
            ol_level = random.randint(0, 20)

        il_level = inside_light_level()

        publish_ol_level = random.choices([True, False], weights=(20, 80))[0]
        publish_il_level = random.choices([True, False], weights=(20, 80))[0]

        if publish_ol_level:
            publish(client, OLL, str(ol_level), log_file=log_file)

        if publish_il_level:
            publish(client, ILL, str(il_level), log_file=log_file)

        sleep(1)


if __name__ == '__main__':
    run()
