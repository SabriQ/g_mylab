
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os,sys,glob,re,copy
import scipy.io as spio
import pickle
import itertools
import scipy.stats as stats
from mylab.ana.miniscope.Mplacecells import *
from mylab.ana.miniscope.Mpca import *
from mylab.ana.miniscope.context_exposure.Canamini import AnaMini

#%% for single cell analysis

def cellid_Context(s:AnaMini,*args,**kwargs):
    """
    s.add_Context()
    s.add_Trial_Num_Process()
    s.add_alltrack_placebin_num(placebins=[4,4,30,4,4,4])
    """
    print("FUNC::cellids_Context")
    df,index = s.trim_df(*args,**kwargs)
    df = df[index]


    Trial_Num = s.result["Trial_Num"][index]
    Context= s.result["Context"][index]

    meanfr_df = df.groupby([Trial_Num,Context]).mean()
    ctx_meanfr = meanfr_df.groupby(["Context"]).mean()

    result = {}
    result["meanfr_df"] = meanfr_df
    result["ctx_meanfr"] = ctx_meanfr

    if len(set(Context)) > 1:
        for ctxes in itertools.combinations(set(Context),2):
            a,b = ctxes
            idx_a = meanfr_df.index.get_level_values(level="Context")==a
            idx_b = meanfr_df.index.get_level_values(level="Context")==b
            ctx_pvalue = meanfr_df.apply(func=lambda x: stats.ranksums(x[idx_a],x[idx_b])[1],axis=0)
            CSI = (ctx_meanfr.loc[a,:]-ctx_meanfr.loc[b,:])/(ctx_meanfr.loc[a,:]+ctx_meanfr.loc[b,:])

            ContextA_cells=[]
            ContextB_cells=[]
            non_context_cells=[]

            for cellid,csi, p in zip(ctx_meanfr.columns,CSI,ctx_pvalue):
                if p>=0.05:
                    non_context_cells.append(cellid)
                else:
                    if csi>0:
                        ContextA_cells.append(cellid)
                    elif csi<0:
                        ContextB_cells.append(cellid)
                    else:
                        print("meanfr of cell %s is equal in Context %s and Context %s"%(cellid,a,b))
                        non_context_cells.append(cellid)

            result["ctx%s_%s"%(a,b)]={
            "ctx_pvalue":ctx_pvalue,
            "CSI":CSI,
            "context%s_cells"%a:ContextA_cells,
            "context%s_cells"%b:ContextB_cells,
            "non_context_cells":non_context_cells
            }


    return result

def cellid_RD_incontext(s:AnaMini,*args,**kwargs):
    """
    s.align_behave_ms()
    s.add_Trial_Num_Process()
    s.add_alltrack_placebin_num()
    s.add_Context
    s.add_Body_speed(scale=0.33)
    s.add_running_direction(self,according="Body")
    """
    print("FUNC::cellid_RD_incontext")
    df,index = s.trim_df(*args,**kwargs)
    df = df[index]
    Trial_Num = s.result["Trial_Num"][index]
    Context= s.result["Context"][index]
    in_context_running_direction=s.result["running_direction"][index]

    meanfr_df=df.groupby([Trial_Num,Context,in_context_running_direction]).mean()

    ctx_rd_meanfr=meanfr_df.groupby(["Context","running_direction"]).mean()
    result = {}

    result["meanfr_df"] = meanfr_df
    result["ctx_rd_meanfr"] = ctx_rd_meanfr

    for ctx in set(Context):
        ctx_idx = meanfr_df.index.get_level_values(level="Context")==ctx
        idx_0 = meanfr_df[ctx_idx].index.get_level_values(level="running_direction")==0
        idx_1 = meanfr_df[ctx_idx].index.get_level_values(level="running_direction")==1
        ctx_rd_pvalue = meanfr_df[ctx_idx].apply(func=lambda x: stats.ranksums(x[idx_0],x[idx_1])[1],axis=0)
        ctx_rd_RDSI = (ctx_rd_meanfr.loc[(ctx,0),:]-ctx_rd_meanfr.loc[(ctx,1),:])/(ctx_rd_meanfr.loc[(ctx,0),:]+ctx_rd_meanfr.loc[(ctx,1),:])
        left_cells=[]
        right_cells=[]
        non_rd_cells=[]
        for cellid, p, si in zip(meanfr_df.columns,ctx_rd_pvalue,ctx_rd_RDSI):
            if p>=0.05:
                non_rd_cells.append(cellid)
            else:
                if si > 0:
                    left_cells.append(cellid)
                elif si<0:
                    right_cells.append(cellid)
                else:
                    non_rd_cells.append(cellid)
                    print("meanfr of cell %s is equal in two runnin directions"%cellid)

        result["context_%s"%ctx] = {
        "ctx_rd_pvalue":ctx_rd_pvalue,
        "ctx_rd_RDSI":ctx_rd_RDSI,
        "left_cells":left_cells,
        "right_cells":right_cells,
        "non_rd_cells":non_rd_cells
        }

    return result


