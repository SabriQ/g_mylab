import numpy as np
from numpy import trapz
import pandas as pd
import matplotlib.pyplot as plt
import os,sys,glob

# refer to 'jessica 2020 Neuron Contextual fear memory retrieval by correlated ensembles of ventral CA1 neurons'

def detect_ca_transients(idx,raw_cell,thresh,baseline,t_half=0.2,FR=30,show=True):
    """
    idx, all the cell_ids in raw_cell
    raw_cell, numpy matrix.  m rows, n columns;m means each obeservation in each time point,n means each cell.
    """
    idx = np.array(idx)
    if not raw_cell.shape[1]>=len(idx):
        print("raw_cell doesn't match idx")
        sys.exit()
        
    pophist = np.reshape(raw_cell,(1,-1))[0]    #将所有的细胞发放变成一列
    pop_offset=np.quantile(pophist,0.50)
    silent=pophist<pop_offset
    mu=np.mean(pophist[silent==1]) #根据发放大小 最小的前百分之五十 发放的均值？应该是为了模拟baseline 的均值
    celldata = np.apply_along_axis(lambda x:(x-mu)/np.std(x,ddof=0),axis=0,arr=raw_cell) #z_score

    celldata_detect = np.zeros_like(celldata)
    # define minimum duration of calcium transient based on gcamp type used
    decayrate=0.693/t_half #simplified from (-ln(A/Ao)/t_half), [A/Ao]=0.5 at t half-life, [-ln(A/Ao)]=0.693
    minduration=-(np.log(baseline/thresh))/decayrate #minimum (s) duration for ca transient of minimum specified s.d. amplitude threshold
    minframes= round(minduration*FR); #minimum number of frames the ca transient should last above basel
    print("minframes: %s"%minframes)
    ca_transients=dict()
    for j,cellid in enumerate(idx):
        sys.stdout.write("calcium transients detecting: %s/%s cells"%(j+1,celldata.shape[1]))
        sys.stdout.write("\r")
        x = celldata[:,j]
        onset = np.argwhere(x>thresh)
        offset = np.argwhere(x>baseline)
        cell_transients=[]
        found = 1;
        for i in range(len(offset)-1):
            if found == 1:
                start = offset[i][0]
                found=0
            if offset[i+1][0]-offset[i][0]>1:
                finish = offset[i][0]+1# 包括索引的最后一个
                cell_transient = pd.Series(x)[start:finish]
                M = cell_transient.max()
                maxamp_ind = cell_transient.idxmax()
                peak_to_offset_vect= cell_transient.loc[maxamp_ind:finish+1]
                found=1                
                if maxamp_ind in onset.T[0] and len(peak_to_offset_vect)>minframes:
                    # cell transient,id, maximum,area_AUC
                    cell_transients.append((cell_transient,maxamp_ind,M,trapz(cell_transient)))
                    celldata_detect[:,j][start:finish]=cell_transient.values
#                     print("%s==%s==%s==%s=="%(start,finish,maxamp_ind,len(peak_to_offset_vect)))

            if i == (len(offset)-1):
                finish = offset[-1][0]
                cell_transient = pd.Series(x)[start:finish]            
                M = cell_transient.max()
                maxamp_ind = cell_transient.idxmax()
                peak_to_offset_vect= cell_transient.loc[maxamp_ind:finish]
                found=1
                if maxamp_ind in onset.T[0] and len(peak_to_offset_vect)>minframes:
                    # cell_transient,id, maximum,area_AUC
                    cell_transients.append((cell_transient,maxamp_ind,M,trapz(cell_transient)))
                    celldata_detect[:,j][start:finish]=cell_transient.values
            
        ca_transients[cellid]=pd.DataFrame(cell_transients,columns=["cell_transient","maxamp_ind", "maximum","area_AUC"])
    if show:
        print("plotting")
        plt.figure(figsize=(40*celldata.shape[0]/20000,len(idx)))
        y_j=[]
        for j,id in enumerate(idx):
            plt.plot(celldata[:,j]+j*10,color="black",linewidth=1)
            y_j.append(j*10)
            for i in ca_transients[id]["cell_transient"]:
                plt.plot(i+j*10,"r",linewidth=1)
        plt.yticks(ticks=y_j,labels=idx)
        plt.ylabel("Cellids")
        plt.show()
        def single_cell_detected_transient(id):
            try:
                j = np.argwhere(idx==id)[0][0]
            except:
                print("cell %s is not exist")
                sys.exit()
            plt.figure(figsize=(40*celldata.shape[0]/20000,1))
            plt.plot(celldata[:,j],color="black",linewidth=1)
            for i in ca_transients[id]["cell_transient"]:
                plt.plot(i,"r",linewidth=1)
                # plt.gca().set_axis_off()
                plt.title(id)
            plt.show()
    return ca_transients,celldata_detect,single_cell_detected_transient