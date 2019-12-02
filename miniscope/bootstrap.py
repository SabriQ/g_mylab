# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 23:43:57 2019

@author: Sabri
"""
#bootstrap
#for blocks
#for trails
#for 
from functions import *
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import sys
#%%
view_variable_structure(result) 
#for i in range(100): 
#    in_context_msblocks --shuffle-->sf_in_context_msblocks # only trace shuffled but not ms_ts
#    
#    for sf_in_context_msblock in sf_in_context_msblocks:
#        --> sf_block_average_tracevalue # for each neuro in each block
#        --> sf_block_context_selectivities
    

#%%
def _bootstrap_dataframe(dataframe,shuffle_times):
    for i in range(shuffle_times):
        print(f"shuffled for {i}/{shuffle_times}")
        yield dataframe.sample(frac=1).reset_index(drop=True)

def context_selectivity(blocks,shuffle_times):
    temp = pd.DataFrame()
    temp.append(blocks)
    
    
    for i _bootstrap_dataframe(temp,shuffle_times):
 
        
    

        
    
def context_selectivity(in_context_msblocks,blocknames,blocks=[0,1,2,3,4,5,6,7,8,9,10,11],A=[0,3,5,6,8],B=[1,2,4,7,9],shuffle = True,shuffle_times =100):
    filtered_in_context_msblocks =[]    
    for block in blocks:
        filtered_in_context_msblocks.append(in_context_msblocks[block])
        
    new_filtered_in_context_ms =pd.DataFrame()
    dims=[]
    for filtered_in_context_msblock in filtered_in_context_msblocks:
        dims.append(new_filtered_in_context_ms.shape)
        new_filtered_in_context_ms = new_filtered_in_context_ms.append(filtered_in_context_msblock)        
    dims.append(new_filtered_in_context_ms.shape)   
    sf_block_context_selectivitiess = []   

    if not shuffle:
        shuffle_times=1
    for k in range(shuffle_times):
        filtered_block_context_average_tracevalue=pd.DataFrame()
        block_context_selectivies = pd.DataFrame()
        
        if shuffle:
            #shuffle sample 
            sf_filtered_in_context_ms = new_filtered_in_context_ms.sample(frac=1).reset_index(drop=True)      
            sf_filtered_in_context_msblocks = []
            for i in range(len(dims)-1):            
                sf_filtered_in_context_msblocks.append(sf_filtered_in_context_ms.iloc[dims[i][0]:dims[i+1][0],:])
        else:
            sf_filtered_in_context_msblocks = filtered_in_context_msblocks
            
        for blockname,sf_filtered_in_context_msblock in zip(blocknames,sf_filtered_in_context_msblocks):
            filtered_block_context_average_tracevalue[blockname]=np.mean(sf_filtered_in_context_msblock.iloc[:,0:-1],axis=0)
       
            
        temp_diff = np.mean(filtered_block_context_average_tracevalue.iloc[:,A],axis=1)-np.mean(filtered_block_context_average_tracevalue.iloc[:,B],axis=1)
        temp_sum = np.mean(filtered_block_context_average_tracevalue.iloc[:,A],axis=1)+np.mean(filtered_block_context_average_tracevalue.iloc[:,B],axis=1)
        block_context_selectivies['AB'] = temp_diff/temp_sum
        block_context_selectivies['day1-2_AB(90)'] = (filtered_block_context_average_tracevalue.iloc[:,0]-filtered_block_context_average_tracevalue.iloc[:,1])/(filtered_block_context_average_tracevalue.iloc[:,0]+filtered_block_context_average_tracevalue.iloc[:,1])
        block_context_selectivies['day3-4_BA(135)']= (filtered_block_context_average_tracevalue.iloc[:,3]-filtered_block_context_average_tracevalue.iloc[:,2])/(filtered_block_context_average_tracevalue.iloc[:,3]+filtered_block_context_average_tracevalue.iloc[:,2])
        block_context_selectivies['day5-6_BA(90)']=(filtered_block_context_average_tracevalue.iloc[:,5]-filtered_block_context_average_tracevalue.iloc[:,4])/(filtered_block_context_average_tracevalue.iloc[:,5]+filtered_block_context_average_tracevalue.iloc[:,4])
        block_context_selectivies['day7-8_AB(45)']=(filtered_block_context_average_tracevalue.iloc[:,6]-filtered_block_context_average_tracevalue.iloc[:,7])/(filtered_block_context_average_tracevalue.iloc[:,6]+filtered_block_context_average_tracevalue.iloc[:,7])
        block_context_selectivies['day9-10_AB(90)']=(filtered_block_context_average_tracevalue.iloc[:,8]-filtered_block_context_average_tracevalue.iloc[:,9])/(filtered_block_context_average_tracevalue.iloc[:,8]+filtered_block_context_average_tracevalue.iloc[:,9])
        block_context_selectivies['day11-12_A1B1(90)']=(filtered_block_context_average_tracevalue.iloc[:,10]-filtered_block_context_average_tracevalue.iloc[:,11])/(filtered_block_context_average_tracevalue.iloc[:,10]+filtered_block_context_average_tracevalue.iloc[:,11])
        if shuffle:
            print(f'have shuffled for {k+1}/{shuffle_times} times')
            sf_block_context_selectivitiess.append(block_context_selectivies)
    if shuffle:
        return sf_block_context_selectivitiess
    else:
        return block_context_selectivies
    
def plot_context_selectivity(sf_block_context_selectivities,block_context_selectivies):
    rows,columns = sf_block_context_selectivities[0].axes
    print(rows,columns)
    plt.figure()
    plt.figure(0)
    for i,row in enumerate(rows,1):
        for j,column in enumerate(columns,1):
#            plt.subplot2grid((len(rows),len(columns)),(i,j),colspan=len(columns),rowspan=len(rows))
            trace = []
            for sf_block_context_selectivity in sf_block_context_selectivities:
                trace.append(sf_block_context_selectivity.loc[row,column])
            left_percentile = np.percentile(trace,5)
            right_percentile = np.percentile(trace,95)
            sns.distplot(trace,color="grey",)
            plt.axvline(left_percentile,0,1,color='green',linestyle="--")
            plt.axvline(right_percentile,0,1,color='green',linestyle="--")
            plt.axvline(block_context_selectivies.loc[row,column],0,1,color='red')
#            plt.xlim((-0.3,0.3))
            plt.title(f"{row}-{columnfigsize=(80,200)}")
            plt.show()
#            if j==5:
#                sys.exit()
            
    

plot_context_selectivity(sf_block_context_selectivities,block_context_selectivies)
        
    
