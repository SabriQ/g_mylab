import scipy.io as spio
import matplotlib.pyplot as plt
import numpy as np
def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict
#
def Traceview(RawTraces,neuronsToPlot):
    maxRawTraces = np.amax(RawTraces)
    plt.figure(figsize=(60,15))
                              
#    plt.subplot(2,1,1); 
    plt.figure; plt.title(f'Example traces (first {neuronsToPlot} cells)')
    plot_gain = 10 # To change the value gain of traces
    
    for i in range(neuronsToPlot):
#        if i == 0:        
#          plt.plot(RawTraces[i,:])
#        else:             
      trace = RawTraces[i,:] + maxRawTraces*i/plot_gain
      plt.plot(trace)

#    plt.subplot(2,1,2); 
#    plt.figure; 
#    plt.title(f'Deconvolved traces (first {neuronsToPlot} cells)')
#    plot_gain = 20 # To change the value gain of traces
   
#    for i in range(neuronsToPlot):
#        if i == 0:       
#          plt.plot(DeconvTraces[i,:],'k')
#        else:            
#          trace = DeconvTraces[i,:] + maxRawTraces*i/plot_gain
#          plt.plot(trace,'k')
 

