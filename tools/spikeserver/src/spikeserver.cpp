#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>

#include "sigHandler.h"
#include "help.h"
#include "globals.h"

//#define DEBUG

/*
Getting the clock timer resolution

#include <stdio.h>
#include <unistd.h>
#include <time.h>

main()
{
struct timespec     clock_resolution;
int stat;

stat = clock_getres(CLOCK_REALTIME, &clock_resolution);

printf("Clock resolution is %d seconds, %ld nanoseconds\n",
     clock_resolution.tv_sec, clock_resolution.tv_nsec);
}
*/

int main(int argc, char *argv[])
{
    char oc;

    int ms_tick = 0;
    int core_id, x_chip, y_chip, SDP_port;

    core_id = 1;
    x_chip = 0;
    y_chip = 0;
    SDP_port = 1;

    replicate_output = 0;
    finput = stdin;
    foutput = stdout;    
    realTime = true;
    binary_input = 2;

//    visualizer1.setFormat(spikeChannel::SDP_PACKET);
//    visualizer2.setFormat(spikeChannel::SDP_PACKET);
    
    if (argc == 1)
        print_help(argv[0]);

    while ((oc = getopt(argc, argv, "abc:fhi:m:o:p:rs:tv:w:x:y:")) != -1)
    {
        int port;
        char *visualizerAddr;

        switch (oc) {
        case 'a':
#ifdef DEBUG
            fprintf (stderr, "identified -a parameter\n");
#endif
            realTime = 0;
            break;
            
        case 'b':
#ifdef DEBUG
            fprintf (stderr, "identified -b parameter\n");
#endif
            binary_input = 1;
            break;

        case 'c':
#ifdef DEBUG
            fprintf (stderr, "identified -c parameter with argument: %s\n", optarg);
#endif
            core_id = atoi(optarg);
            break;
            
        case 'f':
#ifdef DEBUG
            fprintf (stderr, "identified -f parameter\n");
#endif
            visualizer1.setFormat(spikeChannel::SPINNAKER_PACKET);
            visualizer2.setFormat(spikeChannel::SPINNAKER_PACKET);
            break;

        case 'i':
#ifdef DEBUG
            fprintf (stderr, "identified -i parameter with argument: %s\n", optarg);
#endif
            finput = fopen(optarg, "r");
#ifdef DEBUG
            unsigned int a, temp;
            fseek(finput, 0, SEEK_END);
            fprintf (stderr, "file size: %ld bytes\n", ftell(finput));
            fseek(finput, 0, SEEK_SET);
            a = fread(&temp, sizeof (unsigned int), 1, finput);
            fprintf (stderr, "file handle: %ld\n", (long) finput);
            fprintf (stderr, "read %u integers from input file data\n", a);
            fprintf (stderr, "read %u from input file data\n", temp);
            fflush (stderr);
            fseek(finput, 0, SEEK_SET);
#endif
            break;

        case 'm':
#ifdef DEBUG
            fprintf (stderr, "identified -m parameter with argument: %s\n", optarg);
#endif
            ms_tick = atoi(optarg);
            break;

        case 'o':
#ifdef DEBUG
            fprintf (stderr, "identified -o parameter with argument: %s\n", optarg);
#endif
            foutput = fopen(optarg, "w");
            break;

        case 'p':
#ifdef DEBUG
            fprintf (stderr, "identified -p parameter with argument: %s\n", optarg);
#endif
            SDP_port = atoi(optarg);
            break;
            
        case 'r':
#ifdef DEBUG
            fprintf (stderr, "identified -r parameter\n");
#endif
            replicate_output = 1;
            break;

        case 's':
#ifdef DEBUG
            fprintf (stderr, "identified -s parameter with argument: %s\n", optarg);
#endif
            fprintf (stderr, "Board hostname: %s\n", optarg);
            fflush (stderr);

            spinnBoard.setDestination(optarg, OUTPUT_UDP_PORT_BOARD);
            spinnBoard.openConnection();

            receiver.setReceiverPort(INPUT_PORT_SPINNAKER);
            receiver.startReceiverServer();
            break;

        case 't':
#ifdef DEBUG
            fprintf (stderr, "identified -t parameter\n");
#endif
            binary_input = 0;
            break;

        case 'v':
#ifdef DEBUG
            fprintf (stderr, "identified -v parameter with argument: %s\n", optarg);
#endif
            visualizerAddr = strtok (optarg, ":");
            port = atoi (strtok(NULL, ":"));
            fprintf (stderr, "visualizer 1 address: %s, port: %d\n", visualizerAddr, port);
            fflush (stderr);

            visualizer1.setDestination(visualizerAddr, port);
            visualizer1.openConnection();

            break;

        case 'w':
#ifdef DEBUG
            fprintf (stderr, "identified -w parameter with argument: %s\n", optarg);
#endif
            visualizerAddr = strtok (optarg, ":");
            port = atoi (strtok(NULL, ":"));
            fprintf (stderr, "visualizer 2 address: %s, port: %d\n", visualizerAddr, port);
            fflush (stderr);

            visualizer2.setDestination(visualizerAddr, port);
            visualizer2.openConnection();

            break;

        case 'x':
#ifdef DEBUG
            fprintf (stderr, "identified -x parameter with argument: %s\n", optarg);
#endif
            x_chip = atoi(optarg);
            break;

        case 'y':
#ifdef DEBUG
            fprintf (stderr, "identified -y parameter with argument: %s\n", optarg);
#endif
            y_chip = atoi(optarg);
            break;
            
        case 'h':
        case ':':
        case '?':
        default:
#ifdef DEBUG
            fprintf (stderr, "identified -h parameter or following the default path for unknown parameters\n");
#endif
            print_help(argv[0]);
            break;
        }
    }

    if (binary_input == 2)
        print_help(argv[0]);

    if (replicate_output == 1 && foutput == stdout)
        print_help(argv[0]);

    if (ms_tick == 0)
        print_help(argv[0]);

    if (!spinnBoard.ison())
        print_help(argv[0]);

    if (core_id < 1 || core_id > 18)
        print_help(argv[0]);

    if (x_chip < 0 || x_chip >= 256)
        print_help(argv[0]);

    if (y_chip < 0 || y_chip >= 256)
        print_help(argv[0]);

    if (SDP_port < 1 || SDP_port > 7)
        print_help(argv[0]);

    fprintf (stderr, "Destination chip X: %d, Y: %d, core: %d, SDP port: %d\n", x_chip, y_chip, core_id, SDP_port);
    queue.setDestinationCore(x_chip, y_chip, core_id, SDP_port);
    
#ifdef DEBUG
    fprintf (stderr, "input/output format: %s\n", (binary_input==0)?"Text":"Binary");
    fprintf (stderr, "visualizer1 in use: %s\n", (visualizer1.ison())?"True":"False");
    fprintf (stderr, "visualizer2 in use: %s\n", (visualizer2.ison())?"True":"False");
    fflush (stderr);
#endif

    pthread_mutex_init(&readmutex, NULL);
    pthread_cond_init(&readcond, NULL);

    //initialization of the millisecond signal generator
    timer.setTimerInterval(ms_tick);

    //initialization of the receiver from the SpiNNaker board
    receiver.startReceiverThread (NULL);

    //start the thread that reads the input stream
    input.startInputThread(NULL);

    //start the timer
    timer.setTimerThread((void*)sigHandler);
    
    //read from stdin until EOF

    //wait until the input stream is finished
    input.waitForInputThread();

    //terminate the receiver thread
    receiver.killReceiverThread();
    receiver.waitForReceiverThread();
}
