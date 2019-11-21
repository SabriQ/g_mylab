# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 17:27:19 2019

@author: Sabri
"""
#%%
from mylab.miniscope.functions import *
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
#%% info
mouse_id = "191172"
ms_mat_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms.mat"
behave_dir = os.path.join(r"X:\miniscope\2019*" , mouse_id)
def sort_key(s):     
    if s:            
        try:         
            date = re.findall('-(\d{8})-', s)[0]
        except:      
            date = -1            
        try:         
            HMS = re.findall('-(\d{6})[_|D]',s)[0]
        except:      
            HMS = -1          
        return [int(date),int(HMS)]

behave_trackfiledir = os.path.join(behave_dir,"*.h5")
behave_trackfiles = [i for i in glob.glob(behave_trackfiledir) if '2019111' not in i]
behave_trackfiles.sort(key=sort_key)
behave_timestampdir = os.path.join(behave_dir,"*_ts.txt")
behave_timestamps = [i for i in glob.glob(behave_timestampdir) if '2019111' not in i]
behave_timestamps.sort(key=sort_key)
behave_logffiledir = os.path.join(behave_dir,"*log.csv")
behave_logfiles = [i for i in glob.glob(behave_logffiledir) if '2019111' not in i]
behave_logfiles.sort(key=sort_key)
result = {}
result_path =os.path.dirname(ms_mat_path)+'.pkl'
#%% read miniscale trace
#os.path.exists(ms_mat_path)
ms = loadmat(ms_mat_path)['ms']
dff = ms['dff']
#S_dff=ms['S_dff']# S_dff is deconvolved dff
ms_ts = ms['ms_ts']
del ms
#dict_keys(['height', 'width', 'CorrProj', 'PNR', 'old_sigraw', 'old_sigdeconvolved', 'sigraw',
#'sigdeconvolved', 'SFP', 'numNeurons', 'ms_ts', 'dff', 'S_dff', 'idx_accepted', 'idx_deleted'])

#%% view trace
#Traceview(ms['sigraw'].T,4)
#Traceview(ms['sigdeconvolved'].T,40)
#Traceview(dff,16)
#Traceview(S_dff,40)
#%% read track coordinates
behave_data=[]
i = 1
for behave_trackfile,behave_timestamp,behave_logfile in zip(behave_trackfiles,behave_timestamps,behave_logfiles):
    blocknum = i
    i = i+1
    blockname = os.path.basename(behave_timestamp).split('_ts.txt')[0]
    if blockname in behave_trackfile:
        track = pd.read_hdf(behave_trackfile)
#        Head_x = track[track.columns[0]]
#        Head_y = track[track.columns[1]]
#        Head_lh = track[track.columns[2]]
#        Body_x = track[track.columns[3]]
#        Body_y = track[track.columns[4]]
#        Body_lh = track[track.columns[5]]
#        Tail_x = track[track.columns[6]]
#        Tail_y = track[track.columns[7]]
#        Tail_lh = track[track.columns[8]]
    if blockname in behave_timestamp:
        ts = pd.read_table(behave_timestamp,sep='\n',header=None)
        
    if blockname in behave_logfile:
        log = pd.read_csv(behave_logfile,header=0)
    block={}
    block = {"blocknum" : blocknum,
            "blockname" : blockname,
            "track" : track,
            "ts" : ts,
            "log" : log}
    behave_data.append(block)
#%%
result={"mouse_id":mouse_id,
       "ms_mat_path":ms_mat_path,
       "dff":dff,
       "ms_ts":ms_ts,
       "behave_trackfiles":behave_trackfiles,
       "behave_timestamps":behave_timestamps,
       "behave_logfiles":behave_logfiles,     
       "behave_data":behave_data}
#%%
with open(result_path,'wb') as f:
    pickle.dump(result,f)
