from sklearn.decomposition import PCA
from dPCA import dPCA
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#%% for population analysis
#累计可解释方差贡献率曲线

#降维，得到新的降维后的特征空间矩阵

# n_components 有三种选择模式
## 数字
## mle
## 在(0,1)的数字， svd_solver = "auto",full","arpack","randomized"

# 返还原空间用于数据降噪inverse_transform



def pca(x,**kargws):
    """
    x: dataframe with "context" and "placebins" as two of the multi-indexes
    """

    x_arr = x.values
    
    context_0_index = x.index.get_level_values(level="Context")==0
    context_1_index = x.index.get_level_values(level="Context")==1
    context_2_index = x.index.get_level_values(level="Context")==2

    pca = PCA(**kargws)
    pca = pca.fit(x_arr)
    x_dr = pca.transform(x_arr)

    fig,axes = plt.subplots(3,3,figsize=(20,15))
    axes[0,0].plot(np.arange(0,10),np.cumsum(pca.explained_variance_ratio_)[0:10])
    axes[0,0].scatter(np.arange(0,10),np.cumsum(pca.explained_variance_ratio_)[0:10],s=15)
    axes[0,0].scatter(np.arange(0,10),pca.explained_variance_ratio_[0:10],s=15)
    axes[0,0].set_xticks(np.arange(0,10))
    axes[0,0].set_title("PCA-analysis")
    axes[0,0].set_xlabel("number of components after dimension reduction")
    axes[0,0].set_ylabel("cumulative explained variance ratio")

    spatial_points={
    "nosepoke": 0,
    "turnover_1": 3,
    "context_enter": 7,
    "context_exit": 37,
    "turnover_2": 41,
    "choice1": 45,
    "choice2": 49,
    "turnover_3": 57,
    "context_reverse_enter": 61,
    "context_reverse_exit":91,
    "turnover_4": 95,
    "trial_end": 99}

    for ax,c in zip(axes.flat[1:],[0,1,2,3,4,5,6,7]):
        for ctx in [context_0_index,context_1_index]:
            ax.plot(np.arange(0,len(x_dr[ctx,:])),x_dr[ctx,:][:,c])
            ax.legend(["ctx0","ctx1"])
        for point in spatial_points.keys(): # for different point
            if "choice" in point:
                color = "red"
            elif "turn" in point:
                color = "green"
            elif "context" in point:
                color = "orange"
            else:
                color = "black"
            ax.axvline(spatial_points[point],linestyle="--",color=color)
        ax.set_title("PC%s"%(c+1))
        ax.set_xlabel("Placebins")
    plt.tight_layout()
    plt.show()
    
    result = {
    "x_dr":x_dr,
    "pca":pca,
    "context_0_index":context_0_index,
    "context_1_index":context_1_index,
    "context_2_index":context_2_index
    }

    return result

def demixed_pca(R,trialR,**kwargs):
    """
    R
    trialR
    """

    dpca = dPCA.dPCA(labels='cdp',regularizer='auto',n_components=100,**kwargs) 
    dpca.protect = ['p']

    dpca = dpca.fit(R,trialR)
    Z = dpca.transform(R,marginalization=None)
    significance_masks = dpca.significance_analysis(X = R,trialX=trialR ,n_shuffles=20, n_splits=10, n_consecutive=10)
    
    result = {
    "dpca":dpca,
    "Z":Z,
    "significance_masks":significance_masks
    }
    return result