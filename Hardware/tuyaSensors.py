import logging
import json
from tuya_connector import (
    TUYA_LOGGER,
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
)
import Simulation.simulation_utilities as su

ACCESS_ID = "tjdpt9t3bkgqymek0wgo"
ACCESS_KEY = "37b2391a3d1c49cc916056186bae518d"
API_ENDPOINT = "https://openapi.tuyaeu.com"
MQ_ENDPOINT = "wss://mqe.tuyaeu.com:8285/"

TUYA_LOGGER.setLevel(logging.DEBUG)

# Init Message Queue
open_pulsar = TuyaOpenPulsar(
    ACCESS_ID, ACCESS_KEY, MQ_ENDPOINT, TuyaCloudPulsarTopic.PROD
)

topic1 = "tuya/door_sensor_1"
devId1 = "05036145e098061f6062"
topic2 = "tuya/door_sensor_2"
devId2 = "0503614524a16027b455"


def handle_msg(msg):
    client = su.connect_mqtt()

    print("Received message!")
    data = json.loads(msg)
    # print(data)
    if 'status' in data and data['status'][0]['code'] == "doorcontact_state":
        value = data['status'][0]['value']
        if data['devId'] == devId1:
            su.publish(client, topic1, value)
        elif data['devId'] == devId2:
            su.publish(client, topic2, value)


# Add Message Queue listener
open_pulsar.add_message_listener(handle_msg)

# Start Message Queue
open_pulsar.start()

input()
# Stop Message Queue
open_pulsar.stop()
