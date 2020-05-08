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
mouse_id = "191174"
ms_mat_path = r"G:\data\miniscope\Results_191174\20191110_161017_20191029-1102all\191174_post_processed.mat"
ms_ts_pkl_path = os.path.join(os.path.dirname(ms_mat_path),'ms_ts.pkl')
result_path = os.path.join(os.path.dirname(ms_mat_path),'191174_in_context.pkl')

context_orders=["A","B","B","A","B","A","A","B","A","B","A1","B1"]
context_angles=["90","90","135","135","90","90","45","45","90","90","90","90"]
behave_dir = os.path.join(r"W:\qiushou\miniscope\2019*" , mouse_id)
ms_starts = [359,144,349,186,179,171,304,294,276,217,296,140]# the frame in behave_bideo which present the start of ms
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
#result_path =os.path.dirname(ms_mat_path)+'.pkl'

mouseinfo = MouseInfo(mouse_info_path=r"Z:\QiuShou\mouse_info\191174_info.txt")
mouseinfo.add_key("context_orders", context_orders, exp="lick_water")
mouseinfo.add_key("context_angles", context_angles, exp="lick_water")
mouseinfo.add_key("ms_starts", ms_starts, exp="lick_water")
mouseinfo.save
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

ms_ts = ms_load['ms']['ms_ts']


#%% check whether frames of ms_ts are equal to that of traces
#l_dff = dff.shape[0] # or sigraw.shape[1] or sigdeconvolved.shape[1] or CaTraces.shape[1]
#l_ms_ts = []
#for i in ms_ts:
#    l_ms_ts.append(len(i))
#    del i
#if l_dff != sum(l_ms_ts):
#    print(f"l_dff: {l_dff} is not the same length of l_ms_ts: {l_ms_ts}")
#    sys.exit()
#print("frames of timestaps and traces are equal!")
def equal_frames(dff,ms_ts):
    l_dff = dff.shape[0]# or sigraw.shape[0] or sigdeconvolved.shape[0] or CaTraces.shape[0]
    l_ms_ts = sum([len(i) for i in ms_ts])
    if l_dff != l_ms_ts:
        return 0
    else:
        return 1
    
equal = equal_frames(dff,ms_ts)

if equal==0:    
    with open(ms_ts_pkl_path,'rb') as f:
        ms_ts_pkl = pickle.load(f) 
    if equal_frames(dff,ms_ts_pkl)==1:
        ms_load['ms']['ms_ts'] = ms_ts_pkl
        spio.savemat(ms_mat_path,ms_load)
        print("reset the ms_ts with ms_ts.pkl,frames of timestaps and traces are equal!")
    else:
        print(f"l_dff: {l_dff} is not the same length of l_ms_ts: {l_ms_ts}")
        sys.exit()
else:
    print("frames of timestaps and traces are equal!")