def cellid_PC_incontext(s:AnaMini,*args,shuffle_times=1000,**kwargs):
    """
    s.align_behave_ms()
    s.add_Trial_Num_Process()
    s.add_alltrack_placebin_num(according="Head",place_bin_nums=[4,4,30,4,4,4],behavevideo)
    s.add_Body_speed(scale=0.33)
    """
    print("FUNC::cellid_PC_incontext")
    df,index = s.trim_df(*args,**kwargs)
    df=df[index]
    Trial_Num = s.result["Trial_Num"][index]
    Context= s.result["Context"][index]

    in_context_placebin_num = s.result["place_bin_No"][index]


    result = {}
    for ctx in set(Context):
        result["context_%s"%ctx]={
        "observed_SIs":Cal_SIs(df[Context==ctx],in_context_placebin_num[Context==ctx]),
        "shuffle_func":bootstrap_Cal_SIs(df[Context==ctx],in_context_placebin_num[Context==ctx]),
        "shuffle_SIs":[]
        }


    for i in range(shuffle_times):
        sys.stdout.write("%s/%s"%(i+1,shuffle_times))
        sys.stdout.write("\r")
        for ctx in set(Context):
            result["context_%s"%ctx]["shuffle_SIs"].append(result["context_%s"%ctx]["shuffle_func"]().values)
    for ctx in set(Context):
        del result["context_%s"%ctx]["shuffle_func"]
        result["context_%s"%ctx]["shuffle_SIs"] = pd.DataFrame(result["context_%s"%ctx]["shuffle_SIs"],columns=df.columns)
        result["context_%s"%ctx]["zscore"] = (result["context_%s"%ctx]["observed_SIs"]-result["context_%s"%ctx]["shuffle_SIs"].mean())/result["context_%s"%ctx]["shuffle_SIs"].std()
        result["context_%s"%ctx]["place_cells"] = result["context_%s"%ctx]["zscore"][result["context_%s"%ctx]["zscore"]>1.96].index.tolist()

    return result





