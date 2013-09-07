#include <stdbool.h>
#include <stdlib.h>

#include "globals.h"
#include "RTtimer.h"
#include "TimerSignalHandler.h"

TimerSignalHandler::TimerSignalHandler()
{

}

TimerSignalHandler::~TimerSignalHandler()
{

}

void TimerSignalHandler::timer_signal (int j)
{
    int i;

#ifdef DEBUG
    fprintf (stderr, "into timer signal interrupt\n");
    fflush (stderr);
#endif

    if (terminate)
    {
        timer.stopTimer();
    }

    if (sent_before_end == false && ((spike_heard == true && realTime == false) || (realTime == true)))
    {

        struct sendPacket * packetPtr;
        int packet_num;

        timer.incrementTimeCount();

        pthread_mutex_lock (&readmutex);
        if (wait_for_timer == false)
        {
            sent_before_end = true;
            pthread_mutex_unlock (&readmutex);
            pthread_cond_signal (&readcond);
#ifdef DEBUG
            fprintf (stderr, "Sending spike packets before the end of the input spike frame...\n");
            fflush (stderr);
#endif
        }
        else
        {
            pthread_mutex_unlock (&readmutex);
            pthread_cond_signal (&readcond);
        }

        packet_num = queue.getPacketNum();
        packetPtr = queue.flushSpikes();

#ifdef DEBUG
        fprintf (stderr, "sending %d packet(s)\n", packet_num);
        fflush (stderr);
#endif
        
        // send the packets
        for (i = 0; i < packet_num; i++)
        {
#ifdef DEBUG
            fprintf (stderr, "Sending %d spikes to the spinn board\n", packetPtr -> packet_lengths[i]);
            fflush (stderr);
#endif

            spinnBoard.sendPacket(packetPtr -> packet_lengths[i], &(packetPtr -> packets_ptr[i]));

            if (visualizer1.ison() && (packetPtr -> packet_lengths[i] > 0))
            {
                visualizer1.sendSpikes(packetPtr->packets_ptr[i].arg1*4, (unsigned int*) &packetPtr->packets_ptr[i].data);
            }
        }

        if (packet_num != 0)
        {
            free(packetPtr->packets_ptr);
            delete [] packetPtr->packet_lengths;
            delete packetPtr;
            packetPtr = NULL;

            packet_num = 0;
        }

#ifdef DEBUG
        fprintf (stderr, "packet(s) succesfully sent\n");
        fflush (stderr);
#endif
    }

    if (realTime == true || (realTime == false && spike_heard == 1))
    {
        pthread_mutex_lock (&readmutex);
        wait_for_timer = 0;
#ifdef DEBUG
        fprintf (stderr, "setting wait_for_timer to 0\n");
        fflush (stderr);
#endif
        pthread_mutex_unlock (&readmutex);
        pthread_cond_signal(&readcond);
    }

#ifdef DEBUG
    fprintf (stderr, "exiting timer signal interrupt\n");
    fflush (stderr);
#endif
}

