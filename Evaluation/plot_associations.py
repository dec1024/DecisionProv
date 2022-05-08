import json
import matplotlib.pyplot as plt
import numpy as np

ys = ['WiZColorBulb_Color', 'WiZColorBulb_ColorTemperature', 'Sensor2_DoorSensor2', 'WiZColorBulb_LastUpdate', 'Sensor1_DoorSensor1', 'WiZColorBulb_DynamicLightModeSpeed', 'WiZColorBulb_Power', 'WiZColorBulb_SignalStrength']
xs = ['WiZColorBulb_Color']

files = [f"data_n={i}.json" for i in range(1, 6)]
files = [f"data.json" for i in range(1, 6)]

for i, file in enumerate(files):
    n = i + 1
    with open(file) as json_file:
        data = json.load(json_file)

        print(type(data))
        print(data)

    values = [[np.round(data[x][y], 2) for x in xs] for y in ys]

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(values, aspect='auto')

    ax.set_xticks(np.arange(len(xs)), labels=xs)
    ax.set_yticks(np.arange(len(ys)), labels=ys)

    for i in range(len(xs)):
        for j in range(len(ys)):
            text = ax.text(i, j, values[j][i], ha="center", va="center", color="w")

    ax.set_title(f"Association Strength Scores (n={n})")
    ax.set_xlabel("Command Type", labelpad=10)
    ax.set_ylabel("Association Score")
    fig.tight_layout()
    plt.savefig(f"Associations_n={n}.png")