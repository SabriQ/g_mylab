# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 14:57:37 2019

@author: Sabri
"""
#%%
import pickle
import pandas as pd
from mylab.miniscope.Mfunctions import *

#%%
result_path = r"C:\Users\Sabri\Desktop\program\data\miniscope\processed_191172_20191110_160835_all.pkl"
with open(result_path,'rb') as f:
    result = pickle.load(f)

#%% align timepoint of ms_ts & track/ts,log & track/ts, all are aligned to time of ms_ts
starts = [979,403,168,251,315,187,283,223,501,154,211,171]# the frame in behave_bideo which present the start of ms
for i,start in enumerate(starts,0):
    delta_t = result['behaveblocks'][i]['be_ts'][start+1]
    result['behaveblocks'][i]['correct_ts']=result['behaveblocks'][i]['be_ts']-delta_t
del i
del start
#for start,block in zip(starts,result['behave_data']):
#    delta_t = block['ts'][0][start+1]
#    block['ts'][0] = block['ts'][0]-delta_t 
aligned_behaveblocks = []
i = 1
for msblock,behaveblock in zip(result['msblocks'],result['behaveblocks']):
    aligned_behaveblock = pd.DataFrame()
    aligned_behaveblock['ms_ts'] = msblock['ms_ts'] 
    print(f"{i}/{len(result['msblocks'])} index behave DataFrame according to ms_ts")
    aligned_behaveblock['be_frame']=[find_close_fast((behaveblock['correct_ts']*1000),i) for i in msblock['ms_ts']]
    aligned_behaveblock = aligned_behaveblock.join(behaveblock.iloc[aligned_behaveblock['be_frame'].tolist(),].reset_index())
    aligned_behaveblocks.append(aligned_behaveblock)
    i = i+1
    del aligned_behaveblock
del i

#%%
result['aligned_behaveblocks'] = aligned_behaveblocks
del aligned_behaveblocks

with open(result_path,'wb') as f:
    print('saving result...')
    pickle.dump(result,f)
print("result is saved.")     

    

