#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>

#include "spikeReceiver.h"
#include "globals.h"
#include "sigHandler.h"

spikeReceiver::spikeReceiver()
{

}

spikeReceiver::~spikeReceiver()
{
    pthread_detach(p1);
}

void spikeReceiver::setReceiverPort(int inputPort)
{
    port = inputPort;
}

void spikeReceiver::startReceiverServer()
{
    char portno_input[6];
    struct addrinfo hints_input, *servinfo_input, *p_input;
    int rv_input;

    snprintf (portno_input, 6, "%d", port);

    memset(&hints_input, 0, sizeof(hints_input));
    hints_input.ai_family = AF_INET; // set to AF_INET to force IPv4
    hints_input.ai_socktype = SOCK_DGRAM;
    hints_input.ai_flags = AI_PASSIVE; // use my IP
    hints_input.ai_protocol = 0;
    hints_input.ai_canonname = NULL;
    hints_input.ai_addr = INADDR_ANY;
    hints_input.ai_next = NULL;

    if ((rv_input = getaddrinfo(NULL, portno_input, &hints_input, &servinfo_input)) != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv_input));
        fflush (stderr);
        exit(1);
    }

    // loop through all the results and bind to the first we can
    for(p_input = servinfo_input; p_input != NULL; p_input = p_input->ai_next)
    {
        if ((receiveFD = socket(p_input->ai_family, p_input->ai_socktype, p_input->ai_protocol)) == -1)
        {
            fprintf(stderr, "listener: socket\n");
            fflush (stderr);
            continue;
        }

        if (bind(receiveFD, p_input->ai_addr, p_input->ai_addrlen) == -1)
        {
            close(receiveFD);
            fprintf(stderr, "listener: bind\n");
            fflush (stderr);
            continue;
        }

        break;
    }

    if (p_input == NULL)
    {
        fprintf(stderr, "listener: failed to bind socket\n");
        fflush (stderr);
        exit(-1);
    }

    freeaddrinfo(servinfo_input);

    fprintf (stderr, "Spinnaker UDP listener setup complete!\n");
    fflush (stderr);
}

void spikeReceiver::killReceiverThread()
{
    pthread_kill(p1, SIGUSR1);
}

void spikeReceiver::waitForReceiverThread()
{
    pthread_join(p1, NULL);
}

bool spikeReceiver::startReceiverThread(void* ptr)
{
    return (pthread_create(&p1, NULL, receiverThread, ptr) == 0);
}

void spikeReceiver::exitReceiverThread()
{
    pthread_exit(NULL);
}

void* spikeReceiver::receiverThread(void* ptr)
{
    unsigned char buffer_input[1515];
    struct sockaddr_storage their_addr_input;
    socklen_t addr_len_input;
    int numbytes_input;
    struct sdp_msg * scanptr;

    signal(SIGUSR1, user_signal);
    while (terminate != 1)
    {
        struct timespec recv_time;

#ifdef DEBUG
        fprintf(stderr, "listener: waiting to recvfrom...\n");
        fflush (stderr);
#endif

        addr_len_input = sizeof(their_addr_input);
        if ((numbytes_input = recvfrom(receiver.receiveFD, buffer_input, 1514 , 0, (struct sockaddr *)&their_addr_input, &addr_len_input)) == -1)
        {
            perror((char*)"error recvfrom");
            fflush (stderr);
            exit(-1);
        }

        clock_gettime(CLOCK_REALTIME, &recv_time);

        scanptr = (sdp_msg*) buffer_input;

#ifdef DEBUG
        fprintf (stderr, "received %d bytes\n", numbytes_input);
        fprintf (stderr, "destination port %X\n", scanptr->dest_port);
        fprintf (stderr, "source port %X\n", scanptr->srce_port);
        fprintf (stderr, "command %d\n", scanptr->cmd_rc);
        fflush (stderr);
#endif

        if (scanptr -> cmd_rc == 0 && scanptr->srce_port >> 5 == 3) //not using htonl to convert the endianness
        {
            struct destinationCore core;
#ifdef DEBUG
            fprintf (stderr, "identified sync packet\n");
            fflush (stderr);
#endif

            core = queue.getDestinationCore();
            if((scanptr -> srce_addr == (core.x_chip << 8 | core.y_chip)) && ((scanptr->srce_port & 0x1F) == core.core_id))
            {
#ifdef DEBUG
                fprintf (stderr, "sync core identified. Resync in progress\n");
                fflush (stderr);
#endif
                timer.resync_timer(&recv_time, scanptr -> arg2);
                spike_heard = 1;
            }
        }

        if ((scanptr -> cmd_rc == 256 && scanptr->srce_port >> 5 == 1) || (scanptr -> cmd_rc == 80 && scanptr->srce_port >> 5 == 3)) //not using htonl to convert the endianness
        {
            int i;
            int numSpikes = 0;
            unsigned int board_time;
            //unsigned int *neuronIDs = (unsigned int *) (&(scanptr -> data));

#ifdef DEBUG
            fprintf (stderr, "recognized spike\n");
            fflush (stderr);
#endif

            if (scanptr -> cmd_rc == 80 && scanptr->srce_port >> 5 == 3)
            {
                board_time = scanptr -> arg1;   //from app_monitoring
                numSpikes = scanptr -> arg2;
            }
            else
            {
                board_time = scanptr -> arg2;   //from original spike_send
                numSpikes = scanptr -> arg1;
            }

            for (i = 0; i < numSpikes; i++)
            {
                unsigned int currentID = ((unsigned int*) &(scanptr -> data)) [i];

#ifdef DEBUG
//                fprintf (stderr, "received: %8.8X, converted: %8.8X\n", neuronIDs[i], currentID);
                fprintf (stderr, "Time: %d, Spike received: %8.8X\n", board_time, currentID); //writing the received ID to the stderr (printed on screen)
                fflush (stderr);
#endif

                fflush (stderr);

                if (binary_input)
                {
                    fwrite(&board_time, sizeof(unsigned int), 1, foutput); //writing the time to the stdout in binary format
                    fwrite(&currentID, sizeof(unsigned int), 1, foutput); //writing the received ID to the stdout in binary format
                    fflush(foutput);
                    if (replicate_output)
                    {
                        fwrite(&board_time, sizeof(unsigned int), 1, stdout); //writing the time to the stdout in binary format
                        fwrite(&currentID, sizeof(unsigned int), 1, stdout); //writing the received ID to the stdout in binary
                        fflush(stdout);
                    }
                }
                else
                {
                    fprintf(foutput, "%X;%X;",board_time, currentID);
                    fflush (foutput);
                    if (replicate_output)
                    {
                        fprintf(stdout, "%X;%X;",board_time, currentID);
                        fflush (stdout);
                    }
                }

            }

            if (visualizer2.ison())
            {
                visualizer2.sendSpikes(numSpikes * 4, (unsigned int*) &(scanptr->data));
            }

        }

        fflush (stderr);

        if (terminate == 1)
            break;
    }

    return NULL;
}

