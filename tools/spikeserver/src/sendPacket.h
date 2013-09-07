#ifndef __SEND_PACKET_H
#define __SEND_PACKET_H

#include "SDPmsg.h"

struct sendPacket
{
    unsigned int * packet_lengths;
    struct sdp_msg * packets_ptr;
};

#endif
