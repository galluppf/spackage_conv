#!/usr/bin/python
"""
Interface to translate nengo scripts into PACMAN. Cycles nengo nodes and connections iin nengo_values.py and builds PACMAN Populations and Projections

Contains the interfaces to PACMAN:
- cell type, populations, projections
- sets the number of neurons for each neural type (can be overwritten with a constraint)
- sets the runtime
- cycles populations, evaluating if thei are input (encoding), neural (lif32) or output (lif32+nef decoder) populations"
- cycles projections

Author: Terry Stewart, Francesco Galluppi
Email:  francesco.galluppi@cs.man.ac.uk
"""

import sys, os
import pyNN.spiNNaker as spinn
import nengo_values as nengo
import math
import pickle
import numpy
import pacman

NOLOG = 0
LOGDEBUG = 1
LOGINFO = 2

LOGLEVEL = LOGINFO


#### DEFAULTS
tau_syn = 100                # default value
neurons_per_core = 100       # default value

#### COUNTERS
n_outs = 0                  # output counter for placing NEF_out populations in chip 0,0


# Setting up the connection with the DB and the number of cells
spinn.setup(db_name = os.path.abspath('%s/nengo_model.sqlite' % pacman.BINARIES_DIRECTORY))

spinn.get_db().set_number_of_neurons_per_core('NEF_out_2d', neurons_per_core*2)        # this will set one population per core
#spinn.get_db().set_number_of_neurons_per_core('IF_curr_exp_32', neurons_per_core)        # this will set one population per core
spinn.get_db().set_number_of_neurons_per_core('IF_NEF_input_2d', neurons_per_core*2)        # this will set one population per core


# PACMAN INTERFACES

class general_cell():
    """
    PACMAN Interface class giving a cell type with parameters, class, size, label, id and mapping constraints
    """
    def __init__(self, cellname):
        self.__name__ = cellname

class population_interface():
    """
    PACMAN Population interface specifying cellparams, class, label and mapping constraints
    """
    def __init__(self, size, cellparams=None, cellclass=None, label=None, constrain=None):
        self.cellparams = cellparams
        self.cellclass = cellclass
        self.size = size
        self.label = label
        self.id = None
        self.constrain=constrain
        
class general_method():
    """
    PACMAN interface for connection method interface 
    """
    def __init__(self, methodname):
        self.__name__ = methodname

class projection_interface():
    """
    PACMAN Interface for Projections
    """
    def __init__(self,presynaptic_population,postsynaptic_population, parameters, method_name, target):
        pass
        self.presynaptic_population = presynaptic_population
        self.postsynaptic_population = postsynaptic_population
        self.method = general_method(method_name)
        self.parameters = parameters
        self.size = 0   # TODO
        self.synapse_dynamics = None
        self.plasticity_id = 0
        self.target=target
        self.label = '%s_to_%s_proj' % (presynaptic_population.label, postsynaptic_population.label)



#### NEURAL TYPE AND PARAMETERS INTERFACES

IF_NEF_1D = general_cell('IF_NEF_1D')
IF_NEF_2D = general_cell('IF_NEF_2D')


cell_params_nef_enc = {'tau_m'     : 20,
                'v_init'        : 0,
                'v_rest'        : 0,   
                'v_reset'       : 0,  
                'v_thresh'      : 1,
                'tau_syn_E'     : tau_syn,
                'tau_syn_I'     : tau_syn,
                'tau_refrac'    : 2,
                'tau_refrac_clock'     : 0,
                'resistance'    : 1,
                'value_current':0,}

NEF_OUT_1D = general_cell('NEF_OUT_1D')
NEF_OUT_2D = general_cell('NEF_OUT_2D')

cell_params_nef_dec = {'v_init':0, 'v_rest':0}

cell_params_lif = {'tau_m'     : 20,
                'v_init'        : 0,
                'v_rest'        : 0,   
                'v_reset'       : 0,  
                'v_thresh'      : 1,
                'tau_syn_E'     : tau_syn,
                'tau_syn_I'     : tau_syn,
                'tau_refrac'    : 2,
                'tau_refrac_clock'     : 0,
                'resistance'    : 1}              
## app_frame lif
#cell_params_lif_app = {'tau_m'     : 20,
#                'cm'            : 1
#                'v_init'        : 0,
#                'v_rest'        : 0,   
#                'v_reset'       : 0,  
#                'v_thresh'      : 1,
#                'tau_syn_E'     : tau_syn,
#                'tau_syn_I'     : tau_syn,
#                'tau_refrac'    : 2,
#                'tau_refrac_clock'     : 0,
#                'resistance'    : 1}              
                        
LIF_32 = general_cell('IF_curr_exp_32')


# Cycling populations (nengo nodes)
populations = dict()        # used for projections

