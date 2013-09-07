"""
integrator example for nengo/spinnaker

A->B->C implementing an integrator in the B node, which is self connected.

Results can be viewed using the following command:
./nengo-cl nengo_spinnaker_interface/viewer_1d.py -b spinn-1 -d 1 -s 2
"""
import nef

# importing the Nengo/SpiNNakerinterface module
import nengo_spinnaker_interface.spinn as spinn

net=nef.Network('SpiNN Integrator',quick=False)


input=net.make_input('input',[0])


tau_syn = .2

n = 100

A=net.make('A', neurons=n, dimensions=1, max_rate=(120,150), intercept=(-.90,.90))
B=net.make('B', neurons=n*2, dimensions=1, max_rate=(120,150), intercept=(-.90,.90))
C=net.make('C', neurons=n, dimensions=1, max_rate=(120,150), intercept=(-.90,.90))


net.connect(input,A,pstc=.001)
net.connect(A,B,pstc=tau_syn, weight=tau_syn)
net.connect(B,B,pstc=tau_syn)
net.connect(B,C)

s=spinn.SpiNN(net.network)      # instantiates a SpiNNaker/NEF network
s.print_info()                  # prints informations about the nodes 
s.write_to_file('nengo_spinnaker_interface/nengo_values.py')    # dumps network values into a python file

