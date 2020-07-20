
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mylab.process.miniscope.lick_water.Mfunctions import *
import os
import seaborn as sns
import gc

def TraceView(RawTraces,title="TraceView"):
    plt.figure(figsize=(10,0.5))
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

def TrackinZoneView(ZoneCoordinates,align_msblocks_behaveblocks,blocknames,window_title="Track_in_context",figsize=(20,5)):
    #coordinates = result['contextcoords']
    #output contextcoords (contextcoord in each block)
    contextcoords=ZoneCoordinates
    plt.figure(window_title,figsize=figsize)
    for i in range(len(align_msblocks_behaveblocks)):           
        plt.subplot(2,6,i+1)
        x=align_msblocks_behaveblocks[i]['Body_x'] 
        y=align_msblocks_behaveblocks[i]['Body_y'] 
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
    plt.figure(figsize=(8,20));
    x_max = max(contextcoord[1][0][:,0])
    x_min = min(contextcoord[1][0][:,0])    
    colors = []
    x = aligned_behaveblock["Body_x"]
    y=[]
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

def in_context_Extract_trials():
    pass
def Extract_trials(aligned_behaveblock,contextcoord,in_context_msblock,column="in_context",title="title",example_neuron=1):
    df = rlc2(aligned_behaveblock[column])
    trials_in_block=[]
#    sns.distplot(df['length'])    
    x_max = max(np.array(contextcoord[1][0])[:,0])
    x_min = min(np.array(contextcoord[1][0])[:,0])
    i=1
    plt.figure(figsize=(5,10))
    plt.subplot(1,2,1)
    trial_traces_in_block = []
    colors_in_block=[]
    for index,row in df.iterrows():
        if row['name'] == 1 and row['idx_min']<row['idx_max']:     
            x = aligned_behaveblock["Body_x"][row['idx_min']:row['idx_max']]
            x_max2 = max(x)
            x_min2 = min(x)   
            if (x_max2-x_min2)>0.5*(x_max-x_min): # 轨迹要大于一半的context长度
                trials_in_block.append(aligned_behaveblock.iloc[row['idx_min']:row['idx_max']].as_matrix())
                trial_traces_in_block.append(in_context_msblock.loc[in_context_msblock["ms_ts"].isin(aligned_behaveblock["ms_ts"][row['idx_min']:row['idx_max']])])
                trial_num = [i]                
                y = trial_num*(row['idx_max']-row['idx_min'])
                colors = []                
                for angle in aligned_behaveblock["Bodyspeed_angles"][row['idx_min']:row['idx_max']]:
                    if angle>100 and angle<260:
                        colors.append('r')
                    else:
                        colors.append('g')
                colors_in_block.append(colors)
                iter_color = iter(colors)
#                iter_size = iter(in_context_msblock.loc[in_context_msblock["ms_ts"].isin(aligned_behaveblock['ms_ts'][row['idx_min']:row['idx_max']])].iloc[:,0:-1].iloc[:,neuron_No])
#                iter_size = iter(aligned_behaveblock["Bodyspeeds"][row['idx_min']:row['idx_max']])
#                plt.plot(x,y,'.',markersize = next(iter_size)/2,color=next(iter_color))  
                plt.plot(x,y,'.',color=next(iter_color))
#                y2 = y+ in_context_msblock.loc[in_context_msblock["ms_ts"].isin(aligned_behaveblock['ms_ts'][row['idx_min']:row['idx_max']])].iloc[:,0:-1].iloc[:,neuron_No]
#                plt.plot(x,y2,'b')                
                i=i+1
#    print(len(trials_in_block),len(trial_traces_in_block),len(colors))
    plt.xlabel('Body_x')
    plt.ylabel('Trial_num')
    plt.title(title)
    plt.show()    
#    figname=str(neuron_No)+"_"+title+'.png'
#    fname=os.path.join(r"C:\Users\Sabri\Desktop\test\results",figname)
#    plt.savefig(fname)
#    print(f"{fname} is saved!")
#    plt.close()
    colors = []
    for color in colors_in_block:
        colors = colors+color
    
    plt.figure(figsize=(20,2))
    x = list(range(1,len(colors)+1))
    y = pd.concat(trial_traces_in_block,ignore_index=True).iloc[:,example_neuron].tolist()
#    plt.plot(x,y,'black',alpha=0.5)
    plt.scatter(x,y,c=colors,marker='.')
    plt.title("neuron_id:"+str(in_context_msblock.columns[example_neuron]))
    plt.xticks([])
#    plt.yticks([])
    plt.show()    
#    TraceView(pd.concat(trail_traces_blocks,ignore_index=True).iloc[:,0])
    return trials_in_block,trial_traces_in_block

