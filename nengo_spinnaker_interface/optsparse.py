"""
Implementation of sparse connectivity for NEF/SpiNNaker
The Spinn constructor can be passed a max_fan_in parameters,
which limits the number of connections a neuron can receive in the network.

Author: Terry Stewart
"""

import numeric as np
import random
import ca.nengo.util.MU as MU
#import Jama.Matrix as Matrix
import subprocess
import os
import struct
from array import array
from java.lang import System

#def pinv(matrix, limit):
#    m = Matrix([[x for x in row] for row in matrix])
#    svd = m.svd()
#    sInv = svd.getS().inverse()
#    
#    i = 0
#    while i<svd.getS().rowDimension and svd.getS().get(i, i)>limit:
#        i += 1
#    while i<len(matrix):
#        sInv.set(i, i, 0)
#        i+=1
#    result = svd.getV().times(sInv).times(svd.getU().transpose()).getArray()
#    return result
    
def pinv(matrix, limit):
    shortfile = "matrix_%f" % random.random()
    filename = os.path.join("external", shortfile)
    
    #write matrix data to file
    infile = file(filename, "wb")
    float_array = array('f', [x for row in matrix for x in row])
    float_array.tofile(infile)
    infile.close() 
    
    #create output file
    outfile = file(filename+".inv", "wb")
    outfile.close()
    
#    print System.getProperty("os.name")
    if "windows" in System.getProperty("os.name").lower():
        subprocess.call("cmd /c pseudoInverse.bat "+shortfile+" "+shortfile+".inv"+" "+str(limit)+" "+str(-1), 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="external")
    else:
        subprocess.call("external/pseudoInverse "+filename+" "+filename+".inv"+" "+str(limit)+" "+str(-1), shell=True)
    
    mfile = file(filename+".inv", "rb")
    invmatrix = array("f")
    invmatrix.fromfile(mfile, len(matrix)*len(matrix[0]))
    return [[invmatrix[i*len(matrix[0])+j] for j in range(len(matrix[0]))] for i in range(len(matrix))]
        
def compute_sparse_weights(origin, post, transform, fan_in, noise=0.1, num_samples=100):
    encoder = post.encoders
    radius = post.radii[0]
    
    if hasattr(transform, 'tolist'): transform=transform.tolist()
    
    approx = origin.node.getDecodingApproximator('AXON')    
    
    # create X matrix
    X = approx.evalPoints        
    X = MU.transpose([f.multiMap(X) for f in origin.functions])
    
    # create A matrix
    A = approx.values
    
    S = fan_in
    N_A = len(A)
    samples = len(A[0])
    N_B = len(encoder)
    w_sparse = np.zeros((N_B, N_A),'f')
    noise_sd = MU.max(A)*noise
    decoder_list = [None for _ in range(num_samples)]
    for i in range(num_samples):
        indices = random.sample(range(N_A), S)
        activity = [A[j] for j in indices]
        n = [[random.gauss(0, noise_sd) for _ in range(samples)] for j in range(S)]
        activity = MU.sum(activity, n)
        activityT = MU.transpose(activity)
        gamma = MU.prod(activity, activityT)
        
        upsilon = MU.prod(activity, X)
        
        gamma_inv = pinv(gamma, noise_sd*noise_sd)
        
        
        decoder_list[i] = MU.prod([[x for x in row] for row in gamma_inv], upsilon)
    
    for i in range(N_B):
        ww = MU.prod(random.choice(decoder_list), MU.prod(MU.transpose(transform), encoder[i]))
        
        for j, k in enumerate(indices):
            w_sparse[i,k] = float(ww[j])/radius
    
    return list(w_sparse)

