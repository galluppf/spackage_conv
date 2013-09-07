#ifndef __SPINNPACKET_H
#define __SPINNPACKET_H

#include "defines.h"

#pragma pack(1)

struct spinnpacket
{
    unsigned short version;
    unsigned command;
    unsigned int option1;
    unsigned int option2;
    unsigned int option3;
    unsigned int neuronIDs;
};


// section for global defs for SpiNN output functions
struct SpiNNakerPacket {
    unsigned char subversion;
    unsigned char version;
    unsigned int opcode;
    unsigned int option1;
    unsigned int option2;
    unsigned int option3;
    unsigned int array[MAXBLOCKSIZE];
};

#endif