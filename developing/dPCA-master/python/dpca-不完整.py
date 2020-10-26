dpca_matrix = pd.DataFrame(s.result["S_dff"]).groupby([s.result["Trial_Num"],s.result["place_bin_No"]]).mean()
dpca_matrix = dpca_matrix.drop(index=(-1))
dpca_matrix

context = s.result["behavelog_info"]["Enter_ctx"]
decision = s.result["behavelog_info"]["choice_side"]
ctx0_decision0_trial = s.result["behavelog_info"]["Trial_Num"][(context==0)&(decision==0)]
ctx0_decision1_trial = s.result["behavelog_info"]["Trial_Num"][(context==0)&(decision==1)]
ctx1_decision0_trial = s.result["behavelog_info"]["Trial_Num"][(context==1)&(decision==0)]
ctx1_decision1_trial = s.result["behavelog_info"]["Trial_Num"][(context==1)&(decision==1)]


# 判断以下变量的size
max_Trial_Num = max(ctx0_decision0_trial.shape[0],ctx0_decision1_trial.shape[0]
     ,ctx1_decision0_trial.shape[0] ,ctx1_decision1_trial.shape[0])# 这个Trial_Num应该是每单个（Trial_Num,feature1,featurn2,...）组合的最大值
neurons = dpca_matrix.shape[1]
placebin = len(set(s.result["place_bin_No"]))
context = len(set(context))
decision = len(set(decision))
print(max_Trial_Num,neurons,place_bin,context,decision)

#构建 空的np.array
trialR = np.full((max_Trial_Num,neurons,placebin,context,decision),np.nan)
trialR.shape

for i,trial in enumerate(ctx0_decision0_trial,0):
    temp_trial_matrix = dpca_matrix.loc[trial]
#     print(temp_trial_matrix.shape,trialR[i,:,temp_trial_matrix.index,0,0].shape)
    trialR[i,:,temp_trial_matrix.index,0,0]=temp_trial_matrix
    
for i,trial in enumerate(ctx0_decision1_trial,0):
    temp_trial_matrix = dpca_matrix.loc[trial]
#     print(temp_trial_matrix.shape,trialR[i,:,temp_trial_matrix.index,0,1].shape)
    trialR[i,:,temp_trial_matrix.index,0,1]=temp_trial_matrix
    
for i,trial in enumerate(ctx1_decision0_trial,0):
    temp_trial_matrix = dpca_matrix.loc[trial]
#     print(temp_trial_matrix.shape,trialR[i,:,temp_trial_matrix.index,1,0].shape)
    trialR[i,:,temp_trial_matrix.index,1,0]=temp_trial_matrix
    
for i,trial in enumerate(ctx1_decision1_trial,0):
    temp_trial_matrix = dpca_matrix.loc[trial]
#     print(temp_trial_matrix.shape,trialR[i,:,temp_trial_matrix.index,1,1].shape)
    trialR[i,:,temp_trial_matrix.index,1,1]=temp_trial_matrix


from dPCA import dPCA
dpca = dPCA.dPCA(labels='pcd',regularizer='auto') 
dpca.protect = ['p']

Z = dpca.fit_transform(R,trialR)