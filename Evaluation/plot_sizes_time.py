import matplotlib.pyplot as plt
import numpy as np

monitor_agents = [13, 13, 13, 13, 13]
monitor_entities = [45, 116, 175, 201, 270]
monitor_activities = [27, 67, 101, 115, 160]
times_monitor = [1, 3, 5, 7, 10]

reconstructor_agents = [11, 11, 11, 11, 11]
reconstructor_entities = [67, 152, 216, 365, 430]
reconstructor_activities = [28, 67, 100, 171, 280]
times_reconstructor = [1, 3, 5, 7, 10]

fig, (ax1, ax2) = plt.subplots(2, sharex='all', sharey='all')

ax1.scatter(times_monitor, monitor_entities)
ax1.scatter(times_monitor, monitor_agents)
ax1.scatter(times_monitor, monitor_activities)
ax1.plot(np.unique(times_monitor),
         np.poly1d(np.polyfit(times_monitor, monitor_entities, 1))(np.unique(times_monitor)),
         label="entities")
ax1.plot(np.unique(times_monitor),
         np.poly1d(np.polyfit(times_monitor, monitor_agents, 1))(np.unique(times_monitor)),
         label="agents")
ax1.plot(np.unique(times_monitor),
         np.poly1d(np.polyfit(times_monitor, monitor_activities, 1))(np.unique(times_monitor)),
         label="activities")

ax1.set_title("Monitor")
ax1.legend()

ax2.scatter(times_reconstructor, reconstructor_entities)
ax2.scatter(times_reconstructor, reconstructor_agents)
ax2.scatter(times_reconstructor, reconstructor_activities)
ax2.plot(np.unique(times_reconstructor),
         np.poly1d(np.polyfit(times_reconstructor, reconstructor_entities, 1))(np.unique(times_reconstructor)),
         label="entities")
ax2.plot(np.unique(times_reconstructor),
         np.poly1d(np.polyfit(times_reconstructor, reconstructor_agents, 1))(np.unique(times_reconstructor)),
         label="agents")
ax2.plot(np.unique(times_reconstructor),
         np.poly1d(np.polyfit(times_reconstructor, reconstructor_activities, 1))(np.unique(times_reconstructor)),
         label="activities")

ax2.set_title("Reconstructor")
ax2.legend()

plt.xlabel("Minutes")
ax1.set_ylabel("Number of Entries")
ax2.set_ylabel("Number of Entries")

plt.savefig(f"sizes.png")
