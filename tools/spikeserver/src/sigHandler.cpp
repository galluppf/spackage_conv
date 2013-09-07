#include <signal.h>

#include "globals.h"

void sigHandler(union sigval sig)
{
    if (sig.sival_int == SIGRTMIN)
        timerHandler.timer_signal(SIGRTMIN);
}

void user_signal (int sig)
{
    receiver.exitReceiverThread();
}