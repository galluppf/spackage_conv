"""
Neural model creation utility for PACMAN Quarantotto

Creating a neural model for PACMAN/SpiNNaker involves 3 steps:

1. Writing PyNN/PACMAN bindings
2. Writing neural model/synaptic translations in PACMAN
3. Creating a C/header file containing the neural model

The class :class:`NeuralModel` is used to instantiate a new neural model, and has
as attributes a list of paramters (with their translation) and a list of :class:`SynapseModel`
objects. 

Each :class:`SynapseModel` object has itself a list of parameters driving 
the synaptic translation.

Utilities to dynamically generate code for all the 3 steps required are provided:

:func:`NeuralModel.write_pynn_bindings` generates the python code to be imported
in PyNN (through the cells.py file) to map the neuron in PyNN.

:func:`NeuralModel.write_sql_bindings` writes an SQL script containing the PACMAN bindings

:func:`NeuralModel.write_neural_header_file` generates the c header file for the model
to be executed on SpiNNaker.

:func:`SynapseModel.write_decode_synaptic_word_function` generates the function translating
a synaptic word for the model to be executed on SpiNNaker.

:func:`NeuralModel.write_neural_c_file` and :func:`NeuralModel.write_neural_header_file`
can be used to generate c code to be executed on SpiNNaker.

.. moduleauthor:: Francesco Galluppi email: francesco.galluppi@cs.man.ac.uk

"""
import pacman
import os
import math
import pyNN.spiNNaker as p
import model_templates

DEBUG = False

dao = p.setup(db_name='/tmp/model_creator.db')

class NeuralModel():
    """
    Initialises a new neural model:
    
    :param model_name: A string identifiying the Neural Model class in PyNN
    :type model_name: str.
    :param default_neurons_per_core: The default number of neurons of this type \
    modelled by a single core
    :param image_name: (str) the name of the associated aplx image

    """    
    def __init__(self, model_name=None, default_neurons_per_core=None, \
        image_name=None, generate_sdram_connectivity=True):
        
        self.model_name = model_name
        self.default_neurons_per_core = default_neurons_per_core
        self.image_name = image_name
        if self.image_name == None:
            self.image_name = model_name + ".aplx"
        self.id = None
        self.num_parameters = 0
        self.parameters = list()
        self.synapses = dict()
        self.generate_sdram_connectivity = 1
        
    def add_parameter(self, param_name, param_type, translation, default=0, translate=True):
        """
        Function used to add a parameter to a neural model. Requires the translations
        string for each parameter.
        
        :param param_name: (str) The name of the parameter (eg. v_thresh)
        :param param_type: (char) A python format character identifying the type \
        of parameter (int, short, uint, etc.) see http://docs.python.org/2/library/struct.html#format-characters
        :param translation: (str) A translation string used to translate the parameter.

        .. note::        
          The macro *value* can be used to refer to the parameter itself. Other parameters
          for the same neurons can be accessed with the macro *param[param_name][i]*, 
          where param_name is the name of the parameter to refer. 
 
        Examples:: 
        
          n.add_parameter('i_offset', param_type = 'i', translation = 'int(value)*65536')
          n.add_parameter('cm', param_type = 'i', \
translation = "int(params['tau_m'][i]/params['cm'][i]*65536)")
       
        
        """
    
        if translate:   self.num_parameters += 1
        neural_parameter = {
            'param_name'    : param_name,
            'param_type'    : param_type,
            'translation'   : translation,
            'position'      : self.num_parameters,
            'default'       : default
            }
        

        self.parameters.append(neural_parameter)
        
    def add_synapse(self, synapse_name):
        """
        Creates a SynapseModel object and adds it to the NeuralModel.
        
        :param synapse_name: the name of the synapse type (eg. 'excitatory')
        """
        self.synapses['%s' % synapse_name] = SynapseModel(synapse_name, self)
        
    def write_model_to_db(self):
        """
        Function used to finalise the neural model to the model_library.
        
        :returns:  int -- the id of the new neural model just inserted.
        """
#        self.id = dao.insert_neural_model(self)
        
        print "\nInserting Neural Parameters..."
#        for i in self.parameters:  print i


        for s in self.synapses: 
            print "\nInserting %s synapse..." % s
            self.calculate_synapse_types(self.synapses[s])
            self.synapses[s].write_synaptic_parameters()