def SingleCell_MeanFr_in_SingleTrial_along_Placebin(s:AnaMini,*args,**kwargs) :    
    """
    generate a dict contains a matrix of each context
    the structure of matrix is [len(cellids),len(place_bins),len(trials)]

    s.add_Trial_Num_Process()
    s.add_Context()
    s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
    s.add_Body_speed(scale=0.33)

    s.add_behave_forward_context(according="Enter_ctx")
    s.add_behave_choice_side()
    s.add_behave_reward()
    """
    # 添加需要的数据
    
    print("FUNC::SingleCell_MeanFr_in_SingleTrial_along_Placebin")
    df,index = s.trim_df(*args,**kwargs)
    df = df[index]
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

    
    #  meanfr by untrimmed "Trial_Num","Context","place_bin_No"
    # meanfr = df.groupby([s.result["Trial_Num"],s.result["Context"],s.result["place_bin_No"]]).mean()
    meanfr = df.groupby([Trial_Num,Context,place_bin_No]).mean()
    meanfr.index.names = ['Trial_Num', 'Context', 'place_bin_No']

    cellids = s.result["idx_accepted"]
    Context_Matrix_info = {}
    Context_Matrix_info["cellids"] = cellids
    Context_Matrix_info["mouse_id"] = s.result["mouse_id"][0]
    Context_Matrix_info["part"] = s.result["part"][0]
    Context_Matrix_info["index"] = s.result["index"][0]
    Context_Matrix_info["aim"] = s.result["aim"][0]

    Context_Matrix_info["place_bins"] = np.unique(meanfr.index.get_level_values("place_bin_No")) 
    

    ###
    trials =np.unique(meanfr.index.get_level_values("Trial_Num"))
    place_bins = np.unique(meanfr.index.get_level_values("place_bin_No")) 
    matrix = np.full([len(cellids),len(place_bins),len(trials)],np.nan)
    for i,t in enumerate(trials):
        for j,p in enumerate(place_bins):
            try:
                matrix[:,j,i] = meanfr.xs((t,p),level=["Trial_Num","place_bin_No"]).values
            except:
                pass
    Matrix_cellids_placebins_trials=matrix
    Context_Matrix_info["Matrix_cellids_placebins_trials"] = Matrix_cellids_placebins_trials


    Context_Matrix_info["trials"] = {}
    for c in set(Context):
        trials = np.unique(meanfr.xs(c,level="Context").index.get_level_values("Trial_Num"))
        Context_Matrix_info["trials"]["context%s"%c] = list(trials)

    Context_Matrix_info["trials"]["left_right"] = []
    Context_Matrix_info["trials"]["right_right"] = []
    Context_Matrix_info["trials"]["left_wrong"] = []
    Context_Matrix_info["trials"]["right_wrong"]= []
    for i,choice in enumerate(zip(s.result["behave_choice_side"],s.result["behave_reward"]),1):
        if choice == ('left',1):
            Context_Matrix_info["trials"]["left_right"].append(i)
        elif choice == ('left',0):
            Context_Matrix_info["trials"]["left_wrong"].append(i)
        elif choice == ('right',1):
            Context_Matrix_info["trials"]["right_right"].append(i)
        elif choice == ('right',0):
            Context_Matrix_info["trials"]["right_wrong"].append(i)
        else:
            print("unexpected trial type")

    return Context_Matrix_info

