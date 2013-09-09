#include "spin1_api.h"
#include "spinn_io.h"
#include "spinn_sdp.h" // Required by comms.h

#include "comms.h"
#include "config.h"
#include "dma.h"
#include "model_general.h"

#ifdef STDP
#include "stdp.h"
#endif

#ifdef STDP_SP
#include "stdp_sp.h"
#endif

#ifdef STDP_TTS
#include "stdp_tts.h"
#endif

//#define DEBUG

dma_pipeline_t dma_pipeline;
synapse_lookup_t *synapse_lookup;

int overflows = 0;


void buffer_mc_packet(uint key, uint payload)
{
    if((mc_packet_buffer.end + 1) % MC_PACKET_BUFFER_SIZE != mc_packet_buffer.start)
    {
        mc_packet_buffer.buffer[mc_packet_buffer.end] = key;
        mc_packet_buffer.end = (mc_packet_buffer.end + 1) % MC_PACKET_BUFFER_SIZE;

        if(!dma_pipeline.busy)
        {
            dma_pipeline.busy = TRUE;
            spin1_trigger_user_event(0, 0); //TODO should this be spin1_schedule_callback?
        }

    }
    else
    {
        overflows++;
    }
}

void dma_callback(uint null0, uint tag)
{

    return;
}


void feed_dma_pipeline(uint null0, uint null1)
{
    return;
}


void lookup_synapses(uint key)
{
    return;
}


uint mc_packet_buffer_empty()
{
    uint cpsr = spin1_int_disable();
    uint empty = mc_packet_buffer.start == mc_packet_buffer.end ? TRUE : FALSE;
    spin1_mode_restore(cpsr);

    return empty;
}
