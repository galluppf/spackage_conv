"""
square example for nengo/spinnaker

A->B implementing the identity function f(x)=x^2

Results can be viewed using the following command:
./nengo-cl nengo_spinnaker_interface/viewer_1d.py -b <spinnaker board address> -d 1 -s 2
"""
import nef                      

# importing the Nengo/SpiNNakerinterface module
import nengo_spinnaker_interface.spinn as spinn

def square(x):
    return(x[0]*x[0])

net=nef.Network('square_spinnaker',quick=True)
input=net.make_input('input',[0])

A=net.make('A', neurons=100, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))
B=net.make('B', neurons=100, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))

net.connect(input,A)
net.connect(A,B,func=square)


s=spinn.SpiNN(net.network)
s.print_info()
s.write_to_file('nengo_spinnaker_interface/nengo_values.py')


