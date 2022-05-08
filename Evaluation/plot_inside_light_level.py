import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

with open("records_n=2.json", encoding='utf-8-sig') as f:
    data_2 = json.load(f)

with open("records_n=3.json", encoding='utf-8-sig') as f:
    data_3 = json.load(f)

datas = [(data_2, "n = 2"), (data_3, "n = 3")]

dfs = []

for i, entry in enumerate(datas):
    data = entry[0]
    print(data[0]["ill.`meta:identifier`"][-12:])
    tos = [int(data[0]["ill.To"])]
    removals = 0
    for i in range(1, len(data)):
        if data[i-1]["n.`meta:identifier`"] == data[i]["n.`meta:identifier`"]:
            time_prev = datetime.strptime(data[i-1]["ill.`meta:identifier`"][-12:], "%H:%M:%S.%f")
            time_curr = datetime.strptime(data[i]["ill.`meta:identifier`"][-12:], "%H:%M:%S.%f")
            removals += 1
            if time_curr > time_prev:
                tos.pop()
                tos.append(int(data[i]["ill.To"]))
        else:
            tos.append(int(data[i]["ill.To"]))
    df = pd.DataFrame(tos, columns=[f'Inside Light Level Values ({entry[1]})'])

    print(df)
    print(f"removals {entry[1]}: {str(removals)}")
    dfs.append(df)

fig, (ax1, ax2) = plt.subplots(1, 2, sharey='all')
fig.set_size_inches(10, 6)

dfs[0].plot.hist(ax=ax1)
dfs[1].plot.hist(ax=ax2)
plt.savefig(f"histogram.png")
