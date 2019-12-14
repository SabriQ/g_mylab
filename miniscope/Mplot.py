
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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
def TrackINTrialsView(in_context_behaveblock,contextcoord,title):
#    sns.distplot(in_context_behaveblock["Tailspeed_angles"])
    plt.figure(figsize=(4,20));
    x_max = max(result["contextcoords"][1][1][0][:,0])
    x_min = min(result["contextcoords"][1][1][0][:,0])
    for i in range(44):
        if in_context_behaveblock["Headspeed_angles"].tolist()[i] >100 and in_context_behaveblock["Headspeed_angles"].tolist()[i] <260:
            plt.plot(in_context_behaveblock["Body_x"].tolist()[i],i,"r.")
            if i >40:
                print(in_context_behaveblock["Body_x"].tolist()[i])
        if in_context_behaveblock["Headspeed_angles"].tolist()[i] <100 or in_context_behaveblock["Headspeed_angles"].tolist()[i] >260:
            plt.plot(in_context_behaveblock["Body_x"].tolist()[i],i,"g.")
            if i >40:
                print(in_context_behaveblock["Body_x"].tolist()[i])
    plt.axvspan(x_min,x_max,0,1,color="gray",alpha=0.3)
    plt.xticks([])
    plt.yticks([])
    plt.title(title)
    plt.show()
if __name__=="__main__":
#    for i in range(12):
    TrackINTrialsView(aligned_behaveblocks[8],contextcoords[8],"9")