for p in nengo.pop:    
    node = nengo.pop[p]
    pop_size = len(node['bias'])

    # if the node is not sending populations then we decode it and will set up a LIF32 + NEF_OUT population
    is_output_population = (len([ i for i in nengo.proj if i[0]==p]) == 0)
    
    # if the node is marked as an input node
    if p in nengo.inputs:
        print "[ nengo_pacman_interface ] : Creating IF_NEF encoding population for", p, "with dimension", node['dimensions']

        params = cell_params_nef_enc
        params['i_offset'] = node['bias']

        for d in range(node['dimensions']):            
#            print "encoders %s : %f - %f" % (p, min(encoders), max(encoders))
#            print "bias %s : %f - %f" % (p, min(params['i_offset']), max(params['i_offset']))
            params['encoder_%d' %d] = node['encoders'][d]

        pop = population_interface(size=pop_size, cellparams=params, cellclass=eval("IF_NEF_%dD" % node['dimensions']), label=p)
        
        pop.id = spinn.simulator.db_run.insert_population(pop)
        spinn.simulator.db_run.set_mapping_constraint(pop.id, {'x':0, 'y':0, 'p': 1+n_outs})		# core n. 1 is configuring the routing tables!
        n_outs += 1
        
        populations[p]=pop
#        pop_source = pop

    # if the node is an output node
    elif is_output_population:
        print "[ nengo_pacman_interface ] : Creating LIF32 + NEF_OUT decoding population for", p, "with dimension", node['dimensions']

        params = cell_params_lif
        params['i_offset'] = node['bias']    
        
        # FIXME for multiple taus    
        params['tau_syn_E'] = node['taus'][0]
        params['tau_syn_I'] = node['taus'][0]
                
        pop_lif_32 = population_interface(size=pop_size, cellparams=params, cellclass=LIF_32, label=p)
        pop_lif_32.id = spinn.simulator.db_run.insert_population(pop_lif_32)          

        populations[p]=pop_lif_32

        if p in nengo.neurons_per_core:
            print "[ nengo_pacman_interface ] : updating constraints for population %s: %d" % (p, nengo.neurons_per_core[p])
            spinn.simulator.db_run.generic_update(  'populations', 
                                                    'splitter_constraint=%d' % nengo.neurons_per_core[p], 
                                                    'id=%d' % pop_lif_32.id)        

        # create NEF_OUT population for decoding    
        params = cell_params_nef_dec    
        for d in range(node['dimensions']):            
            params['decoder_%d' % d] = node['decoders'][d]



        pop_nef_out = population_interface( size=pop_size, 
                                            cellparams=params, 
                                            cellclass=eval("NEF_OUT_%dD" % node['dimensions']), 
                                            label='decoder_%s' % p)
                                            
        pop_nef_out.id = spinn.simulator.db_run.insert_population(pop_nef_out)          
        spinn.simulator.db_run.set_mapping_constraint(pop_nef_out.id, {'x':0, 'y':0, 'p':1+n_outs})

        n_outs += 1
                
        # make projection between the LIF32 and the NEF_OUT population
        # OneToOneConnector using a list
#        proj = projection_interface(pop_source, pop, '{\'weights\':1, \'delays\':1}',method_name='OneToOneConnector', target='excitatory')
        conn_list = [ (x, x, 1, 1) for x in range(pop_size)]
        
        conn_list_array = numpy.ones((pop_size,4))
        conn_list_array[:,0] = numpy.arange((pop_size))
        conn_list_array[:,1] = numpy.arange((pop_size))

    
        projection = projection_interface(pop_lif_32, pop_nef_out, 
                                '', # list is saved to a file
                                method_name='FromListConnector', target='excitatory')
        proj_id = spinn.simulator.db_run.insert_projection(projection)
        
#        print 'dumping proj', proj_id
        pickle.dump(conn_list_array, open( "/tmp/proj_%d.raw" % proj_id, "wb" ) )   
        
        
        if p in nengo.robot_outputs:
            print "[ nengo_spinnaker_interface_2d ] : flagging population %s as a robotic output" % (p)
            spinn.simulator.db_run.insert_probe(pop_nef_out.id, 'VALUE', 'ROBOT_OUTPUT')
        
        
    else:
        print "[ nengo_pacman_interface ] : Creating LIF32 population for", p, "with dimension", node['dimensions']
        params = cell_params_lif
        params['i_offset'] = node['bias']    
        
        # FIXME for multiple taus    
        params['tau_syn_E'] = node['taus'][0]
        params['tau_syn_I'] = node['taus'][0]
                
        pop_lif_32 = population_interface(size=pop_size, cellparams=params, cellclass=LIF_32, label=p)
        pop_lif_32.id = spinn.simulator.db_run.insert_population(pop_lif_32)          

        if p in nengo.neurons_per_core:
            print "[ nengo_pacman_interface ] : updating constraints for population %s: %d" % (p, nengo.neurons_per_core[p])
            spinn.simulator.db_run.generic_update(  'populations', 
                                                    'splitter_constraint=%d' % nengo.neurons_per_core[p], 
                                                    'id=%d' % pop_lif_32.id)        
        populations[p]=pop_lif_32

