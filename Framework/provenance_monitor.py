import threading
from datetime import datetime
import requests

import prov.model as prov
from prov.dot import prov_to_dot

from mqtt import _MQTT
from link_neo4j import save_document

document = prov.ProvDocument()

class ProvenanceMonitor:
    def __init__(self):
        self.token = "oh.Monitor.LtfJqewJBMHQzgz0bLRX8goIYRdtBYmNHHIWRJFsqGVUhm7BxIBSqR17FGpSKeDD2Y75fhd4uVnmKgX0MyQ"
        self.rulesURL = "http://localhost:8080/rest/rules"
        self.itemsURL = "http://localhost:8080/rest/items"

        headers = {'accept': 'application/json'}
        self.rules = requests.get(self.rulesURL, headers=headers, auth=(self.token, '')).json()
        self.items = requests.get(self.itemsURL, headers=headers, auth=(self.token, '')).json()

        print(self.rules)
        print(self.items)
        document.set_default_namespace('')
        self.entities = set()

        self.agents = {item["name"]: document.agent(item['name']) for item in self.items}

    def _get_state(self, item: str):
        url = f"http://localhost:8080/rest/items/{item}/state"
        headers = {'accept': 'text/plain'}
        state = requests.get(url, headers=headers, auth=(self.token, ''))
        return state.text

    def draw_prov(self, file_name):
        dot = prov_to_dot(document)
        dot.write_png(file_name + ".png")

    def _on_message(self, client, userdata, msg):
        pass


class DirectedProvenanceMonitor(ProvenanceMonitor):
    def __init__(self):
        super().__init__()
        # Find prov-enabled commands
        self.commands = []
        for rule in self.rules:
            for action in rule["actions"]:
                if action["configuration"]["itemName"] == "ProvRuleNotification":
                    self.commands.append(action["configuration"]["command"])

        # Match commands with their rules
        self.rule_matches = {}
        for i in range(len(self.commands)):
            self.rule_matches[self.commands[i]] = self.rules[i]

        print(self.rule_matches)

        _MQTT(self._on_message)

    def _used_prov(self, items, rule_activity, item_states):
        for i, item in enumerate(items):
            attributes = {}
            item_name = item["configuration"]["itemName"]
            entity_name = f'{item_name} at {self.caught_time}'

            match item["type"]:
                case "core.ItemStateChangeTrigger":
                    attributes = item["configuration"]
                    attributes["observedState"] = item_states[i]
                    attributes["type"] = item["type"]
                case "core.ItemStateCondition":
                    attributes = item["configuration"]
                    attributes["observedState"] = item_states[i]
                    attributes["type"] = item["type"]

            # Sometimes we will be using the same item more than once, so should only create one entity in this case
            if entity_name not in self.entities:
                entity = document.entity(entity_name, other_attributes=attributes)
                self.entities.add(entity_name)
                entity.wasAttributedTo(item_name)

            rule_activity.used(entity_name)

    def _actions_prov(self, actions, rule_activity):
        for action in actions:
            item_associated_with = action["configuration"]["itemName"]
            if item_associated_with == "ProvRuleNotification":
                continue
            attributes = {}
            match action["type"]:
                case "core.ItemCommandAction":
                    command = action["configuration"]["command"]
                    attributes = {"command": command, "type": action["type"]}

            rule_activity.wasAssociatedWith(item_associated_with, attributes=attributes)

    def _on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        rule = self.rule_matches[message]

        triggers = rule["triggers"]
        conditions = rule["conditions"]
        actions = rule["actions"]

        # get current states of the items asap
        trigger_item_states = [self._get_state(trigger["configuration"]["itemName"]) for trigger in triggers]
        condition_item_states = [self._get_state(condition["configuration"]["itemName"]) for condition in conditions]

        self.caught_time = datetime.now()

        # NO MORE API CALLS PAST THIS POINT
        rule_activity = document.activity(f'{message} at {self.caught_time}')

        # add provenance
        self._used_prov(triggers, rule_activity, trigger_item_states)
        self._used_prov(conditions, rule_activity, condition_item_states)
        self._actions_prov(actions, rule_activity)

        self.draw_prov("monitored")


if __name__ == '__main__':
    prov_thread = threading.Thread(target=DirectedProvenanceMonitor)
    prov_thread.start()

    while True:
        print("Type anything to save PROV to Neo4J")
        input()
        print(document.get_provn())
        save_document(document)

