#include <signal.h>
#include <time.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#include "RTtimer.h"

RTtimer::RTtimer()
{
    timerid = NULL;

    start_pkt_timestamp = 0;
    start_time_set = false;
    time_count = 0;

    memset (&tout_val, 0, sizeof(struct itimerspec));
    memset (&start_timer, 0, sizeof(struct timespec));
    memset (&evp, 0, sizeof(struct sigevent));
}

RTtimer::~RTtimer()
{
    if (timerid != NULL)
    {
        fprintf (stderr, "ticks: %d\n", time_count);
        fflush (stderr);

        timer_delete (timerid);
    }
}

void RTtimer::setTimerInterval(int ms_tick)
{
    tout_val.it_interval.tv_sec = tout_val.it_value.tv_sec = (long int) floor((double)ms_tick / (double)1000);
    tout_val.it_interval.tv_nsec = tout_val.it_value.tv_nsec = 1000000 * (ms_tick % 1000); // set timer for ms_tick millisecond
}

void RTtimer::setTimerThread (void *ptr)
{
    int status;

    evp.sigev_notify = SIGEV_THREAD;
    evp.sigev_signo = SIGRTMIN;
    evp.sigev_value.sival_int = SIGRTMIN;
    evp.sigev_notify_function = (void (*)(sigval_t)) ptr;
    evp.sigev_notify_attributes = NULL;

    status = timer_create(CLOCK_REALTIME, &evp, &timerid);
    if (status != 0)
    {
        perror ("timer_create");
        exit(status);
    }

    status = timer_settime(timerid, 0, &tout_val, NULL);
    if (status != 0)
    {
        perror ("timer_settime");
        exit(status);
    }

    fprintf (stderr, "Timer setup complete!\n");
    fflush (stderr);
}

void RTtimer::incrementTimeCount()
{
    time_count++;
}

unsigned int RTtimer::getTimeCount()
{
    return time_count;
}

