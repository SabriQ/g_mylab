
import numpy as np
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



from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, train_test_split,cross_validate
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from itertools import combinations

def generate_svm_data(data,use_PCA=False):
    svm_score_dict={}
    for contexta,contextb in combinations(np.unique(data.index.get_level_values("Context")),2):
        new_data = data[data.index.get_level_values("Context").isin([contexta,contextb])]
        trials = np.array(new_data.groupby(["Trial_Num","Context"]).mean().index.get_level_values("Trial_Num"))
        placebins = np.arange(0,100)
        
        target = np.array(new_data.groupby(["Trial_Num","Context"]).mean().index.get_level_values("Context"))

        target_len=[]
        for ta in np.unique(target):
            target_len.append(sum(target==ta))
        if (np.array(target_len) < 10).any():
            break

        matrix = np.full((len(trials),len(placebins)),0) # [trials,placebins]
        svm_score={}
        cell_num = len(new_data.columns)
        for i,cell in enumerate(new_data.columns,0): # for different cells
            print("cell:%s/total:%s"%(i,cell_num))
            for t,trial in enumerate(trials,0):
                for placebin in placebins:
                    try:
                        meanfr = new_data.xs(key=(trial,placebin),level=("Trial_Num","place_bin_No"))[cell]
                        matrix[t,placebin] = meanfr
    #                     print(t,placebin)
                    except:
                        pass
            # yield cell,matrix,target
            X = StandardScaler().fit_transform(matrix)
            y=target
            if use_PCA:
                X[np.isnan(X)]=0
                X = PCA(2).fit_transform(X)
            clf = SVC(kernel="rbf",gamma="auto",cache_size=5000)
            svm_score[cell] = cross_val_score(clf,X,y,cv=5).mean()
        svm_score_dict["context_%s_%s"%(contexta,contextb)]=svm_score
    return svm_score_dict


def main_svm_score(s,*args,**kwargs):

    data = construct_svm_dict(s,*args,**kwargs)
    svm_score_dict = generate_svm_data(data)
    return svm_score_dict


