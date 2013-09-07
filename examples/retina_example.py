#!/usr/bin/python
"""
This examples show how to use SpiNNaker and a silicon retina. 
The silicon retina is represented by 2 populations (one for each polarity) each comprising 128 x 128 neurons (pixels), placed on (virtual) chips (254,254) and (254,255).
The retina populations feed into a LIF population of 16 x 16, where the weights are arranged so to compute a spatial subsample in the neural domain.

This test requires:
 - an FPGA/robot MC translating the AER sensor events to MC packets (see the application note by Luis Plana at http://solem.cs.man.ac.uk/documentation/spinn-app-8.pdf)
 - the visualiser in tools/visualiser
 
.. moduleauthor:: Francesco Galluppi, SpiNNaker Project, University of Manchester 2013. email: francesco.galluppi@cs.man.ac.uk

"""
import sys
import pyNN.spiNNaker as p

input_size = 128             # Size of each population
subsample_size = 32
runtime = 60000

def subSamplerConnector2D(size_in, size_out, weights, delays):
    """
    size_in = size of the input population (2D = size_in x size_in)    
    size_out = size of the sampled population
    weights = averaging weight value (each connection will have this value) must be float
    delays = averaging delay value (each connection will have this value)
    """
    out = []
    step = size_in/size_out
    for i in range(size_in):
         for j in range(size_in):
            i_out = i/step
            j_out = j/step
            out.append((i*size_in + j, i_out*size_out + j_out, weights, delays))
    return out

# Simulation Setup
p.setup(timestep=1.0, min_delay = 1.0, max_delay = 11.0)            # Will add some extra parameters for the spinnPredef.ini in here

p.get_db().set_number_of_neurons_per_core('IF_curr_exp', 128)      # this will set one population per core

cell_params = { 'tau_m' : 64, 'v_init'  : -75, 'i_offset'  : 0,
    'v_rest'    : -75,  'v_reset'    : -95, 'v_thresh'   : -40,
    'tau_syn_E' : 15,   'tau_syn_I'  : 15,  'tau_refrac' : 10}


print "Creating input population: %d x %d in X=0, Y=0" % (input_size, input_size)
input_pol_0, input_pol_1 = p.instantiate_retina(size=128, constraint={'x':0,'y':0})


subsampled = p.Population(subsample_size*subsample_size,         # size 
                   p.IF_curr_exp,   # Neuron Type
                   cell_params,   # Neuron Parameters
                   label="Input") # Label


# select one population to observe with the visualiser in tools/visualiser 
# the visualiser needs to be started with the following configuration files:
# ./visualiser -c retina_full_128.ini for observing the retina input
# ./visualiser -c retina_32_128pc.ini for observing the subsampling population

input_pol_0.record()      # to visualise the retina input
#subsampled.record()         # to visualise the subsampled input


p1 = p.Projection(input_pol_0, subsampled, p.FromListConnector(subSamplerConnector2D(128,subsample_size,.25,1)), label='subsampling projection')
p2 = p.Projection(input_pol_1, subsampled, p.FromListConnector(subSamplerConnector2D(128,subsample_size,.25,1)), label='subsampling projection')

p.run(runtime)              # Simulation time



p.end()