del ms_load
#%% construct list blocks each block of which has a DataFrame containing all the traces and ms_ts
msblocks=sigraw2msblocks(ms_ts,sigraw,acceptedPool-1)
msblocks2=sigraw2msblocks(ms_ts,CaTraces,acceptedPool-1)
#%%  output behaveblocks, logblocks,blocknamesread track coordinates as lists of dataframe
blocknames = []
behaveblocks=[]
logblocks=[]
i=1 
for behave_trackfile,behave_timestamp,behave_logfile in zip(behave_trackfiles,behave_timestamps,behave_logfiles):    
    print(f'{i}/{len(behave_trackfiles)} blocks:')
    blockname = os.path.basename(behave_timestamp).split('_ts.txt')[0]
    blocknames.append(blockname)
    print("generate 'blocknames'")

    if blockname in behave_trackfile:
        track = pd.read_hdf(behave_trackfile) #这一步比其他步骤耗时，不知道是
        behaveblock=pd.DataFrame(track[track.columns[0:9]].values,
         columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
# 如果每一帧都放进来做计算，那么 点的抖动对速度值的影响非常大，因此根据miniscope的采样率来进行计算，降采样后大概是10fps,也就是每3个点才取一个点进行计算，这样会稍微降低一点速度的抖动
#        behaveblock['Headspeeds'],behaveblock['Headspeed_angles'] = speed(behaveblock['Head_x'],behaveblock['Head_y'],behaveblock['be_ts'],s)
#        behaveblock['Bodyspeeds'],behaveblock['Bodyspeed_angles'] = speed(behaveblock['Body_x'],behaveblock['Body_y'],behaveblock['be_ts'],s)
#        behaveblock['Tailspeeds'],behaveblock['Tailspeed_angles'] = speed(behaveblock['Tail_x'],behaveblock['Tail_y'],behaveblock['be_ts'],s)
#        behaveblock['headdirections'],behaveblock['taildirections'], behaveblock['arch_angles'] = direction(behaveblock['Head_x'].tolist(),behaveblock['Head_y'].tolist(),behaveblock['Body_x'].tolist(),behaveblock['Body_y'].tolist(),behaveblock['Tail_x'].tolist(),behaveblock['Tail_y'].tolist())
    if blockname in behave_timestamp:
        ts = pd.read_table(behave_timestamp,sep='\n',header=None)
        behaveblock['be_ts']=ts[0]
    behaveblocks.append(behaveblock)
    print("generate 'behaveblocks'")
    if blockname in behave_logfile:
        logblock = pd.read_csv(behave_logfile,header=0)
        logblocks.append(logblock)
    print("generate 'logblocks'")
    print(f"behave data of {blockname} has been constructed as DataFrame")
    del behave_trackfile,behave_timestamp,behave_logfile
    i= i+1
print("All the behave info has been constructed as a list of DataFrame. ")
del i 
#%% align timepoint of ms_ts & track/ts,log & track/ts, all are aligned to time of ms_ts
result['video_scale'] = scale(behave_videos[0],40)
s = result['video_scale']
for i,start in enumerate(ms_starts,0):
    delta_t = behaveblocks[i]['be_ts'][start-1]-0.1 
    #这个-0.1s即100ms指的大概是 miniscope启动大概需要100ms的时间，即miniscope的0时刻大约比led_on要晚大约100ms,
    #这是通过对比ms_ts(原始)的最大值，和视频的结束时间的出来的，如果不-0.1,差值的平均在113ms左右
    behaveblocks[i]['correct_ts']=behaveblocks[i]['be_ts']-delta_t
    del i
    del start
print("be_ts has been corrected as correct_ts")
#for start,block in zip(starts,result['behave_data']):
#    delta_t = block['ts'][0][start+1]
#    block['ts'][0] = block['ts'][0]-delta_t 
aligned_behaveblocks = []
i = 1
for msblock,behaveblock in zip(msblocks,behaveblocks):
    aligned_behaveblock = pd.DataFrame()
    aligned_behaveblock['ms_ts'] = msblock['ms_ts']     
    print(f"{i}/{len(msblocks)} block is aligning behave DataFrame according to ms_ts...",end=' ')
    aligned_behaveblock['be_frame']=[find_close_fast((behaveblock['correct_ts']*1000),i) for i in msblock['ms_ts']]
    print('-->aligned.',end=' ')
    aligned_behaveblock = aligned_behaveblock.join(behaveblock.iloc[aligned_behaveblock['be_frame'].tolist(),].reset_index())
    aligned_behaveblock['Headspeeds'],aligned_behaveblock['Headspeed_angles'] = speed(aligned_behaveblock['Head_x'],aligned_behaveblock['Head_y'],aligned_behaveblock['be_ts'],s)
    aligned_behaveblock['Bodyspeeds'],aligned_behaveblock['Bodyspeed_angles'] = speed(aligned_behaveblock['Body_x'],aligned_behaveblock['Body_y'],aligned_behaveblock['be_ts'],s)
    aligned_behaveblock['Tailspeeds'],aligned_behaveblock['Tailspeed_angles'] = speed(aligned_behaveblock['Tail_x'],aligned_behaveblock['Tail_y'],aligned_behaveblock['be_ts'],s)
    aligned_behaveblock['headdirections'],aligned_behaveblock['taildirections'], aligned_behaveblock['arch_angles'] = direction(aligned_behaveblock['Head_x'].tolist(),aligned_behaveblock['Head_y'].tolist(),aligned_behaveblock['Body_x'].tolist(),aligned_behaveblock['Body_y'].tolist(),aligned_behaveblock['Tail_x'].tolist(),aligned_behaveblock['Tail_y'].tolist())
    aligned_behaveblocks.append(aligned_behaveblock)    
    print(f"Caculated speeds.")
    i = i+1
    del aligned_behaveblock
    del msblock
    del behaveblock
del i
#beframe的起始包括0，所以如果显示100，其实已经是101张
#output ms_starts,aligned_behaveblock; update behaveblocks
#%% crop video get the interested areas
contextcoords=[]
for video in behave_videos:
    print(os.path.basename(video),end=': ')
    masks,coords = Video(video).draw_rois(aim="context",count=1)
    contextcoords.append((masks,coords))
TrackinZoneView(contextcoords,aligned_behaveblocks,blocknames)
#%% add aligned_behaveblock['in_context']    
for aligned_behaveblock, contextcoord in zip(aligned_behaveblocks,contextcoords):
    masks = contextcoord[0][0]
    in_context = []
    for x,y in zip(aligned_behaveblock['Body_x'],aligned_behaveblock['Body_y']):
        if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
            in_context.append(0)
        else:
            in_context.append(1)
    aligned_behaveblock['in_context'] = in_context
print("add condition 'in_context'")
#%% for each block(context),calculate the averate trace value of each neuron
in_context_msblocks=[]
in_context_msblocks2=[]
in_context_behaveblocks=[]
for msblock,msblock2,aligned_behaveblock in zip(msblocks,msblocks2,aligned_behaveblocks):
    in_context  = aligned_behaveblock['in_context']
#    print(len(in_context))
    in_context_msblock = msblock.iloc[(in_context==1).tolist(),]
    in_context_msblock2 = msblock2.iloc[(in_context==1).tolist(),]
    in_context_behaveblock = aligned_behaveblock.iloc[(in_context==1).tolist(),]
    # for each neuron in each block
    in_context_msblocks.append(in_context_msblock)
    in_context_msblocks2.append(in_context_msblock2)
    in_context_behaveblocks.append(in_context_behaveblock)
#output in_context_msblocks,in_context_behaveblock    
print("generated 'in_context_msblocks' and 'in_context_behaveblocks")
#%% output result["in_context_behavetrialblocks"]
in_context_behavetrialblocks = []
for aligned_behaveblock,contextcoord, blockname, in_context_msblock in zip(aligned_behaveblocks,contextcoords,blocknames, in_context_msblocks2):
    in_context_behavetrialblock,_ = Extract_trials(aligned_behaveblock,contextcoord, in_context_msblock, title = blockname,column="in_context",example_neuron=3)
    in_context_behavetrialblocks.append(in_context_behavetrialblock) 
#%%
result={"mouse_id":mouse_id,
       "ms_mat_path":ms_mat_path,
       "context_orders":context_orders,
       "context_angles":context_angles,
       "behave_trackfiles":behave_trackfiles,
       "behave_timestamps":behave_timestamps,
       "behave_logfiles":behave_logfiles,  
       "behave_videos":behave_videos,
       "msblocks":msblocks,
       "msblocks2":msblocks2,
       "behaveblocks":behaveblocks,
       "logblocks":logblocks,
       "blocknames":blocknames,
       "ms_starts":ms_starts,
       "aligned_behaveblocks":aligned_behaveblocks,
       "contextcoords":contextcoords,
       "in_context_msblocks":in_context_msblocks,    
       "in_context_msblocks2":in_context_msblocks2,
       "in_context_behaveblocks":in_context_behaveblocks,
       "in_context_behavetrialblocks":in_context_behavetrialblocks
       }

# output result
#%%
#view_variable_structure(result)
#save_result(result,result_path)
#%% Define <savemat>
def savemat(result_path,result):
    spio.savemat(result_path,
     {'in_context_columns':np.array(result["in_context_msblocks"][0].columns), # cell ID.
      'in_context_msblocks':np.array([i.values for i in result["in_context_msblocks"]]),
      'in_context_msblocksCaEvent':np.array([i.values for i in result["in_context_msblocks2"]]),
      'in_context_behaveblocks':np.array([i.values for i in result["in_context_behaveblocks"]]),
      'in_context_behavetrial_columns':np.array(result["aligned_behaveblocks"][0].columns),
      'in_context_behavetrialblocks':np.array([np.array([j for j in i]) for i in result["in_context_behavetrialblocks"]]),
      'in_context_coords' :np.array( result["contextcoords"])      
      })
#%% Save <result>    
savemat(r"G:\data\miniscope\LinearTrackAll\191174_in_context.mat",result)