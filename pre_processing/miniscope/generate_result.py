# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 17:27:19 2019

@author: Sabri
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
#%% info
mouse_id = "191172"
ms_mat_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms.mat"
behave_dir = os.path.join(r"X:\miniscope\2019*" , mouse_id)
ms_starts = [979,403,168,251,315,187,283,223,501,154,211,171]# the frame in behave_bideo which present the start of ms
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
behave_videodir = os.path.join(behave_dir,"*_labeled.mp4")
behave_videos = [i for i in glob.glob(behave_videodir) if '2019111' not in i]
behave_videos.sort(key=sort_key)
result = {}
result_path =os.path.dirname(ms_mat_path)+'.pkl'
#%% read miniscale trace
#os.path.exists(ms_mat_path)
print("loading ms_mat ...")
ms = loadmat(ms_mat_path)['ms']
dff = ms['dff'] # 
#S_dff=ms['S_dff']# S_dff is deconvolved dff
#sigraw = ms['sigraw'] # estimate.c
#sigdeconvolved=ms['sigdeconvolved'] # estimate.s
ms_ts = ms['ms_ts']
# check results
# length of dff == length of ms_ts
l_dff = dff.shape[1]
l_ms_ts = []
for i in ms_ts:
    l_ms_ts.append(len(i))
    del i
if l_dff != sum(l_ms_ts):
    print(f"l_dff: {l_dff} is not the same length of l_ms_ts: {l_ms_ts}")
    sys.exit()
print("load ms_ts successfully")
del ms
del l_dff
del l_ms_ts
#output dff,ms_ts
#dict_keys(['height', 'width', 'CorrProj', 'PNR', 'old_sigraw', 'old_sigdeconvolved', 'sigraw',
#'sigdeconvolved', 'SFP', 'numNeurons', 'ms_ts', 'dff', 'S_dff', 'idx_accepted', 'idx_deleted'])
#%% construct list blocks each block of which has a DataFrame containing all the traces and ms_ts
starts = [0]
ends=[]
len_ms_ts = []
msblocks = []
for i,temp in enumerate(ms_ts,1):
    len_ms_ts.append(len(temp))     
    if i != len(ms_ts):
        block = pd.DataFrame()
        ends.append(sum(len_ms_ts))
        starts.append(ends[-1])
        print('trace and ms_ts[',starts[i-1],ends[i-1],']constructed as DataFrame')
        for j in range(1,len(dff)+1):
            block[str(j)]=dff[j-1,starts[i-1]:ends[i-1]]
        
    else:
        block = pd.DataFrame()
        print('trace and ms_ts[',starts[i-1],'end',']constructed as DataFrame')
        for j in range(1,len(dff)+1):
            block[str(j)]=dff[j-1,starts[i-1]:]
    block['ms_ts']=temp
    msblocks.append(block)
    del i,temp,j
print("dff and ms_ts have been constructed as DataFrame. ")      
del starts
del ends
del len_ms_ts
del block
del dff
del ms_ts

#out put 'msblocks'

#%% view trace
#TracesView(ms['sigraw'].T,4)
#TracesView(ms['sigdeconvolved'].T,40)
#TracesView(dff,16)
#TracesView(S_dff,40)

#%% read track coordinates
blocknames = []
behaveblocks=[]
logblocks=[]
i=1 

for behave_trackfile,behave_timestamp,behave_logfile in zip(behave_trackfiles,behave_timestamps,behave_logfiles):    
    print(f'{i}/{len(behave_trackfiles)} blocks',end= ' ')
    blockname = os.path.basename(behave_timestamp).split('_ts.txt')[0]
    blocknames.append(blockname)
    print("generate 'blocknames'",end = ' ')
    behaveblock=pd.DataFrame()
    if blockname in behave_timestamp:
        ts = pd.read_table(behave_timestamp,sep='\n',header=None)
        behaveblock['be_ts']=ts[0]
    behaveblocks.append(behaveblock)
    if blockname in behave_trackfile:
        track = pd.read_hdf(behave_trackfile)
        behaveblock['Head_x'] = track[track.columns[0]]
        behaveblock['Head_y'] = track[track.columns[1]]
        behaveblock['Head_lh'] = track[track.columns[2]]
        behaveblock['Body_x'] = track[track.columns[3]]
        behaveblock['Body_y'] = track[track.columns[4]]
        behaveblock['Body_lh'] = track[track.columns[5]]
        behaveblock['Tail_x'] = track[track.columns[6]]
        behaveblock['Tail_y'] = track[track.columns[7]]
        behaveblock['Tail_lh'] = track[track.columns[8]]       
