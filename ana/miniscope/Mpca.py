from sklearn.decomposition import PCA
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

    for ax,c in zip(axes.flat[1:],[0,1,2,3,4,5,6,7]):
        for ctx in [context_0_index,context_1_index]:
            ax.plot(np.arange(0,len(x_dr[ctx,:])),x_dr[ctx,:][:,c])
            ax.legend(["ctx0","ctx1"])
        for x in [4,8,48,52,56]:
            ax.axvline(x,linestyle="--",color="gray")
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