def plot_MeanFr_along_Placebin2(Context_Matrix_info,idx,placebins:list=None,save=False,show=True,savedir=None):
    if save:
        filename = "mouse%sid%spart%sindex%saim%s.png"%(Context_Matrix_info["mouse_id"],idx,Context_Matrix_info["part"],Context_Matrix_info["index"],Context_Matrix_info["aim"])
        savepath = os.path.join(savedir,filename)
        if os.path.exists(savepath):
            return 
    Matrix_cellids_placebins_trials = Context_Matrix_info["Matrix_cellids_placebins_trials"]
    trialtypes = Context_Matrix_info["trials"]
    
    if idx in Context_Matrix_info["cellids"]:
        dim1 = np.where(Context_Matrix_info["cellids"]==idx)[0][0]
    else:
        print("Cell %s doesn't exist"%idx)
        return 
    
    
    placebins = Context_Matrix_info["place_bins"] if placebins is None else placebins
    try:
        dim2 = np.array([np.where(Context_Matrix_info["place_bins"]==i)[0][0] for i in placebins])
    except:        
        dim2 = np.array(Context_Matrix_info["place_bins"])
        print("the placebins you specified is out of index:%s"%dim2)
    # print(dim2)    
    spatial_points={
    "nosepoke": np.where(placebins==0),
    "turnover_1": np.where(placebins==3),
    "context_enter": np.where(placebins==7),
    "context_exit": np.where(placebins==37),
    "turnover_2": np.where(placebins==41),
    "choice1": np.where(placebins==45),
    "choice2": np.where(placebins==49),
    "turnover_3": np.where(placebins==57),
    "context_reverse_enter": np.where(placebins==61),
    "context_reverse_exit": np.where(placebins==91),
    "turnover_4": np.where(placebins==95),
    "trial_end": np.where(placebins==99)}
    
    n_type = len(trialtypes)
    fig = plt.figure(figsize=(10,n_type*4),dpi=300)
    plt.rc('font',family='Times New Roman')
    
    for i,trialtype in enumerate(trialtypes.keys(),1):
        # 根据条件去对应type 的trials
        dim3 = np.array(Context_Matrix_info["trials"][trialtype])-1
        if len(dim3)==0:
            continue
        matrix = Matrix_cellids_placebins_trials[dim1,:,:]
        matrix = matrix[dim2,:]
        matrix = matrix[:,dim3] # placebins * trials
        
        #mean 所有的trials
        matrix_mean = np.nanmean(matrix,axis=1) 
        #sem 所有的trials
        matrix_sem = np.nanstd(matrix,axis=1,ddof=1)/np.sqrt(matrix.shape[1]) 
        # matrix_and_mean = np.row_stack((matrix,matrix_mean)) # 在最后一行合并评论值
        
        ## axis =1 每一行的placebins进行 standarization ,每一行是一个trial
        matrix_standarization = np.apply_along_axis(lambda x:(x-np.nanmean(x))/np.nanstd(x,ddof=1)
                                                   ,axis=0
                                                   ,arr=matrix)
        matrix_standarization_mean = np.nanmean(matrix_standarization,axis=1)
        matrix_standarization_sem = np.nanstd(matrix_standarization,axis=1,ddof=1)/np.sqrt(matrix_standarization.shape[1]) 
        
        plt.subplot(n_type+1,2,i*2-1)
        sns.heatmap(matrix_standarization.T)
        # plt.imshow(matrix_standarization.T)
        plt.ylabel("Trials")
        plt.xlabel("Placebins")
        plt.title("mouse:%s-id:%s in %s"%(Context_Matrix_info["mouse_id"],idx,trialtype))
        
        plt.subplot(n_type+1,2,i*2)
        plt.plot(matrix_standarization_mean,color="blue",linestyle="--")
        plt.fill_between(np.arange(0,len(matrix_mean))
                         ,matrix_standarization_mean-matrix_standarization_sem
                         ,matrix_standarization_mean+matrix_standarization_sem
                        ,color="blue"
                        ,alpha=0.3
                        ,edgecolor="white")
        # plt.plot(matrix_mean,color="blue",linestyle="--")
        # plt.fill_between(np.arange(0,len(matrix_mean))
        #                  ,matrix_mean-matrix_sem
        #                  ,matrix_mean+matrix_sem
        #                 ,color="blue"
        #                 ,alpha=0.3
        #                 ,edgecolor="white")

        for point in spatial_points.keys():
            try:
                if "choice" in point:
                    color = "red"
                elif "turn" in point:
                    color = "green"
                elif "context" in point:
                    color = "orange"
                else:
                    color = "black"
                plt.axvline(spatial_points[point][0][0],color=color,linestyle="--")
            except:
                pass
        plt.ylabel("Z-score(MeanFr)")
        plt.xlabel("Placebins")
        plt.title("mouse:%s-id:%s in %s"%(Context_Matrix_info["mouse_id"],idx,trialtype))
        plt.tight_layout()
    if save:
        if savedir is None:
            savedir = os.getcwd()
        filename = "mouse%sid%spart%sindex%saim%s.png"%(Context_Matrix_info["mouse_id"],idx,Context_Matrix_info["part"],Context_Matrix_info["index"],Context_Matrix_info["aim"])
        savepath = os.path.join(savedir,filename)
        plt.savefig(savepath,format="png")
        print("%s is saved"%filename)
    if show:
        plt.show()
    plt.close('all')

