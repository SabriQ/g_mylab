# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 01:21:46 2020

@author: admin
"""

#%%
from mylab.miniscope.Mfunctions import *
from mylab.miniscope.Mplot import *
from mylab.Cvideo import Video
import os,sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import re
import scipy
#%%
ms_mat_path = r"G:\data\miniscope\Results_191172\20191218_111624_20191028-1102all_30fps\ms30fps.mat"
ms_ts_pkl_path = os.path.join(os.path.dirname(ms_mat_path),'ms_ts.pkl')

#%% load ms.mat come from CAIMAN
print("loading ms_mat ...") 
ms_load = loadmat(ms_mat_path)
print("load ms_ts successfully")
#%%
def equal_frames(dff,ms_ts):
    l_dff = dff.shape[0]# or sigraw.shape[0] or sigdeconvolved.shape[0] or CaTraces.shape[0]
    l_ms_ts = sum([len(i) for i in ms_ts])
    if l_dff != l_ms_ts:
        return 0
    else:
        return 1
#%%
    
sigraw=ms_load['ms']['sigraw']
#equal = equal_frames(dff,ms_ts)
equal =0

if equal==0:    
    with open(ms_ts_pkl_path,'rb') as f:
        ms_ts_pkl = pickle.load(f) 
    if equal_frames(sigraw,ms_ts_pkl)==1:
        ms_load['ms']['ms_ts'] = ms_ts_pkl
        spio.savemat(ms_mat_path,ms_load)
        print("reset the ms_ts with ms_ts.pkl,frames of timestaps and traces are equal!")
    else:
        print(f"l_dff: {l_dff} is not the same length of l_ms_ts: {l_ms_ts}")
        sys.exit()
else:
    print("frames of timestaps and traces are equal!")