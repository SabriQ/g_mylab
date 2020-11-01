from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#%% for population analysis
#累计可解释方差贡献率曲线

#降维，得到新的降维后的特征空间矩阵

# 返还原空间用于数据降噪
def cumulative_contribution_curve(X):
	pca_line = PCA().fit(X)
	plt.plot([1,2,3,4],np.cumsum(pca_line.explained_variance_ratio_))
	plt.xticks([1,2,3,4]) #这是为了限制坐标轴显示为整数
	plt.xlabel("number of components after dimension reduction")
	plt.ylabel("cumulative explained variance ratio")
	plt.show()

def pca(X,n_components="mle"):
	x_mle = PCA(n_components = n_components).fit_transform(X)
	return x_mle