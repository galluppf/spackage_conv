"""
A convolution layer fed with spikes from a spike source.

Run as:

$ python IF_cond_exp.py <simulator>

where <simulator> is 'neuron', 'nest', etc

Andrew Davison, UNIC, CNRS
May 2006

$Id: IF_cond_exp.py 917 2011-01-31 15:23:34Z apdavison $
"""

#!/usr/bin/python
simulator_name = 'spiNNaker'
import numpy
#import ev_pos
#import ev_pos_short
import ev_pos_50000ev

exec("import pyNN.%s as p" % simulator_name)


p.setup(timestep=1.0,min_delay=1.0,max_delay=10.0, db_name='if_cond.sqlite')



cell_params1 = {     'tau_m' :   16, 'tau_refrac' : 1.0, 'v_rest' : -60.0,
                    'v_thresh' : 60.0, 'v_reset'    : 0.0, 
                      'v' : 0, 'time_last_input_spike' : 0, 'time_last_output_spike' : 0,
                    'size_map_x' : 128, 'size_map_y' : 128}
cell_params2 = {     'tau_m' :   16, 'tau_refrac' : 10.0, 'v_rest' : -60.0,
                    'v_thresh' : 60.0, 'v_reset'    : 0.0, 
                    'size_map_x' : 128, 'size_map_y' : 128}

cell_params_lif = {     'i_offset' : .1,    'tau_refrac' : 3.0, 'v_rest' : -65.0,
                    'v_thresh' : -51.0,  'tau_syn_E'  : 2.0,
                    'tau_syn_I': 5.0,    'v_reset'    : -70.0,
                    'e_rev_E'  : 0.,     'e_rev_I'    : -80.}



convmodule1 = p.Population(16384, p.convolution, cell_params1, label='convolution_module')
"""convmodule2 = p.Population(16384, p.convolution, cell_params2, label='convolution_module')"""

"""spike_times = [range(0,500,30),[],[],[]]"""
"""spike_times = numpy.genfromtxt('ev_pos_short.txt')"""
"""spike_times = numpy.loadtxt('ev_pos_short.txt')"""
#ev_pos_short = ev_pos_short.ev_pos_short
"""eventos = ev_pos.eventos"""
eventos = ev_pos_50000ev.eventos
"""f = open ('ev_pos_short.txt','r')
spike_times = f.read()"""

spike_sourceE = p.Population(1*128*128, p.SpikeSourceArray, {'spike_times': eventos}, label='spike_sourceE')
spike_sourceEneg = p.Population(1*128*128, p.SpikeSourceArray, {'spike_times': eventos}, label='spike_sourceE')

spike_sourceE.set_mapping_constraint({'x':1,'y':0})
spike_sourceEneg.set_mapping_constraint({'x':1,'y':0})
spike_sourceE.record()

"""spike_sourceI = p.Population(4, p.SpikeSourceArray, {'spike_times': [[150,189],[160,199],[170,175],[]]}, label='spike_sourceI')"""


conn1 = p.Projection(spike_sourceE, convmodule1, p.ConvolutionConnector(weights=[0,0,0,0, 100,0,0,0,0], 
    displacement_x = 0, displacement_y = 0,
    kernel_size_x = 3, kernel_size_y = 3)
    )

"""conn2 = p.Projection(convmodule1, convmodule2, p.ConvolutionConnector(weights=10*range(-9,0,1), 
   displacement_x = 5, displacement_y = 3,
   kernel_size_x = 3, kernel_size_y = 3)
    )"""
    
ifcell = p.Population(1, p.IF_cond_exp, cell_params_lif, label='IF_cond_exp')
connE = p.Projection(spike_sourceE, ifcell, p.OneToOneConnector(weights=0.006, delays=2), target='excitatory')

#convmodule1.record()
    
p.run(5000)
convmodule1.printSpikes('./convmodule1_spikes.txt')

p.end()

