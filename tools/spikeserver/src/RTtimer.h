#ifndef __RTTIMER_H
#define __RTTIMER_H

#include <signal.h>
#include <time.h>
       
class RTtimer
{    
public:
    RTtimer();
    ~RTtimer();
    void resync_timer(struct timespec * current_time, unsigned int current_pkt_timestamp);
    void setTimerInterval(int ms_tick);
    void setTimerThread (void *ptr);
    void incrementTimeCount ();
    unsigned int getTimeCount();
    void stopTimer();

private:
    timer_t timerid;
    
    struct itimerspec tout_val;
    struct timespec start_timer;
    unsigned int start_pkt_timestamp;

    struct sigevent evp;
    bool start_time_set;

    unsigned int time_count;
};

#endif