void RTtimer::resync_timer(timespec* currentTime, unsigned int currentPktPimestamp)
{
    struct itimerspec tout_val_sync, stop_timer;

    memset (&tout_val_sync, 0, sizeof(struct itimerspec));
    memset (&stop_timer, 0, sizeof(struct itimerspec));

#ifdef DEBUG
    fprintf (stderr, "resync timer\n");
    fflush (stderr);
#endif
    
    if (start_time_set == true)
    {
        int board_tick_diff;
        long long elapsed_time, current_time;
        long double new_interval;
        int status;
        unsigned int current_board_tick;

        current_time = ((long long)currentTime -> tv_sec * 1000000000) + (long long) currentTime -> tv_nsec;
        current_board_tick = currentPktPimestamp; //scanptr -> arg2

        elapsed_time = current_time - ((long long)start_timer.tv_sec * 1000000000 + (long long) start_timer.tv_nsec);
        board_tick_diff = current_board_tick - start_pkt_timestamp;
        new_interval = ((long double)elapsed_time) / ((long double)board_tick_diff);

#ifdef DEBUG
        fprintf (stderr, "resync timer: initial timer value: %ld sec, %ld nsec\n", tout_val.it_interval.tv_sec, tout_val.it_interval.tv_nsec);
        fprintf (stderr, "board ticks: %d\nelapsed host time: %lld usec\n", board_tick_diff, elapsed_time);
        fprintf (stderr, "tick time interval: %Lf usec\n", new_interval);
        fflush (stderr);
#endif

        status = timer_settime(timerid, 0, &stop_timer, &tout_val_sync);
        if (status != 0)
        {
            perror ("timer_settime");
            exit(status);
        }

        if (currentPktPimestamp >= time_count)
        { //sync packet arriving after timer tick -> recharge timer with appropriate value
            new_interval = floorl(new_interval); //make the timer quicker so to oscillate between the two possibilities

            tout_val.it_interval.tv_sec = (long) truncl((new_interval) / (long double)1000000000);
            tout_val.it_interval.tv_nsec = (long) roundl(new_interval - (long double)(tout_val.it_interval.tv_sec * 1000000000));

            if (tout_val_sync.it_value.tv_sec == 0 && tout_val_sync.it_value.tv_nsec < 50000)
                tout_val_sync.it_value.tv_nsec = 50000;
        }
        else
        { //sync packet arriving before timer tick -> trigger timer immediately and recharge the interval with the appropriate value
            new_interval = ceill(new_interval); //make the timer slower so to oscillate between the two possibilities

            tout_val.it_interval.tv_sec = (long) truncl((new_interval) / (long double)1000000000);
            tout_val.it_interval.tv_nsec = (long) roundl(new_interval - (long double)(tout_val.it_interval.tv_sec * 1000000000));

            tout_val_sync.it_value.tv_sec = 0;
            tout_val_sync.it_value.tv_nsec = 50000;
        }

        tout_val_sync.it_interval.tv_sec = tout_val.it_interval.tv_sec;
        tout_val_sync.it_interval.tv_nsec = tout_val.it_interval.tv_nsec;

#ifdef DEBUG
        fprintf (stderr, "resync timer: current timer value: %ld sec, %ld nsec\n", tout_val.it_interval.tv_sec, tout_val.it_interval.tv_nsec);
        fflush (stderr);
#endif

        //resync timer
        status = timer_settime(timerid, 0, &tout_val_sync, NULL);
        if (status != 0)
        {
            perror ("timer_settime");
            exit(status);
        }
    }
    else //first synchronization: start the next time slot with a delay of 10000 nsec
    {
#ifdef DEBUG
        fprintf (stderr, "first resync\n");
        fflush (stderr);
#endif
        
        int status;

        start_timer.tv_sec = currentTime -> tv_sec; //recv_time
        start_timer.tv_nsec = currentTime -> tv_nsec; //recv_time
        start_pkt_timestamp = currentPktPimestamp; //scanptr -> arg2
        start_time_set = true;
        
        tout_val_sync.it_interval.tv_sec = tout_val.it_interval.tv_sec;
        tout_val_sync.it_interval.tv_nsec = tout_val.it_interval.tv_nsec;


        if (currentPktPimestamp >= time_count)
        { //sync packet arriving after timer tick -> recharge timer with appropriate value
        
#ifdef DEBUG
            fprintf (stderr, "currentPktPimestamp >= time_count: %d >= %d\n", currentPktPimestamp, time_count);
            fflush (stderr);
#endif
            
            tout_val_sync.it_value.tv_sec = tout_val.it_interval.tv_sec;
            tout_val_sync.it_value.tv_nsec = tout_val.it_interval.tv_nsec;
        }
        else
        { //sync packet arriving before timer tick -> trigger timer immediately and recharge the interval with the appropriate value
#ifdef DEBUG
            fprintf (stderr, "currentPktPimestamp < time_count: %d < %d\n", currentPktPimestamp, time_count);
            fflush (stderr);
#endif
            tout_val_sync.it_value.tv_sec = 0;
            tout_val_sync.it_value.tv_nsec = 10000;
        }

#ifdef DEBUG
        fprintf (stderr, "resync timer: current timer value: %ld sec, %ld nsec\n", tout_val.it_interval.tv_sec, tout_val.it_interval.tv_nsec);
        fflush (stderr);
#endif

        //resync timer
        status = timer_settime(timerid, 0, &tout_val_sync, NULL);
        if (status != 0)
        {
            perror ("timer_settime");
            exit(status);
        }
    }
}

void RTtimer::stopTimer()
{
    int status;

    tout_val.it_value.tv_sec = tout_val.it_interval.tv_sec = 0;
    tout_val.it_value.tv_nsec = tout_val.it_interval.tv_nsec = 0;

    status = timer_settime(timerid, 0, &tout_val, NULL);
    if (status != 0)
    {
        perror ("timer_settime");
        exit(status);
    }
}
