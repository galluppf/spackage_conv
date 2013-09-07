#!/usr/bin/python
"""
Interface to dump a nengo network in a python file that can be
imported by PACMAN


This Nengo module is called at the end of a Nengo script that needs 
to be translated for spinnaker, and produces a python file containing 
the network specifications as follows :: 

   pop = {} # a dictionary of populations


Each entry in the pop dictionary has as the keyname the name of the population, 
and the following entries:
 - n: number of neurons in the population, int
 - dimensions: dimensions of the encoders/decoders in the population, int
 - bias: bias current values, n x 1 array
 - encoders: encoders for the population, Dxn array
 - decoders: decoders for the population, Dxn array
 - taus: a 4 value array, with synaptic time constants (up to 4 different synapses)

Analogously, a projection dictionary proj{} is created :: 

   proj = {} # a dictionary of projections
   
where each entry is a dictionary, with a double key [pre, post] where 
pre and post are the presynaptic and postsynaptic label names, with the 
following entries:

 - tau: synaptic time constant
 - w: weight matrix
 - The following structures are also inserted:
 - inputs: a list of population labels, identified as inputs, which can be controlled in the runtime environment
 - outputs: a list of population labels identified as outputs, which can be controlled in the runtime environment
 - robot outputs: a list of population labels identified as robotic outputs, which can be used to control the robot
 - neurons_per_core: a dictionary of {'population label' : number of neurons per core (int)}, 
 as an indication to override default options in the splitter on a population basis
 - runtime: the simulation duration

Author: Terry Stewart, Francesco Galluppi
Email:  francesco.galluppi@cs.man.ac.uk 
"""


import ca.nengo.model.nef
import numeric as np
import optsparse
from ca.nengo.util import MU


def iszero(transform):
    for row in transform:
        for x in row:
            if x!=0: return False
    return True

class Population:
    def __init__(self, n, prefix=''):
        DT = 0.001
        self.bias = [nn.bias for nn in n.nodes]
        self.encoders = [[nn.scale*n.encoders[i][j] for i,nn in enumerate(n.nodes) ] for j in range(n.dimension) ]
        self.decoders = [[x[j]/DT for x in n.getOrigin('X').decoders ] for j in range(n.dimension)]
        self.name = prefix+n.name        
        self.dimension = n.dimension
        self.taus = []

    def generate_text(self):
        spacing = ' '*4
        text=['{']
        text.append("%s'%s': %s,"%(spacing, 'dimensions', self.dimension))
        text.append("%s'%s': %s,"%(spacing, 'bias', self.bias))
        text.append("%s'%s': %s,"%(spacing, 'encoders', self.encoders))
        text.append("%s'%s': %s,"%(spacing, 'decoders', self.decoders))
        while len(self.taus)<4: self.taus.append(2)
        text.append("%s'%s': %s,"%(spacing, 'taus', self.taus))
        text.append("%s}"%spacing)
        return '\n'.join(text)
        
        
class Projection:    
    def __init__(self, spinn, origin, termination, transform = None):
        scale = [nn.scale for nn in termination.node.nodes]
    
        if transform is None: 
            transform = termination.transform
        
        if origin.node.neurons>spinn.max_fan_in:
            w = optsparse.compute_sparse_weights(origin, termination.node, transform, spinn.max_fan_in)
        else:    
            w = MU.prod(termination.node.encoders,MU.prod(transform,MU.transpose(origin.decoders)))
            w = MU.prod(w,1.0/termination.node.radii[0])
        
        for i in range(len(w)):
            for j in range(len(w[i])):
                w[i][j] *= scale[i] / termination.tau
    
        w = MU.transpose(w)
        
        self.weights = w
        self.tau = int(round(termination.tau*1000))
        if self.tau not in spinn.populations[termination.node].taus:
            spinn.populations[termination.node].taus.append(self.tau)
        self.pre = spinn.populations[origin.node].name
        self.post = spinn.populations[termination.node].name
        
    def generate_text(self):
        spacing = ' '*4

        weight=[]
        for row in self.weights:
            t=', '.join(['%1.5f'%w for w in row])
            weight.append('[%s],'%(t))
        weight='\n          '.join(weight)

        text=['{']
        text.append("%s'%s': %d,"%(spacing, 'tau', self.tau))
        text.append("%s'%s': [%s],"%(spacing, 'w', weight))
        text.append("%s}"%spacing)
        
        return '\n'.join(text)
        
        
