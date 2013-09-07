#ifndef __TIMERSIGNALHANDLER_H
#define __TIMERSIGNALHANDLER_H

#include <pthread.h>

#include "RTtimer.h"
#include "sharedQueue.h"

class TimerSignalHandler
{
public:
    TimerSignalHandler();
    ~TimerSignalHandler();
    
    void timer_signal (int j);
};

#endif