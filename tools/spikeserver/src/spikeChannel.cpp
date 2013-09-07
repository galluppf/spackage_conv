#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>

#include "spikeChannel.h"
#include "spinnpacket.h"
#include "sendPacket.h"
#include "SDPmsg.h"
#include "defines.h"

spikeChannel::spikeChannel()
{
    hostAddress = NULL;
    hostPort = 0;
    visualizerFD = 0;
    formatValue = spikeChannel::SDP_PACKET;
    in_use = false;

    HEVisualizer = NULL;
    VisualizerAddr = NULL;
    bzero(&SInVisualizer, sizeof(SInVisualizer));
}

spikeChannel::~spikeChannel()
{
    closeConnection();

    delete [] hostAddress;
}

bool spikeChannel::ison()
{
    return in_use;
}

int spikeChannel::setFormat(spikeChannel::format value)
{
    switch (value)
    {
        case spikeChannel::SDP_PACKET:
            formatValue = spikeChannel::SDP_PACKET;
            return 0;
            break;
        case spikeChannel::SPINNAKER_PACKET:
            formatValue = spikeChannel::SPINNAKER_PACKET;
            return 0;
            break;
        default:
            fprintf (stderr, "Visualizer: unknown packer format type: %d\n", value);
            fflush (stderr);
            return -1;
            break;
            
    }
}

int spikeChannel::setDestination(char *host , int port )
{
    hostPort = port;

    hostAddress = new char [(strlen(host)+1)];
    if (hostAddress == NULL)
    {
        fprintf (stderr, "Memory allocation error in setVisualizer\n");
        return -1;
    }
    else
    {
        memcpy(hostAddress, host, (strlen(host)+1));
        return 0;
    }
}

int spikeChannel::openConnection()
{
    if (hostAddress == NULL)
    {
        fprintf (stderr, "Unable to open a connection towards a NULL address\n");
        fflush (stderr);
        return -1;
    }
    if (hostPort == 0)
    {
        fprintf (stderr, "Unable to open a connection towards address: %s on port 0\n", hostAddress);
        fflush (stderr);
        return -2;
    }
    
    if ((HEVisualizer = gethostbyname(hostAddress)) == NULL)
    {
        fprintf (stderr, "Error during gethostbyname in openConnection for visualizer: %s, port: %d\n", hostAddress, hostPort);
        fflush (stderr);
        return -3;
    }

    VisualizerAddr = inet_ntoa(*(struct in_addr*)HEVisualizer->h_addr_list[0]);
    fprintf (stderr, "Spike channel towards host: %s, port: %d\n", VisualizerAddr, hostPort);
    fflush (stderr);

    if ((visualizerFD = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP))==-1)
    {
        fprintf (stderr, "Error during socket opening in openConnection for visualizer: %s, port: %d\n", hostAddress, hostPort);
        perror ("socket creation error towards visualizer");
        fflush (stderr);
        return -4;
    }

    SInVisualizer.sin_family = AF_INET;
    SInVisualizer.sin_port = htons(hostPort);
    if (inet_aton(VisualizerAddr, &SInVisualizer.sin_addr)==0)
    {
        fprintf(stderr, "inet_aton() towards the visualizer %s, port %d failed\n", hostAddress, hostPort);
        fflush (stderr);
        return -5;
    }

    in_use = true;
    return 0;
}

void spikeChannel::closeConnection()
{
    close(visualizerFD);
    visualizerFD = 0;

/*
    delete hostAddress;
    delete HEVisualizer;
    delete VisualizerAddr;

    hostAddress = NULL;
    HEVisualizer = NULL;
    VisualizerAddr = NULL;
*/

    in_use = false;
}

int spikeChannel::sendSpikes(unsigned int length, unsigned int* spikes)
{
    if (visualizerFD == 0)
    {
        fprintf (stderr, "socket not open for visualization to host %s, port %d\n", hostAddress, hostPort);
        return -1;
    }
    
    switch (formatValue)
    {
        case spikeChannel::SPINNAKER_PACKET:
            return sendSpiNNakerPacket(length, spikes);
            break;
        case spikeChannel::SDP_PACKET:
            return sendSDPPacket(length, spikes);
            break;
        default:
            //should never arrive here...
            fprintf (stderr, "Visualizer: unknown packer format type: %d\n", formatValue);
            fflush (stderr);
            return -1;
            break;
    }
    
}

