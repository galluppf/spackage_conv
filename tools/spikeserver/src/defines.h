#ifndef __DEFINES_H
#define __DEFINES_H

#define INPUT_PORT_SPINNAKER    54321                   //port to receive spinnaker packets
#define OUTPUT_UDP_PORT_BOARD   17893                   //port to send stimuli to spinnaker board
#define SPINNPROTVERSION        0x1                     // this is the Spinnaker Protocol Version (1= 1st release (ROM)) !!!
#define SPINNPROTSUBVERSION     0x0                     // for testing
#define SPINNHEADERLENGTH       18                      // this is the SpiNNaker protocol byte overhead, ver(2)+opcode(4)+3options(4)
#define STIM_OUT                73                      // opcode for the SpiNNaker packet
#define ACK                     61                      // opcode for the ack spinnaker packet
#define SDP_BUF_SIZE            256                     //max size of the SDP data buffer (in bytes)
#define MAXBLOCKSIZE            (SDP_BUF_SIZE / 4)      // max number of words in a block - !! should be 64
#define SDPHEADERLENGHT         26                      // this is the SDP packet byte overhead

#endif
