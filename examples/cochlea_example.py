"""
Example using the cochlea with 4 chip boards (**check system_library=4_chip_board_cochlea.db in your pacman.cfg file**)

The cochlea is mapped to virtual chip (2,0) in cores 0 and 1 (left and right ears).
The routing key (MC/AER SpiNNaker packet) is defined as follows::
   ----------------------------------------------------------------
   | x = 2  | y = 0  | zeros  | ear   | zeros  | channel | neuron |
   ----------------------------------------------------------------
   | 8 bits | 8 bits | 4 bits | 1 bit | 3 bits | 6 bits  | 2 bits |
   ----------------------------------------------------------------

The example instantiates two populations, one for the left and one for the right ear, and connects them to a population of leaky integrate and fire neurons. 

**Populations need to be instantiated and mapped to processors (2,0,0) and (2,0,1) using the set_mapping_constraint() Population function** whenever you want to use the cochlea::
   
   left_cochlea_ear = p.Population(256, p.SpikeSource, {}, label='left_cochlea_ear')
   left_cochlea_ear.set_mapping_constraint({'x':2, 'y':0, 'p': 0})
   right_cochlea_ear = p.Population(256, p.SpikeSource, {}, label='right_cochlea_ear')
   right_cochlea_ear.set_mapping_constraint({'x':2, 'y':0, 'p': 1})




Each population has 256 neurons (4 neurons x 64 channels).
Neurons in each population (ear) are numbered from 0 to 255, where::

   id = ( channel * 4 ) + neuron

.. moduleauthor:: Francesco Galluppi, SpiNNaker Project, francesco.galluppi@cs.man.ac.uk
"""
from pyNN.utility import get_script_args
from pyNN.errors import RecordingError
import pyNN.spiNNaker as p

p.setup(timestep=1.0,min_delay=1.0,max_delay=10.0, db_name='cochlea_example.sqlite')

nNeurons = 4 * 64 # 4 neurons and 64 channels per ear

p.get_db().set_number_of_neurons_per_core('IF_curr_exp', nNeurons)      # this will set 256 neurons per core

cell_params = {     'i_offset' : .1,    'tau_refrac' : 3.0, 'v_rest' : -65.0,
                    'v_thresh' : -51.0,  'tau_syn_E'  : 2.0,
                    'tau_syn_I': 5.0,    'v_reset'    : -70.0,
                    'e_rev_E'  : 0.,     'e_rev_I'    : -80.}

left_cochlea_ear = p.Population(nNeurons, p.ProxyNeuron, {'x_source':254, 'y_source':254}, label='left_cochlea_ear')
left_cochlea_ear.set_mapping_constraint({'x':0, 'y':0})
left_cochlea_ear.record()   #    this should record spikes from the cochlea


right_cochlea_ear = p.Population(nNeurons, p.SpikeSource, {}, label='right_cochlea_ear')
right_cochlea_ear = p.Population(nNeurons, p.ProxyNeuron, {'x_source':254, 'y_source':255}, label='left_cochlea_ear')
right_cochlea_ear.set_mapping_constraint({'x':0, 'y':0})

right_cochlea_ear.record()   #    this should record spikes from the cochlea

ifcell = p.Population(nNeurons, p.IF_curr_exp, cell_params, label='IF_curr_exp')
ifcell.record_v()

p1 = p.Projection(left_cochlea_ear, ifcell, p.OneToOneConnector(weights=1, delays=1), target='excitatory')
p2 = p.Projection(right_cochlea_ear, ifcell, p.OneToOneConnector(weights=1, delays=1), target='excitatory')

p.run(200.0)

p.end()