# CYCLING PROJECTIONS
for projection in nengo.proj:
#    print projection
    source_pop = populations[projection[0]]
    dest_pop = populations[projection[1]]
    conn_list_exc = []
    conn_list_inh = []    
    weights = nengo.proj[projection]['w']
    
    if LOGLEVEL >= LOGDEBUG: print "[ nengo_pacman_interface ] : range weights %s_%s : %f - %f" % (projection[0], projection[1], min(min(weights)), max(max(weights)))
#    assert abs(min(min(weights))) >  math.pow(2,-16), "weight %f out of min precision range" % min(min(weights))
#    assert abs(max(max(weights))) <  math.pow(2,4), "weight %f out of max precision range" % max(max(weights))


#   splitting into 2 projections
    for i in range(source_pop.size):
        for j in range(dest_pop.size):
    #        print [i, j, weights[i][j], 1]
            if weights[i][j] > 0:         
                conn_list_exc.append([i, j, weights[i][j], 1])
            elif weights[i][j] < 0:         
                conn_list_inh.append([i, j, -weights[i][j], 1])
                            
    conn_list_exc_array = numpy.array(conn_list_exc)
    conn_list_inh_array = numpy.array(conn_list_inh)
            
    proj_exc = projection_interface(source_pop, dest_pop, 
                                '%s' % '',
                                method_name='FromListConnector', target='excitatory')
    proj_inh = projection_interface(source_pop, dest_pop, 
                                '%s' % '',
                                method_name='FromListConnector', target='inhibitory')


    if len(conn_list_exc_array > 0):
        proj_id = spinn.simulator.db_run.insert_projection(proj_exc)
        pickle.dump(conn_list_exc_array, open( "/tmp/proj_%d.raw" % proj_id, "wb" ) )   
    
    if len(conn_list_inh_array > 0):
        proj_id = spinn.simulator.db_run.insert_projection(proj_inh)        
        pickle.dump(conn_list_inh_array, open( "/tmp/proj_%d.raw" % proj_id, "wb" ) )
        

        
#### dynamic splitting constraints evaluation            
def run(db_run, runtime):
    """ 
    Commits the DB and runs the simulation.
    Switches on what to run are in the nengo_pacman_interface section of pacman.cfg:
    """
#    global original_pynn_script_directory
    original_script_directory = os.getcwd()
    
    print "[ nengo_pacman_interface ] : Running simulation - connection  with the DB will be now committed"
    db_run.set_runtime(runtime)
    db_run.close_connection()   # FIXME why do I need to close and reopen?
    
    
    if pacman.pacman_configuration.getboolean('nengo_interface', 'run_pacman'):
        print "\n[ nengo_pacman_interface ] : Running pacman from", os.path.dirname(pacman.PACMAN_DIR)
        os.chdir(pacman.PACMAN_DIR)
#        os.system('./pacman.sh %s' % db_run.db_abs_path)
#        os.system('./pacman %s' % db_run.db_abs_path)        
        # FIXME FIXME FIXME
        db = pacman.load_db(db_run.db_abs_path)
        db.clean_part_db()              # cleans the part_* tables
#        pacman.run_pacman(db)
        pacman.run_pacman(db, simulator='nengo')

        print "[ nengo_pacman_interface ] closing db...."
        db.close_connection()       # will close the connection to the db and commit the transaction    


    if pacman.pacman_configuration.getboolean('nengo_interface', 'run_simulation'):
        board_address = pacman.pacman_configuration.get('board', 'default_board_address')
        if pacman.pacman_configuration.getboolean('nengo_interface', 'run_pacman') == False:
            print "[ nengo_pacman_interface ] : cannot run simulation before pacman. change your %s file" % pacman_cfg_filename
            quit(1)
            
        print "\n[ nengo_pacman_interface ] : Running simulation on board %s (%s/tools/run.sh %s)\n" % (board_address, os.path.dirname(pacman.PACMAN_DIR), board_address)

        os.chdir(pacman.PACMAN_DIR)
        os.chdir(os.pardir)        
        os.chdir('tools')
        os.system('./run.sh %s' % board_address)

#        print "\n[ nengo_pacman_interface ] : Waiting for simulation on board %s on to finish..." % (board_address)
#        pacman.wait_for_simulation()    # will wait for the simulation to finish it run_simulation is set to true in pacman.cfg
#        print "[ nengo_pacman_interface ] : ...done!\n"
#        os.chdir(pacman.original_pynn_script_directory)

run(spinn.simulator.db_run, nengo.runtime)

