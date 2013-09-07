#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "SDPmsg.h"

class spikeChannel
{
public:
    enum format {SPINNAKER_PACKET, SDP_PACKET};
    
public:
    spikeChannel();
    ~spikeChannel();

    int setDestination(char *host , int port);
    int setFormat(format value);
    int openConnection();
    int sendSpikes(unsigned int length, unsigned int* spikes);
    int sendPacket(unsigned int length, struct sdp_msg * packet);
    void closeConnection();
    bool ison();
    
private:
    int visualizerFD;
    int formatValue;
    char *hostAddress;
    int hostPort;

    bool in_use;

    struct hostent *HEVisualizer;
    struct sockaddr_in SInVisualizer;
    char *VisualizerAddr;
    int sendSpiNNakerPacket(unsigned int length, unsigned int* spikes);
    int sendSDPPacket(unsigned int length, unsigned int* spikes);
};
