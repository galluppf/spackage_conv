"""
Neural model creation example. 

.. moduleauthor:: Francesco Galluppi email: francesco.galluppi@cs.man.ac.uk
"""

from pyNN.spiNNaker.standardmodels import create_neural_model as c
n = c.NeuralModel('IF_curr_exp_hp', 100, 'app_frame_lif_curr_hp.aplx')

n.add_parameter('v_init', param_type = 'i', translation ='int(value)*65536')
n.add_parameter('v_thresh', param_type = 'i', translation = 'int(value)*65536')
n.add_parameter('v_reset', param_type = 'i', translation = 'int(value)*65536')
n.add_parameter('v_rest', param_type = 'i', translation = 'int(value)*65536')
n.add_parameter('i_offset', param_type = 'i', translation = 'int(value)*65536')
n.add_parameter('cm', param_type = 'i', \
    translation = "int(params['tau_m'][i]/params['cm'][i]*65536)")

n.add_parameter('tau_refrac', param_type = 'i', translation = 'int(value)')
n.add_parameter('tau_refrac_clock', param_type = 'i', translation = 'int(value)')
n.add_parameter('tau_syn_E', param_type = 'i', translation = 'int(65536/value)')
n.add_parameter('tau_syn_I', param_type = 'i', translation = 'int(65536/value)')
n.add_parameter('tau_m', param_type = 'i', translation = 'int(65536/value)')

for s in ('excitatory', 'inhibitory'):
    n.add_synapse(s)    
    n.synapses[s].set_neuron_id_bits(11)
    n.synapses[s].set_plasticity_bit()
    negative_bool = True if s == 'inhibitory' else False
    
    n.synapses[s].add_parameter('weight', 
                    number_of_decimal_bits = 14,
                    number_of_integer_bits = 1,
                    offset = 0,
                    negative=negative_bool)

    n.synapses[s].add_parameter('delay', 
                    number_of_decimal_bits = 0,
                    number_of_integer_bits = 4,
                    offset = -1)

n.write_model_to_db()

print "\n---> PyNN Bindings:"
print n.write_pynn_bindings()
n.write_pynn_bindings('/tmp/pynn_bindings.py')

print "\n---> SQL bindings"
print n.write_sql_bindings()
n.write_sql_bindings('/tmp/pacman_bindings.sql')


print "\n---> synaptic functions:"
print n.synapses['excitatory'].write_decode_synaptic_word_function()
print n.write_buffer_post_synaptic_potentials()

print "\n---> neural header file:"
print n.write_neural_header_file()
n.write_neural_header_file('/tmp/model_if_curr_exp_hp.h')

print "\n---> write neural c file:"
print n.write_neural_c_file()
n.write_neural_c_file('/tmp/model_if_curr_exp_hp.c')


