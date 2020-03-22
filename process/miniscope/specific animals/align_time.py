# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 20:13:04 2020

@author: admin
"""

import glob          
import re            
import os
import numpy as np
import pandas as pd
import pickle   
import cv2          
from mylab.miniscope.Mplot import *
#%% glob all the timestamps.dat and msCam.avi 
animal_id = "191126"

tsFileList = glob.glob(os.path.join(r'W:\qiushou\miniscope\2019*',animal_id,"H*/timestamp.dat"))   
msCamFileList = glob.glob(os.path.join(r'W:\qiushou\miniscope\2019*',animal_id,"H*/msCam*.avi"))

ms_mat_path = r"G:\data\miniscope\Results_191126\20191016_110707_all\191126_post_processed.mat"
ms_ts_name = os.path.join(r'G:\data\miniscope\Results_191126\20191016_110707_all','ms_ts.pkl')


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
msCamFileList.sort(key=sort_key)

#%%#generate  ms_ts.pkl
temporal_downsampling=3   
if not os.path.exists(ms_ts_name):
    ts_session=[]
    for tsFile in tsFileList:
        datatemp=pd.read_csv(tsFile,sep = "\t", header = 0)
        ts_session.append(datatemp['sysClock'].values)    
    ttemp=np.hstack(ts_session)[::temporal_downsampling]
    # remporally downsample for each video
    # [i[::3] for i in ts_session][0]
    session_indend=(np.where(np.diff(ttemp)<0)[0]).tolist()
#    session_indend.append(-1)
    ts_session_ds=[]
    i0=0
    session_indstart=[]
    if len(session_indend)>0:
        for i in range(len(session_indend)):
            session_indstart.append(i0)
            ts_session_ds.append(ttemp[i0:(session_indend[i]+1)])
            i0=session_indend[i]+1
        ts_session_ds.append(ttemp[(session_indend[-1]+1):])
    else:
        ts_session_ds.append(ttemp[i0:])
    ms_ts=np.array(ts_session_ds)    
    with open(ms_ts_name,'wb') as output:
        pickle.dump(ms_ts,output,pickle.HIGHEST_PROTOCOL)
else:
    with open(ms_ts_name, "rb") as f:
        ms_ts= pickle.load(f)
print(f'concatenated timestamp of miniscope_video is located at {ms_ts_name}')
#%%
ts_lens = []
framenums = []
for tsFile in tsFileList:
    print(tsFile)
    print(">",end="")
    ts = pd.read_csv(tsFile,sep = "\t", header = 0)
    ts_len=ts.shape[0]        
    videoFileList=glob.glob(os.path.dirname(tsFile)+'\*.avi')   
    framenum=[]
    for video in videoFileList:
#         print(video)
        print("<",end="")
        cap = cv2.VideoCapture(video)
        framenum.append(int(cap.get(7)))
        cap.release()
    print([ts_len,sum(framenum)])
    ts_lens.append(ts_len)
    framenums.append(sum(framenum))
print(sum(ts_lens),sum(framenums))

#%%
#block_orders=[1,2,3,4,5,6,7,8,9,10,11,12]
#keep_blocks=[1,1,0,0,0,1,1,1,1,1,1,1]
#block_context_orders=["A","B","B","A","A","B","A","A","A","B","A","B"]
tsFile_orders=[1,2,3,4,5,6,6,6,7,8,9,9,10,10,11,12]

keep_tsfiles=[1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1]
block_conditions = []
for i in range(len(ts_lens)):
    ts = (sum(ts_lens[0:i]),sum(ts_lens[0:(i+1)]))
    frame = (sum(framenums[0:i]),sum(framenums[0:(i+1)]))
#    print(keep_blocks[i])
    block_conditions.append([keep_tsfiles[i],ts,frame])
print(block_conditions)
#%% load ms.mat come from CAIMAN
print("loading ms_mat ...") 
ms_load = loadmat(ms_mat_path)
print("load ms_ts successfully")
#cell ids mannually accepted
acceptedPool = ms_load['acceptedPool'] # start from 1,generated from miniscopeGUI
deletePool = ms_load['deletePool'] # start from 1, generated from miniscopeGUI
#cell ids caiman accepted
idx_accepted = ms_load['ms']['idx_accepted'] # start from 0
idx_deleted = ms_load['ms']['idx_deleted'] # start from 0
#sigraw and sigdeconvolved and CaTraces (removed baseline from sigdeconvolved) contains cells only involved in the acceptedPool 
sigraw = ms_load['ms']['sigraw'][:,acceptedPool-1] # estimate.c
sigdeconvolved=ms_load['ms']['sigdeconvolved'][:,acceptedPool-1] # estimate.s
CaTraces = np.transpose(np.array([i for i in ms_load['CaTraces'][:,0]]))[:,acceptedPool-1] # removeing the baseline of sigraw
print("only keep cells in acceptedPool!")
#idx_accepted deltf/f0 based on sigraw
dff =np.transpose( ms_load['ms']['dff'])

    
         