def plot_MeanFr_along_Placebin(Context_Matrix_info):    
    """
    is about to discard
    Context_Matrix_info: the output of FUNCTION: SingleCell_MeanFr_in_SingleTrial_along_Placebin
    return two internal functions for plotting place fields or continuous MeanFr along place bins
    """
    
    Matrix_cellids_placebins_trials = Context_Matrix_info["Matrix_cellids_placebins_trials"]    
    
    def plot(idx:list,trialtype,placebins:list=None):
        """
        return an internal funtion 
            that could plot MeanFr in each place bin of each cellid in each context by specify cellid and context
        
        """
        # specified idx and context 
        if idx in Context_Matrix_info["cellids"]:
            dim1 = np.where(Context_Matrix_info["cellids"]==idx)[0][0]
        else:
            print("Cell %s doesn't exist"%idx)
            return 

        dim2 = Context_Matrix_info["place_bins"] if placebins==None else placebins

        if trialtype in Context_Matrix_info["trials"].keys():
            dim3 = np.array(Context_Matrix_info["trials"][trialtype])-1
        else:
            print("trialtype '%s' don't exist"%context)
            return 
        
        # for specifed neuron in specified context, there are row-number of placebin and column-number of trials
        matrix = Matrix_cellids_placebins_trials[dim1,:,dim3] # [cells,placebins,trials]        
        matrix = matrix[:,dim2] # 不能三个同时进行切片操作 # trials * placebins
        matrix_mean = np.nanmean(matrix,axis=0)
        matrix_and_mean = np.row_stack((matrix,matrix_mean))
        ## axis =1 每一行进行 standarization ,每一行是一个trial
        matrix_and_mean_norm = np.apply_along_axis(lambda x:(x-np.nanmean(x))/np.nanstd(x,ddof=1)
            ,axis=1,arr=matrix_and_mean)
        
        
        plt.imshow(matrix_and_mean_norm)
        plt.axhline(y=matrix_and_mean_norm.shape[1]-1.6,color="red",linewidth=0.8,linestyle="--")
        plt.xlabel("Place bins")
        plt.ylabel("Trials")
        plt.title("MeanFr in Context %s"%context)
               
        plt.show()
        
    def plot2(idx):
        """
        return an internal function
            that could plot MeanFr along placebins for each cellid in different contexts
        """
        # specified idx
        if idx in Context_Matrix_info["cellids"]:
            dim1 = np.where(Context_Matrix_info["cellids"]==idx)[0][0]
        else:
            print("Cell %s doesn't exist"%idx)
            return 

        matrix_0 = Matrix_cellids_placebins_trials[0][dim1,:,:] # [placebins,trials]    
        matrix_1 = Matrix_cellids_placebins_trials[1][dim1,:,:] # [placebins,trials]  
        
        matrix_0_mean = np.nanmean(matrix_0,axis=1)
        matrix_1_mean = np.nanmean(matrix_1,axis=1)
        
        matrix_0_sem = np.nanstd(matrix_0,axis=1,ddof=1)/np.sqrt(matrix_0.shape[1])
        matrix_1_sem = np.nanstd(matrix_1,axis=1,ddof=1)/np.sqrt(matrix_1.shape[1])
        

        plt.plot(matrix_0_mean,linestyle="--",color="red")
        plt.plot(matrix_1_mean,linestyle="--",color="green")
        plt.fill_between(x=np.arange(len(matrix_0_mean)),y1=matrix_0_mean-matrix_0_sem,y2=matrix_0_mean+matrix_0_sem,alpha=0.3,color="red")
        plt.fill_between(x=np.arange(len(matrix_1_mean)),y1=matrix_1_mean-matrix_1_sem,y2=matrix_1_mean+matrix_1_sem,alpha=0.3,color="green")
        plt.legend(["Ctx 0","Ctx 1"])
        plt.title("MeanFr in different contexts")
        plt.xlabel("Place bins")
        plt.ylabel("MeanFr (UnNorm.)")
        plt.show()
        
    return plot,plot2

def SingleCell_trace_in_SingleTrial(s:AnaMini,*args,**kwargs):
    """
    generate a dict containing lists of each context in which are dataframe of each trials
    the columns of the dataframe are [ms_ts,Body_speed_angle,idxes...]

    s.add_Trial_Num_Process()
    s.add_Context(context_map=None) # add Contxt as a set of [0,1,2]
    s.add_alltrack_placebin_num(according = "Head",place_bin_nums=[4,4,30,4,4,4],behavevideo=None) # add "place_bin_No"
    s.add_Body_speed(scale=0.33) # Body_speed & Body_speed_angle are ready

    """

    print("FUNC::SingleCell_trace_in_SingleTrial")
    df,index = s.trim_df(*args,**kwargs)
    df = df[index]
    Trial_Num = s.result["Trial_Num"][index]
    Context= s.result["Context"][index]

    # Trials is ready    

    df["Context"] = s.result["Context"]
    df["place_bin_No"] = s.result["place_bin_No"] # used only in screen data in context. actually s.add_is_in_context is alternative way to screen this.
    df["Trial_Num"] = s.result["Trial_Num"]
    df["ms_ts"] = s.result["aligned_behave2ms"]["corrected_ms_ts"]
    df["Body_speed_angle"] = s.result["Body_speed_angle"]

    #screen contexts
    contexts = np.unique(s.result["Context"]) 
    df = df.loc[df["Context"].isin(contexts)]
    print("screen df according to given contexts")

    #screen placebins
    placebins = np.unique(s.result["place_bin_No"]) 
    df = df.loc[df["place_bin_No"].isin(placebins)]
    df.drop(columns="place_bin_No",inplace=True) 
    print("screen df according to given place bins")

    #screen trials
    trials = np.unique(s.result["Trial_Num"]) 
    df = df.loc[df["Trial_Num"].isin(trials)]
    print("screen df according to given tirals")
    

    Context_dataframe_info=dict()
    
    for context in np.unique(df["Context"]):
        if not context==-1:
            Trial_list_info = list()
            context_df = df[df["Context"]==context]
            context_df.drop(columns="Context",inplace=True)
            for trial in np.unique(context_df["Trial_Num"]):
                temp = context_df[context_df["Trial_Num"]==trial]
                temp.drop(columns="Trial_Num",inplace=True)
                Trial_list_info.append(temp) #Besides idxes only "ms_ts" and "Body_speed_angle" left
            Context_dataframe_info["context%s"%context]=Trial_list_info

    return Context_dataframe_info
