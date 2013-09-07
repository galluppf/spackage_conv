#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#include "inputThread.h"
#include "globals.h"

inputThread::inputThread()
{

}

inputThread::~inputThread()
{

}

bool inputThread::startInputThread(void* ptr)
{
    return (pthread_create(&p1, NULL, inputThread::file_input_thread, ptr) == 0);
}

void inputThread::waitForInputThread()
{
    pthread_join(p1, NULL);
}

void* inputThread::file_input_thread (void *ptr)
{
    unsigned int temp_value_in, ans;

    fprintf (stderr, "into file input thread\n");
    fflush (stderr);

#ifdef DEBUG
    fprintf (stderr, "file handle: %ld\n", (long) finput);
    if (finput != stdin)
    {
        fprintf (stderr, "input/output format: %s\n", (binary_input==0)?"Text":"Binary");
        fseek(finput, 0, SEEK_END);
        fprintf (stderr, "file size: %ld bytes\n", ftell(finput));
        fseek(finput, 0, SEEK_SET);
    }
    fflush (stderr);
#endif

    do {
        if (binary_input)
        {
            ans = fread(&temp_value_in, sizeof (unsigned int), 1, finput);
#ifdef DEBUG
        fprintf (stderr, "into binary reading section\n");
        fflush (stderr);
#endif
        }
        else
        {
            ans = fscanf(finput, "%u;", &temp_value_in);
#ifdef DEBUG
        fprintf (stderr, "into text reading section\n");
        fflush (stderr);
#endif
        }

#ifdef DEBUG
        fprintf (stderr, "read %d integers from input file data\n", ans);
        fprintf (stderr, "read %d from input file data\n", temp_value_in);
        fflush (stderr);
#endif

        if (ans == 1 && sent_before_end == 0)
        {
            if (temp_value_in == 0xFFFFFFFF)
            {
#ifdef DEBUG
                fprintf (stderr, "%d spikes ready to be sent. wait for signal\n", (queue.getPacketNum()-1)*MAXBLOCKSIZE + queue.getLastPacketEntriesNum());
                fflush (stderr);
#endif

                pthread_mutex_lock (&readmutex);
                wait_for_timer = 1;
                while (wait_for_timer == 1)
                {
                    pthread_cond_wait(&readcond, &readmutex);
                }
                pthread_mutex_unlock (&readmutex);

#ifdef DEBUG
                fprintf (stderr, "signal received\n");
                fflush (stderr);
#endif
            }
            else
            {
                queue.insertSpike(temp_value_in);
            }
        }

        if (sent_before_end == 1)
        {
            int b;
#ifdef DEBUG
            fprintf (stderr, "Packets sent before end of frame - dropping following spikes\n");
            fflush (stderr);
#endif
            do {

                if (binary_input)
                    b = fread(&temp_value_in, sizeof (unsigned int), 1, finput);
                else
                    b = fscanf(finput, "%d;", &temp_value_in);


            } while (b == 1 && temp_value_in != 0xFFFFFFFF);

            sent_before_end = 0;

#ifdef DEBUG
            fprintf (stderr, "End re-synchronization routine (Sent before end of frame)\n");
            fflush (stderr);
#endif
        }

#ifdef DEBUG
        fprintf (stderr, "End file input loop\n");
        fflush (stderr);
#endif
    } while (!feof(finput));
    terminate = 1;

    if (finput != stdin)
        fclose (finput);

    return NULL;
}
