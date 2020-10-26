
from mylab.ana.miniscope.context_exposure.Cminiana import MiniAna as MA
from mylab.ana.miniscope.context_exposure.ana_funtions import *

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob,sys,os,re


def cellids(session,scale=0.33,placebin_number=20,shuffle_times=1000):
    s = MA(session)
    if s.exp == "task":
        try:
            del s.result["aligned_behave2ms"]
        except:
            pass
        s.align_behave_ms()
        s.add_is_in_context()
        s.add_Body_speed(scale=scale)
        s.add_in_context_running_direction_Body()
        s.add_incontext_placebin_num(placebin_number=20)
        contextcells = cellids_Context(s)
        rdcells = cellid_RD_incontext(s)
        pccells = cellid_PC_incontext(s,placebin_number=20,shuffle_times=1000)
        return contextcells, rdcells,pccells
    else:
        return -1,-1,-1

def plot_trace_with_running_direction(Context_dataframe_info):
    """
    return internal functions for plotting trace of each trial with two colors means two direction
    """
    Context_dataframe_info.keys()
    pass
    
def plot_MeanFr_along_Placebin(Context_Matrix_info):    
    """
    Context_Matrix_info: the output of FUNCTION: SingleCell_MeanFr_in_SingleTrial_along_Placebin
    return two internal functions for plotting place fields or continuous MeanFr along place bins
    """
    
    Context_Matrix_cellids_placebins_trials = Context_Matrix_info["Context_Matrix_cellids_placebins_trials"]    
    
    def plot(idx,context):
        """
        return an internal funtion 
            that could plot MeanFr in each place bin of each cellid in each context by specify cellid and context
        
        """
        # specified idx and context 
        if context in Context_Matrix_cellids_placebins_trials.keys():
            if idx in Context_Matrix_info["cellids"]:
                dim1 = np.where(Context_Matrix_info["cellids"]==idx)[0][0]
            else:
                print("Cell %s doesn't exist"%idx)
                return 
        
        # for specifed neuron in specified context, there are row-number of placebin and column-number of trials
        matrix = Context_Matrix_cellids_placebins_trials[context][dim1,:,:] # [placebins,trials]        
        matrix_mean = np.nanmean(matrix,axis=1)
        matrix_and_mean = np.column_stack((matrix,matrix_mean))
        matrix_and_mean_norm = np.apply_along_axis(lambda x:(x-np.nanmean(x))/np.nanstd(x,ddof=1),axis=0,arr=matrix_and_mean)
        
        
        plt.imshow(matrix_and_mean_norm.T)
        plt.axhline(y=matrix_and_mean_norm.shape[1]-1.6,color="red",linewidth=0.8,linestyle="--")
        plt.xlabel("Place bins")
        plt.ylabel("Trials")
        plt.title("MeanFr in Context %s"%context)
               
        plt.show()
        
    def plot2(idx):
        """
        return an internal function
            that could plot MeanFr along placebins for each cellid in different contexts
        """
        # specified idx
        if idx in Context_Matrix_info["cellids"]:
            dim1 = np.where(Context_Matrix_info["cellids"]==idx)[0][0]
        else:
            print("Cell %s doesn't exist"%idx)
            return 

        matrix_0 = Context_Matrix_cellids_placebins_trials[0][dim1,:,:] # [placebins,trials]    
        matrix_1 = Context_Matrix_cellids_placebins_trials[1][dim1,:,:] # [placebins,trials]  
        
        matrix_0_mean = np.nanmean(matrix_0,axis=1)
        matrix_1_mean = np.nanmean(matrix_1,axis=1)
        
        matrix_0_sem = np.nanstd(matrix_0,axis=1,ddof=1)/np.sqrt(matrix_0.shape[1])
        matrix_1_sem = np.nanstd(matrix_1,axis=1,ddof=1)/np.sqrt(matrix_1.shape[1])
        

        plt.plot(matrix_0_mean,linestyle="--",color="red")
        plt.plot(matrix_1_mean,linestyle="--",color="green")
        plt.fill_between(x=np.arange(len(matrix_0_mean)),y1=matrix_0_mean-matrix_0_sem,y2=matrix_0_mean+matrix_0_sem,alpha=0.3,color="red")
        plt.fill_between(x=np.arange(len(matrix_1_mean)),y1=matrix_1_mean-matrix_1_sem,y2=matrix_1_mean+matrix_1_sem,alpha=0.3,color="green")
        plt.legend(["Ctx 0","Ctx 1"])
        plt.title("MeanFr in different contexts")
        plt.xlabel("Place bins")
        plt.ylabel("MeanFr (UnNorm.)")
        plt.show()
        
    return plot,plot2
            