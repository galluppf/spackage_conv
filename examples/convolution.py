"""
A single IF neuron with exponential, conductance-based synapses, fed by two
spike sources.

Run as:

$ python IF_cond_exp.py <simulator>

where <simulator> is 'neuron', 'nest', etc

Andrew Davison, UNIC, CNRS
May 2006

$Id: IF_cond_exp.py 917 2011-01-31 15:23:34Z apdavison $
"""

#!/usr/bin/python
simulator_name = 'spiNNaker'

exec("import pyNN.%s as p" % simulator_name)


p.setup(timestep=1.0,min_delay=1.0,max_delay=10.0, db_name='if_cond.sqlite')



cell_params = {     'tau_m' :   16, 'tau_refrac' : 3.0, 'v_rest' : -65.0,
                    'v_thresh' : -51.0, 'v_reset'    : -70.0}

cell_params_lif = {     'i_offset' : .1,    'tau_refrac' : 3.0, 'v_rest' : -65.0,
                    'v_thresh' : -51.0,  'tau_syn_E'  : 2.0,
                    'tau_syn_I': 5.0,    'v_reset'    : -70.0,
                    'e_rev_E'  : 0.,     'e_rev_I'    : -80.}


convmodule = p.Population(128*128, p.convolution, cell_params, label='convolution_module')

spike_sourceE = p.Population(4, p.SpikeSourceArray, {'spike_times': [[50,100],[60,110],[],[61]]}, label='spike_sourceE')

spike_sourceI = p.Population(4, p.SpikeSourceArray, {'spike_times': [[150,189],[160,199],[170,175],[]]}, label='spike_sourceI')

connE = p.Projection(spike_sourceE, convmodule, p.ConvolutionConnector(weights=range(20)))
connI = p.Projection(spike_sourceI, convmodule, p.ConvolutionConnector(weights=range(-20,0,1)))
    
ifcell = p.Population(1, p.IF_cond_exp, cell_params_lif, label='IF_cond_exp')
connE = p.Projection(spike_sourceE, ifcell, p.OneToOneConnector(weights=0.006, delays=2), target='excitatory')
    
p.run(5000)

p.end()

