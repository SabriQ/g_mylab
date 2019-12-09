# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 14:57:37 2019

@author: Sabri
"""
#%%
import pickle
import pandas as pd
from mylab.miniscope.functions import *
#from mylab.Cvideo import Video
import matplotlib.pyplot as plt
import numpy as np
import time
#%%
if __name__ == "__main__":
    #%% load
    result_path = r"C:\Users\Sabri\Desktop\test\20191110_160835_all.pkl"
    result = load_result(result_path)
    #result["results"]={}
    #%%
    blocknames = result['blocknames']
    msblocks = result['msblocks']
    aligned_behaveblocks=result['aligned_behaveblocks']
    behave_videos = result['behave_videos']
    #%%
    #crop video get the interested areas
    #contextcoords=[]
    #for video in behave_videos:
    #    masks,coords = Video(video).draw_rois(aim="context",count=1)
    #    contextcoords.append((masks,coords))
    #result['contextcoords']=contextcoords
    #%% output contextcoords (contextcoord in each block)
    contextcoords=result['contextcoords']
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
    #output contextcoords
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
    from bootstrap import bootstrap_context_selectivity,context_selectivity
    result["context_selectivities"]=context_selectivity(in_context_msblocks,blocknames,[[0,3,5,6,8],[1,2,4,7,9]],[0,1],[3,2],[5,4],[6,7],[8,9],[10,11])
    result["bootstrap_context_selectivities"] = bootstrap_context_selectivity(in_context_msblocks,blocknames, 10,[[0,3,5,6,8],[1,2,4,7,9]],[0,1],[3,2],[5,4],[6,7],[8,9],[10,11])
    
    #%% multiprocessing bootstrap
    from multiprocessing  import Pool
    from bootstrap import *
    import concurrent.futures
    pool = multiprocessing.Pool()
    bootstrap_context_selectivities=[]
    args_list = [(in_context_msblocks,blocknames,[[0,3,5,6,8],[1,2,4,7,9]],[0,1],[3,2],[5,4],[6,7],[8,9],[10,11])]*100
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for i,_ in enumerate(executor.map(context_selectivity,args_list),1):
            print (i)
    
#    for i in range(2):
#        pool.apply_async(context_selectivity
#                               ,args=).get()
#        print(i)
##        bootstrap_context_selectivities.append(ret)
#    
#    print("processes start")
#    pool.close()
#    pool.join()
    print("processes done")
    #%% for view context selectivity
    #traces_no = 1000
    #if traces_no > np.shape(block_context_average_tracevalue)[0]:
    #    traces_no = np.shape(block_context_average_tracevalue)[0]
    #plt.figure(figsize=(80,100))
    #i=1
    #for row in range(traces_no):
    #    plt.subplot(int(np.ceil(traces_no/16)),16,i)
    ##    if i == 220:
    #    plt.plot(block_context_selectivities.iloc[row,],'.')
    #    plt.plot(block_context_selectivities.iloc[row,])    
    #    plt.hlines(y=0.0,xmin=0,xmax=6,colors='black',linestyles='dashed',lw=2)
    #    plt.xticks([],rotation=-90)
    #    plt.yticks([])
    #    i=1+i
    #plt.show()
    #output block_context_selectivities
    #%% save
    view_variable_structure(result)
    save_result(result,result_path)  

    

