import numpy as np
import scipy.stats as stats
import pandas as pd
import os,sys

def normalized_distribution_test(datalist):
    """
    检查数据是否符合正太分布

    如果是检测是否有差异
        服从正太分布：还需要判定方差齐次性来选择,
        不服从正太分布： 用到非参数检验，wilcoxon_ranksumstest
    如果是计算相关性的P值，
        不服从正态分布：spearman, kendall
        服从正态分布：pearson (default)
    零假设：数据是正太分布的
    P值小于0.05时拒绝零假设，即数据不服从正态分布
    返回的第二个值是p-value
    """
    return stats.shapiro(datalist)

def var_test(rvs1,rvs2):
    """
    两独立样本t检验-ttest_ind
    方差齐次性检验
    LeveneResult(statistic=1.0117186648494396, pvalue=0.31473525853990908)
    p值远大于0.05，认为两总体具有方差齐性
    """
    return stats.levene(rvs1, rvs2)

def ttest_ind(rvs1, rvs2):
    """
    如果具备方差齐性，equal_var = True
    如果不具备方差齐性，equal_var = False
    """
    normalizations = []
    normalization_1 = normalized_distribution_test(rvs1)[1]
    normalization_2 = normalized_distribution_test(rvs2)[1]
    if normalization_1 > 0.05:
        normalizations.append(1)
    else:
        normalizations.append(0)

    if normalization_1 > 0.05:
        normalizations.append(1)
    else:
        normalizations.append(0)

    if all(normalizations):
        print("数据均符合正太分布")
    else:
        print("数据至少有一个不符合正太分布%s"%normalizations)
        print("请使用Wilcoxon_ranksumstest")
        sys.exit()


    if var_test(rvs1,rvs2)[1]>0.05:
        equal_var = True
        print("数据具备方差齐性")
    else:
        equal_var = False
        print("数据不具备方差齐性")

    return stats.ttest_ind(rvs1,rvs2, equal_var = equal_var)

def Wilcoxon_ranksumstest(data1,data2):
    """
    for two independent samples
    result is something like this
    WilcoxonResult(statistic=2.0, pvalue=0.01471359242280415)
    """
    return stats.ranksums(data1,data2)

def Wilcoxon_signed_ranktest(paired_data1):
    """
    for one sample and two paired samples 
    result is something like this
    WilcoxonResult(statistic=2.0, pvalue=0.01471359242280415)
    """
    return stats.wilcoxon(paired_data1,y=None, zero_method='wilcox', correction=False, alternative='two-sided')

def kstest(*args):
    if len(args)==1:
        x=args[0]
        statistic,pvalue = stats.kstest(x,'norm')
        print(r"H0: single sample is normally distributed: ")
        present(pvalue)
    elif len(args)==2:
        x,y = list(args[0]),list(args[1])
        statistic,pvalue = stats.ks_2samp(x,y)
        print(r"H0: two samples are similarily distributed: ")
        present(pvalue)
    else:
        print("inputs are more than 2 list.")

def present(pvalue):
    if pvalue<0.05 and pvalue >=0.01:
        print("* p-value: %s"%pvalue)
    elif pvalue <0.01 and pvalue >= 0.001:
        print("** p-value: %s"%pvalue)
    elif pvalue < 0.001 and pvalue >= 0.0001:
        print("*** p-value: %s"%pvalue)
    elif pvalue < 0.0001:
        print("**** p-value: %s"%pvalue)
    else:
        print("n.s. %s"%pvalue)

if __name__ == "__main__":
    result = Wilcoxon_ranksumstest([1,2,4,6,8],[3,5,7,1])