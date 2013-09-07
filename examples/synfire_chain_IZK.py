#!/usr/bin/python
"""
Synfirechain-like example (Izhikevich neuron)

Expected results in
  .. figure::  ./examples/results/synfire_chain_IZK.png

"""

import pyNN.spiNNaker as p
import numpy, pylab

p.setup(timestep=1.0, min_delay = 1.0, max_delay = 8.0, db_name='synfire.sqlite')

n_pop = 64
nNeurons = 10

p.get_db().set_number_of_neurons_per_core('IZK_curr_exp', nNeurons)      # this will set one population per core
#p.get_db().set_number_of_neurons_per_core('IF_curr_exp', 2*nNeurons)      # this will set 2 populations per core
#p.get_db().set_number_of_neurons_per_core('IF_curr_exp', nNeurons/2)      # this will set 1 population every 2 cores


rng = p.NumpyRNG(seed=28374)
rng1 = p.NumpyRNG(seed=12345)

delay_distr = p.RandomDistribution('uniform', [1,5], rng)
weight_distr = p.RandomDistribution('uniform', [0,2], rng1)

v_distr = p.RandomDistribution('uniform', [-85,-95], rng)



v_inits = []
for i in range(nNeurons):
    v_inits.append(v_distr.next())


RS_params = {   'a'      : 0.02, 'b'    : 0.2, 'c' : -70,   'd'    : 8,  
                'v_init'   : -70,'u_init'   : 0,
                'tau_syn_E'   : 5, 'tau_syn_I'   : 15,
                'i_offset': 0
                }


populations = list()
projections = list()


populations = list()
projections = list()

weight_to_spike = 28

for i in range(n_pop):
    if i == 0:
        populations.append(p.Population(nNeurons, p.IZK_curr_exp, RS_params, label='pop_%d' % i))
        populations[i].set('i_offset', 10)
        populations[i].randomInit(v_distr)
    else:    
        populations.append(p.Population(nNeurons, p.IZK_curr_exp, RS_params, label='pop_%d' % i))
    if i > 0: 
#        print i, n_pop-1, len(populations)   
        projections.append(p.Projection(populations[i-1], populations[i], p.OneToOneConnector(weights=weight_to_spike, delays=1), target='excitatory'))


#    populations[i].record_v()           # at the moment is only possible to observe one population per core        
    populations[i].record() # sends spike to the Monitoring application


populations[0].record_v()    
p.run(1000)

# retrieving spike results and plotting...

id_accumulator=0

for i in range(n_pop):
    data = numpy.asarray(populations[i].getSpikes())
    pylab.scatter(data[:,1], data[:,0] + id_accumulator, color='green', s=1)
    id_accumulator = id_accumulator + populations[i].size


pylab.show()

pylab.show()


p.end()