int spikeChannel::sendSpiNNakerPacket(unsigned int length, unsigned int* spikes)
{
    struct SpiNNakerPacket packetVisualizer;
    unsigned int packetVisualizerLength;
    ssize_t numbytes;

    packetVisualizer.version = SPINNPROTVERSION;
    packetVisualizer.subversion = SPINNPROTSUBVERSION;
    packetVisualizer.opcode = htonl(STIM_OUT);
    packetVisualizer.option1 = htonl(0);
    packetVisualizer.option2 = htonl(length); //packetPtr->packets_ptr[i].arg1*4
    packetVisualizer.option3 = htonl(0);
    memcpy(&packetVisualizer.array, spikes, length);

    packetVisualizerLength = SPINNHEADERLENGTH + length;

#ifdef DEBUG
    fprintf (stderr, "output to visualizer - socket: %d, address: %s, port: %d\n", visualizerFD, VisualizerAddr, hostPort);
    fflush (stderr);
#endif

    if ((numbytes = sendto(visualizerFD, &packetVisualizer, packetVisualizerLength, 0, (struct sockaddr *) &SInVisualizer, sizeof(SInVisualizer))) == -1)  // send packet
    {
        perror ("visualizer spinnpacket - sendto:");
        fprintf (stderr, "oh dear - we didn't send our data to visualizer to host %s, port %d\n", hostAddress, hostPort);   // if numbytes = 0 then didn't send any data
        fflush (stderr);
    }

    return numbytes;
}

int spikeChannel::sendSDPPacket(unsigned int length, unsigned int* spikes)
{
    struct sdp_msg packetVisualizer;
    unsigned int packetVisualizerLength;
    ssize_t numbytes;

    packetVisualizer.ip_time_out = 0x01;
    packetVisualizer.pad = 0;
    packetVisualizer.flags = 0x07;
    packetVisualizer.tag = 255;
    packetVisualizer.dest_port = 1 << 5 | 1;
    packetVisualizer.srce_port = 255;
    packetVisualizer.dest_addr = 0;
    packetVisualizer.srce_addr = 0;
    packetVisualizer.cmd_rc = 256;
    packetVisualizer.sequence = 0;
    packetVisualizer.arg1 = length;
    packetVisualizer.arg2 = 0;
    packetVisualizer.arg3 = 0;

    packetVisualizerLength = SDPHEADERLENGHT + (length * 4); //(packetEntriesNum * 4)

    memcpy(&packetVisualizer.data, spikes, (length*4));

#ifdef DEBUG
    fprintf (stderr, "output to visualizer - socket: %d, address: %s, port: %d\n", visualizerFD, VisualizerAddr, hostPort);
    fflush (stderr);
#endif

    if ((numbytes = sendto(visualizerFD, &packetVisualizer, packetVisualizerLength, 0, (struct sockaddr *) &SInVisualizer, sizeof(SInVisualizer))) == -1)  // send packet
    {
        perror ("visualizer SDP - sendto:");
        fprintf (stderr, "oh dear - we didn't send our data to visualizer to host %s, port %d\n", hostAddress, hostPort);   // if numbytes = 0 then didn't send any data
        fflush (stderr);
    }

    return numbytes;
}

int spikeChannel::sendPacket(unsigned int length, sdp_msg* packet)
{
    ssize_t numbytes;
    
    if ((numbytes = sendto(visualizerFD, packet, length, 0, (struct sockaddr *) &SInVisualizer, sizeof(SInVisualizer))) == -1)  // send packet
    {
        perror ("sendPacket - sendto:");
        fprintf (stderr, "oh dear - we didn't send our data to visualizer to host %s, port %d\n", hostAddress, hostPort);   // if numbytes = 0 then didn't send any data
        fflush (stderr);
    }

    return numbytes;
}
