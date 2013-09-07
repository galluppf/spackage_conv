#ifndef __SHARED_QUEUE_H
#define __SHARED_QUEUE_H

#include <pthread.h>

#include "defines.h"
#include "SDPmsg.h"
#include "sendPacket.h"
#include "destinationCore.h"

class sharedQueue
{
public:
    sharedQueue();
    ~sharedQueue();

    int insertSpike(unsigned int spike);
    struct sendPacket *flushSpikes();

    unsigned int getPacketNum();
    unsigned int getLastPacketEntriesNum();

    void setDestinationCore(int x, int y, int core, int SDPport);
    struct destinationCore getDestinationCore();

private:
//    pthread_mutex_t newSpikeMutex = PTHREAD_MUTEX_INITIALIZER;
//    pthread_cond_t newSpikeCond = PTHREAD_COND_INITIALIZER;

    pthread_mutex_t newSpikeMutex;
    pthread_cond_t newSpikeCond;

    volatile int queueingSpike;

    struct sdp_msg *packets;
    struct sendPacket * packetPtr;

    unsigned int packetEntriesNum;
    unsigned int packetNum;

    unsigned char x_chip, y_chip, core_id, SDP_port;
};

#endif