# 如果每一帧都放进来做计算，那么点的抖动对速度值的影响非常大，因此根据miniscope的采样率来进行计算，降采样后大概是10fps,也就是每3个点才取一个点进行计算，这样会稍微降低一点速度的抖动
#        behaveblock['Headspeeds'],behaveblock['Headspeed_angles'] = speed(behaveblock['Head_x'],behaveblock['Head_y'],behaveblock['be_ts'],s)
#        behaveblock['Bodyspeeds'],behaveblock['Bodyspeed_angles'] = speed(behaveblock['Body_x'],behaveblock['Body_y'],behaveblock['be_ts'],s)
#        behaveblock['Tailspeeds'],behaveblock['Tailspeed_angles'] = speed(behaveblock['Tail_x'],behaveblock['Tail_y'],behaveblock['be_ts'],s)
#        behaveblock['headdirections'],behaveblock['taildirections'], behaveblock['arch_angles'] = direction(behaveblock['Head_x'].tolist(),behaveblock['Head_y'].tolist(),behaveblock['Body_x'].tolist(),behaveblock['Body_y'].tolist(),behaveblock['Tail_x'].tolist(),behaveblock['Tail_y'].tolist())
    print("generate 'behaveblocks'",end = ' ')
    if blockname in behave_logfile:
        logblock = pd.read_csv(behave_logfile,header=0)
        logblocks.append(logblock)
    print("generate 'logblocks'")
    print(f"behave data of {blockname} has been constructed as DataFrame")
    del behave_trackfile,behave_timestamp,behave_logfile
    i= i+1
print("All the behave data has been constructed as DataFrame. ")
del i 
# output behaveblocks, logblocks,blocknames

#%% align timepoint of ms_ts & track/ts,log & track/ts, all are aligned to time of ms_ts
result['video_scale'] = scale(behave_videos[0])
s = result['video_scale'][0]
for i,start in enumerate(ms_starts,0):
    delta_t = behaveblocks[i]['be_ts'][start-1]-0.1 
    #这个-0.1s即100ms指的大概是 miniscope启动大概需要100ms的时间，即miniscope的0时刻大约比led_on要晚大约100ms,
    #这是通过对比ms_ts(原始)的最大值，和视频的结束时间的出来的，如果不-0.1,差值的平均在113ms左右
    behaveblocks[i]['correct_ts']=behaveblocks[i]['be_ts']-delta_t
    del i
    del start
#for start,block in zip(starts,result['behave_data']):
#    delta_t = block['ts'][0][start+1]
#    block['ts'][0] = block['ts'][0]-delta_t 
aligned_behaveblocks = []
i = 1
for msblock,behaveblock in zip(msblocks,behaveblocks):
    aligned_behaveblock = pd.DataFrame()
    aligned_behaveblock['ms_ts'] = msblock['ms_ts'] 
    print(f"{i}/{len(msblocks)} blocks index behave DataFrame according to ms_ts")
    aligned_behaveblock['be_frame']=[find_close_fast((behaveblock['correct_ts']*1000),i) for i in msblock['ms_ts']]
    aligned_behaveblock = aligned_behaveblock.join(behaveblock.iloc[aligned_behaveblock['be_frame'].tolist(),].reset_index())
    aligned_behaveblock['Headspeeds'],aligned_behaveblock['Headspeed_angles'] = speed(aligned_behaveblock['Head_x'],aligned_behaveblock['Head_y'],aligned_behaveblock['be_ts'],s)
    aligned_behaveblock['Bodyspeeds'],aligned_behaveblock['Bodyspeed_angles'] = speed(aligned_behaveblock['Body_x'],aligned_behaveblock['Body_y'],aligned_behaveblock['be_ts'],s)
    aligned_behaveblock['Tailspeeds'],aligned_behaveblock['Tailspeed_angles'] = speed(aligned_behaveblock['Tail_x'],aligned_behaveblock['Tail_y'],aligned_behaveblock['be_ts'],s)
    aligned_behaveblock['headdirections'],aligned_behaveblock['taildirections'], aligned_behaveblock['arch_angles'] = direction(aligned_behaveblock['Head_x'].tolist(),aligned_behaveblock['Head_y'].tolist(),aligned_behaveblock['Body_x'].tolist(),aligned_behaveblock['Body_y'].tolist(),aligned_behaveblock['Tail_x'].tolist(),aligned_behaveblock['Tail_y'].tolist())
    aligned_behaveblocks.append(aligned_behaveblock)    
    i = i+1
    del aligned_behaveblock
    del msblock
    del behaveblock
del i
#beframe的起始包括0，所以如果显示100，其实已经是101张
#output ms_starts,aligned_behaveblock; update behaveblocks

#%%
result={"mouse_id":mouse_id,
       "ms_mat_path":ms_mat_path,
       "behave_trackfiles":behave_trackfiles,
       "behave_timestamps":behave_timestamps,
       "behave_logfiles":behave_logfiles,  
       "behave_videos":behave_videos,
       "msblocks":msblocks,
       "behaveblocks":behaveblocks,
       "logblocks":logblocks,
       "blocknames":blocknames,
       "ms_starts":ms_starts,
       "aligned_behaveblocks":aligned_behaveblocks,
       "results":results}
del mouse_id
del ms_mat_path
del behave_trackfiles
del behave_timestamps
del behave_logfiles
del msblocks
del behaveblocks
del logblocks
del blocknames
del ms_starts
del aligned_behaveblocks
# output result
#%%
view_variable_structure(result)
save_result(result,result_path)
