"""
Synfirechain-like example

Expected results in
  .. figure::  ./examples/results/synfire_chain_lif.png

"""
#!/usr/bin/python
import pyNN.spiNNaker as p
import numpy, pylab



p.setup(timestep=1.0, min_delay = 1.0, max_delay = 8.0, db_name='synfire.sqlite')

n_pop = 16    # number of populations
nNeurons = 10  # number of neurons in each population

p.get_db().set_number_of_neurons_per_core('IF_curr_exp', nNeurons)      # this will set one population per core

# random distributions
rng = p.NumpyRNG(seed=28374)
delay_distr = p.RandomDistribution('uniform', [1,10], rng=rng)
weight_distr = p.RandomDistribution('uniform', [0,2], rng=rng)
v_distr = p.RandomDistribution('uniform', [-55,-95], rng)


cell_params_lif_in = { 'tau_m'      : 32,
                'v_init'    : -80,
                'v_rest'     : -75,   
                'v_reset'    : -95,  
                'v_thresh'   : -55,
                'tau_syn_E'   : 5,
                'tau_syn_I'   : 10,
                'tau_refrac'   : 100, 
                'i_offset'   : 1
                }

cell_params_lif = { 'tau_m'      : 32,
                'v_init'    : -80,
                'v_rest'     : -70,   
                'v_reset'    : -95,  
                'v_thresh'   : -55,
                'tau_syn_E'   : 5,
                'tau_syn_I'   : 10,
                'tau_refrac'   : 5,                 
                'i_offset'   : 0
                }


populations = list()
projections = list()

weight_to_spike = 8

for i in range(n_pop):
    if i == 0:
        populations.append(p.Population(nNeurons, p.IF_curr_exp, cell_params_lif_in, label='pop_%d' % i))
        populations[i].randomInit(v_distr)
    else:    
        populations.append(p.Population(nNeurons, p.IF_curr_exp, cell_params_lif, label='pop_%d' % i))        
    if i > 0: 
        projections.append(p.Projection(populations[i-1], populations[i], p.OneToOneConnector(weights=weight_to_spike, delays=1)))
    populations[i].record()
    populations[i].record_v()           

    
p.run(3000)

# retrieving spike results and plotting...

id_accumulator=0

for i in range(n_pop):
    data = numpy.asarray(populations[i].getSpikes())
    pylab.scatter(data[:,1], data[:,0] + id_accumulator, color='green', s=1)
    id_accumulator = id_accumulator + populations[i].size


pylab.show()

p.end()


