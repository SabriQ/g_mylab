import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import h5py
import sys
import seaborn as sns
from mylab.ana.Mstat import *




def shuffle_arr(arr,axis=1,times=1000):
    """
    arr: numpy array mxn
    times
    axis: shuffle along rows for each columns, the sum of each row stay the same.
    """
    arr_c = arr.copy()
    for i in range(times):
        np.apply_along_axis(np.random.shuffle,axis,arr_c) # arr will be inplaced.
        sys.stdout.write("shuffle for %s/%s times "%(i+1,times))
        sys.stdout.write("\r")
        yield arr_c

def shuffle_corrcoef(arr):


    shuffle_cor= []
    shuffled_arr = shuffle_arr(arr,axis=1,times=1000)
    for i in shuffled_arr:
        shuffle_cor.append(np.corrcoef(i))        
    print("\r")
    shuffle_cor = np.array(shuffle_cor)
    
    return shuffle_cor #(shuffle_times, neuron_num,neuron_num)
    
def correlated_pair_threshold(arr,thresh):
    """
    arr: each row means neuron, each column means fr in timebin
    times: shuffle times
    thresh: the specifice Pearson's R
    refer to Fig s2_panel B correlated pair threshold 
    """
    # calculate the Pearson's correlation for each pair of each neuron
    arr_cor = np.corrcoef(arr)
    # Pearson R > thresh
    rows,cols = np.where(arr_cor>thresh)
    correlated_pair = np.array([(row,col,arr_cor[row,col]) for row,col in zip(rows,cols) if row <col])
    paried_neurons = [i[0:2] for i in correlated_pair]
    pearson_r = [i[2] for i in correlated_pair]


    # p<0.05 from shuffle distribution
    shuffle_cor = shuffle_corrcoef(arr)
    rows2,cols2 = np.where(arr_cor > np.quantile(shuffle_cor,0.95,axis=0))
    correlated_pair2 = np.array([(row,col,arr_cor[row,col]) for row,col in zip(rows2,cols2) if row <col])
    paried_neurons2 = [i[0:2] for i in correlated_pair2]
    pearson_r2 = [i[2] for i in correlated_pair2]


    probablity = 1 * np.arange(len(pearson_r)) / (len(pearson_r) - 1)
    r_sorted1 = pearson_r.copy()
    r_sorted1.sort()
   
    probablity2 = 1 * np.arange(len(pearson_r2)) / (len(pearson_r2) - 1)
    r_sorted2 = pearson_r2.copy()
    r_sorted2.sort()
#     sns.kdeplot(pearson_r[:,2],cumulative=True,color="red")
#     print(pearson_r,pearson_r2)
    #plot
    plt.figure(figsize=(10,4))
    plt.subplot(121)
    plt.plot(r_sorted1,probablity,"r-")
    plt.plot(r_sorted2,probablity2,"g-")

#     sns.kdeplot(pearson_r2[:,2],cumulative=True,color="green")
    plt.title("Correlated Pairs")
    plt.xlabel("Pearson's R")
    plt.ylabel("Fraction of neuronal pairs")
    plt.legend(["Pearson's R>0.3",">0.95 shuffle Dist."])
    
    plt.subplot(122)
    #计算与每一行（表示每一个neuron） correlated 的neurons 个数， 包括 0
    correlated_counts = dict()
    correlated_counts2 = dict()
    
    for i in range(arr.shape[0]):
        correlated_counts[i]=len([paired_neuron[0] for paired_neuron in paried_neurons if paired_neuron[0]==i ])
        correlated_counts2[i]=len([paired_neuron[0] for paired_neuron in paried_neurons2 if paired_neuron[0]==i ])
    
    plt.hist(correlated_counts.values(),bins=max(correlated_counts.values())-1,edgecolor="black",facecolor="red",alpha=0.5)
    plt.hist(correlated_counts2.values(),bins=max(correlated_counts2.values())-1,edgecolor="black",facecolor="green",alpha=0.5)
    plt.ylabel("Cell numbers")
    plt.xlabel("Pair numbers")
    plt.title("Correlated Pairs")
    plt.legend(["Pearson's R>0.3",">0.95 shuffle Dist."])
    

    return correlated_pair, correlated_pair2,kstest(correlated_counts.values(),correlated_counts2.values())


