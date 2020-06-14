# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 16:55:49 2020

@author: SabriQ
"""

#%%
from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
from mylab.Cvideo import Video
import os,sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import re
import scipy
from mylab.Cmouseinfo import MouseInfo
#%% info
mouse_id = "191082"
# ms_mat_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_20191028-1102all\191172_post_processed3.mat"
# ms_ts_pkl_path = os.path.join(os.path.dirname(ms_mat_path),'ms_ts.pkl')
# result_path = os.path.join(os.path.dirname(ms_mat_path),'191172_whole_track.pkl')
mouseinfo = MouseInfo(mouse_info_path=r"Z:\QiuShou\mouse_info\191082_info.txt")

context_orders=mouseinfo.lick_water["context_orders"]
context_angles=mouseinfo.lick_water["context_angles"]
ms_starts=mouseinfo.lick_water["context_orders"]

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
behave_trackfiles = [i for i in glob.glob(behave_trackfiledir) if '0928' not in i]
behave_trackfiles.sort(key=sort_key)

behave_timestampdir = os.path.join(behave_dir,"*_ts.txt")
behave_timestamps = [i for i in glob.glob(behave_timestampdir) if '0928' not in i]
behave_timestamps.sort(key=sort_key)

behave_logffiledir = os.path.join(behave_dir,"*log.csv")
behave_logfiles = [i for i in glob.glob(behave_logffiledir) if '0928' not in i]
behave_logfiles.sort(key=sort_key)

behave_videodir = os.path.join(behave_dir,"*_labeled.mp4")
behave_videos = [i for i in glob.glob(behave_videodir) if '0928' not in i]
behave_videos.sort(key=sort_key)

mouseinfo.add_key("behave_trackfiles", behave_trackfiles, exp="lick_water")
mouseinfo.add_key("behave_timestamps", behave_timestamps, exp="lick_water")
mouseinfo.add_key("behave_logfiles", behave_logfiles, exp="lick_water")
mouseinfo.add_key("behave_videos", behave_videos, exp="lick_water")
mouseinfo.save