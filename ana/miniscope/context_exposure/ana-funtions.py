
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys,glob
import scipy.io as spio
import pickle
import scipy.stats as stats

def cellids_Context(s,context_map=["A","B","C","N"]):
    """

    """
    # trim df, get the trimed df and index. 
    df,index = s.trim_df(df=None
        ,force_neg2zero=True
        ,Normalize=False
        ,standarize=False
        ,in_context=True)

    meanfr_df = df[index].groupby(s.result["Trial_Num"][index]).mean().reset_index(drop=False)

    temp = pd.merge(meanfr_df,s.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])
    Context = temp["Enter_ctx"]
    Context = pd.Series([context_map[i] for i in Context])



    ctx_pvalue = meanfr_df[idxes].apply(func=lambda x: stats.ranksums(x[Context=="A"],x[Context=="B"])[1],axis=0)
    ctx_meanfr = meanfr_df[idxes].groupby(Context).mean().T
    ctx_meanfr["ranksums_p_value"] = ctx_pvalue
    ctx_meanfr["CSI"] = (ctx_meanfr["A"]-ctx_meanfr["B"])/(ctx_meanfr["A"]+ctx_meanfr["B"])
    ContextA_cells=[]
    ContextB_cells=[]
    non_context_cells=[]

    for cellid,a, b, p in zip(ctx_meanfr.index,ctx_meanfr["A"],ctx_meanfr["B"],ctx_meanfr["ranksums_p_value"]):
        if p>=0.05:
            non_context_cells.append(cellid)
        else:
            if a>b:
                ContextA_cells.append(cellid)
            elif a<b:
                ContextB_cells.append(cellid)
            else:
                logger.warning("meanfr of cell % is equal in Context A and Context B"%cellid)
                non_context_cells.append(cellid)

    return{
    "meanfr_df":meanfr_df,
    "ctx_meanfr":ctx_meanfr, # meanfr in context A and B, rank_sum_pvalue,CSI
    "ContextA_cells":ContextA_cells,
    "ContextB_cells":ContextB_cells,
    "non_context_cells":non_context_cells
    }
