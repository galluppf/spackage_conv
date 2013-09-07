#ifndef __SPIKERECEIVER_H
#define __SPIKERECEIVER_H

#include <pthread.h>

class spikeReceiver
{
public:
    spikeReceiver();
    ~spikeReceiver();
    
    void setReceiverPort(int inputPort);
    void startReceiverServer();
    bool startReceiverThread (void* ptr);
    void killReceiverThread();
    void waitForReceiverThread();
    void exitReceiverThread();
    
private:
    static void* receiverThread (void* ptr);

private:
    int port;
    int receiveFD;
    pthread_t p1;
};

#endif
