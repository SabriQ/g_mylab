# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 23:43:57 2019

@author: Sabri
"""
#bootstrap
#for blocks
#for trails
#for 
from mylab.miniscope.Mfunctions import *
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import sys
import multiprocessing
#%%
#view_variable_structure(result["in_context_blocks"]) 
#for i in range(100): 
#    in_context_msblocks --shuffle-->sf_in_context_msblocks # only trace shuffled but not ms_ts
#    
#    for sf_in_context_msblock in sf_in_context_msblocks:
#        --> sf_block_average_tracevalue # for each neuro in each block
#        --> sf_block_context_selectivities
    

#%%
def _shuffle(dataframe,shuffle_times):
    for i in range(shuffle_times):
        print(f"\rshuffled for {i+1}/{shuffle_times} times",end=" ")
        yield dataframe.sample(frac=1).reset_index(drop=True)
        
def generete_context_selectivities_blocks(dataframe,*paired_context_args):
    #*args=[[0,3,5,6,8],[1,2,4,7,9]],[0,1],[3,2],[5,4],[6,7],[8,9],[10,11], for each list,list[0] for A, list[1] for B
    #dataframe here are trace for each row and block for each column 
    context_selectivities=[]
    for arg in paired_context_args:
        if isinstance(arg[0],list):
            temp_diff = np.mean(dataframe.iloc[:,arg[0]],axis=1)-np.mean(dataframe.iloc[:,arg[1]],axis=1)
            temp_sum = np.mean(dataframe.iloc[:,arg[0]],axis=1)+np.mean(dataframe.iloc[:,arg[1]],axis=1)
        else:
            temp_diff = dataframe.iloc[:,arg[0]]-dataframe.iloc[:,arg[1]]
            temp_sum = dataframe.iloc[:,arg[0]] + dataframe.iloc[:,arg[1]]
        context_selectivity = temp_diff/temp_sum
        context_selectivities.append(context_selectivity.tolist())
        #print(context_selectivity.shape,end=" ")
    return np.array(context_selectivities)            

def bootstrap_context_selectivity_blocks(msblocks,blocknames,shuffle_times,*paired_context_args):
    temp = pd.DataFrame()
    dims = []
    for msblock in msblocks:
        dims.append(temp.shape)
        temp=temp.append(msblock)
    dims.append(temp.shape)
    boots_context_selectivites = []
    for sf_in_context_ms in _shuffle(temp,shuffle_times):
        sf_block_context_average_tracevalues=pd.DataFrame()
        sf_in_context_msblocks=[]
        #首先将shuffle过后的dataframe按照block大小重新分块，得到sf_in_context_msblocks
        for i in range(len(dims)-1):            
            sf_in_context_msblocks.append(sf_in_context_ms.iloc[dims[i][0]:dims[i+1][0],:])
        #然后求每一个block的平均值，得到sf_block_context_average_tracevalues        
        for blockname, sf_in_context_msblock in zip(blocknames,sf_in_context_msblocks):
            sf_block_context_average_tracevalues[blockname] = np.mean(sf_in_context_msblock.iloc[:,0:-1],axis=0)
#        然后根据*paired_context_args计算得到  context_selectivity
        context_selectivities = generete_context_selectivities(sf_block_context_average_tracevalues,*paired_context_args)
        boots_context_selectivites.append(context_selectivities)     
    return np.array(boots_context_selectivites)
#%% 以下是希望进行并行运算的时候用到的 单次shuffle
def shuffle_context_selectivity_blocks(msblocks,blocknames,*paired_context_args):
    sf_in_context_ms = pd.DataFrame()
    sf_block_context_average_tracevalues = pd.DataFrame()
    dims = []
    for msblock in msblocks:
        dims.append(sf_in_context_ms.shape)
        sf_in_context_ms=sf_in_context_ms.append(msblock)
    dims.append(sf_in_context_ms.shape)    
    sf_in_context_ms = sf_in_context_ms.sample(frac=1).reset_index(drop=True)
    sf_in_context_msblocks=[]
    #首先将shuffle过后的dataframe按照block大小重新分块，得到sf_in_context_msblocks
    for i in range(len(dims)-1):            
        sf_in_context_msblocks.append(sf_in_context_ms.iloc[dims[i][0]:dims[i+1][0],:])
    #然后求每一个block的平均值，得到sf_block_context_average_tracevalues        
    for blockname, sf_in_context_msblock in zip(blocknames,sf_in_context_msblocks):
        sf_block_context_average_tracevalues[blockname] = np.mean(sf_in_context_msblock.iloc[:,0:-1],axis=0)
#        然后根据*paired_context_args计算得到  context_selectivity
    context_selectivities = generete_context_selectivities(sf_block_context_average_tracevalues,*paired_context_args)
    print("done")
    return np.array(context_selectivities)


#from multiprocesing import Pool

#def collecting_data(q):
#    i=1
#    while True:
#        temp = q.get()
#        bootstrap_context_selectivities.append(temp)
#        print(f"shuffled for {i} times")
#        if q.empty():
#            break
#        
##多进程不能共享全局变量
#
#def boot(shuffle_times,msblocks,blocknames,*paired_context_args):
#    bootstrap_context_selectivities = []
#    po = multiprocessing.Pool(3)
#    q = multiprocessing.Queue()
#
#    for i in range(0,shuffle_times):
#        po.apply_async(context_selectivity,(msblocks,blocknames,True,q,*paired_context_args,))
#        print("----start bootstrap---")
#        po.close()
#        po.join()
#        print("----end bootstrap---")
#
#    bootstrap_context_selectivities=[i for i in q.get()]
#    print(len(bootstrap_context_selectivities))

    

#多线程共享全局变量
#import threading
#def main():
#    p1 = threading.Thread(target=bootstrap_context_selectivity)
#    p2 = threading.Thread(target=bootstrap_context_selectivity)
#    p1.start()
#    p2.start()
#           
    
#def context_selectivity(in_context_msblocks,blocknames,blocks=[0,1,2,3,4,5,6,7,8,9,10,11],A=[0,3,5,6,8],B=[1,2,4,7,9],shuffle = True,shuffle_times =100):
#    filtered_in_context_msblocks =[]    
#    for block in blocks:
#        filtered_in_context_msblocks.append(in_context_msblocks[block])
#        
#    new_filtered_in_context_ms =pd.DataFrame()
#    dims=[]
#    for filtered_in_context_msblock in filtered_in_context_msblocks:
#        dims.append(new_filtered_in_context_ms.shape)
#        new_filtered_in_context_ms = new_filtered_in_context_ms.append(filtered_in_context_msblock)        
#    dims.append(new_filtered_in_context_ms.shape)   
#    sf_block_context_selectivitiess = []   
#
#    if not shuffle:
#        shuffle_times=1
#    for k in range(shuffle_times):
#        filtered_block_context_average_tracevalue=pd.DataFrame()
#        block_context_selectivies = pd.DataFrame()
#        
#        if shuffle:
#            #shuffle sample 
#            sf_filtered_in_context_ms = new_filtered_in_context_ms.sample(frac=1).reset_index(drop=True)      
#            sf_filtered_in_context_msblocks = []
#            for i in range(len(dims)-1):            
#                sf_filtered_in_context_msblocks.append(sf_filtered_in_context_ms.iloc[dims[i][0]:dims[i+1][0],:])
#        else:
#            sf_filtered_in_context_msblocks = filtered_in_context_msblocks
#            
#        for blockname,sf_filtered_in_context_msblock in zip(blocknames,sf_filtered_in_context_msblocks):
#            filtered_block_context_average_tracevalue[blockname]=np.mean(sf_filtered_in_context_msblock.iloc[:,0:-1],axis=0)
#       
#            
#        temp_diff = np.mean(filtered_block_context_average_tracevalue.iloc[:,A],axis=1)-np.mean(filtered_block_context_average_tracevalue.iloc[:,B],axis=1)
#        temp_sum = np.mean(filtered_block_context_average_tracevalue.iloc[:,A],axis=1)+np.mean(filtered_block_context_average_tracevalue.iloc[:,B],axis=1)
#        block_context_selectivies['AB'] = temp_diff/temp_sum
#        block_context_selectivies['day1-2_AB(90)'] = (filtered_block_context_average_tracevalue.iloc[:,0]-filtered_block_context_average_tracevalue.iloc[:,1])/(filtered_block_context_average_tracevalue.iloc[:,0]+filtered_block_context_average_tracevalue.iloc[:,1])
#        block_context_selectivies['day3-4_BA(135)']= (filtered_block_context_average_tracevalue.iloc[:,3]-filtered_block_context_average_tracevalue.iloc[:,2])/(filtered_block_context_average_tracevalue.iloc[:,3]+filtered_block_context_average_tracevalue.iloc[:,2])
#        block_context_selectivies['day5-6_BA(90)']=(filtered_block_context_average_tracevalue.iloc[:,5]-filtered_block_context_average_tracevalue.iloc[:,4])/(filtered_block_context_average_tracevalue.iloc[:,5]+filtered_block_context_average_tracevalue.iloc[:,4])
#        block_context_selectivies['day7-8_AB(45)']=(filtered_block_context_average_tracevalue.iloc[:,6]-filtered_block_context_average_tracevalue.iloc[:,7])/(filtered_block_context_average_tracevalue.iloc[:,6]+filtered_block_context_average_tracevalue.iloc[:,7])
#        block_context_selectivies['day9-10_AB(90)']=(filtered_block_context_average_tracevalue.iloc[:,8]-filtered_block_context_average_tracevalue.iloc[:,9])/(filtered_block_context_average_tracevalue.iloc[:,8]+filtered_block_context_average_tracevalue.iloc[:,9])
#        block_context_selectivies['day11-12_A1B1(90)']=(filtered_block_context_average_tracevalue.iloc[:,10]-filtered_block_context_average_tracevalue.iloc[:,11])/(filtered_block_context_average_tracevalue.iloc[:,10]+filtered_block_context_average_tracevalue.iloc[:,11])
#        if shuffle:
#            print(f'have shuffled for {k+1}/{shuffle_times} times')
#            sf_block_context_selectivitiess.append(block_context_selectivies)
#    if shuffle:
#        return sf_block_context_selectivitiess
#    else:
#        return block_context_selectivies
    
#def plot_context_selectivity(sf_block_context_selectivities,block_context_selectivies):
#    rows,columns = sf_block_context_selectivities[0].axes
#    print(rows,columns)
#    plt.figure()
#    plt.figure(0)
#    for i,row in enumerate(rows,1):
#        for j,column in enumerate(columns,1):
##            plt.subplot2grid((len(rows),len(columns)),(i,j),colspan=len(columns),rowspan=len(rows))
#            trace = []
#            for sf_block_context_selectivity in sf_block_context_selectivities:
#                trace.append(sf_block_context_selectivity.loc[row,column])
#            left_percentile = np.percentile(trace,5)
#            right_percentile = np.percentile(trace,95)
#            sns.distplot(trace,color="grey",)
#            plt.axvline(left_percentile,0,1,color='green',linestyle="--")
#            plt.axvline(right_percentile,0,1,color='green',linestyle="--")
#            plt.axvline(block_context_selectivies.loc[row,column],0,1,color='red')
##            plt.xlim((-0.3,0.3))
#            plt.title(f"{row}-{columnfigsize=(80,200)}")
#            plt.show()
#            if j==5:
#                sys.exit()
            
    

#plot_context_selectivity(sf_block_context_selectivities,block_context_selectivies)
def generete_context_selectivities_trials(in_context_trialblock,in_context_msblock,blockname):
    context_selectivities_trials=[]
    for df in in_context_trialblock:
        context_selectivities_trials.append(in_context_msblock.loc[in_context_msblock["ms_ts"].isin(df["ms_ts"])].iloc[:,0:-1].mean().tolist())
    return np.array(context_selectivities_trials)

def View_in_context_context_selectivities_trialblocks(in_context_context_selectivities_trialblocks,blocknames):
    average_trace_value_in_trialblocks=[]
    std_trace_value_in_trialblocks=[]
    for in_context_context_selectivities_trialblock in in_context_context_selectivities_trialblocks:
        average_trace_value_in_trials = np.mean(in_context_context_selectivities_trialblock,axis=0)
        std_trace_value_in_trials = np.std(in_context_context_selectivities_trialblock,axis=0)
        average_trace_value_in_trialblocks.append(average_trace_value_in_trials)
        std_trace_value_in_trialblocks.append(std_trace_value_in_trials)
        
    neuron_no = 5
    plt.figure(figsize=(10,5))
    for i in range(len(blocknames)):
        x = [i]*len(in_context_context_selectivities_trialblocks[i][:,neuron_no])
        y = in_context_context_selectivities_trialblocks[i][:,neuron_no]
        plt.plot(x,y,'r.',alpha=0.2)
        y_mean = average_trace_value_in_trialblocks[i][neuron_no]
        yerr = std_trace_value_in_trialblocks[i][neuron_no]
        plt.plot(i,y_mean,'.',color='black',markersize=12)
        plt.errorbar(i,y_mean,yerr=yerr,color="black",elinewidth=2,barsabove=True,visible=True)
        plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11],labels=blocknames,rotation=-90)
        plt.title(neuron_no)           
    plt.show()
    
if __name__ == "__main__":
    #%%
    context_selectivities_trials = generete_context_selectivities_trials(in_context_trialblocks[0],in_context_msblocks[0],blocknames[0])
    #%%
#    View_in_context_context_selectivities_trialblocks(in_context_context_selectivities_trialblocks,blocknames)
        
    
