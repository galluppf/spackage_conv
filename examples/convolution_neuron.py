"""
Neural model creation example. 

.. moduleauthor:: Francesco Galluppi email: francesco.galluppi@cs.man.ac.uk
"""
from pyNN.spiNNaker.standardmodels import create_neural_model as c
name = 'convolution'
n = c.NeuralModel('convolution', 2048, 'app_%s.aplx' % name)

n.add_parameter('v', param_type = 'h', translation ='int(value)*256')
n.add_parameter('v_thresh', param_type = 'h', translation = 'int(value)*256')
n.add_parameter('v_reset', param_type = 'h', translation = 'int(value)*256')
n.add_parameter('v_rest', param_type = 'h', translation = 'int(value)*256')

n.add_parameter('tau_refrac', param_type = 'h', translation = 'int(value)')
n.add_parameter('tau_refrac_clock', param_type = 'h', translation = 'int(value)')
n.add_parameter('tau_m', param_type = 'i', translation = 'int(65536/value)')

for s in ('excitatory', 'inhibitory'):
    n.add_synapse(s)    
    n.synapses[s].set_neuron_id_bits(11)
    n.synapses[s].add_parameter('weight', 
                    number_of_decimal_bits = 8,
                    number_of_integer_bits = 8,
                    offset = 0)
    n.synapses[s].add_parameter('delay', 
                    number_of_decimal_bits = 0,
                    number_of_integer_bits = 4,
                    offset = 0)


n.write_model_to_db()

print "\n---> PyNN Bindings:"
print n.write_pynn_bindings()
n.write_pynn_bindings('/tmp/%s_pynn_bindings.py' % name)

print "\n---> SQL bindings"
print n.write_sql_bindings()
n.write_sql_bindings('/tmp/%s_pacman_bindings.sql' % name)


print "\n---> synaptic functions:"
print n.synapses['excitatory'].write_decode_synaptic_word_function()
print n.write_buffer_post_synaptic_potentials()

print "\n---> neural header file:"
print n.write_neural_header_file()
n.write_neural_header_file('/tmp/model_%s.h'% name)

print "\n---> write neural c file:"
print n.write_neural_c_file()
n.write_neural_c_file('/tmp/model_%s.c' % name)


