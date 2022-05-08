import random
import threading
from time import sleep
from enum import Enum
import numpy as np

from paho.mqtt import client as mqtt_client
from threading import Thread
from Simulation.simulation_utilities import connect_mqtt, publish

NL = "sim1/NL"
PS = "sim1/PS"
SAS = "sim1/SAS"

phone_status = "DISENGAGED"
known_sa_state = "OFF"

log_file = "./Data/assistant.log"
with open(log_file, "w"):
    pass


def noise_level():
    if phone_status == "ENGAGED":
        return np.random.normal(20, 5)
    else:
        return np.random.normal(5, 10)


def subscribe_assistant(client: mqtt_client, msg):
    if msg == "ON":
        p = 0.1 if phone_status == "ENGAGED" else 0.9
        remember_on = np.random.choice([True, False], p=[p, 1-p])
        if remember_on:
            global known_sa_state
            known_sa_state = "ON"


def subscribe_phone(client: mqtt_client, msg):
    global phone_status
    phone_status = msg


def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == PS:
            subscribe_phone(client, msg.payload.decode())
        elif msg.topic == SAS:
            subscribe_assistant(client, msg.payload.decode())

    client.subscribe(PS)
    client.subscribe(SAS)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

    global phone_status
    while True:
        if phone_status == "ENGAGED":
            end = np.random.choice([True, False], p=[0.1, 0.9])
            if end:
                phone_status = "DISENGAGED"
                publish(client, PS, phone_status, log_file=log_file)

        else:
            engaged = np.random.choice([True, False], p=[0.15, 0.85])
            if engaged:
                phone_status = "ENGAGED"
                publish(client, PS, phone_status, log_file=log_file)

            publish_noise = np.random.choice([True, False], p=[0.1, 0.9])
            if publish_noise:
                publish(client, NL, str(noise_level()), log_file=log_file)

            global known_sa_state
            if known_sa_state == "OFF":
                activate_sa = np.random.choice([True, False], p=[0.05, 0.95])
                if activate_sa:
                    publish(client, SAS, "ON", log_file=log_file)
                    known_sa_state = "ON"
            elif known_sa_state == "ON":
                stop_sa = np.random.choice([True, False], p=[0.5, 0.5])
                if stop_sa:
                    publish(client, SAS, "OFF", log_file=log_file)
                    known_sa_state = "OFF"
            sleep(1)


if __name__ == '__main__':
    run()
