#include <stdlib.h>
#include <stdio.h>

#include "sharedQueue.h"

sharedQueue::sharedQueue()
{
    pthread_mutex_init(&newSpikeMutex, NULL);
    pthread_cond_init(&newSpikeCond, NULL);

    queueingSpike = 0;
    packets = NULL;
    packetPtr = NULL;

    packetEntriesNum = 0;
    packetNum = 0;
}

sharedQueue::~sharedQueue()
{
    pthread_mutex_lock (&newSpikeMutex);
    while (queueingSpike == 1)
        pthread_cond_wait(&newSpikeCond, &newSpikeMutex);

    if (packets != NULL)
    {
        free (packets);

        packets = NULL;
        packetEntriesNum = 0;
        packetNum = 0;
    }

    pthread_mutex_unlock (&newSpikeMutex);

//    pthread_mutex_destroy(&newSpikeMutex);
//    pthread_cond_destroy(&newSpikeCond);
}

unsigned int sharedQueue::getPacketNum()
{
    return packetNum;
}

unsigned int sharedQueue::getLastPacketEntriesNum()
{
    return packetEntriesNum;
}

int sharedQueue::insertSpike(unsigned int spike)
{
    pthread_mutex_lock (&newSpikeMutex);
    queueingSpike = 1;

    //queue spike list
    if (packetNum == 0)
            packetPtr = new struct sendPacket;
    
    if (packetEntriesNum % MAXBLOCKSIZE == 0)
    {
#ifdef DEBUG
        fprintf (stderr, "generating new packet\n");
        fflush (stderr);
#endif

        packets = (struct sdp_msg *) realloc(packets, sizeof(struct sdp_msg) * (packetNum + 1) ); //allocating a new spinnaker packet structure
        if (packets == NULL)
        {
            fprintf (stderr, "error allocating memory for received spikes\n");
            fflush (stderr);
            return -1;
        }
        /*
        packets[packet_num].version = SPINNPROTVERSION;
        packets[packet_num].subversion = SPINNPROTSUBVERSION;
        packets[packet_num].opcode = htonl(STIM_OUT);
        packets[packet_num].option1 = htonl(0);
        */

        packets[packetNum].ip_time_out = 0x01;
        packets[packetNum].pad = 0;
        packets[packetNum].flags = 0x07;
        packets[packetNum].tag = 255;
        //packets[packetNum].dest_port = 1 << 5 | 1;
        packets[packetNum].dest_port = (SDP_port << 5) | core_id;
        packets[packetNum].srce_port = 255;
        //packets[packetNum].dest_addr = 0;
        packets[packetNum].dest_addr = (((short unsigned int) x_chip) << 8) | ((short unsigned int) y_chip);
        packets[packetNum].srce_addr = 0;
        packets[packetNum].cmd_rc = 256;
        packets[packetNum].sequence = 0;
        packets[packetNum].arg2 = 0;
        packets[packetNum].arg3 = 0;
        packetNum ++;
        packetEntriesNum = 0;

#ifdef DEBUG
        fprintf (stderr, "packet generation complete\n");
        fflush (stderr);
#endif
    }

#ifdef DEBUG
    fprintf (stderr, "Queueing spike\n");
    fflush (stderr);
#endif
    packets[packetNum - 1].data[packetEntriesNum] = spike;
    packetEntriesNum++;
#ifdef DEBUG
    fprintf (stderr, "Queue spike complete\n");
    fflush (stderr);
#endif
    queueingSpike = 0;
    pthread_mutex_unlock(&newSpikeMutex);
    pthread_cond_signal(&newSpikeCond);

    return 0;
}

struct sendPacket * sharedQueue::flushSpikes()
{
    if (packetNum > 0)
    {
        unsigned int i;

        packetPtr->packets_ptr = packets;
        packetPtr->packet_lengths = new unsigned int [packetNum];

        pthread_mutex_lock(&newSpikeMutex);
        while (queueingSpike == 1)
            pthread_cond_wait(&newSpikeCond, &newSpikeMutex);

        // send the packets
        for (i = 0; i < packetNum; i++)
        {
            if (i + 1 < packetNum)
            {
                packetPtr->packet_lengths[i] = SDPHEADERLENGHT + (MAXBLOCKSIZE * 4);
                packets[i].arg1 = 64; //removed htonl because is not used on the simulator side
            }
            else
            {
                packetPtr->packet_lengths[i] = SDPHEADERLENGHT + (packetEntriesNum * 4);
                packets[i].arg1 = packetEntriesNum;
            }

        }

        packets = NULL;
        packetEntriesNum = 0;
        packetNum = 0;

        pthread_mutex_unlock(&newSpikeMutex);

        return packetPtr;
    }
    else
        return NULL;
}

void sharedQueue::setDestinationCore(int x, int y, int core, int SDPport)
{
    x_chip = (char) x;
    y_chip = (char) y;
    core_id = (char) core;
    SDP_port = (char) SDPport;
}

struct destinationCore sharedQueue::getDestinationCore()
{
    struct destinationCore data;

    data.x_chip = x_chip;
    data.y_chip = y_chip;
    data.core_id = core_id;
    data.SDP_port = SDP_port;

    return data;
}

