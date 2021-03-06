from pyNN.standardmodels import cells, build_translations, ModelNotAvailable
from pyNN import errors

class IF_curr_exp(cells.IF_curr_exp):
    """Leaky integrate and fire model with fixed threshold and
    decaying-exponential post-synaptic current. (Separate synaptic currents for
    excitatory and inhibitory synapses."""
    __name__ = "IF_curr_exp"
    cell_params = ['v_rest', 'v_reset', 'cm', 'tau_m', 'tau_refrac', 'tau_syn_E', 'tau_syn_I', 'v_thresh', 'i_offset']
    synapses  =   {'excitatory': 0, 'inhibitory': 1}
    default_parameters = {'tau_refrac_clock' : 0, 'v_init': -65, 'cm':1, 'v_rest' : -65, 'tau_m' : 20, 'i_offset' : 0}
    def __init__(self):
        self.__name__ = __name__
        pass

        
class IF_cond_exp(cells.IF_cond_exp):
    """Leaky integrate and fire model with fixed threshold and
    decaying-exponential post-synaptic conductances. (Separate synaptic currents for
    excitatory and inhibitory synapses."""
    __name__ = "IF_curr_exp"
    cell_params = ['v_rest', 'v_reset', 'cm', 'tau_m', 'tau_refrac', 'tau_syn_E', 'tau_syn_I', 'v_thresh', 'i_offset', 'e_rev_E', 'e_rev_I']
    synapses  =   {'excitatory': 0, 'inhibitory': 1}
    default_parameters = {'tau_refrac_clock' : 0, 'v_init': -65, 'cm':1, 'v_rest' : -65, 'tau_m' : 20, 'i_offset' : 0}
    def __init__(self):
        self.__name__ = __name__
        pass


class IF_curr_exp_32(cells.IF_curr_exp):
    """Leaky integrate and fire model with fixed threshold and
    decaying-exponential post-synaptic current. (Separate synaptic currents for
    excitatory and inhibitory synapses."""
    __name__ = "IF_curr_exp"
    cell_params = ['v_rest', 'v_reset', 'cm', 'tau_m', 'tau_refrac', 'tau_syn_E', 'tau_syn_I', 'v_thresh', 'i_offset']
    synapses  =   {'excitatory': 0, 'inhibitory': 1}
    default_parameters = {'resistance' : 1, 'tau_refrac_clock' : 0, 'v_init': -75, 'i_offset' : 0}
    def __init__(self):
        self.__name__ = __name__
        pass


class IZK_curr_exp(cells.IF_curr_exp):
    cell_params = []
    default_parameters = {'v_init' : -75, 'u_init' : 0, 'i_offset' : 0}
    __name__ = "IZK_curr_exp"
    def __init__(self):
        self.__name__ = "IZK_curr_exp"
        pass


class Dummy(cells.IF_curr_exp):
    cell_params = []
    default_parameters ={}
    __name__ = "dummy"
    def __init__(self):
        self.__name__ = "dummy"
        pass


class SpikeSourceArray(cells.SpikeSourceArray):
    """Spike source generating spikes at the times given in the spike_times array."""
    cell_params = ['spike_times']
    default_parameters ={}
    cell_params = []
    synapses  =   {'excitatory': 0, 'inhibitory': 1}

    def __init__(self):
        self.__name__ = "SpikeSourceArray"
        pass


#class SpikeSource(cells.SpikeSourceArray):
#    """Spike source generating spikes at the times given in the spike_times array."""
#    cell_params = ['spike_times']
#    default_parameters ={}
#    cell_params = []
#    synapses  =   {'excitatory': 0, 'inhibitory': 1}

#    def __init__(self):
#        self.__name__ = "SpikeSourceLive"
#        pass

#class SpikeSink(cells.SpikeSourceArray):
#    cell_params = []
#    default_parameters ={}
#    __name__ = "spike_sink"
#    def __init__(self):
#        self.__name__ = "spike_sink"
#        pass

class SpikeSourceArray(cells.SpikeSourceArray):
    """Spike source generating spikes at the times given in the spike_times array."""
    cell_params = ['spike_times']
    default_parameters ={}
    cell_params = []
    synapses  =   {'excitatory': 0, 'inhibitory': 1}

    def __init__(self):
        self.__name__ = "SpikeSourceArray"
        pass


class SpikeSourcePoisson(cells.SpikeSourcePoisson):
    """Spike source generating spikes according to a poisson process that determines the inter-spike time"""
    cell_params = ['rate','start','duration','time_to_next_spike']
    default_parameters ={'start' : 0, 'duration' : 1000000000, 'time_to_next_spike' : 1000000001}
    cell_params = []
    synapses  =   {'excitatory': 0, 'inhibitory': 1}

    def __init__(self):
        self.__name__ = "SpikeSourcePoisson"
        pass


class SpikeSource(cells.SpikeSourceArray):
    """Spike source generating spikes at the times given in the spike_times array."""
    cell_params = ['spike_times']
    default_parameters ={}
    cell_params = []
    synapses  =   {'excitatory': 0, 'inhibitory': 1}

    def __init__(self):
        self.__name__ = "SpikeSourceLive"
        pass


class Recorder(cells.SpikeSourceArray):
    cell_params = []
    default_parameters ={}
    __name__ = "Recorder"
    def __init__(self):
        self.__name__ = "app_monitoring"
        pass


class IF_NEF_input(cells.IF_curr_exp):
    cell_params = []
    __name__ = "IF_NEF_input"
    default_parameters = {'resistance' : 1, 'tau_refrac_clock' : 0, 'v_init': -75, 'value_current' : 0}
    def __init__(self):
        self.__name__ = "IF_NEF_input"
        pass


class IF_NEF_output(cells.IF_curr_exp):
    cell_params = []
    default_parameters = {}
    __name__ = "IF_NEF_output"
    def __init__(self):
        self.__name__ = "IF_NEF_output"
        pass
        
class ProxyNeuron(cells.IF_curr_exp):
    """
    The proxy neuron cell type operates a translation on a MC packet (x_source, y_source) with (x_local, y_local)
    Used in robotic applications for mapping sensors.
    ProxyNeuron can only live in row 0 (y=0) of the system for the moment.
    It needs to have as many neurons as the sensor it's mapping
    """
    cell_params = []
    default_parameters ={"x_source":255, "y_source":255}
    __name__ = "proxy"
    def __init__(self):
        self.__name__ = "proxy"
        pass



class convolution(cells.IF_curr_exp): 
    __name__ = "convolution" 
    cell_params = ['v', 'time_last_input_spike', 'time_last_output_spike', 'tau_m', 'v_thresh', 'v_reset', 'v_rest', 'tau_refrac', 'size_map_x', 'size_map_y']
    synapses  =   {'excitatory': 0, 'inhibitory': 1}
    default_parameters = {'tau_refrac': 0, 'size_map_y': 0, 'tau_m': 16, 'time_last_input_spike': 0, 'v_thresh': -60.0, 'v_reset': -60.0, 'v': 0, 'size_map_x': 0, 'time_last_output_spike': 0, 'v_rest': -60.0}

    def __init__(self): 
        self.__name__ = __name__ 

