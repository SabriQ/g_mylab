# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 14:57:37 2019

@author: Sabri
"""
#%%
import pickle
import pandas as pd
from mylab.miniscope.functions import *
from mylab.Cvideo import Video
import matplotlib.pyplot as plt
import numpy as np
import time
#%% read
result_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all.pkl"
with open(result_path,'rb') as f:
    result = pickle.load(f)
#%%
blocknames = result['blocknames']
msblocks = result['msblocks']
aligned_behaveblocks=result['aligned_behaveblocks']
behave_videos = result['behave_videos']
#%%
#crop video get the interested areas
contextcoords=[]
for video in behave_videos:
    masks,coords = Video(video).draw_rois(aim="context",count=1)
    contextcoords.append((masks,coords))

#%% view trace in context
plt.figure('trace',figsize=(20,5))
for i in range(len(aligned_behaveblocks)):           
    plt.subplot(2,6,i+1)
    x=aligned_behaveblocks[i]['Body_x'] 
    y=aligned_behaveblocks[i]['Body_y'] 
    plt.imshow(contextcoords[i][0][0])
    plt.scatter(x,y,c='r')
#    plt.plot(0,480,'r.',)
    plt.title(f"{blocknames[i]}")
    plt.xticks([])
    plt.yticks([])
plt.show()
#%% add aligned_behaveblock['in_context']
for aligned_behaveblock, contextcoord in zip(aligned_behaveblocks,contextcoords):
    masks = contextcoord[0][0]
    in_context = []
    for x,y in zip(aligned_behaveblock['Body_x'],aligned_behaveblock['Body_y']):
        if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
            in_context.append(1)
        else:
            in_context.append(0)
    aligned_behaveblock['in_context'] = in_context
#%% for each block(context),calculate the averate trace value of each neuron
context_average_tracevalue=pd.DataFrame()
for blockname, msblock,aligned_behaveblock in zip(blocknames,msblocks,aligned_behaveblocks):
    in_context  = aligned_behaveblock['in_context']
    context_average_tracevalue[blockname]=np.mean(msblock.iloc[:,0:-1].iloc[(in_context==1).tolist(),],axis=0)
#output context_average_tracevalue
#%%for row in range(np.shape(context_average_tracevalue)[0]):
# CONTEXT_order AB(90) BA(135) BA(90) AB(45) AB(90) A1B1(90)
days = [0,1,2,3,4,5,6,7,8,9,10,11]
traces_no =1000
if traces_no > np.shape(context_average_tracevalue)[0]:
    traces_no = np.shape(context_average_tracevalue)[0]
plt.figure(figsize=(20,10))
for row in range(traces_no):
    plt.plot(context_average_tracevalue.iloc[row,days],'r.',alpha=0.1)
#    plt.plot(context_average_tracevalue.iloc[row,days])
plt.xticks(rotation=-90)
temp_mean = np.mean(context_average_tracevalue)
temp_std = np.std(context_average_tracevalue)
plt.errorbar(context_average_tracevalue.columns,temp_mean,yerr=temp_std,fmt='.',color='black',elinewidth=3,capsize=5,capthick=3)
plt.scatter(context_average_tracevalue.columns,temp_mean,s=50,color='red')
plt.show()

#%% for exploring context selectivity 
context_selectivities=pd.DataFrame()
A = [0,3,5,6,8]
B = [1,2,4,7,9]
temp_diff = np.mean(context_average_tracevalue.iloc[:,A],axis=1)-np.mean(context_average_tracevalue.iloc[:,B],axis=1)
temp_sum = np.mean(context_average_tracevalue.iloc[:,A],axis=1)+np.mean(context_average_tracevalue.iloc[:,B],axis=1)
context_selectivities['AB'] = temp_diff/temp_sum
context_selectivities['day1-2_AB(90)'] = (context_average_tracevalue.iloc[:,0]-context_average_tracevalue.iloc[:,1])/(context_average_tracevalue.iloc[:,0]+context_average_tracevalue.iloc[:,1])
context_selectivities['day3-4_BA(135)']= (context_average_tracevalue.iloc[:,3]-context_average_tracevalue.iloc[:,2])/(context_average_tracevalue.iloc[:,3]+context_average_tracevalue.iloc[:,2])
context_selectivities['day5-6_BA(90)']=(context_average_tracevalue.iloc[:,5]-context_average_tracevalue.iloc[:,4])/(context_average_tracevalue.iloc[:,5]+context_average_tracevalue.iloc[:,4])
context_selectivities['day7-8_AB(45)']=(context_average_tracevalue.iloc[:,6]-context_average_tracevalue.iloc[:,7])/(context_average_tracevalue.iloc[:,6]+context_average_tracevalue.iloc[:,7])
context_selectivities['day9-10_AB(90)']=(context_average_tracevalue.iloc[:,8]-context_average_tracevalue.iloc[:,9])/(context_average_tracevalue.iloc[:,8]+context_average_tracevalue.iloc[:,9])
context_selectivities['day11-12_A1B1(90)']=(context_average_tracevalue.iloc[:,10]-context_average_tracevalue.iloc[:,11])/(context_average_tracevalue.iloc[:,10]+context_average_tracevalue.iloc[:,11])
#%% for view context selectivity
traces_no = 1000
if traces_no > np.shape(context_average_tracevalue)[0]:
    traces_no = np.shape(context_average_tracevalue)[0]
plt.figure(figsize=(80,100))
i=1
for row in range(traces_no):
    plt.subplot(int(np.ceil(traces_no/16)),16,i)
#    if i == 220:
    plt.plot(context_selectivities.iloc[row,],'.')
    plt.plot(context_selectivities.iloc[row,])    
    plt.hlines(y=0.0,xmin=0,xmax=6,colors='black',linestyles='dashed',lw=2)
    plt.xticks([],rotation=-90)
    plt.yticks([])
    i=1+i
plt.show()
#output context_selectivities
#%% save

with open(result_path,'wb') as f:
    print('saving result...')
    pickle.dump(result,f)
print("result is saved.")     

    

