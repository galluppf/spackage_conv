"""
2D communication channel, used to manually control the spiNNaker/robot system in a navigation task.
An input + 3 population are connected in a communication channel:

input (in nengo) --> source --> middle --> target --> nengo/robot

./nengo-cl nengo_spinnaker_interface/viewer_2d.py -n 2d_view -b <spinnaker board address> -d 2 -s 1

The input is provided by the nengo benchmark; the output is sent to both nengo (for visualisation) and to the robot (for control)
.. moduleauthor:: Francesco Galluppi, University of Manchester, francesco.galluppi@cs.man.ac.uk
"""

import nef

# importing the Nengo/SpiNNakerinterface module
import nengo_spinnaker_interface.spinn as spinn

net=nef.Network('2D Representation/Robot')

# Input is used to control the first population, and it's not explicitly modelled in SpiNNaker
input=net.make_input('input',[0,0])

# source is the population which has input (a 2D vector) as the value it's representing. 
# the source population is encoded as a LIF/NEF neuron, translating a (2D) value coming from input into spiking activity
source=net.make('source', 100, dimensions=2, quick=True, intercept=(-.9,.9),max_rate=(120,140))

# middle is a LIF neuron, receiving spikes and encoding its output in another population spike train
middle=net.make('middle', 100, dimensions=2, quick=True, intercept=(-.9,.9),max_rate=(120,140))

# target is a NEF/OUT population, receiving a spike train and translating it into a value to be sent out (to nengo or robot)
# intercept is set to .1, .9 so to not send small (~0) motor commands
target=net.make('target', 100, dimensions=2, quick=True, intercept=(.01,.9),max_rate=(120,140))

# connecting the input + 3 population in a communication channel
# input (in nengo) --> source --> middle --> target --> nengo/robot
net.connect(input,source)
net.connect(source,middle)
net.connect(middle,target)

# values from the target population will be interpreted as 2D motor commands and sent to the robot and to nengo for visualisation


# dumps the nengo network in a text file
#spinn.dump_network(net)

s=spinn.SpiNN(net.network)
s.set_robot_output('target')
s.print_info()
s.write_to_file('nengo_spinnaker_interface/nengo_values.py')

# at this point it is possible to execute the "compile_nengo_model" script in the nengo_spinnaker_interface directory
# the compile_nengo_model script runs PACMAN and deploys the model on the default_board_address 
#  if run_pacman and run_simulation are set to true in pacman.cfg (nengo_interface section)

# in order to visualise the results use ... 
