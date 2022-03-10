import shutil
import os
import re
from collections import Counter

import prov.model as prov
from prov.dot import prov_to_dot
from provdbconnector import ProvDb, Neo4jAdapter

NEO4J_USER = 'neo4j'
NEO4J_PASS = os.environ.get('NEO4J_PASSWORD', 'test')
NEO4J_HOST = os.environ.get('NEO4J_HOST', 'localhost')
NEO4J_BOLT_PORT = os.environ.get('NEO4J_BOLT_PORT', '7687')

# Auth info
auth_info = {"user_name": NEO4J_USER,
             "user_password": NEO4J_PASS,
             "host": NEO4J_HOST + ":" + NEO4J_BOLT_PORT
             }

# create the api
prov_api = ProvDb(adapter=Neo4jAdapter, auth_info=auth_info)

def parsed_action(action, event_type):
    words = action.split(" ")
    item = words[1].strip("\'() ")
    match event_type:
        case "ItemStateChangedEvent":
            return {
                "Item": item,
                "From": words[4],
                "To": words[6]
            }
        case "ItemCommandEvent":
            return {
                "Item": item,
                "Value": words[4],
            }
    return {"Text": action}


def logged_events(file_path="/Users/declanshafi/openhab/userdata/logs/events.log"):
    shutil.copyfile(file_path, "./events.log")

    with open("./events.log", "r") as events:
        lines = events.readlines()

    return [{"time": event[0:23],
             "type": event[33:70].split(' ')[0].split(']')[0].split('.')[2],
             "action": parsed_action(event[73:-1], event[33:70].split(' ')[0].split(']')[0].split('.')[2])}
            for event in lines]


def sequence_last_n(outflow, n=3):
    position = outflow["position"]
    bottom = max(position - n, 0)
    return bottom, position


def data_flows(events, last_n_determiner):
    inflows_count = 0
    inflows = []
    outflows = []

    for i in range(len(events)):
        event = events[i]
        match event["type"]:
            case "ItemCommandEvent":
                outflows.append({"event": event, "position": inflows_count})
            case "ItemStateChangedEvent":
                inflows.append(event)
                inflows_count += 1

    # Get last n inflows for each outflow
    for outflow in outflows:
        bottom, top = last_n_determiner(outflow)
        outflow["last_n"] = inflows[bottom:top]

    return inflows, outflows


def unique_items(inflows, outflows):
    outflow_items = set()
    inflow_items = set()

    # Get unique outflow items
    for outflow in outflows:
        item = outflow["event"]["action"]["Item"]
        outflow_items.add(item)

    # Get unique inflow items
    for inflow in inflows:
        item = inflow["action"]["Item"]
        inflow_items.add(item)

    return inflow_items, outflow_items


def preceding_probabilities(inflows, outflows, n):
    inflow_items, outflow_items = unique_items(inflows, outflows)
    items_frequencies = {outflow: {inflow: 0 for inflow in inflow_items} for outflow in outflow_items}

    # Count frequencies
    for outflow in outflows:
        outflow_item = outflow["event"]["action"]["Item"]
        last_n = outflow["last_n"]
        last_n_items = list(entry["action"]["Item"] for entry in last_n)
        for i, inflow_item in enumerate(last_n_items):
            items_frequencies[outflow_item][inflow_item] += n + 1 - i

    # get prob table
    items_probs = {}

    for outflow_item in outflow_items:
        total = sum(items_frequencies[outflow_item].values())
        items_probs[outflow_item] = {inflow_item: items_frequencies[outflow_item][inflow_item] / total
                                     for inflow_item in inflow_items}

    return items_probs


def allowed_items(probs, boundary):
    return {
        outflow_item: set(inflow_item for inflow_item, p in probs[outflow_item].items() if p > boundary)
        for outflow_item in probs
    }


# Produce provenance graph
def infer_provenance(events, probs, boundary, document):
    _, outflows = data_flows(events, sequence_last_n)
    allowed = allowed_items(probs, boundary)
    entities = set()

    print(outflows)
    # print(allowed)

    for outflow in outflows:
        if outflow["event"]["action"]["Item"] == "ProvRuleNotification":
            continue
        activity = document.activity(
            f'Send {outflow["event"]["action"]["Value"]} to {outflow["event"]["action"]["Item"]} at {outflow["event"]["time"]}')
        activity.wasAssociatedWith(outflow["event"]["action"]["Item"])
        used = []
        inflows = outflow["last_n"]
        # print(inflows)
        # print(outflow)
        for inflow in inflows:
            if inflow["action"]["Item"] in allowed[outflow["event"]["action"]["Item"]]:
                used.append(inflow)

        for entry in used:
            entity_name = f'Reading from {entry["action"]["Item"]} at {entry["time"]}'
            if entity_name not in entities:
                entity = document.entity(entity_name, other_attributes=entry["action"])
                entity.wasAttributedTo(entry["action"]["Item"])
                entities.add(entity_name)
            activity.used(entity_name)


def create_prov_graph():
    document = prov.ProvDocument()
    document.set_default_namespace('')

    events = logged_events()
    inflows, outflows = data_flows(events, sequence_last_n)
    probs = preceding_probabilities(inflows, outflows, 5)

    agents_in, agents_out = unique_items(inflows, outflows)

    agents = agents_in.union(agents_out)

    print(agents)
    for agent in agents:
        document.agent(agent)

    infer_provenance(events, probs, 0.2, document)

    print(probs)

    dot = prov_to_dot(document)
    dot.write_png("reconstructed.png")

    document_id = prov_api.save_document(document)


if __name__ == '__main__':
    create_prov_graph()