def plot_trace_with_running_direction(Context_dataframe_info):
    """
    return internal functions for plotting trace of each trial with two colors means two direction
    """
    def plot(idx,context):
        """
        return an inter function
            That could plot trace along each trial which have "ms_ts" and "Body_speed_angle" Besides idxes 
        """

        if context in Context_dataframe_info.keys():
            trials = Context_dataframe_info[context]

        else:
            print("Context %s doesn't exist."%context)
            return 

        trial_lens = len(trials)

        fig,axes = plt.subplots(trial_lens,1
                                ,figsize=(8,0.5*trial_lens)
                                ,subplot_kw = {"xticks":[],"yticks":[]}
                                )

        for i,ax in enumerate(axes):
            if i==0:
                ax.set_title("incontext(placebins) firing rate cellid:%s, context:%s"%(idx,context))
            if i==len(axes)-1:
                ax.set_xlabel("Trial Time(ctx enter > r-ctx_exit)")
            ax.set_ylabel(i+1,rotation=0)
            ax.set_aspect("auto")
            #ax.set_axis_off() 
            ax.spines['top'].set_visible(False)
            #ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            color=["red" if i>90 and i<280 else "green" for i in trials[i]["Body_speed_angle"]]
            ax.scatter(x=trials[i]["ms_ts"]-np.min(trials[i]["ms_ts"]),y=trials[i][idx],c=color,s=1)
        plt.show()


    return plot


            
            


#%% for population analysis


def PCA(s:AnaMini,**kwargs):
    """
    return a fig and x_dr
    """
    s.add_Trial_Num_Process()
    s.add_alltrack_placebin_num()
    s.add_Context()
    s.trim_df("S_dff",placebin = np.arange(0,56))
    index = s.trim_index.all(axis=1)

    sigraw = s.df[index]
    placebins = s.result["place_bin_No"][index]
    context = s.result["Context"][index]
    x = sigraw.groupby([context,placebins]).mean()

    result = pca(x,**kwargs)

    return result

