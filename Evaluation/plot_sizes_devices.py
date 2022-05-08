import numpy as np
import matplotlib.pyplot as plt

groups = ["Blinds Only", "Blinds + Temp", "All"]
monitor_sizes = [(70, 13, 120), (111, 13, 200), (101, 13, 185)]
reconstructor_sizes = [(70, 5, 178), (111, 8, 209), (101, 11, 173)]

monitor_activities = [e[0] for e in monitor_sizes]
monitor_agents = [e[1] for e in monitor_sizes]
monitor_entities = [e[2] for e in monitor_sizes]

reconstructor_activities = [e[0] for e in reconstructor_sizes]
reconstructor_agents = [e[1] for e in reconstructor_sizes]
reconstructor_entities = [e[2] for e in reconstructor_sizes]

x_axis = np.arange(len(groups))

fig, (ax1, ax2) = plt.subplots(2, sharex='all', sharey='all')

ax1.bar(x_axis - 0.2, monitor_entities, 0.2, label="Entities")
ax1.bar(x_axis, monitor_activities, 0.2, label="Activities")
ax1.bar(x_axis + 0.2, monitor_agents, 0.2, label="Agents")
ax1.set_title("Monitor")

ax2.bar(x_axis - 0.2, reconstructor_entities, 0.2, label="Entities")
ax2.bar(x_axis, reconstructor_activities, 0.2, label="Activities")
ax2.bar(x_axis + 0.2, reconstructor_agents, 0.2, label="Agents")
ax2.set_title("Reconstructor")

plt.legend(loc='upper right')
plt.xticks(x_axis, groups)
ax2.set_ylabel("Number of Entries")
ax1.set_ylabel("Number of Entries")

plt.savefig("Simulation_sizes.png")