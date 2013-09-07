"""
communication channel example for nengo/spinnaker

A->B implementing the identity function f(x)=x

Results can be viewed using the following command:
./nengo-cl nengo_spinnaker_interface/viewer_1d.py -b <spinnaker board address> -d 1 -s 2
"""
import nef                      

# importing the Nengo/SpiNNakerinterface module
import nengo_spinnaker_interface.spinn as spinn

net=nef.Network('communication_channel_spinnaker',quick=True)
               
input=net.make_input('input',[0])

A=net.make('A', neurons=128, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))
B=net.make('B', neurons=128, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))

net.connect(input,A)
net.connect(A,B)

s=spinn.SpiNN(net.network)
s.print_info()
#s.set_runtime(5*60*1000)
s.write_to_file('nengo_spinnaker_interface/nengo_values.py')