class SpiNN:
    def __init__(self, network, max_fan_in=50000):
        self.neurons_per_core = {}
        self.robot_outputs = []
        self.network = network
        self.populations = {}
        self.projections = []
        self.inputs = []        
        self.max_fan_in = max_fan_in
        self.runtime = 1*60*1000
        self.process_network(self.network)
        
    def get_taus(self):
        taus = []
        for p in self.projections:
            if p.tau not in taus: taus.append(p.tau)
        return taus
    
    def set_neurons_per_core(self, name, neurons_per_core):
        self.neurons_per_core[name] = neurons_per_core

    def set_runtime(self, runtime):
        self.runtime = runtime

        
    def set_robot_output(self, name):
        self.robot_outputs.append(name)    
        
    def set_runtime(self, runtime):
        """
        This function is used to set the duration of the simulation on spinnaker
        """
        self.runtime = runtime
        
    def process_network(self, network, prefix=''):
        for n in network.nodes:
            if isinstance(n, ca.nengo.model.nef.NEFEnsemble):
                self.populations[n] = Population(n, prefix)
            elif isinstance(n, ca.nengo.model.Network):
                self.process_network(n, prefix + n.name + '.')
            elif isinstance(n, ca.nengo.model.impl.FunctionInput):
                pass
            else:
                print 'WARNING: Unknown node',n
        
        for p in network.projections:
            print p.origin.node.name, '->', p.termination.node.name
            self.process_projection(p)
        
    def process_projection(self, p):
        origin = p.origin
        termination = p.termination
        
        if hasattr(origin, 'baseOrigin'): origin = origin.baseOrigin
        if hasattr(termination, 'baseTermination'): termination = termination.baseTermination
    
        pre = origin.node
        post = termination.node
        
                
                
        if isinstance(pre, ca.nengo.model.impl.NetworkArrayImpl) and isinstance(post, ca.nengo.model.impl.NetworkArrayImpl):
            for term in termination.nodeTerminations:
                transform = np.array(term.transform)
                index = 0
                for i,n in enumerate(origin.nodeOrigins):
                    t = transform[:,index:index+n.dimensions]
                    index += n.dimensions
                    if not iszero(t):
                        self.projections.append(Projection(self, n, term, transform=t))        
        elif isinstance(pre, ca.nengo.model.impl.NetworkArrayImpl):
            transform = np.array(termination.transform)
            index = 0
            for i,n in enumerate(origin.nodeOrigins):
                t = transform[:,index:index+n.dimensions]
                index += n.dimensions
                self.projections.append(Projection(self, n, termination, transform=t))
        elif isinstance(post, ca.nengo.model.impl.NetworkArrayImpl):
            for t in termination.nodeTerminations:
                if isinstance(pre, ca.nengo.model.impl.FunctionInput):
                    self.inputs.append(str(self.populations[t.node].name))
                else:
                    self.projections.append(Projection(self, origin, t))
        elif isinstance(pre, ca.nengo.model.impl.FunctionInput):
            self.inputs.append(str(self.populations[post].name))
        elif pre in self.populations and post in self.populations:
            self.projections.append(Projection(self, origin, termination))
        else:
            print 'WARNING: Unknown projection', p
            print '         pre: ',pre
            print '         post: ',post
    
    def print_info(self):
        print self.get_taus()
        for p in sorted(self.populations.values(), key=lambda a: a.name): print p.name
        for p in self.projections: print '%s -> %s'%(p.pre, p.post)
        
    def generate_text(self):
        text = []
        text.append('pop = {}')
        for p in sorted(self.populations.values(), key=lambda p:p.name):
            text.append("pop['%s'] = %s"%(p.name, p.generate_text()))
        text.append('proj = {}')    
        for p in sorted(self.projections, key=lambda p:(p.pre, p.post)):
            text.append("proj['%s', '%s'] = %s"%(p.pre, p.post, p.generate_text()))
        text.append("inputs = %s"%self.inputs)
        text.append("robot_outputs = %s"%self.robot_outputs)
        text.append("neurons_per_core = %s"%self.neurons_per_core)
        text.append("runtime = %s\n"%self.runtime)
        
        
        return '\n'.join(text)
        
        
    def write_to_file(self, filename):
        f=open(filename,'w')
        f.write(self.generate_text())
        f.close()
    
