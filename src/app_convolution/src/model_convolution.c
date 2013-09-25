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

neuron_t *neuron;

uint csubpop_min, csubpop_max; //minimum and maximum coordinates of the subpopulation within the core

int SIGNMASK =    0x00000001;
int MASK_XY_RET = 0x0000003F;
int MASK_XY =     0x000003FF;
int Vmax = 2147483647;
int Vmin = -2147483647;
int MASK_LAST_OUTPUT_SPIKE = 0x7FFFFFFF;

//ATTENTION: REDEFINE TIME TICKS FOR RESOLUTION BETTER THAN 1ms
//ATTENTION: ALL VOLTAGE PARAMETERS SHOULD BE CONVERTED TO HAVE THE SAME SCALING 

void process_incoming_packets(uint payload, uint null1) {
    neuron = (neuron_t *) population[0].neuron;
    while(!mc_packet_buffer_empty())
    {   uint xsource, ysource, sign; //decoded address of the source spike
        uint key = mc_packet_buffer.buffer[mc_packet_buffer.start];
        mc_packet_buffer.start = (mc_packet_buffer.start + 1) % MC_PACKET_BUFFER_SIZE;
        uint tactual = spin1_get_simulation_time();

        if (payload != NULL ) {
            xsource = (payload)       & MASK_XY_RET ;
            ysource = (payload >> 7)  & MASK_XY_RET ;
            sign    = (payload >> 14) & SIGNMASK;
        } else {  
            xsource =  key        & MASK_XY_RET;
            ysource = (key >> 7)  & MASK_XY_RET;
            sign    = (key >> 14) & SIGNMASK;
        }
        //io_printf(IO_STD, "xsource: %d ysource: %d sign: %d\n", xsource, ysource, sign); 

        int * kernel = NULL;
        //ushort kernel_size = 0;
        uint kernel_displacement_x, kernel_displacement_y;
        uint kernel_size_x, kernel_size_y;
        
        //io_printf(IO_STD, "Time: %d key: 0x%x\n",tactual, key);
        for(uint i = 0; synapse_lookup[i].core_id != 0xffffffff; i++)
        {            
            if((LOOKUP_MASK & key) == synapse_lookup[i].core_id)
            {
                kernel = (int *) synapse_lookup[i].kernel_block;
                //kernel_size = synapse_lookup[i].row_size;
                kernel_displacement_x = (synapse_lookup[i].displacement & 0xFFFF);
                kernel_displacement_y = (synapse_lookup[i].displacement >> 16) & 0xFFFF;
                kernel_size_x = (synapse_lookup[i].kernel_geometry & 0xFFFF);
                kernel_size_y = (synapse_lookup[i].kernel_geometry >> 16) & 0xFFFF;
            }
        }
         //compute the projection field of the kernel based on the arriving address + kernel geometry + displacement. First, compute the limits of the projection field in the population. This defines the limits of the two nested for loops. (in the same two nested loops do all the computation below)
       
      //update the leakage and tlastupdate
      //update the corresponding membrane voltage v 
               //check for overflow
                      //if overflow saturate to overflow limit
      //check if the membrane voltage reaches thresholds if yes
                //check the time since last firing and compare with refractory period
                     //if the refractory period is fullfilled fire and update tlastfiring and send the event as multicast packet with payload (to send the absolute address of the firing neuron inside its feature map) 
                     //if the refractory period is not fullfilled activate flad of delayed spike (bit 32 of tlastfiring) 

        //compute the minimum destination coordinate hit by the incoming spike
        uint xdest_min = xsource + kernel_displacement_x - (kernel_size_x >> 1);
        uint ydest_min = ysource + kernel_displacement_y - (kernel_size_y >> 1);
        uint cdest_min = ydest_min * population[0].size_map_x + xdest_min; 
        //compute the maximum destination coordinate hit by the incoming spike
        uint xdest_max = xdest_min + kernel_size_x - 1;
        uint ydest_max = ydest_min + kernel_size_y - 1;
        uint cdest_max = ydest_max * population[0].size_map_x + xdest_max;
        uint  cdest = cdest_min; // destination neuron number in absolute coordinates
        uint  cdest_core; // destination neuron number within the core subpopulation
        uint  xdest;
        uint  ydest;
        //io_printf(IO_STD, "K: disp: (%d, %d) s: (%d, %d) ", 
        //    kernel_displacement_x, kernel_displacement_y,
        //    kernel_size_x, kernel_size_y);

        if (cdest_min > csubpop_max || cdest_max < csubpop_min)
        { 
         //io_printf(IO_STD, "population not hit by incoming spike: xdest_min:%d , ydest_min: %d, cdest_min=%d , xdest_max=%d, ydest_max=%d, cdest_max=%d",xdest_min, ydest_min, cdest_min, xdest_max, ydest_max, cdest_max);
        } 
        else 
        {  //io_printf(IO_STD, "processing event key: %x xsource: %d ysource: %d sign: %d\n", key, xsource, ysource, sign);
           uint pp=0;
           for (uint ydest = ydest_min ; ydest <= ydest_max ; ydest++, cdest = cdest+population[0].size_map_x-kernel_size_x) 
            {  
              for (uint xdest = xdest_min; xdest <= xdest_max ; xdest++)
               {   
                  if (cdest >= csubpop_min )
                  {
                     if (cdest <= csubpop_max)
                     { //compute leakage since last neuron update
                        //use population[0].tau_m as leakage parameter - has dimensions of v/s
                        cdest_core = cdest - csubpop_min;
                        //io_printf(IO_STD, "cdest: %d membrane voltage before leakage: %d ", cdest, neuron[cdest_core].v);
                        if ( neuron[cdest_core].v >= 0 )
                        {  neuron[cdest_core].v = neuron[cdest_core].v - population[0].tau_m * (tactual - neuron[cdest_core].time_last_input_spike);
                           if (neuron[cdest_core].v < 0)
                                neuron[cdest_core].v = 0;
                        }
                        else
                        {  neuron[cdest_core].v = neuron[cdest_core].v + population[0].tau_m * (tactual - neuron[cdest_core].time_last_input_spike);
                           if (neuron[cdest_core].v > 0)
                                neuron[cdest_core].v = 0;
                        }
                         //io_printf(IO_STD, "membrane voltage after leakage: %d ", neuron[cdest_core].v);
                         //update time_last_input_spike;
                        neuron[cdest_core].time_last_input_spike = tactual;
                        //io_printf(IO_STD, "tlast_input_spike: %d ", neuron[cdest_core].time_last_input_spike);
                         // add the kernel influence on the membrane voltage taking into account the sign of the incoming event and checking for overflow. if overflow, saturate to maximum/minimum value
                        int vtmp;
                        if (sign == 0 ) {
                             vtmp = neuron[cdest_core].v + kernel[pp];
                             if (kernel[pp] > 0)
                                 if (vtmp < neuron[cdest_core].v)
                                        neuron[cdest_core].v = Vmax;
                                 else   neuron[cdest_core].v = vtmp;
                             else if (vtmp > neuron[cdest_core].v)
                                        neuron[cdest_core].v = Vmin;
                                  else  neuron[cdest_core].v = vtmp;
                        }
                        else {
                           if (sign == 1 ) {
                              vtmp = neuron[cdest_core].v - kernel[pp];
                              if (kernel[pp] < 0)
                                 if (vtmp < neuron[cdest_core].v)
                                        neuron[cdest_core].v = Vmax;
                                 else   neuron[cdest_core].v = vtmp;
                             else if (vtmp > neuron[cdest_core].v)
                                        neuron[cdest_core].v = Vmin;
                                  else  neuron[cdest_core].v = vtmp;
                           }
                           else 
                              io_printf(IO_STD, "warning incorrect event sign = %d", sign);
                        }
                        
                        io_printf(IO_STD, "membrane voltage after kernel computing: %d ", neuron[cdest_core].v);
                        if ( neuron[cdest_core].v > population[0].v_thresh )
                        {
                         if ( (tactual - (neuron[cdest_core].time_last_output_spike & MASK_LAST_OUTPUT_SPIKE) ) >= population[0].tau_refrac )
                          {  neuron[cdest_core].v = population[0].v_reset;
                            
                              //to correct the time_last_output_spike in case a previous event was not fired due to unfullfilment of the refractory period a flag of delayedspike must be added to the neurons. We use the most significant bit of time_last_output_spike as such a flag
                             if ( (neuron[cdest_core].time_last_output_spike >> 31) == 1)
                                 neuron[cdest_core].time_last_output_spike = (neuron[cdest_core].time_last_output_spike & MASK_LAST_OUTPUT_SPIKE) + population[0].tau_refrac;
                             else
                                 neuron[cdest_core].time_last_output_spike = tactual & MASK_LAST_OUTPUT_SPIKE;
                             uint key = spin1_get_chip_id() << 16 | app_data.virtual_core_id << 11 | cdest_core;
                             //uint payload = xdest << 11 | ydest << 1 | 0 ;
                             uint payload = 0 << 14 | ydest << 7 | xdest;
                             spin1_send_mc_packet(key, payload, WITH_PAYLOAD);
                             io_printf(IO_STD, "sending positive spike: x:%d y:%d, time_last_output_spike: %d, tactual: %d\n", xdest, ydest, neuron[cdest_core].time_last_output_spike,tactual);
                           }
                         else neuron[cdest_core].time_last_output_spike = (1 << 31) | neuron[cdest_core].time_last_output_spike;
                        }
                        
                        if ( neuron[cdest_core].v < population[0].v_rest ) 
                        {
                         if ( (tactual - (neuron[cdest_core].time_last_output_spike & MASK_LAST_OUTPUT_SPIKE) ) >= population[0].tau_refrac )
                          {  neuron[cdest_core].v = population[0].v_reset;
                             //to correct the time_last_output_spike in case a previous event was not fired due to unfullfilment of the refractory period a flag of delayedspike must be added to the neurons. We use the most significant bit of time_last_output_spike as such a flag
                             if ( (neuron[cdest_core].time_last_output_spike >> 31) == 1)
                                 neuron[cdest_core].time_last_output_spike = (neuron[cdest_core].time_last_output_spike & MASK_LAST_OUTPUT_SPIKE) + population[0].tau_refrac;
                             else
                             neuron[cdest_core].time_last_output_spike = tactual & MASK_LAST_OUTPUT_SPIKE;
                             uint key = spin1_get_chip_id() << 16 | app_data.virtual_core_id << 11 | cdest_core;
                             //uint payload = xdest << 11 | ydest << 1 | 1 ;
                             uint payload = 1 << 14 | ydest << 7 | xdest;
                             spin1_send_mc_packet(key, payload, WITH_PAYLOAD);
                             io_printf(IO_STD, "sending negative spike: x:%d y:%d,  time_last_output_spike: %d tactual: %d\n", xdest, ydest, neuron[cdest_core].time_last_output_spike,tactual);
                           }
                           else neuron[cdest_core].time_last_output_spike =  (1 << 31) | neuron[cdest_core].time_last_output_spike;
                        }
          //             spin1_delay_us(10);
       
                     } 
                     else
                     goto endpopulation;
                   }
                   pp = pp + 1;
                   cdest= cdest + 1;
               }              
             }
          }
          endpopulation:  io_printf(IO_STD, "population finished\n");

    }
    dma_pipeline.busy = FALSE;
}

void buffer_post_synaptic_potentials(void *dma_copy, uint row_size) //TODO row size should be taken from the row itself, and not passed via the DMA tag
{
    return;
}

void timer_callback(uint ticks, uint null)
{
    //uint neuron_count = 0;
    //neuron_t *neuron = (neuron_t *) population[0].neuron;
    
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

        //uint j = 0;  // only print neuron 0
        //io_printf(IO_STD, "%d;%d;%d;%d\n", 
        //                        j, 
        //                        neuron[j].v,
        //                        neuron[j].time_last_input_spike,
        //                        neuron[j].time_last_output_spike
        //                        );


        csubpop_min = app_data.offset;
        csubpop_max = app_data.offset + population[0].num_neurons -1; // id start from 0, hence -1
                   
        io_printf(IO_STD, "start_id: %d, end_id: %d, total_neurons: %d\n", 
                            csubpop_min, 
                            csubpop_max,     
                            app_data.population_size);
       
    }
        
    if(ticks >= app_data.run_time)
    {
        io_printf(IO_STD, "Simulation complete.\n");
        spin1_stop();
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


