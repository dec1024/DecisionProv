import random

from paho.mqtt import client as mqtt_client


class _MQTT:
    def __init__(self, on_message):
        self.broker = 'localhost'
        self.port = 1883
        self.topic = "PROV/Notify"
        # generate client ID with pub prefix randomly
        self.client_id = f'python-mqtt-{random.randint(0, 100)}'
        self.on_message = on_message
        client = self._connect()
        self._subscribe(client)
        client.loop_forever()

    def _connect(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def _subscribe(self, client: mqtt_client):
        client.subscribe(self.topic)
        client.on_message = self.on_message
