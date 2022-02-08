import requests

import prov.model as prov
from prov.dot import prov_to_dot

from mqtt import _MQTT


class ProvenanceMonitor:
    def __init__(self):
        self.token = "oh.Prov.WLfzbVdEwCFyoFHPnTJzJTBSeZbaqNfOrsov28o8sutbUrcdzMe2Zq8WNgYOmG18aJmj8bOjeppfFi49NvnppA"
        self.rulesURL = "http://localhost:8080/rest/rules"
        self.itemsURL = "http://localhost:8080/rest/items"

        headers = {'accept': 'application/json'}
        self.rules = requests.get(self.rulesURL, headers=headers, auth=(self.token, '')).json()
        self.items = requests.get(self.itemsURL, headers=headers, auth=(self.token, '')).json()

        self.document = prov.ProvDocument()
        self.document.set_default_namespace('')

        self.agents = {item["name"]: self.document.agent(item['name']) for item in self.items}

    def _get_state(self, item: str):
        url = f"http://localhost:8080/rest/items/{item}/state"
        headers = {'accept': 'text/plain'}
        state = requests.get(url, headers=headers, auth=(self.token, ''))
        return state.text

    def draw_prov(self, file_name):
        dot = prov_to_dot(self.document)
        dot.write_png(file_name + ".png")

    def _on_message(self, client, userdata, msg):
        pass


class DirectedProvenanceMonitor(ProvenanceMonitor):
    def __init__(self):
        super().__init__()
        self.commands = []
        for rule in self.rules:
            for action in rule["actions"]:
                if action["configuration"]["itemName"] == "ProvRuleNotification":
                    self.commands.append(action["configuration"]["command"])

        self.rule_matches = {}
        for i in range(len(self.commands)):
            self.rule_matches[self.commands[i]] = (self.rules[i], 0)

        _MQTT(self._on_message)

    @staticmethod
    def _triggers_prov(self, triggers, rule_activity, trigger_item_states):
        print("Processing rule triggers")
        for i, trigger in enumerate(triggers):
            attributes = {}
            match trigger["type"]:
                case "core.ItemStateChangeTrigger":
                    attributes = trigger["configuration"]
                    attributes["observedState"] = trigger_item_states[i]
                    attributes["type"] = trigger["type"]

            rule_activity.used(trigger["configuration"]["itemName"], attributes=attributes)

    @staticmethod
    def _conditions_prov(self, conditions, rule_activity, condition_item_states):
        print("Processing conditions triggers")
        for i, condition in enumerate(conditions):
            attributes = {}
            match condition["type"]:
                case "core.ItemStateCondition":
                    attributes = condition["configuration"]
                    attributes["observedState"] = condition_item_states[i]
                    attributes["type"] = condition["type"]

            rule_activity.used(condition["configuration"]["itemName"], attributes=attributes)

    @staticmethod
    def _actions_prov(self, actions, rule_activity):
        for action in actions:
            item_associated_with = action["configuration"]["itemName"]
            attributes = {}
            match action["type"]:
                case "core.ItemCommandAction":
                    command = action["configuration"]["command"]
                    attributes = {"command": command, "type": action["type"]}

            rule_activity.wasAssociatedWith(item_associated_with, attributes=attributes)

    def _on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        rule = self.rule_matches[message][0]

        triggers = rule["triggers"]
        conditions = rule["conditions"]
        actions = rule["actions"]

        # get current states of the items asap
        trigger_item_states = [self._get_state(trigger["configuration"]["itemName"]) for trigger in triggers]
        condition_item_states = [self._get_state(condition["configuration"]["itemName"]) for condition in conditions]

        # NO MORE API CALLS PAST THIS POINT
        rule_activity = self.document.activity(message)

        # add provenance
        self._triggers_prov(triggers, rule_activity, trigger_item_states)
        self._conditions_prov(conditions, rule_activity, condition_item_states)
        self._actions_prov(actions, rule_activity)

        self.draw_prov("hope")


if __name__ == '__main__':
    directed_provenance_monitor = DirectedProvenanceMonitor()
