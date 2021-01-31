
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
from mylab.ana.miniscope.context_exposure.Canamini import AnaMini
import copy
from multiprocessing import Pool

def construct_svm_dict(s:AnaMini,*args,**kwargs):
    """
    Returns
        dict is constructed with data and target. data is [n_samples,n_features], target is as long as n_samples

    s.add_Trial_Num_Process()
    s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
    s.add_Context()
    """

    df,index = s.trim_df(*args,**kwargs)
    
    Trial_Num = s.result["Trial_Num"]
    process = s.result["process"]
    place_bin_No = copy.deepcopy(s.result["place_bin_No"])

    # 将backward的place_bin_No 反向增加
    max_placebin = 49
    for i in place_bin_No[(process>3) | (process==0)].index:
        place_bin_No[i] = 2*max_placebin-place_bin_No[i]+1

    Trial_Num=Trial_Num[index]
    process=process[index]
    Context= s.result["Context"][index]


    data = df[index].groupby([Trial_Num,Context,place_bin_No]).mean()

    return data

def construct_pvalue_matrix(data):
    matrix_pvalue = {}
    for c1,c2 in combinations(np.unique(data.index.get_level_values(level="Context")),2):
    matrix_pvalue["context%s_%s"%(c1,c2)] = np.full((len(data.columns),100),np.nan) # [cells,placebins]
    for i,cell in enumerate(data.columns,0):
#         print("i:%s"%i)
        for placebin in np.arange(0,100):
#             print("%s"%placebin,end=" ")
            try:
                context_a = data.xs(key=(c1,placebin),level=("Context","place_bin_No"))[cell]
                context_b = data.xs(key=(c2,placebin),level=("Context","place_bin_No"))[cell]
                if len(context_a) < 3 or len(context_b) < 3:
                    pass
                else:
                    statistic,p_value = Wilcoxon_ranksumstest(context_a,context_b)
            
                    matrix_pvalue["context%s_%s"%(c1,c2)][i,placebin] = p_value
            except:
                p_value = np.nan
    return matrix_pvalue

def construct_pvalue_matrixes(datas:list):
    matrix_pvalues = []
    matrix_pvalues.append(construct_pvalue_matrix(data))
    keys = []
    for matrix_pvalue in matrix_pvalues:
        keys = keys + matrix_pvalue.keys()
    keys = np.unique(keys)
    concated_matrix_pvalue={}
    for key in keys():
        
    concated_matrix_pvalue = np.concatenate([],axis=1)

    return concated_matrix_pvalue

def plot_matrix_pvalue(matrix_pvalue):
    plt.rc('font',family='Times New Roman')
    for key in matrix_pvalue.keys():
        matrix = matrix_pvalue[key]
        plt.figure(figsize=(20,10))
        ax = sns.heatmap(matrix,vmin=0,vmax=0.05,mask=matrix>0.05,cbar_kws = {'label':'P_value',"pad":0.05})
        cbar = ax.collections[0].colorbar
        cbar.set_label(label="p_value",fontsize=20)
        for x in [3,7,37,41,45,49,53,57,61,91,95]:
            color = "red"
            linetype="-"
            if x in [3,41,57,95]:
                color = "green"
                linetype="-"
            if x in [45,53]:
                color = "blue"
                linetype="-"
            if x in [49]:
                color = "blue"
                linetype="--"
            plt.axvline(x,c=color,linestyle=linetype)
            plt.ylabel("Cells",fontdict={"fontsize":20},labelpad=20)
            plt.xlabel("Placebins",fontdict={"fontsize":20},labelpad=20)
            plt.title(key,fontdict={
                "fontsize":20
            },pad=20)
            