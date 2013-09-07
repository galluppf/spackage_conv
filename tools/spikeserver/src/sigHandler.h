#ifndef __SIGHANDLER_H
#define __SIGHANDLER_H

#include <signal.h>

void sigHandler(union sigval sig);
void user_signal (int sig);

#endif