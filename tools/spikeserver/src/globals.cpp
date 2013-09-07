#include <stdio.h>
#include <pthread.h>

#include "sharedQueue.h"
#include "spikeChannel.h"
#include "RTtimer.h"
#include "TimerSignalHandler.h"
#include "spikeReceiver.h"
#include "inputThread.h"

sharedQueue queue;
spikeChannel visualizer1, visualizer2;
spikeChannel spinnBoard;
RTtimer timer;
TimerSignalHandler timerHandler;
spikeReceiver receiver;
inputThread input;

pthread_mutex_t readmutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t readcond = PTHREAD_COND_INITIALIZER;

bool realTime = false;
volatile bool spike_heard = false;
volatile bool wait_for_timer = false;
volatile bool sent_before_end = false;
volatile bool terminate = false;

int binary_input;
int replicate_output;
FILE *finput, *foutput;
