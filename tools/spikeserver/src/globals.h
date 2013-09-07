#ifndef __GLOBALS_H
#define __GLOBALS_H

#include "sharedQueue.h"
#include "RTtimer.h"
#include "spikeChannel.h"
#include "TimerSignalHandler.h"
#include "spikeReceiver.h"
#include "inputThread.h"

#include <stdio.h>
#include <pthread.h>

extern sharedQueue queue;
extern spikeChannel visualizer1, visualizer2;
extern spikeChannel spinnBoard;
extern RTtimer timer;
extern TimerSignalHandler timerHandler;
extern spikeReceiver receiver;
extern inputThread input;

extern pthread_cond_t readcond;
extern pthread_mutex_t readmutex;
extern bool realTime;
extern bool spike_heard;
extern bool sent_before_end;
extern bool wait_for_timer;
extern bool terminate;

extern int binary_input;
extern int replicate_output;
extern FILE *finput, *foutput;

#endif
