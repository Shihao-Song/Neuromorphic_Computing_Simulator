# Plotting Linear Leak Integrate and Fire (LLIF)
# Source: IBM TrueNorth System (https://ieeexplore.ieee.org/document/6252637)
# Equation: Vt = MAX(Vt-1 - Vl, 0) + SUM(Sti * Wi * VeMax)
# Vl is a constant leak value
# VeMax is a spike's maximum contribution to membrane potential (when Wi = 1)
# For example, assume the required voltage to read a PCM cell is 3V, 
# then logically, VeMax should equal to 3V.
# TODO, Vl may be determined by experiment.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Assume deltaT is 1ms
# Assume volley period is 25ms
# Assume Tmax is 8
DT = 1
PERIOD = 25
TMAX = 8

# TODO, something important to think, there are multiple paths between two excitatory neurons.
# [Physiology and anatomy of synaptic connections between thick tufted pyramidal neurones
# in the developing rat neocortex] identifies there are between 4 and 8 potential synaptic
# contacts between pairs of excitatory neurons.

# Assume
# spike from axon 0 arrives at time 0
# spike from axon 1 arrives at time 3
# spike from axon 2 arrives at time 1
# spike from axon 3 arrives at time 2
spike_input=[0, 3, 1, 2]

def printSpikeInput(spikes, tMax):
    # Create a figure object
    fig = plt.figure()

    plt.title('Spike Input', fontsize=16, fontweight='bold')
    plt.xlabel('Spike Arrival', fontsize=12)
    plt.ylabel('Axons', fontsize=12)
    plt.yticks([])
    plt.xlim(-1,tMax)
    plt.ylim(0,len(spikes))

    # Draw axons
    for i in range(0, len(spikes)):
        plt.axhline(y=i,ls='--',color='k')

    # Plot timings
    for i in range(0, len(spikes)):
        plt.plot([spikes[i],spikes[i]],[i,i+1],color='b')
    plt.show()

printSpikeInput(spike_input, TMAX)

#axs[0].axhline(y=1, '-')
#fig = plt.figure()
#fig.suptitle('Spike Input', fontsize=20, fontweight='bold')
#plt.xlabel('Spike Arrival', fontsize=18)
#plt.ylable('Axon Index')

#plt.axhline(y=1)

#plt.xlim(0, 8)
#plt.ylim(0, 4)

exit(0)

x = np.arange(10)
y = np.random.random(10)

fig = plt.figure()
plt.xlim(0, 10)
plt.ylim(0, 1)
graph, = plt.plot([], [], 'o')

def animate(i):
    graph.set_data(x[:i+1], y[:i+1])
    return graph

ani = FuncAnimation(fig, animate, frames=10, interval=200)
plt.show()
