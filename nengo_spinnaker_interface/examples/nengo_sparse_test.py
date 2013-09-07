import nef

import nengo_spinnaker_interface.spinn as spinn


net = nef.Network('Test', fixed_seed=1)

input=net.make_input('input',[0])
A=net.make('A', neurons=100, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))
B=net.make('B', neurons=200, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))
C=net.make('C', neurons=100, dimensions=1, max_rate=(100,150),radius=1, intercept=(-.9,.9))


net.connect(input, A)
net.connect(A, B)
net.connect(B, C)

s=spinn.SpiNN(net.network)
s.print_info()
s.write_to_file('nengo_spinnaker_interface/nengo_values.py')
