#ifndef __SDP_MSG_H
#define __SDP_MSG_H

#include "defines.h"

#pragma pack(1)

struct sdp_msg      // SDP message (=292 bytes)
{
    unsigned char ip_time_out;
    unsigned char pad;

    // sdp_hdr_t

    unsigned char flags;            // SDP flag byte
    unsigned char tag;          // SDP IPtag
    unsigned char dest_port;        // SDP destination port
    unsigned char srce_port;        // SDP source port
    unsigned short dest_addr;       // SDP destination address
    unsigned short srce_addr;       // SDP source address

    // cmd_hdr_t (optional)

    unsigned short int cmd_rc;          // Command/Return Code
    unsigned short int sequence;            // Packet Sequence number (if used, otherwise 0)
    unsigned int arg1;          // Arg 1
    unsigned int arg2;          // Arg 2
    unsigned int arg3;          // Arg 3

    // user data (optional)

    unsigned int data[MAXBLOCKSIZE];    // User data (256 bytes)
};

#endif
