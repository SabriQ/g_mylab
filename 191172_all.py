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
#%% info
mouse_id = "191172"
mouse = {}
#%% read miniscale trace
ms_mat_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms.mat"
#os.path.exists(ms_mat_path)
ms = loadmat(ms_mat_path)['ms']
dff = ms['dff']
#S_dff=ms['S_dff']
ms_ts = ms['ms_ts']


del ms
#dict_keys(['height', 'width', 'CorrProj', 'PNR', 'old_sigraw', 'old_sigdeconvolved', 'sigraw',
#'sigdeconvolved', 'SFP', 'numNeurons', 'ms_ts', 'dff', 'S_dff', 'idx_accepted', 'idx_deleted'])
#%% view trace
#Traceview(ms['sigraw'].T,4)
#Traceview(ms['sigdeconvolved'].T,40)
Traceview(dff,16)
#Traceview(S_dff,40)
#%% read track coordinates
behave_trackfiledir = r'X:\\miniscope\\*\\' + mouse_id+"\\*.h5"
behave_trackfiles = [i for i in glob.glob(behave_trackfiledir) if '2019111' not in i]
behave_timestampdir = r'X:\\miniscope\\*\\' + mouse_id+"\\*_ts.txt"
behave_timestamps = [i for i in glob.glob(behave_timestampdir) if '2019111' not in i]
#if len(ms['ms_ts']) != len(trackfiles):
#    print("Attention: The number of miniscope videos are not the same to the number of behaviral videos")
blocks[]
for behave_trackfile,behave_timestamp in zip(behave_trackfiles,behave_timestamps):
    trackpd.read_hdf(behave_trackfile)
    blocks.append
    