def dPCA(s:AnaMini,**kwargs):
    """
    """
    s.add_Trial_Num_Process()
    del s.result["place_bin_No"]
    s.add_alltrack_placebin_num(according="Body",place_bin_nums=[4,4,30,4,4,4])

    s.trim_df("S_dff")
    index = s.trim_index.all(axis=1)

    df = s.df[index]
    Trial_Num = s.result["Trial_Num"][index]
    placebins = s.result["place_bin_No"][index]

    dpca_matrix = pd.DataFrame(df).groupby([Trial_Num,placebins]).mean()
    try:
        dpca_matrix = dpca_matrix.drop(index=(-1))
        print("Trial -1 was deleted")
    except:
        pass

    s.add_behave_choice_side()
    choice_side = pd.Series([0 if i =="left" else 1 for i in s.result["behave_choice_side"]],name="behave_choice_side")
    s.add_behave_context(according="Enter_ctx")
    context = s.result["behave_context"]


    
    ctx0_choice0_trial = s.result["behavelog_info"]["Trial_Num"][(context==0)&(choice_side==0)]
    ctx0_choice1_trial = s.result["behavelog_info"]["Trial_Num"][(context==0)&(choice_side==1)]

    ctx1_choice0_trial = s.result["behavelog_info"]["Trial_Num"][(context==1)&(choice_side==0)]
    ctx1_choice1_trial = s.result["behavelog_info"]["Trial_Num"][(context==1)&(choice_side==1)]

    # 判断以下变量的size
    # max trial num in each condition(contexts)
    max_Trial_Num = max(ctx0_choice0_trial.shape[0],ctx0_choice1_trial.shape[0],ctx1_choice0_trial.shape[0],ctx1_choice1_trial.shape[0])
    neurons = dpca_matrix.shape[1]
    placebin = len(set(s.result["place_bin_No"]))
    context=2
    decision=2
    print("max_Trial_Num:%s,neurons:%s,context:%s,decision:%s,placebin:%s."%(max_Trial_Num,neurons,context,decision,placebin))
    #构建 空的np.array
    trialR = np.full((max_Trial_Num,neurons,context,decision,placebin),np.nan)
    # 填充矩阵，其中没有值的地方都是np.nan
    for i,trial in enumerate(ctx0_choice0_trial,0):
        temp_trial_matrix = dpca_matrix.loc[trial]
        for p in np.arange(0,placebin):
            try:
                trialR[i,:,0,0,p]=temp_trial_matrix.loc[p]
            except:
                trialR[i,:,0,0,p]=0 # 将np.nan替换为0
        
    for i,trial in enumerate(ctx0_choice1_trial,0):
        temp_trial_matrix = dpca_matrix.loc[trial]
        for p in np.arange(0,placebin):
            try:
                trialR[i,:,0,1,p]=temp_trial_matrix.loc[p]
            except:
                trialR[i,:,0,1,p]=0 # 将np.nan替换为0
                
    for i,trial in enumerate(ctx1_choice0_trial,0):
        temp_trial_matrix = dpca_matrix.loc[trial]
        for p in np.arange(0,placebin):
            try:
                trialR[i,:,1,0,p]=temp_trial_matrix.loc[p]
            except:
                trialR[i,:,1,0,p]=0 # 将np.nan替换为0
                
    for i,trial in enumerate(ctx1_choice1_trial,0):
        temp_trial_matrix = dpca_matrix.loc[trial]
        for p in np.arange(0,placebin):
            try:
                trialR[i,:,1,1,p]=temp_trial_matrix.loc[p]
            except:
                trialR[i,:,1,1,p]=0 # 将np.nan替换为0

    #先求没有np.nan的均值，然后再将np.nan替换为0
    R = np.nanmean(trialR,axis=0)
    # trialR[np.isnan(trialR)]=0

    result = demixed_pca(R,trialR,**kwargs)

    return result


#%% for behavioral analysis

def behave_stat_info(s:AnaMini,):
    """
    计算每一个test or train session的行为学相关参数
    """

    stat_info = {}
    s.add_behave_choice_side()
    Choice_side = s.result["behave_choice_side"]
    s.add_behave_forward_context(according="Enter_ctx")
    Context  = s.result["behave_forward_context"]

    stat_info["date"] = s.result["index"][0]
    stat_info["mouse_id"] = s.result["mouse_id"][0]
    stat_info["aim"] = s.result["aim"][0]
    stat_info["Trial_Num"] = s.result["behavelog_info"].shape[0]


    Left_choice = s.result["behavelog_info"]["Left_choice"]
    Right_choice = s.result["behavelog_info"]["Right_choice"]
    Choice_class = s.result["behavelog_info"]["Choice_class"]
    forward_context = s.result["behave_forward_context"]

    stat_info["bias"] =  (max(Left_choice)-max(Right_choice))/(max(Left_choice)+max(Right_choice))
    stat_info["Total_Accuracy"] = sum(Choice_class)/len(Choice_class)
    try:
        stat_info["Left_Accuracy"] = sum(Choice_class[Choice_side=="left"])/len(Choice_class[Choice_side=="left"])
    except:
        stat_info["Left_Accuracy"] = None
    try:
        stat_info["Right_Accuracy"] = sum(Choice_class[Choice_side=="right"])/len(Choice_class[Choice_side=="right"])
    except:
        stat_info["Right_Accuracy"] = None

    for ctx in set(Context):
        try:
            stat_info["ctx_%s_Accuracy"%ctx]= sum(Choice_class[Context==ctx])/len(Choice_class[Context==ctx])
        except:
            stat_info["ctx_%s_Accuracy"%ctx]= None

    return stat_info

def behave_logistic_regression(s:AnaMini,):
    pass
    
#%% SVM decoding for single neuron with Bayesian optimization


#%% which is about to discard