def Extract_trials2(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No,column="in_context",title="title",):
    df = rlc2(aligned_behaveblock[column])
    trial_behaves_block=[]
    trial_traces_block=[]
    trial_Nums_block=[]
    trial_LoRs_block=[]
    Cx_max = max(contextcoord[1][0][:,0])
    Cx_min = min(contextcoord[1][0][:,0])
    i=1
    for index,row in df.iterrows():
        if row['name'] == 1:          
            Bx = aligned_behaveblock["Body_x"][row['idx_min']:row['idx_max']]
            Bx_max2 = max(Bx)
            Bx_min2 = min(Bx)   
            if (Bx_max2-Bx_min2)>0.5*(Cx_max-Cx_min):
                trial_behaves_block.append(aligned_behaveblock.iloc[row['idx_min']:row['idx_max']])               
                trial_traces_block.append(in_context_msblock.loc[in_context_msblock["ms_ts"].isin(aligned_behaveblock["ms_ts"][row['idx_min']:row['idx_max']])])
                trial_num = [i]                
                trial_Nums_block.append(pd.Series(trial_num*(row['idx_max']-row['idx_min'])))
                LoRs = [] # left or right 
                for angle in aligned_behaveblock["Bodyspeed_angles"][row['idx_min']:row['idx_max']]:
                    if angle>100 and angle<260:
                        LoRs.append('left')
                    else:
                        LoRs.append('right')
                trial_LoRs_block.append(pd.Series(LoRs))
                i=i+1
    #all Trials
    colors = pd.concat(trial_LoRs_block,ignore_index=True).replace(["left","right"],['r','g'])
    direction = pd.concat(trial_LoRs_block,ignore_index=True)
    x_order = list(range(1,len(colors)+1))
    trial_behaves = pd.concat(trial_behaves_block,ignore_index=True)
    Bxs = trial_behaves['Body_x']
    Bxspeeds=trial_behaves['Bodyspeeds']
    TrialNums=pd.concat(trial_Nums_block,ignore_index=True)
    Traces = pd.concat(trial_traces_block,ignore_index=True).iloc[:,neuron_No]#.tolist()
#    Traces = pd.concat(trial_traces_block,ignore_index=True).where(Bxspeeds.abs()<0.01).iloc[:,neuron_No]
    # Trials with speedthreshold > 1
    speed_threshold = 3
    colors_mobile = colors.where(Bxspeeds>speed_threshold).dropna().reset_index(drop=True)
    direction_mobile = direction.where(Bxspeeds>speed_threshold).dropna().reset_index(drop=True)
    Bxs_mobile = Bxs.where(Bxspeeds>speed_threshold).dropna().reset_index(drop=True)
    Bxspeeds_mobile = Bxspeeds.where(Bxspeeds>speed_threshold).dropna().reset_index(drop=True)
    Traces_mobile = Traces.where(Bxspeeds>speed_threshold).dropna().reset_index(drop=True)
    
    colors_static=colors.where(Bxspeeds<speed_threshold).dropna().reset_index(drop=True)
    direction_static=direction.where(Bxspeeds<speed_threshold).dropna().reset_index(drop=True)
    Bxs_static=Bxs.where(Bxspeeds<speed_threshold).dropna().reset_index(drop=True)
    Bxspeeds_static=Bxspeeds.where(Bxspeeds<speed_threshold).dropna().reset_index(drop=True)
    Traces_static=Traces.where(Bxspeeds<speed_threshold).dropna().reset_index(drop=True)
    
#    print(len(colors_mobile),len(Bxs_mobile),len(Bxspeeds_mobile),len(Traces_mobile))
    #plot trial by trial according TrialNums-Bxs
    plt.figure() # for more clear dots, dpi =200
#    plt.title(f"Trace_{neuron_No}")
    ax1 = plt.axes([0.1,-1.1,0.25,2.0])
    ax2 = plt.axes([0.5,0.8,2,0.1],frame_on=True) 
    ax3 = plt.axes([0.5,0.62,2,0.1],frame_on=True)
    ax4 = plt.axes([0.5,0.1,0.4,0.4])
    ax5 = plt.axes([1.0,0.1,0.4,0.4])
    ax6 = plt.axes([1.5,0.1,0.4,0.4])
    ax7 = plt.axes([0.5,-0.5,0.4,0.4])
    ax8 = plt.axes([1.0,-0.5,0.4,0.4])
    ax9 = plt.axes([1.5,-0.5,0.4,0.4])
    ax10 = plt.axes([0.5,-1.1,0.4,0.4])
    ax11 = plt.axes([1.0,-1.1,0.4,0.4])
    ax12 = plt.axes([1.5,-1.1,0.4,0.4])
    ax1.scatter(Bxs,TrialNums,c=colors,marker='.',s=1)
    ax1.set_title(title+"_trials")
    ax1.set_ylabel("Trial_Num")
    ax1.set_xlabel("Body_x(pixel)")
    #plot  Traces-x_order    
    ax2.set_aspect("auto")
    ax2.scatter(x_order,Traces,c=colors,s=1)
    ax2.set_title(f"Trace{neuron_No}-TraceValue-x_order")
    ax2.set_xticklabels([])
    ax2.set_xticks([])
    #plot  Speed-x-order
    ax3.scatter(x_order,Bxspeeds,c=colors,s=1)
    ax3.set_title("Speed-x_order")
    #plot TraceValue-BodySpeed
    ax4.plot(Bxspeeds,Traces,'.',color='black',markersize=1)
    ax4.set(title="Trace-Speed",xlabel="BodySpeed,cm/s",ylabel="TraceValue")
    #plot TraceValue-go_direction    
