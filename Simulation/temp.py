import random
import threading
from time import sleep
from enum import Enum

from simulation_utilities import connect_mqtt, publish
from paho.mqtt import client as mqtt_client
from threading import Thread

ITL = "sim1/ITL"
WS = "sim1/WS"
RL = "sim1/RL"
RD = "sim1/RD"

radiator_level = 0
ambient_temp = 20
window_state = "OPEN"
radiator_dial = "NEUTRAL"

log_file = "./Data/temp.log"
with open(log_file, "w"):
    pass


def temp():
    if window_state == "OPEN":
        return (radiator_level + ambient_temp) / 2
    elif window_state == "CLOSED":
        return (radiator_level + 0.5 * ambient_temp) / 1.5


def subscribe_window(client: mqtt_client, msg):
    global window_state
    # Adjust light state and il_level (but not yet published!)
    window_state = msg


def subscribe_dial(client: mqtt_client, msg):
    global radiator_dial
    # Adjust light state and il_level (but not yet published!)
    radiator_dial = msg


def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == WS:
            subscribe_window(client, msg.payload.decode())
        elif msg.topic == RD:
            subscribe_dial(client, msg.payload.decode())

    client.subscribe(WS)
    client.subscribe(RD)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

    publish(client, RD, "NEUTRAL", log_file=log_file)

    global ambient_temp, radiator_level
    while True:
        change_ambient_temp = random.choice([0, 5, -5])
        ambient_temp += change_ambient_temp
        if ambient_temp < 0:
            ambient_temp = 0

        if ambient_temp > 40:
            ambient_temp = 40

        publish_itl = random.choices([True, False], weights=(20, 80))[0]
        itl = temp()

        if itl > 30 and radiator_dial != "DECREASE":
            publish(client, RD, "DECREASE", log_file=log_file)

        if publish_itl:
            publish(client, ITL, str(itl), log_file=log_file)

        if radiator_dial == "INCREASE":
            radiator_level += 1
        elif radiator_dial == "DECREASE":
            radiator_level -= 1

        sleep(1)


if __name__ == '__main__':
    run()
