# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 14:57:37 2019

@author: Sabri
"""
#%%
import pickle
from mylab.miniscope.functions import *
#%%
result_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all.pkl"
with open(result_path,'rb') as f:
    result = pickle.load(f)
#%% check results
# length of dff == length of ms_ts
l_dff = len(result['dff'][0])
l_ms_ts = []
for i in result['ms_ts']:
    l_ms_ts.append(len(i))
if l_dff != sum(l_ms_ts):
    print("l_dff is not the same length of l_ms_ts")
#%% align timepoint of ms_ts & track/ts,log & track/ts, all are aligned to time of ms_ts
(979,403,168,251,315,187,283,223,501,154,211,171)