#    ax5.scatter(colors,Traces,c=colors,s=1,alpha=0.5)
    x = direction.unique()
    y = [Traces.where(colors==i).mean() for i in colors.unique()]
    yerr = [Traces.where(colors==i).std() for i in colors.unique()]    
    ax5.plot(x,y,'.',color="black",markersize=10)
    ax5.errorbar(x,y,yerr=yerr,color='black')
    ax5.set(title="Trace-Direction",xlabel="go-direction")
    ax5.set_xlim(-0.5,1.5)
#    ax5.set_xticklabels(["go-left","go-right"])
    # plot TraceValue-Bodyx
    ax6.scatter(Bxs,Traces,c=colors,s=1)
    ax6.set(title="Trace-BodyX",xlabel="BodyX")
    #plot TraceValue-BodySpeed mobile
    ax7.plot(Bxspeeds_mobile,Traces_mobile,'.',color='black',markersize=1)
    ax7.set(title="Trace-Speed-mobile",xlabel="BodySpeed,cm/s",ylabel="TraceValue")
    #plot TraceValue-go_direction mobile
    x = direction_mobile.unique()
    y = [Traces_mobile.where(colors_mobile==i).mean() for i in colors_mobile.unique()]
    yerr = [Traces_mobile.where(colors_mobile==i).std() for i in colors_mobile.unique()]    
    ax8.plot(x,y,'.',color="black",markersize=10)
    ax8.errorbar(x,y,yerr=yerr,color='black')
    ax8.set(title="Trace-Direction-mobile",xlabel="go-direction")
    ax8.set_xlim(-0.5,1.5)
    # plot TraceValue-Bodyx mobile
    ax9.scatter(Bxs_mobile,Traces_mobile,c=colors_mobile,s=1)
    ax9.set(title="Trace-BodyX-mobile",xlabel="BodyX")
    #plot TraceValue-BodySpeed static
    ax10.plot(Bxspeeds_static,Traces_static,'.',color='black',markersize=1)
    ax10.set(title="Trace-Speed-static",xlabel="BodySpeed,cm/s",ylabel="TraceValue")
    #plot TraceValue-go_direction static
    x = direction_static.unique()
    y = [Traces_static.where(colors_static==i).mean() for i in colors_static.unique()]
    yerr = [Traces_static.where(colors_static==i).std() for i in colors_static.unique()]    
    ax11.plot(x,y,'.',color="black",markersize=10)
    ax11.errorbar(x,y,yerr=yerr,color='black')
    ax11.set(title="Trace-Direction-static",xlabel="go-direction")
    ax11.set_xlim(-0.5,1.5)
    # plot TraceValue-Bodyx static
    ax12.scatter(Bxs_static,Traces_static,c=colors_static,s=1)
    ax12.set(title="Trace-BodyX-static",xlabel="BodyX")
    
#    plt.show()    
#    TraceView(pd.concat(trail_traces_blocks,ignore_index=True).iloc[:,0])
    figname=str(neuron_No)+"_sum01_"+title+'.png'
    fname=os.path.join(r"C:\Users\Sabri\Desktop\test\results",figname)
    plt.savefig(fname,bbox_inches = 'tight')
    print(f"{fname} is saved!")
    del trial_behaves_block,trial_traces_block,trial_Nums_block
    plt.cla()
    plt.clf()
    plt.close('all')
    gc.collect()

    return 0 

def Trial_TraceValue(in_context_context_selectivities_trialblocks,blocknames):
    pass
    
    
    
if __name__=="__main__":

    #%%
#    for aligned_behaveblock,contextcoord,blockname in zip(aligned_behaveblocks,contextcoords,blocknames):
#        TrackINTrialsView(aligned_behaveblock,contextcoord,blockname)
    #%%
    def traverse(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
        for aligned_behaveblock,contextcoord,in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
            yield [aligned_behaveblock,contextcoord,in_context_msblock,blockname]
    for i in range(531):
        if i>148:
            for aligned_behaveblock,contextcoord,in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
#                trial_BodyXs_block,trial_BodyXspeeds_block,trial_traces_block = Extract_trials2(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No=i,title = blockname,column="in_context")
                Extract_trials2(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No=i,title = blockname,column="in_context")
        