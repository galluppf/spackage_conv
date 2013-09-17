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

exec("import pyNN.%s as p" % simulator_name)


p.setup(timestep=1.0,min_delay=1.0,max_delay=10.0, db_name='if_cond.sqlite')



cell_params1 = {     'tau_m' :   16, 'tau_refrac' : 1.0, 'v_rest' : -60.0,
                    'v_thresh' : 60.0, 'v_reset'    : 0.0, 
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

spike_sourceE = p.Population(4, p.SpikeSourceArray, {'spike_times': [range(0,5000,10),[],[],[]]}, label='spike_sourceE')
spike_sourceE.set_mapping_constraint({'x':1, 'y':0})

"""spike_sourceI = p.Population(4, p.SpikeSourceArray, {'spike_times': [[150,189],[160,199],[170,175],[]]}, label='spike_sourceI')"""

conn1 = p.Projection(spike_sourceE, convmodule1, p.ConvolutionConnector(weights=[0,100,100,100,0,
                                                                                0,100,100,100,0,
                                                                                0,100,100,100,0,
                                                                                0,100,100,100,0,
                                                                                0,100,100,100,0], 
    displacement_x = 2, displacement_y = 2,
    kernel_size_x = 5, kernel_size_y = 5)
    )

"""conn2 = p.Projection(convmodule1, convmodule2, p.ConvolutionConnector(weights=10*range(-9,0,1), 
   displacement_x = 5, displacement_y = 3,
   kernel_size_x = 3, kernel_size_y = 3)
    )"""
    
ifcell = p.Population(1, p.IF_cond_exp, cell_params_lif, label='IF_cond_exp')
connE = p.Projection(spike_sourceE, ifcell, p.OneToOneConnector(weights=0.006, delays=2), target='excitatory')

convmodule1.record()
    
p.run(5000)

p.end()

