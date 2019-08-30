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

# TODO, something important to think, there are multiple paths between two excitatory neurons.
# [Physiology and anatomy of synaptic connections between thick tufted pyramidal neurones
# in the developing rat neocortex] identifies there are between 4 and 8 potential synaptic
# contacts between pairs of excitatory neurons.

# Assume
# spike from axon 0 arrives at time 0
# spike from axon 1 arrives at time 3
# spike from axon 2 arrives at time 1
# spike from axon 3 arrives at time 2
spike_input=[0, 6, 1, 2]

def printSpikeInput(spikes, tMax):
    # Create a figure object
    fig = plt.figure()

    plt.title('Local Buffer', fontsize=16, fontweight='bold')
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

# Assume Tmax is 8 (for encoding)
TMAX = 8
# printSpikeInput(spike_input, TMAX)

## Determine Vl (leak constant) and threshold

# Vl should not exceed VeMax
# spikes arrivals should be controlled by global clock?
# TODO, How global clock and local clock cooperate?

# From the IBM Compass paper, each core is entirely event-driven, global clock is not
# involved.
# Assumption: all the spikes are sent to the local buffer, the first spike
# should trigger the system to send the core the slow clock (1000Hz for example).
# I think the timing in buffer should correlate the timing in the core, say, each spike 
# in the buffer should have its own local timestamp.

# I assume each spike in spike_input resides in local buffer, and its arrival time
# is the core's local timestamp. (It makes sense to me, I doubt it will make sense
# to you. Sorry.)

# An abstract class to represent a spike
class Packet:
    target_core = -1 # Experimental study, only one core is considered.
    target_axon = -1
    target_exci_neuron = -1
    arrival = -1

# An abstract class to represent a core
class BufferEntry:
    def __init__(self):
        self.blocked = False
        self.spikes = [] # All spikes to this neuron

    def push_back(self, pkt):
        self.spikes.append(pkt)

    def extrSpike(self, clock):
        if self.blocked == True:
            # This axon has already been processed in the current period
            return None

        if len(self.spikes) == 0:
            # This axon has no spikes for this neuron
            return None

        if self.spikes[0].arrival == clock:
            spike = self.spikes.pop(0)
            self.blocked = True
            return spike

        return None
        
class Buffer:
    def __init__(self,  _num_neurons):
        # Split the buffer for each neuron for simple simulation
        self.buffer = [BufferEntry() for i in range(_num_neurons)]

    def push_back(self, pkt):
        target_neuron = pkt.target_exci_neuron

        self.buffer[target_neuron].push_back(pkt)

    def extrSpike(self, clock, neuron):
        return self.buffer[neuron].extrSpike(clock)

    # TODO, normalize the spikes after every volley processed.

class Core:
    ## Equation: Vt = MAX(Vt-1 - Vl, 0) + SUM(Sti * Wi * VeMax)
    VeMax = 3 # Required voltage to read a PCM cell.
    # Assume deltaT is 1ms
    # Assume volley period is 25ms
    DT = 1
    PERIOD = 1

    def __init__(self, _num_axons, _num_neurons):
        self.num_axons = _num_axons
        self.num_neurons = _num_neurons
        self.num_synapse = _num_axons * _num_neurons

        # One buffer for each axon
        self.buffers = [Buffer(_num_neurons) for i in range(_num_axons)]

        # synapse can be represented as a matrix (cross-bar)
        self.synapse = [[] for i in range(_num_axons)]
        [[j.append(1) for i in range(_num_neurons)] for j in self.synapse]

        # States
        self.active = False # Event-driven
        self.clock = 0;

        # Spikes
        self.preSpikes = []
        self.postSpikes = []
        self.respAmp = [] # For printing only

    def push_back(self, pkt):
        target_axon = pkt.target_axon

        self.buffers[target_axon].push_back(pkt)

    def recvPkt(self, pkt):
        target_axon = pkt.target_axon
        target_neuron = pkt.target_exci_neuron

        # The first event triggers the activation
        if self.active == False:
            self.active = True
        
        pkt.arrival = self.clock
        #print "Receiving a spike at time:", self.clock, "; Axon:", target_axon, \
        #                                    "; Neuron:", target_neuron
        # Push to buffer
        self.push_back(pkt)

    # Sum of all the spikes to the given neuron at current time-stamp
    def sumOfSpikes(self, neuron):
        spikes = []
        for axon in self.buffers:
            spike = axon.extrSpike(self.clock, neuron)
            if spike != None:
                spikes.append(spike)

        for spike in spikes:
            print "Receiving a spike at time:", spike.arrival, "; Axon:", spike.target_axon, \
                                             "; Neuron:", spike.target_exci_neuron

    def tick(self):
        # Perform operations
        assert self.active == True

        # TODO, for all the neurons
        for i in range(self.num_neurons):
            self.sumOfSpikes(i)
            # Vt = max(Vt-1 - Vl, 0) + SUM(Sti * Wi * VeMax)

        self.clock = self.clock + self.DT
        if self.clock == self.PERIOD:
            return False
        else:
            return True

    def printSynapse(self):
        for i in range(self.num_axons):
            for j in range(self.num_neurons):
                print self.synapse[i][j],
            print ''

# Assume our core has four axons and one excitatory neuron.
core = Core(4,1)
pkt = Packet()
pkt.target_axon = 0
pkt.target_exci_neuron = 0
core.recvPkt(pkt)

while core.tick():
    pass

# Exp 1: set Vl 0.1~1
Vl = np.arange(0.1,1,0.1)
