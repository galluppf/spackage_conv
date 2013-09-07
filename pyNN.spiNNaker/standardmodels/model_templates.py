from string import Template

decode_synaptic_word = Template("""
void decode_synaptic_word (unsigned int word, synaptic_word_t *decoded_word) 
{ 
    decoded_word -> stdp_on = (word >> $stdp_on_shift) & $stdp_on_mask;
    decoded_word -> synapse_type = (word >> $type_shift) & $type_mask; 
    decoded_word -> weight = (word >> $weight_shift) & $weight_mask; 
    decoded_word -> index = (word >> $id_shift) & $id_mask; 
    decoded_word -> delay = $delay_offset + ((word >> $delay_shift) & $delay_mask); 
    decoded_word -> weight_scale = $weight_scale; 
}
""")

cell_bindings_pynn = Template("""
class $cell_name(cells.IF_curr_exp): 
    __name__ = "$cell_name" 
    cell_params = $cell_params
    synapses  =   $synapses
    default_parameters = $defaults

    def __init__(self): 
        self.__name__ = __name__ 

""")

buffer_post_synaptic_potentials = Template("""
void buffer_post_synaptic_potentials(void *dma_copy, uint row_size)
{
    uint time = spin1_get_simulation_time();
    synaptic_row_t *synaptic_row = (synaptic_row_t *) dma_copy;
    
    for(uint i = 0; i < row_size; i++)
    {
        
        uint synapse_type = (word >> $type_shift) & $type_mask; 

        switch(synapse_type)
        {
            $switch_synapses
            default: break;
        }
    }
}
""")

switch_synapses = Template("""
            case $flag: 
                uint index = index = (word >> $id_shift) & $id_mask; 
                uint weight = (word >> $weight_shift) & $weight_mask; 
                uint delay = $delay_offset + ((word >> $delay_shift) & $delay_mask); 
                uint arrival = time + delay;
                psp_buffer[index].$synapse_name[arrival % PSP_BUFFER_SIZE] += (weight << (16 - $weight_scale)); 
            break;
""")


neural_header_file = Template("""
#ifndef __MODEL_${model_name}_H__
#define __MODEL_${model_name}_H__

#define LOG_P1                  (8)
#define LOG_P2                  (16)
#define P1                      (1 << LOG_P1)
#define P2                      (1 << LOG_P2)


typedef struct
{
$parameters
} neuron_t;

#endif
""")

neural_parameter = Template("""    $param_type ${param_name};     // ${param_translation}\n""")

neural_c_file = Template("""#include "spin1_api.h"
#include "spinn_io.h"
#include "spinn_sdp.h" // Required by comms.h

#include "comms.h"
#include "config.h"
#include "dma.h"
#include "model_general.h"
#include "model_${model_name}.h"
#include "recording.h"

#ifdef STDP
#include "stdp.h"
#endif

#ifdef STDP_SP
#include "stdp_sp.h"
#endif

// Neuron data structures
uint num_populations;
population_t *population;
psp_buffer_t *psp_buffer;


$buffer_post_synaptic_potentials


void timer_callback(uint ticks, uint null)
{

    if(ticks >= app_data.run_time)
    {
        io_printf(IO_STD, "Simulation complete.\n");
        spin1_stop();
    }

    for(uint i = 0; i < num_populations; i++)
    {
        neuron_t *neuron = (neuron_t *) population[i].neuron;
        psp_buffer_t *psp_buffer = population[i].psp_buffer;

        for(uint j = 0; j < population[i].num_neurons; j++, neuron_count++)
        {
            psp_buffer_t *curr_psp = &psp_buffer[j];
            
                // ... insert your neural model code here ...

                // ... and emit a spike if necessary
                if(some condition)
                {
                    uint key = spin1_get_chip_id() << 16 |
                               app_data.virtual_core_id << 11 |
                               population[i].id |
                               j;

                    spin1_send_mc_packet(key, NULL, NO_PAYLOAD);

                }
            }

            // Recording:
                    
            // Optionally record voltage and current trace
            if(population[i].flags & RECORD_STATE_BIT)
            {
                record_v[population[i].num_neurons * (ticks) + j] = (short) (neuron[j].v >> LOG_P1);
            }
            
            if(population[i].flags & RECORD_GSYN_BIT)
            {
                record_i[population[i].num_neurons * (ticks) + j] = (short) (current >> LOG_P1);
            }            
            

        } // Cycle neurons in population i 
                                   
    }   // Cycle populations
                
}




void configure_recording_space()
{
    record_v = (short *) 0x72136400 + 0x200000 * (app_data.virtual_core_id - 1);
    record_i = (short *) 0x7309a400 + 0x200000 * (app_data.virtual_core_id - 1);
    
    // cleaning
    for (uint i = 0; i < 0x100000; i++)    record_v[i] = 0;
    for (uint i = 0; i < 0x100000; i++)    record_i[i] = 0;
    
    record_spikes = (uint *) 0x72040000;
    for(uint i = 0; i < 1000; i++) record_spikes[i] = 0; //TODO improve 

    // spike count

    int *spike_count_dest = NULL;
    spike_count_dest = (int *) spin1_malloc(num_populations);
    spike_count =  (int *) spike_count_dest;
    for(uint i = 0; i < num_populations; i++) spike_count[i] = 0; //TODO improve    
    
}

$decode_synaptic_word
""")

insert_neural_parameter_query = Template("""
INSERT INTO 
cell_parameters (model_id, param_name, type, translation, position) 
VALUES (
    (SELECT id FROM cell_types where name = '$model_name'), 
    '$param_name', '$param_type', "$param_translation", $param_position);
""")

insert_neural_model_query = Template("""
INSERT INTO cell_types (name, image_name, max_nuro_per_fasc)
VALUES ('$name', '$image_name', $max_nuro_per_fasc);
""")

insert_synapse_query = Template("""INSERT INTO 
synapse_types (cell_type_id, synapse_name, synapse_flag, translation) 
VALUES (
    (SELECT id FROM cell_types where name = '$model_name'), 
    '$synapse_name', '$synapse_flag', '$translation');
""")

