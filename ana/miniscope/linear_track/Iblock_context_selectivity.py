# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 14:57:37 2019

@author: Sabri
"""
#%%
import pickle
import pandas as pd
from mylab.miniscope.Mfunctions import *
from mylab.miniscope.Mplot import *
from mylab.miniscope.Mcontext_selectivity import *
from mylab.Cvideo import Video
import matplotlib.pyplot as plt
import numpy as np
import time
#%%
if __name__ == "__main__":
    #load
    result_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all.pkl"
    result_path = r"C:\Users\Sabri\Desktop\test\20191110_160835_all.pkl"
    result = load_result(result_path)
    view_variable_structure(result)
    #result["results"]={}
    blocknames = result['blocknames']
    msblocks = result['msblocks']
    aligned_behaveblocks=result['aligned_behaveblocks']
    behave_videos = result['behave_videos']
    #%%
    #crop video get the interested areas
    contextcoords=[]
    for video in behave_videos:
        masks,coords = Video(video).draw_rois(aim="in_context",count=1)
        contextcoords.append((masks,coords))
    result['in_context_coords']=contextcoords
    #%% output contextcoords (contextcoord in each block)
  
    TrackinZoneView(contextcoords,aligned_behaveblocks,blocknames)

    #%% add aligned_behaveblock['in_context']    
    for aligned_behaveblock, contextcoord in zip(aligned_behaveblocks,contextcoords):
        masks = contextcoord[0][0]
#        plt.imshow(masks)
#        plt.show()
        in_context = []
        for x,y in zip(aligned_behaveblock['Body_x'],aligned_behaveblock['Body_y']):
            if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                in_context.append(0)
            else:
                in_context.append(1)
        aligned_behaveblock['in_context'] = in_context
    #%% for each block(context),calculate the averate trace value of each neuron
    block_context_average_tracevalue=pd.DataFrame()
    in_context_msblocks=[]
    in_context_behaveblocks=[]
    for blockname, msblock,aligned_behaveblock in zip(blocknames,msblocks,aligned_behaveblocks):
        in_context  = aligned_behaveblock['in_context']
    #    print(len(in_context))
        in_context_msblock = msblock.iloc[(in_context==1).tolist(),]
        in_context_behaveblock = aligned_behaveblock.iloc[(in_context==1).tolist(),]
        # for each neuron in each block
        block_context_average_tracevalue[blockname]=np.mean(in_context_msblock.iloc[:,0:-1],axis=0)
        in_context_msblocks.append(in_context_msblock)
        in_context_behaveblocks.append(in_context_behaveblock)
    result["results"]["block_context_average_tracevalue"]=block_context_average_tracevalue
    result["in_context_msblocks"]=in_context_msblocks
    result["in_context_behaveblocks"]=in_context_behaveblocks
    #output block_context_average_tracevalue, in_context_msblocks,in_context_behaveblock
    #%%for row in range(np.shape(block_context_average_tracevalue)[0]):
    # CONTEXT_order AB(90) BA(135) BA(90) AB(45) AB(90) A1B1(90)
    days = [0,1,2,3,4,5,6,7,8,9,10,11]
    traces_no =1000
    if traces_no > np.shape(block_context_average_tracevalue)[0]:
        traces_no = np.shape(block_context_average_tracevalue)[0]
    plt.figure(figsize=(20,10))
    for row in range(traces_no):
        plt.plot(block_context_average_tracevalue.iloc[row,days],'r.',alpha=0.1)
    #    plt.plot(block_context_average_tracevalue.iloc[row,days])
    plt.xticks(rotation=-90)
    temp_mean = np.mean(block_context_average_tracevalue)
    temp_std = np.std(block_context_average_tracevalue)
    plt.errorbar(block_context_average_tracevalue.columns,temp_mean,yerr=temp_std,fmt='.',color='black',elinewidth=3,capsize=5,capthick=3)
    plt.scatter(block_context_average_tracevalue.columns,temp_mean,s=50,color='red')
    plt.show()
    # view block_context_average_tracevalue for each neuon in each block
    #%%
    result["results"]["block_context_selectivities"]=generete_context_selectivities_blocks(block_context_average_tracevalue,[[0,3,5,6,8],[1,2,4,7,9]],[0,1],[3,2],[5,4],[6,7],[8,9],[10,11]) 
#    result["results"]["bootstrap_context_selectivities"] = bootstrap_context_selectivity_blockss(in_context_msblocks,blocknames, 10,[[0,3,5,6,8],[1,2,4,7,9]],[0,1],[3,2],[5,4],[6,7],[8,9],[10,11])
#    print("finish bootstrap")
    #%% for view context selectivity
#    traces_no = 531
#    if traces_no > np.shape(block_context_average_tracevalue)[0]:
#        traces_no = np.shape(block_context_average_tracevalue)[0]
#    plt.figure(figsize=(80,100))
#    i=1
#    for trace in range(traces_no):
#        plt.subplot(int(np.ceil(traces_no/16)),16,i)
#    #    if i == 220:
#        plt.plot(result["results"]["block_context_selectivities"][:,trace],'.')
#        plt.plot(result["results"]["block_context_selectivities"][:,trace])    
#        plt.hlines(y=0.0,xmin=0,xmax=6,colors='black',linestyles='dashed',lw=2)
#        plt.xticks([],rotation=-90)
#        plt.yticks([])
#        i=1+i
#    plt.show()
#    output block_context_selectivities
    #%%check
#    i=11
#    print(blocknames[i])
#    #%%
#    Video(behave_videos[i]).check_frames(15374)
#    #%%
#    result["behaveblocks"][0].iloc[32220:32225,:]
    #%% save
    view_variable_structure(result)
    save_result(result,result_path)  

    

