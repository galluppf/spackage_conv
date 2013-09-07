"""
A single IZK neuron with exponential, conductance-based synapses, fed by two
spike sources.

Run as:

$ python IZK_cond_exp.py <simulator>

where <simulator> is 'neuron', 'nest', etc

Originally for LIF neuron (Andrew Davison, UNIC, CNRS), adapted for Izhikevich neuron on SpiNNaker
May 2006

Expected result can be found in: 
  .. figure::  ./examples/results/IZK_cond_exp.png

$Id: IF_cond_exp.py 917 2011-01-31 15:23:34Z apdavison $
"""

#!/usr/bin/python
simulator_name = 'spiNNaker'
#simulator_name = 'brian'


from pyNN.utility import get_script_args
from pyNN.errors import RecordingError

exec("import pyNN.%s as p" % simulator_name)


p.setup(timestep=1.0,min_delay=1.0,max_delay=10.0, db_name='izk.sqlite')

cell_params = {   'a'      : 0.02, 'b'    : 0.2, 'c' : -65,   'd'    : 8,  
                'v_init'   : -80,'u_init'   : 0,
                'tau_syn_E'   : 10, 'tau_syn_I'   : 15,
                'i_offset': 0
                }


izk_pop = p.Population(1, p.IZK_curr_exp, cell_params, label='IZK_cond_exp')

spike_sourceE = p.Population(1, p.SpikeSourceArray, {'spike_times': [[i for i in range(5,105,10)],]}, label='spike_sourceE')
if simulator_name == 'spiNNaker': spike_sourceE.set_mapping_constraint({'x':0,'y':0,'p':5})

spike_sourceI = p.Population(1, p.SpikeSourceArray, {'spike_times': [[i for i in range(155,255,10)],]}, label='spike_sourceE')
if simulator_name == 'spiNNaker': spike_sourceI.set_mapping_constraint({'x':0,'y':0,'p':6})

connE = p.Projection(spike_sourceE, izk_pop, p.OneToOneConnector(weights=5, delays=2), target='excitatory')
connI = p.Projection(spike_sourceI, izk_pop, p.OneToOneConnector(weights=5, delays=4), target='inhibitory')
    
izk_pop.record_v()
izk_pop.record_gsyn()

izk_pop.record()
spike_sourceE.record()
spike_sourceI.record()


try:
    record_gsyn(ifcell, "results/IF_cond_exp_%s.gsyn" % simulator_name)
except (NotImplementedError, RecordingError, NameError):
    pass

p.run(200)

import pylab

izk_pop.print_v('./IZK_curr_exp_%s.v' % simulator_name)
recorded_v =  izk_pop.get_v()
recorded_gsyn =  izk_pop.get_gsyn()

f = pylab.figure()
f.add_subplot(211)
pylab.plot([ i[2] for i in recorded_v ])

f.add_subplot(212)
pylab.plot([ i[2] for i in recorded_gsyn ], color='green')

pylab.show()
p.end()

