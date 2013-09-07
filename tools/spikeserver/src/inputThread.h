#ifndef __INPUTTHREAD_H
#define __INPUTTHREAD_H

#include <pthread.h>

class inputThread
{
public:
    inputThread();
    ~inputThread();

    bool startInputThread(void * ptr);
    void waitForInputThread();

private:
    static void* file_input_thread (void *ptr);

    pthread_t p1;
};

#endif