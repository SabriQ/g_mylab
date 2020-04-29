import scipy.io as spio
from mylab.File import *
import numpy as np
import os
from mylab.Cmouseinfo import MouseInfo
import pandas as pd
#%% path
resultmat_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\LinearTrackAll"
resultpkl_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all"
resultmat_path = os.path.join(resultmat_dir,"191173_in_context.mat")
resultpkl_path = os.path.join(resultpkl_dir,"191173_in_context.pkl")

result_path_xc = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Ctx_HD_PC.mat"

mouse_info_path = r"Z:\QiuShou\mouse_info\191173_info.txt"
#variables 
resultmat = loadmat(resultmat_path)
resultpkl = load_pkl(resultpkl_path)
mouse_info = MouseInfo(mouse_info_path)
behave_info = mouse_info.lick_water
"""
behave_info 
['context_orders', 'context_angles', 'ms_starts', 'behave_dir', 'behave_blocknames']
"""
def saveresult():
    save_pkl(result,resultpkl_path)
#%% resultmat
"""
'in_context_columns',
'in_context_msblocks', 
'in_context_msblocksCaEvent', 
'in_context_behaveblocks', 
'in_context_coords', 
'in_context_behavetrial_columns', 
'in_context_behavetrialblocks', 
'bUpdated', 
'blockname', 
'cellROI'

"""
#%% resultpkl
"""
['mouse_id', 
 'ms_mat_path', 
 'context_orders', 
 'context_angles', 
 'behave_trackfiles', 
 'behave_timestamps', 
 'behave_logfiles',
 'behave_videos',
 'msblocks', 
 'CaEventblocks', 
 'behaveblocks', 
 'logblocks',
 'blocknames',
 'ms_starts', 
 'aligned_behaveblocks',
 'in_context_coords',   ## 储存成pd.DataFrame，便于view, 建议变成np.array再进行计算
 'in_context_msblocks',
 'in_context_CaEventblocks', 
 'in_context_behaveblocks',
 'in_context_behavetrialblocks'] ##提取每个trial主要是为了做shuffle
"""
#%% output
"""
id_CtxAs # Context selectivity for A
id_CtxBs
id_Ctxs
id_HDlefts # Head Direction for left
id_HDrights
id_HDs
id_PCs # place cells

"""
#%%for each block
# average firing rate  
in_context_mean_fr_msblocks = []
for i in resultpkl["in_context_msblocks"]:
    in_context_mean_fr_msblocks.append(i.drop(columns=["ms_ts"]).mean().values)    
in_context_mean_fr_msblocks = pd.DataFrame(in_context_mean_fr_msblocks,index=behave_info["behave_blocknames"],columns=resultpkl["in_context_msblocks"][0].columns.drop("ms_ts"))


in_context_mean_fr_CaEventblocks = []
for i in resultpkl["in_context_CaEventblocks"]:
    in_context_mean_fr_CaEventblocks.append(i.drop(columns=["ms_ts"]).mean().values)
in_context_mean_fr_CaEventblocks = pd.DataFrame(in_context_mean_fr_CaEventblocks,index=behave_info["behave_blocknames"],columns=resultpkl["in_context_CaEventblocks"][0].columns.drop("ms_ts"))


#%% for each trial
# average firing rate
###
for i in range(len(resultpkl["in_context_msblocks"])):
    temp_block = pd.DataFrame(columns=['ms_ts','in_context_trialnum'])
    for num,in_context_trial in enumerate(resultpkl["in_context_behavetrialblocks"][i],1):
        temp_trial = pd.DataFrame(columns=['ms_ts','in_context_trialnum'])
        temp_trial["ms_ts"] = in_context_trial["ms_ts"].astype("int64")
        temp_trial["in_context_trialnum"] = num
        temp_block = temp_block.append(temp_trial).reset_index(drop=True)
        
    resultpkl["in_context_msblocks"][i] = pd.merge(resultpkl["in_context_msblocks"][i],temp_block,on="ms_ts",how="outer")

# for i in (resultpkl["in_context_msblocks"]):
#     del i["in_context_trialnum_x"]
#     del i["in_context_trialnum_y"]
resultpkl["in_context_mean_fr_msblocks_trials"] = [i.groupby("in_context_trialnum",as_index=False).mean() for i in resultpkl["in_context_msblocks"]]

save_pkl(resultpkl,resultpkl_path)

###        



