#!/usr/bin/env python
"""
Simple test for STDP :

   Reproduces a classical plasticity experiment of plasticity induction by
pre/post synaptic pairing specifically :

 * At the begining of the simulation, "n_stim_test" external stimulations of the
   "pre_pop" (presynaptic) population do not trigger activity in the "post_pop"
   (postsynaptic) population.

 * Then the presynaptic and postsynaptic populations are stimulated together
   "n_stim_pairing" times by an external source so that the "post_pop" population
   spikes 10ms after the "pre_pop" population.

 * Ater that period, only the "pre_pop" population is externally stimulated
   "n_stim_test" times, but now it should trigger activity in the "post_pop"
   population (due to STDP learning)

Run as :

   $ ./stdp_example

This example requires that the NeuroTools package is installed
(http://neuralensemble.org/trac/NeuroTools)

Authors : Catherine Wacongne < catherine.waco@gmail.com >
          Xavier Lagorce < Xavier.Lagorce@crans.org >

April 2013
"""

import numpy, pylab, random, sys
import NeuroTools.signals as nt

import pyNN.spiNNaker as sim

# SpiNNaker setup
sim.setup(timestep=1.0,min_delay=1.0,max_delay=10.0, db_name='stdp_example.sqlite')

# +-------------------------------------------------------------------+
# | General Parameters                                                |
# +-------------------------------------------------------------------+

# Population parameters
model = sim.IF_cond_exp
cell_params = {
     'cm'         : 0.281,  # membrane capacitance nF
     'e_rev_E'    : 0.0,    # excitatory reversal potential in mV
     'e_rev_I'    : -80.0,  # inhibitory reversal potential in mV
     'i_offset'   : 0.0,    # offset current
     'tau_m'      : 9.3667, # membrane time constant
     'tau_refrac' : 0.1,    # absolute refractory period
     'tau_syn_E'  : 5.0,    # excitatory synaptic time constant
     'tau_syn_I'  : 5.0,    # inhibitory synaptic time constant
     'v_reset'    : -70.6,  # reset potential in mV
     'v_rest'     : -70.6,  # resting potential in mV
     'v_thresh'   : -50.4,  # spike initiaton threshold voltage in mV
     }

# Other simulation parameters
e_rate = 200
in_rate = 350

n_stim_test = 5
n_stim_pairing = 10
dur_stim = 20.
pop_size = 40

ISI = 150.
start_test_pre_pairing = 200.
start_pairing = 1500.
start_test_post_pairing = 700.

simtime = start_pairing + start_test_post_pairing + ISI*(n_stim_pairing + n_stim_test ) + 550.  # let's make it 5000


# Initialisations of the different types of populations
IAddPre = []
IAddPost = []

# +-------------------------------------------------------------------+
# | Creation of neuron populations                                    |
# +-------------------------------------------------------------------+

# Neuron populations
pre_pop = sim.Population(pop_size, model, cell_params)
post_pop = sim.Population(pop_size, model, cell_params)

# Test of the effect of activity of the pre_pop population on the post_pop
# population prior to the "pairing" protocol : only pre_pop is stimulated
for i in range(n_stim_test):
    IAddPre.append(
            sim.Population(pop_size,
                           sim.SpikeSourcePoisson,
                           {'rate': in_rate,'start':start_test_pre_pairing + ISI*(i), 'duration':dur_stim}
                           )
            )

# Pairing protocol : pre_pop and post_pop are stimulated with a 10 ms
# difference
for i in range(n_stim_pairing):
    IAddPre.append(
            sim.Population(pop_size,
                           sim.SpikeSourcePoisson,
                           {'rate': in_rate,'start':start_pairing + ISI*(i), 'duration':dur_stim}
                           )
            )
    IAddPost.append(
            sim.Population(pop_size,
                           sim.SpikeSourcePoisson,
                           {'rate': in_rate,'start':start_pairing + ISI*(i) + 10., 'duration':dur_stim}
                           )
            )

# Test post pairing : only pre_pop is stimulated (and should trigger activity
# in Post)
for i in range(n_stim_test):
    IAddPre.append(
            sim.Population(pop_size,
                           sim.SpikeSourcePoisson,
                           {'rate': in_rate,'start':start_pairing + ISI*(n_stim_pairing)+start_test_post_pairing+ISI*(i), 'duration':dur_stim}
                           )
            )

# Noise inputs
INoisePre = sim.Population(pop_size,
                           sim.SpikeSourcePoisson,
                           {'rate': e_rate,'start':0,'duration':simtime}, label="expoisson"
                           )
INoisePost = sim.Population(pop_size,
                            sim.SpikeSourcePoisson,
                            {'rate': e_rate,'start':0,'duration':simtime}, label="expoisson"
                            )

# +-------------------------------------------------------------------+
# | Creation of connections                                           |
# +-------------------------------------------------------------------+

# Connection parameters
JEE = 5.

# Connection type between noise poisson generator and excitatory populations
ee_connector = sim.OneToOneConnector(weights=JEE*1e-3)

# Noise projections
sim.Projection(INoisePre, pre_pop, ee_connector, target='excitatory')
sim.Projection(INoisePost, post_pop, ee_connector, target='excitatory')

# Additional Inputs projections
for i in range(len(IAddPre)):
    sim.Projection(IAddPre[i], pre_pop, ee_connector, target='excitatory')
for i in range(len(IAddPost)):
    sim.Projection(IAddPost[i], post_pop, ee_connector, target='excitatory')

# Plastic Connections between pre_pop and post_pop
stdp_model = sim.STDPMechanism(
        timing_dependence = sim.SpikePairRule(tau_plus = 20., tau_minus = 50.0),
        weight_dependence = sim.AdditiveWeightDependence(w_min = 0, w_max = 0.9, A_plus=0.02, A_minus = 0.02)
        )

sim.Projection(pre_pop, post_pop, sim.FixedProbabilityConnector(p_connect=0.5),
               synapse_dynamics = sim.SynapseDynamics(slow= stdp_model))

# +-------------------------------------------------------------------+
# | Simulation and results                                            |
# +-------------------------------------------------------------------+

# Record neurons' potentials
pre_pop.record_v()
post_pop.record_v()

# Record spikes
pre_pop.record()
post_pop.record()

# Run simulation
sim.run(simtime)

# Dump data
pre_pop.printSpikes("results/stdp_pre.spikes")
post_pop.printSpikes("results/stdp_post.spikes")
pre_pop.print_v("results/stdp_pre.v")
post_pop.print_v("results/stdp_post.v")

# End simulation on SpiNNaker
sim.end()

# Function to draw a "nice" raster plot
def plot_spikes(file):
    nt_spikes = nt.load(file, 's')
    nt_spikes = nt_spikes.convert("(id,time)")
    spikes_t = [t for i,t in nt_spikes]
    spikes_id = [i for i,t in nt_spikes]
    pylab.plot(spikes_t, spikes_id, '.')

# Make some graphs
pylab.figure()
plot_spikes('results/stdp_pre.spikes')
pylab.title('Presynaptic population spikes')

pylab.figure()
plot_spikes('results/stdp_post.spikes')
pylab.title('Postsynaptic population spikes')

v = nt.load('results/stdp_pre.v', 'v')
v.plot(2)
pylab.title('potentials of presynaptic population')

pylab.figure()
v = nt.load('results/stdp_post.v', 'v')
vm = v.mean()
pylab.plot(v.time_axis(), vm)
pylab.title('Mean potential of postsynaptic population')

pylab.show()

