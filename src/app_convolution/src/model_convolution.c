#include "spin1_api.h"
#include "spinn_io.h"
#include "spinn_sdp.h" // Required by comms.h

#include "comms.h"
#include "config.h"
#include "dma.h"
#include "model_general.h"
#include "model_convolution.h"
#include "recording.h"

// Neuron data structures
uint num_populations;
population_t *population;
psp_buffer_t *psp_buffer;


void process_incoming_packets(uint null0, uint null1) {
    while(!mc_packet_buffer_empty())
    {
        uint key = mc_packet_buffer.buffer[mc_packet_buffer.start];
        mc_packet_buffer.start = (mc_packet_buffer.start + 1) % MC_PACKET_BUFFER_SIZE;
        
        int * kernel = NULL;
        ushort kernel_size = 0;
        uint kernel_displacement;
        uint kernel_geometry;
        
        io_printf(IO_STD, "Time: %d key: 0x%x\n", spin1_get_simulation_time(), key);
        for(uint i = 0; synapse_lookup[i].core_id != 0xffffffff; i++)
        {            
            if((LOOKUP_MASK & key) == synapse_lookup[i].core_id)
            {
                kernel = (int *) synapse_lookup[i].kernel_block;
                kernel_size = synapse_lookup[i].row_size;
                kernel_displacement = synapse_lookup[i].displacement;
                kernel_geometry = synapse_lookup[i].kernel_geometry;
            }
        }
        
        
        io_printf(IO_STD, "K: disp: (%d, %d) s: (%d, %d) ", 
            kernel_displacement & 0xFFFF, (kernel_displacement >> 16) & 0xFFFF,
            kernel_geometry & 0xFFFF, (kernel_geometry >> 16) & 0xFFFF);
        for (uint j = 0; j < kernel_size; j++) 
        {
            io_printf(IO_STD, "%d ", kernel[j]);
            spin1_delay_us(10);
        }   
        io_printf(IO_STD, "\n");

        

    }
    dma_pipeline.busy = FALSE;
}

void buffer_post_synaptic_potentials(void *dma_copy, uint row_size) //TODO row size should be taken from the row itself, and not passed via the DMA tag
{
    return;
}

void timer_callback(uint ticks, uint null)
{
    uint neuron_count = 0;
    neuron_t *neuron = (neuron_t *) population[0].neuron;
    psp_buffer_t *psp_buffer = population[0].psp_buffer;

#ifdef DEBUG
    io_printf(IO_STD, "Timer Callback. Tick %d\n", ticks);
#endif

    if(ticks == 0)
    {   
        io_printf(IO_STD, "\nv_thresh;v_reset;v_rest;tau_refrac;tau_m;size_map_x;size_map_y\n");

        io_printf(IO_STD, "%d;%d;%d;%d;%d;%d;%d\n", 
                            population[0].v_thresh,
                            population[0].v_reset,
                            population[0].v_rest,
                            population[0].tau_refrac,
                            population[0].tau_m,
                            population[0].size_map_x,
                            population[0].size_map_y
                            );                    

        io_printf(IO_STD, "\nn;v;time_last_input_spike;time_last_output_spike\n");

        uint j = 0;  // only print neuron 0
        for (j = 0; j < 20; j++)
        io_printf(IO_STD, "%d;%d;%d;%d\n", 
                                j, 
                                neuron[j].v,
                                neuron[j].time_last_input_spike,
                                neuron[j].time_last_output_spike
                                );


                            
        io_printf(IO_STD, "start_id: %d, end_id: %d, total_neurons: %d\n", 
                            app_data.offset, 
                            app_data.offset + population[0].num_neurons - 1,     // id start from 0, hence -1
                            app_data.population_size);
    }
        
    if(ticks >= app_data.run_time)
    {
        io_printf(IO_STD, "Simulation complete.\n");
        spin1_stop();
    }

    for(uint i = 0; i < num_populations; i++)
    {

        for(uint j = 0; j < population[i].num_neurons; j++, neuron_count++)
        {
        /*
            // Get excitatory and inhibitory currents from synaptic inputs
            int exci_current = psp_buffer[j].exci[ticks % PSP_BUFFER_SIZE];
            int inhi_current = psp_buffer[j].inhi[ticks % PSP_BUFFER_SIZE];
            int current = exci_current - inhi_current + neuron[j].bias_current;

            // Clear PSP buffers for this timestep
            psp_buffer[j].exci[ticks % PSP_BUFFER_SIZE] = 0;
            psp_buffer[j].inhi[ticks % PSP_BUFFER_SIZE] = 0;
        */
        }

    }

}

// Specific functions for each neural model

void configure_recording_space()
{
    // Navigate lookup tree and find out the maximum row length
    for (uint i = 0; synapse_lookup[i].core_id != 0xffffffff; i++)
    {
        io_printf(IO_STD, "key 0x%x size %d pointer 0x%x\n",
            LOOKUP_MASK,
            synapse_lookup[i].row_size,
            synapse_lookup[i].kernel_block);
    
        int * tcm_address = (int *) spin1_malloc(synapse_lookup[i].row_size * 4);
        int * sdram_address = (int *) synapse_lookup[i].kernel_block;
        for (uint j = 0; j < synapse_lookup[i].row_size; j++)
            tcm_address[j] = sdram_address[j];
            
        synapse_lookup[i].kernel_block = tcm_address;

        io_printf(IO_STD, "mask 0x%x size %d pointer 0x%x\n",
            LOOKUP_MASK,
            synapse_lookup[i].row_size,
            synapse_lookup[i].kernel_block);

        for (uint j = 0; j < synapse_lookup[i].row_size; j++) io_printf(IO_STD, "%d ", tcm_address[j]);
        io_printf(IO_STD, "\n");
        
    }

    return;
}

void handle_sdp_msg(sdp_msg_t *sdp_msg)
{
    return;
}

void decode_synaptic_word (unsigned int word, synaptic_word_t *decoded_word)
{
    decoded_word -> synapse_type = (word >> 31) & 1; 
    decoded_word -> weight = (word >> 15) & 65535; 
    decoded_word -> index = (word >> 4) & 2047; 
    decoded_word -> delay = 0 + ((word >> 0) & 15); 
    decoded_word -> weight_scale = 8; 
}


