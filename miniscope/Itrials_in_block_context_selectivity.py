# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:21:08 2019

@author: Sabri
"""

#%%
from mylab.miniscope.Mfunctions import *
from mylab.miniscope.Mplot import *
from mylab.miniscope.Mcontext_selectivity import *


#%%
if __name__ == "__main__":

#    result_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all.pkl"
    result_path = r"C:\Users\Sabri\Desktop\program\data\miniscope\processed_191172_20191110_160835_all.pkl"
    result = load_result(result_path)
    view_variable_structure(result)
    #%% parameter to extract
    aligned_behaveblocks = result["aligned_behaveblocks"]
    contextcoords = result["contextcoords"]
    blocknames = result["blocknames"]
    in_context_msblocks = result["in_context_msblocks"]
##%%
#    def traverse(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
#        for aligned_behaveblock,contextcoord,in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
#            yield [aligned_behaveblock,contextcoord,in_context_msblock,blockname]
    

    for i in range(531):
        if i==0:
            for aligned_behaveblock,contextcoord,in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
#                trial_BodyXs_block,trial_BodyXspeeds_block,trial_traces_block = Extract_trials2(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No=i,title = blockname,column="in_context")
                Extract_trials2(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No=i,title = blockname,column="in_context")
        
#    for aligned_behaveblock,contextcoord,in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
#        trial_blocks = Extract_trials(aligned_behaveblock,contextcoord,in_context_msblock,neuron_No=i,title = blockname,column="in_context")
    #%% output result["in_context_behavetrialblocks"]
    in_context_behavetrialblocks = []
    for aligned_behaveblock,contextcoord, in_context_msblock,blockname in zip(aligned_behaveblocks,contextcoords,in_context_msblocks,blocknames):
        in_context_behavetrialblock = Extract_trials(aligned_behaveblock,contextcoord,in_context_msblock,title = blockname,column="in_context")
        in_context_behavetrialblocks.append(in_context_behavetrialblock)
    result["in_context_behavetrialblocks"] = in_context_behavetrialblocks    
    #%% in_context_trialblocks, there are 12 blocks. In each block, the number of trials is different
    in_context_context_selectivities_trialblocks=[]
    for in_context_trialblock, in_context_msblock,blockname in zip(in_context_trialblocks,in_context_msblocks,blocknames):
        in_context_context_selectivities_trialblocks.append(generete_context_selectivities_trials(in_context_trialblock,in_context_msblock,blockname))
    result["results"]["in_context_context_selectivities_trialblocks"]=in_context_context_selectivities_trialblocks
    #%% save
    view_variable_structure(result)
    save_result(result,result_path)  