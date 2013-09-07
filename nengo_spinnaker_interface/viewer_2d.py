"""
Script to instantiate a viewer integrating the Nengo workbench with SpiNNaker with a single 2D input and a single 2D output.

./nengo-cl scripts/viewers/2dviewer_args.py -n 2d_view -b big-robospinn-local -d 1 -s 2
 - -n : sets the network_name (identifier for layouts)
 - -b : identifies the SpiNNaker board to use
 - -d : sets the target core in chip (0,0) of the SpiNNaker board receiving UDP packets sent by the UDPValueSender
 - -s : sets the source core in chip (0,0) of the SpiNNaker board sending UDP packets received by the UDPValueReceiver
"""

#./nengo-cl scripts/viewers/2dviewer_args.py -n 2d_view -b big-robospinn-local -d 2 -s 1


import nef
import nengo_spinnaker_interface.packet as packet
import sys

import getopt
opts, args = getopt.getopt(sys.argv[1:], 'b:n:d:s:')

board_name = ""
network_name = ""
source_core_id = dest_core_id = 0

for o, a in opts:
    if o == "-b":
        board_name = a
    elif o == "-n":
        network_name = a
    elif o == "-s":
        source_core_id = eval(a)
    elif o == "-d":
        dest_core_id = eval(a)


print board_name, network_name
            
net=nef.Network(network_name,quick=True)

# instantiates a 2D input
input=net.make_input('input',[0,0])

# instantiates a UDPValueSender to send input values to the SpiNNaker board identified by board_name on port 17893
uvs=packet.UDPValueSender('uss', board_name, 17893, dest_core_id=dest_core_id)
net.add(uvs)

# connects the input control to the UDPValueSender
net.connect(input,uvs.getTermination("input"))

# instantiates a UDPValueReceiver to receive SDP packets from SpiNNaker
uvr=packet.UDPValueReceiver('uvr', source_core_id=source_core_id)
net.add(uvr)

net.view()

                
                

