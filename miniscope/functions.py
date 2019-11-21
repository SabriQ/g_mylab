import scipy.io as spio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle 
import os
import glob
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

def generate_tsFileList(dateDir=r"X:\miniscope\20191028\191172"):    
    tsFileList = glob.glob(os.path.join(dateDir,"H*/timestamp.dat"))
#    tsFileList = [i for i in tsFileList if "2019111" not in i]
    def sort_key(s):     
        if s:            
            try:         
                date = re.findall('\d{8}', s)[0]
            except:      
                date = -1            
            try:         
                H = re.findall('H(\d+)',s)[0]
            except:      
                H = -1            
            try:         
                M = re.findall('M(\d+)',s)[0]
            except:      
                M = -1            
            try:         
                S = re.findall('S(\d+)',s)[0]
            except:      
                S = -1            
            try:         
                ms = re.findall('msCam(\d+)',s)[0]
            except:      
                ms = -1  
            return [int(date),int(H),int(M),int(S),int(ms)]
    tsFileList.sort(key=sort_key)
    print(f"get {len(tsFileList)} timestamps files")
    return tsFileList

def generate_ms_ts(tsFileList,save_path,temporal_downsampling=3):
    if not os.path.exists(save_path):
        ts_sessions=[]       
        for tsFile in tsFileList:
            datatemp=pd.read_csv(tsFile,sep = "\t", header = 0)
            ts_sessions.append(datatemp['sysClock'].values) 
        #         print(len((datatemp['sysClock'].values)))
        if len(tsFileList)>1:
            ts_all=np.hstack(ts_sessions)[::temporal_downsampling]#downsampled timestamps of all the blocks
            # remporally downsample for each video
            # [i[::3] for i in ts_sessions][0]
            ts_breakpoints=(np.where(np.diff(ts_all)<0)[0]).tolist()# ts_breakpoints means the location of the lagest timepoint of each session
    #        print(ts_breakpoints)
            ends = np.add(ts_breakpoints,1)
            starts = np.insert(ends,0,0)
            ts_blocks=[]
            for start,end in zip(starts,ends):
                ts_blocks.append(ts_all[start:end])            
            ts_blocks.append(ts_all[ts_breakpoints[-1]+1:])# append the last block[:]
        elif len(tsFileList)==1:
            ts_blocks = ts_sessions            
        ms_ts=np.array(ts_blocks)
        with open(save_path,'wb') as output:
            pickle.dump(ms_ts,output,pickle.HIGHEST_PROTOCOL)
    else:
        with open(save_path,'rb') as f:
            ms_ts = pickle.load(f)                             
    print(f'concatenated timestamp of miniscope_video is located at {save_path}')
def add_ms_ts2mat(ms_ts_path,mat_path):
    with open(ms_ts_path,"rb") as f:
        ms_ts = pickle.load(f)
    ms_mat = loadmat(mat_path)
    ms_mat['ms']['ms_ts']=ms_ts
    spio.savemat(mat_path,{"ms":ms_mat["ms"]})
    del ms_mat
    del ms_ts
if __name__ == "__main__":
    #%% 产生ms_ts2.pkl 是ms_ts.pkl的纠正
#    dateDir=r"X:\miniscope\20191*\191172"
#    save_path=r'Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms_ts2.pkl'
#    tsFileList=generate_tsFileList(dateDir)
#    print(tsFileList)
#    generate_ms_ts(tsFileList,save_path)
    #%% 将产生的ms_ts2.pkl 合并到对应的ms.mat中去
#    ms_ts_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms_ts2.pkl"
#    mat_path=r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms.mat"
#    add_ms_ts2mat(ms_ts_path,mat_path)