#            self.synapses[s].write_decode_synaptic_word_function()

                    
        
    def calculate_synapse_types(self, s):
        bits_needed = int(math.ceil(math.log(len(self.synapses),2)))
        s.add_parameter('type', bits_needed, 0, 0)
    
    def write_buffer_post_synaptic_potentials(self):
        
        synapse_switch_cases = ""
        for synapse in self.synapses:
            s = self.synapses[synapse]
            synapse_switch_cases += model_templates.switch_synapses.substitute( \
                    weight_shift = s.parameters['weight']['shift'],
                    weight_scale = s.parameters['weight']['number_of_decimal_bits'],
                    weight_mask = s.parameters['weight']['mask'],                
                    id_shift = s.parameters['id']['shift'],
                    id_mask = s.parameters['id']['mask'],
                    delay_shift = s.parameters['delay']['shift'],
                    delay_mask = s.parameters['delay']['mask'],
                    delay_offset = -s.parameters['delay']['offset'],
                    synapse_name = s.synapse_name,
                    flag = s.id                             
                    )
                
        return model_templates.buffer_post_synaptic_potentials.substitute( \
                type_shift = s.parameters['type']['shift'],
                type_mask = s.parameters['type']['mask'],
                switch_synapses = synapse_switch_cases)
                
    def write_neural_c_file(self, filename=None):
        """
        Writes a neural c file.
        
        :param filename: (str) if passed will create a file to the path specified
        """

        out = model_templates.neural_c_file.substitute( \
            model_name = self.model_name,
            buffer_post_synaptic_potentials = self.write_buffer_post_synaptic_potentials(),
            decode_synaptic_word = self.synapses.itervalues().next().write_decode_synaptic_word_function()
            )
        if filename == None:    return out
        else: 
            f = open(filename, 'w')
            f.write(out)
            f.close()        

                
                
    def write_pynn_bindings(self, filename=None):
        """
        Function used to generate the pynn bindings to be loaded in standardmodels.
        
        :param filename: (str) if passed will create a file to the path specified
        """
        cell_params = [ n['param_name'] for n in  self.parameters ]
        defaults = dict()
        synapses = dict()
        for s in self.synapses:
            synapses[s] = self.synapses[s].id
        
        for d in self.parameters:
            defaults[d['param_name']] = d['default']

        out = model_templates.cell_bindings_pynn.substitute( \
            cell_name = self.model_name,
            cell_params = cell_params,
            defaults = defaults,
            synapses = synapses)
        
        if filename == None:    return out
        else: 
            f = open(filename, 'w')
            f.write(out)
            f.close()

                            
    def write_neural_header_file(self, filename=None):
        """
        Writes a neural header file.
        
        :param filename: (str) if passed will create a file to the path specified
        """
        parameters = ""
        for p in self.parameters:
            parameters += model_templates.neural_parameter.substitute( \
                param_name = p['param_name'],
                param_type = translate_types_from_python_to_c(p['param_type']),
                param_translation = p['translation'])
        out = model_templates.neural_header_file.substitute( \
            parameters = parameters,
            model_name = self.model_name.upper())
        if filename == None:    return out
        else: 
            f = open(filename, 'w')
            f.write(out)
            f.close()        
            
    def write_sql_neural_parameters(self):
        """
        Returns the sql bindings for neural parameters        
        """

        sql_out = ""
        for p in self.parameters:
            sql_out += model_templates.insert_neural_parameter_query.substitute( \
                param_name = p['param_name'],
                param_type = p['param_type'],
                param_translation = p['translation'],
                param_position = p['position'],
                model_name = self.model_name,
                generate_sdram_connectivity = self.generate_sdram_connectivity
                )
        return sql_out
        
                
    def write_sql_bindings(self, filename=None):
        """
        Writes all the sql bindings for PACMAN
        
        :param filename: (str) if passed will create a file to the path specified
        """

        out_sql_script = "-- SQL bindings for model %s" % self.model_name
        
        out_sql_script += "\n-- Neural model into cell_types:"
        out_sql_script += model_templates.insert_neural_model_query.substitute( \
            name = self.model_name,
            max_nuro_per_fasc = self.default_neurons_per_core,
            image_name = self.image_name,
            generate_sdram_connectivity = self.generate_sdram_connectivity)
            
        out_sql_script += "\n-- Neural parameters in cell_parameters:"        
        out_sql_script += self.write_sql_neural_parameters()
        
        for s in self.synapses:
            out_sql_script += self.synapses[s].write_sql_synapses()
        if filename == None:
            return out_sql_script
        else:
            f = open(filename, 'w')
            f.write(out_sql_script)
            f.close
            return 0
        
