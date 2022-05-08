import shutil
import os
import re
import json
from collections import Counter

import prov.model as prov
from prov.dot import prov_to_dot

from link_neo4j import save_document
from prov.graph import prov_to_graph, graph_to_prov


def strip_reconstructor(original_path):
    with open(original_path, 'r') as f, open("events_stripped.log", "w") as stripped:
        for line in f:
            if not "ProvRuleNotification" in line:
                stripped.write(line)


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


def logged_events(file_path="../Events/events.log"):
    shutil.copyfile(file_path, "./events.log")
    strip_reconstructor("./events.log")

    with open("./events_stripped.log", "r") as events:
        lines = events.readlines()

    return [{"time": event[0:23],
             "type": event[33:70].split(' ')[0].split(']')[0].split('.')[2],
             "action": parsed_action(event[73:-1], event[33:70].split(' ')[0].split(']')[0].split('.')[2])}
            for event in lines]


def sequence_last_n(outflow, n):
    position = outflow["position"]
    bottom = max(position - n, 0)
    return bottom, position


def data_flows(events, last_n_determiner, n):
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
        bottom, top = last_n_determiner(outflow, n)
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
            score = n - i
            items_frequencies[outflow_item][inflow_item] += score

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
def infer_provenance(events, probs, boundary, document, n):
    _, outflows = data_flows(events, sequence_last_n, n)
    allowed = allowed_items(probs, boundary)
    entities = set()
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


def create_prov_graph(n=3):
    document = prov.ProvDocument()
    document.set_default_namespace('')

    events = logged_events()
    inflows, outflows = data_flows(events, sequence_last_n, n)
    probs = preceding_probabilities(inflows, outflows, n)
    with open("../Evaluation/data.json", "w") as f:
        json.dump(probs, f)
    print(probs)

    agents_in, agents_out = unique_items(inflows, outflows)

    agents = agents_in.union(agents_out)

    for agent in agents:
        document.agent(agent)

    print(events)
    infer_provenance(events, probs, 0.1, document, n)

    dot = prov_to_dot(document)
    dot.write_png("reconstructed.png")
    id = save_document(document)

    return events, probs


if __name__ == '__main__':
    events, probs = create_prov_graph(3)

    while True:
        start = int(input("Starting position in events"))
        end = int(input("Ending position in events"))

        new_document = prov.ProvDocument()
        new_document.set_default_namespace('')
        infer_provenance(events[start:end], probs, 0.1, new_document, 3)
        dot = prov_to_dot(new_document)
        dot.write_png("reconstructed.png")
        print("Picture saved!")