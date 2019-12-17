
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mylab.miniscope.Mfunctions import *
import os
#%%
def TraceView(RawTraces,title="TraceView"):
    plt.figure(figsize=(20,1))
    plt.title(title)
    plt.plot(RawTraces)
    plt.xticks([])
    plt.yticks([])
    plt.show()
def TracesView(RawTraces,neuronsToPlot):
    maxRawTraces = np.amax(RawTraces)
    plt.figure(figsize=(60,15))
                              
#    plt.subplot(2,1,1); 
    plt.figure; plt.title(f'Example traces (first {neuronsToPlot} cells)')
    plot_gain = 10 # To change the value gain of traces
    
    for i in range(neuronsToPlot):
#        if i == 0:        
#          plt.plot(RawTraces[i,:])
#        else:             
      trace = RawTraces[i,:] + maxRawTraces*i/plot_gain
      plt.plot(trace)

#    plt.subplot(2,1,2); 
#    plt.figure; 
#    plt.title(f'Deconvolved traces (first {neuronsToPlot} cells)')
#    plot_gain = 20 # To change the value gain of traces
   
#    for i in range(neuronsToPlot):
#        if i == 0:       
#          plt.plot(DeconvTraces[i,:],'k')
#        else:            
#          trace = DeconvTraces[i,:] + maxRawTraces*i/plot_gain
#          plt.plot(trace,'k')
def TrackView(x,y,figsize=(40,5),title="one of the block"):
    plt.figure("TrackView",figsize=figsize)
    plt.scatter(x,y,color='r')
    plt.title(title)
    plt.xticks([])
    plt.yticks([])
    plt.show()
def TrackinZoneView(ZoneCoordinates,aligned_behaveblocks,blocknames,window_title="Track_in_context",figsize=(20,5)):
    #coordinates = result['contextcoords']
    #output contextcoords (contextcoord in each block)
    contextcoords=ZoneCoordinates
    plt.figure(window_title,figsize=figsize)
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
    plt.ion()
    #output contextcoords
def TrackINTrialsView(aligned_behaveblock,contextcoord,title):
#    sns.distplot(aligned_behaveblock["Tailspeed_angles"])
    plt.figure(figsize=(4,20));
    x_max = max(contextcoord[1][0][:,0])
    x_min = min(contextcoord[1][0][:,0])    
    colors = []
    x = aligned_behaveblock["Body_x"]
    y=[]
    #%%
    for index,row in aligned_behaveblock.iterrows():
        
        if int(row['in_context']) == 0:
            colors.append('black')
        if int(row['in_context']) == 1:
            
            if row['Bodyspeed_angles'] >100 and row['Bodyspeed_angles']<260:
                colors.append('r')
                
            else:
                colors.append('g')
        y.append(index)        
    plt.scatter(x,y,c=colors,s=8)
    plt.axvspan(x_min,x_max,0,1,color="gray",alpha=0.3)
    plt.xticks([])
    plt.yticks([])
    plt.title(title)
    plt.show()
    
def Extract_trials(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No,column="in_context",title="title",):
    df = rlc2(aligned_behaveblock[column])
    trials_in_block=[]
#    sns.distplot(df['length'])    
    x_max = max(contextcoord[1][0][:,0])
    x_min = min(contextcoord[1][0][:,0])
    i=1
    plt.figure(figsize=(5,10))
    for index,row in df.iterrows():
        if row['name'] == 1:          
            x = aligned_behaveblock["Body_x"][row['idx_min']:row['idx_max']]
            x_max2 = max(x)
            x_min2 = min(x)   
            if (x_max2-x_min2)>0.5*(x_max-x_min):
                trials_in_block.append(aligned_behaveblock.iloc[row['idx_min']:row['idx_max']])
                trial_num = [i]
                y = trial_num*(row['idx_max']-row['idx_min'])
                colors = []
                for angle in aligned_behaveblock["Bodyspeed_angles"][row['idx_min']:row['idx_max']]:
                    if angle>100 and angle<260:
                        colors.append('r')
                    else:
                        colors.append('g')
                iter_color = iter(colors)
                iter_size = iter(in_context_msblock.loc[in_context_msblock["ms_ts"].isin(aligned_behaveblock['ms_ts'][row['idx_min']:row['idx_max']])].iloc[:,0:-1].iloc[:,neuron_No])
#                iter_size = iter(aligned_behaveblock["Bodyspeeds"][row['idx_min']:row['idx_max']])
                plt.plot(x,y,'.',markersize = next(iter_size),color=next(iter_color))   
#                y2 = y+ in_context_msblock.loc[in_context_msblock["ms_ts"].isin(aligned_behaveblock['ms_ts'][row['idx_min']:row['idx_max']])].iloc[:,0:-1].iloc[:,neuron_No]
#                plt.plot(x,y2,'b')
                i=i+1
    plt.xlabel('Body_x')
    plt.ylabel('Trial_num')
    plt.title(title)
#    plt.show()
    figname=str(neuron_No)+"_"+title+'.png'
    fname=os.path.join(r"C:\Users\Sabri\Desktop\test\results",figname)
    plt.savefig(fname)
    return trials_in_block


def Trial_TraceValue(in_context_context_selectivities_trialblocks,blocknames):
    pass
    
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
    
    
    
if __name__=="__main__":
    #%%
#    View_in_context_context_selectivities_trialblocks(in_context_context_selectivities_trialblocks,blocknames)
    #%%
#    for aligned_behaveblock,contextcoord,blockname in zip(aligned_behaveblocks,contextcoords,blocknames):
#        TrackINTrialsView(aligned_behaveblock,contextcoord,blockname)
    #%%
    for i in range(531):
        for aligned_behaveblock,contextcoord,in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
            trial_blocks = Extract_trials(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No=i,title = blockname,column="in_context")
        