class SynapseModel():
    """
    Initialises a new synapse model.
    
    :param synapse_name: (str) A string identifiying the Synapse class in PyNN
    :param neural_model: (:class:`NeuralModel`) the neural model associated with \
    the synapse
    
    The SynapseModel object has a dictionary of parameters (weight, delay, etc.)
    that can be added using the add_parameter function.    
    """
    def __init__(self, synapse_name, neural_model):
        self.synapse_name = synapse_name
        self.neural_model = neural_model
        self.length = 0
        self.parameters = dict()
        self.id = len(neural_model.synapses)
        self.negative_weight = False

    def add_parameter(self, name, 
        number_of_integer_bits, number_of_decimal_bits, offset, negative=False):
            """
            Add a parameter to the SynapseModel:
            
            :param name: (str) the name of the parameter (eg. weight)
            :param number_of_decimal_bits: (int) precision of the exponent
            :param number_of_decimal_bits: (int) precision of the mantissa
            :param offset: (int) offset for the parameter
            :param negative: (bool) sets the sign of the parameter
            
            """
            parameter = {'name'  : name, 
                            'number_of_integer_bits' : number_of_integer_bits, 
                            'number_of_decimal_bits' : number_of_decimal_bits,
                            'offset' : offset}
            parameter['mask'] = ((1 << number_of_decimal_bits \
                                    + number_of_integer_bits)-1)
            parameter['scale'] = 2**number_of_decimal_bits
                        
            self.length += number_of_decimal_bits + number_of_integer_bits
            if self.length > 32:    
                raise SystemError("too many bits in your synapse while evaluating parameter %s " + name) 

            if negative:    parameter['scale'] *= -1            
            
            self.parameters[name] = parameter
            
            return None
            
    def set_plasticity_bit(self):
        self.add_parameter('stdp_on', 1, 0, 0)
        
    def set_neuron_id_bits(self, bits):
        self.add_parameter('id', bits, 0, 0)
        
    def write_synaptic_parameters(self):
        """
        Computes the PACMAN synaptic translations for the parameters to be inserted
        in the model library
        """
#        for p in self.parameters:   print p
                    
        if DEBUG:   print "name:", self.synapse_name
        if DEBUG:   print "flag:", self.id
        if DEBUG:   print "model_id:", self.neural_model.id
        
        shift = 0
        self.translations = list()
        for p in ('delay', 'id', 'weight', 'stdp_on', 'type'):        
            try:
                param = self.parameters[p]
            except (KeyError):
                self.add_parameter(p, 0, 0, 0)
                param = self.parameters[p]

            param['shift'] = shift
            if DEBUG:   print p, "[%d, %d, %s, %d]" % ( param['offset'],
                                            param['scale'],
                                            param['mask'],
                                            param['shift'])
            
            self.translations.append([ param['offset'],
                                            param['scale'],
                                            param['mask'],
                                            param['shift']])
                                                              
            shift += param['number_of_decimal_bits'] + param['number_of_integer_bits']
        
    
    
    def write_decode_synaptic_word_function(self):
        return model_templates.decode_synaptic_word.substitute( \
                stdp_on_shift = self.parameters['stdp_on']['shift'],
                stdp_on_scale = self.parameters['stdp_on']['scale'],
                stdp_on_mask = hex(self.parameters['stdp_on']['mask']),
                weight_shift = self.parameters['weight']['shift'],
                weight_scale = self.parameters['weight']['number_of_decimal_bits'],
                weight_mask = hex(self.parameters['weight']['mask']),
                id_shift = self.parameters['id']['shift'],
                id_mask = hex(self.parameters['id']['mask']),
                type_shift = self.parameters['type']['shift'],
                type_mask = hex(self.parameters['type']['mask']),
                delay_shift = self.parameters['delay']['shift'],
                delay_mask = hex(self.parameters['delay']['mask']),
                delay_offset = -self.parameters['delay']['offset']                                
                )
                
    def write_sql_synapses(self):
        return model_templates.insert_synapse_query.substitute( \
            model_name = self.neural_model.model_name,
            synapse_name = self.synapse_name,
            synapse_flag = self.id,
            translation = self.translations
            )
        
                
                                

def translate_types_from_python_to_c(type_name):
    if type_name == "i":    return "int"
    elif type_name == "I":    return "uint"
    elif type_name == "h":    return "short"
    elif type_name == "H":    return "ushort"    
        
    


