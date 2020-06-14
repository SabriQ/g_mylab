from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
from mylab.Cmouseinfo import MouseInfo
from mylab.ana.linear_track.Cminiana import MiniAna as MA
from mylab.ana.Mfunctions import *
import os,sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

class MiniLWAna(MA):
    """
    主要针对第一批实验往返舔水，手动每个session 更换context的实验，mouse_id :

    """
    def __init__(self,mouse_info_path,cnmf_result_dir):
        super().__init__(mouse_info_path,cnmf_result_dir)
        # self.mouse_info = self.mouse_info.lick_water
    @property
    def Idx__ContextCells(self):
        """
        在 self.calculate_in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock() 的结果中计算 （in_context） 每个cell在不同context的平均发放率，并做rank sum test。
        返回分别以all block 和 each block为基础的context cell idxes
        """
        if "idx_ContextCells" in self.keys:
            return self.ana_result["idx_ContextCells"]
        else:
            print("calculating ...")
            return  self.idx_ContextCells()
    
    def _add_in_context2aligned2ms_behavesessions(self):
        #aligned2ms_behavesessions增加“in_context”
        if not "in_context" in self.ana_result["aligned2ms_behavesessions"][0].columns:
            new_aligned2ms_behavesessions = []
            for aligned2ms_behavesession,in_context_contextcoord in zip(self.ana_result["aligned2ms_behavesessions"],self.ana_result["in_context_contextcoords"]):
                masks =in_context_contextcoord[0][0]
                in_context = []
                for x,y in zip(aligned2ms_behavesession['Body_x'],aligned2ms_behavesession['Body_y']):
                    if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                        in_context.append(0)
                    else:
                        in_context.append(1)
                aligned2ms_behavesession['in_context'] = in_context
                new_aligned2ms_behavesessions.append(aligned2ms_behavesession)
            self.update("aligned2ms_behavesessions", new_aligned2ms_behavesessions)
            del new_aligned2ms_behavesessions
            print("add condition 'in_context' in aligned2ms_behavesessions")
        else:
            print("'in_context' is already in aligned2ms_behavesessions")


    def _add_in_context_trialnum2aligaligned2ms_behavesessions(self):
        #aligned2ms_behavesessions增加"in_context_trialnum"
        if not "in_context_trialnum" in self.ana_result["aligned2ms_behavesessions"][0].columns:
            new_aligned2ms_behavesessions=[]
            for aligned2ms_behavesession, in_context_contextcoord in zip(self.ana_result["aligned2ms_behavesessions"],self.ana_result["in_context_contextcoords"]):
                df = rlc2(aligned2ms_behavesession['in_context'])
                
                Cx_max = max(in_context_contextcoord[1][0][:,0])
                Cx_min = min(in_context_contextcoord[1][0][:,0])

                trial_num= 1
                temp_session=pd.DataFrame(columns=["in_context_trialnum","ms_ts"])                
                for index,row in df.iterrows():
                    if row['name'] == 1 and row['idx_min']<row['idx_max']:
                        Bx = aligned2ms_behavesession["Body_x"][row['idx_min']:row['idx_max']]
                        Bx_max=max(Bx)
                        Bx_min=min(Bx)
                        if (Bx_max-Bx_min)>0.5*(Cx_max-Cx_min):#轨迹要大于一半的context长度
                            temp_behavetrial = aligned2ms_behavesession.iloc[row['idx_min']:row['idx_max']]
                            temp_trial = pd.DataFrame(columns=["in_context_trialnum","ms_ts"])
                            temp_trial["ms_ts"]=temp_behavetrial["ms_ts"]
                            temp_trial["in_context_trialnum"] = trial_num
                            temp_session = temp_session.append(temp_trial)
                            
                            trial_num = trial_num+1
                # print(temp_session)
                aligned2ms_behavesession = pd.merge(aligned2ms_behavesession,temp_session,on="ms_ts",how="outer")
                # print(aligned2ms_behavesession.iloc[temp_session.index])
                new_aligned2ms_behavesessions.append(aligned2ms_behavesession)
                
            self.update(key="aligned2ms_behavesessions",value=new_aligned2ms_behavesessions)
            del new_aligned2ms_behavesessions
            print("add condition 'in_context_trialnum' in aligned2ms_behavesessions")
        else:
            print("'in_context_trialnum' is already in aligned2ms_behavesessions")


    def _add_in_context_placebin_num2aligned2ms_behavesessions(self):
        #aligned2ms_behavesessions增加"in_context_placebin_num"
        if not "in_context_placebin_num" in self.ana_result["aligned2ms_behavesessions"][0].columns:
            new_aligned2ms_behavesessions = []
            for aligned2ms_behavesession,in_context_contextcoord in zip(self.ana_result["aligned2ms_behavesessions"],self.ana_result["in_context_contextcoords"]):
                Cx_max = max(in_context_contextcoord[1][0][:,0])
                Cx_min = min(in_context_contextcoord[1][0][:,0])
                placebin_number = 10
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                
                for in_context,x in zip(aligned2ms_behavesession['in_context'],aligned2ms_behavesession['Body_x']):
                    if not in_context:
                        in_context_placebin_num.append(0)
                    else:   
                        temp = []
                        for i in range(placebin_number):
                            if not i == placebin_number-1:
                                if x>=placebins[i][0] and x<placebins[i][1]:
                                    temp.append(i+1)
                                else:
                                    temp.append(0)
                            else:
                                if x>=placebins[i][0] and x<=placebins[i][1]:
                                    temp.append(i+1)
                                else:
                                    temp.append(0)

                                # print("小鼠刚好在第%s个placebin的右边界处，特此提醒"%placebin_number)
                        in_context_placebin_num.append(sum(temp))
                        
                aligned2ms_behavesession["in_context_placebin_num"] = in_context_placebin_num
                new_aligned2ms_behavesessions.append(aligned2ms_behavesession)
            self.update(key="aligned2ms_behavesessions",value=new_aligned2ms_behavesessions)
            del new_aligned2ms_behavesessions
            print("add condition 'in_context_placebin_num' in aligned2ms_behavesessions")
        else:
            print("'in_context_placebin_num' is already in aligned2ms_behavesessions")


    def select_in_context(self):
        #in_context_contextcoords            
        if not "in_context_contextcoords" in self.keys:
            in_context_contextcoords=[]
            for video in self.mouse_info.lick_water["behave_videos"]:
                if os.path.exists(video):
                    # print(os.path.basename(video),end=': ')
                    masks,coords = Video(video).draw_rois(aim="in_context",count=1)
                    in_context_contextcoords.append((masks,coords))
                else:
                    print("%s 盘符不对"%video)
                    sys.exit()
            self.add(key="in_context_contextcoords",value=in_context_contextcoords)

        else:
            print("'in_context_contextcoords' is already in mouse_info")
            
        self._add_in_context2aligned2ms_behavesessions()
        self._add_in_context_placebin_num2aligned2ms_behavesessions()
        self._add_in_context_trialnum2aligaligned2ms_behavesessions()
        self.save


    def generate_in_context_mssessionsAbehavesessions(self):
        """
        condition: in_context
        return: in_context_mssessions, in_context_behavesessions
        """
        in_context_mssessions=[]
        in_context_behavesessions=[]

        for mssession, aligned2ms_behavesession in zip(self.ana_result["mssessions"],self.ana_result["aligned2ms_behavesessions"]):
            in_context = aligned2ms_behavesession['in_context']

            in_context_mssession = mssession.iloc[(in_context==1).values]
            in_context_behavesession=aligned2ms_behavesession.iloc[(in_context==1).values]

            in_context_mssessions.append(in_context_mssession)
            in_context_behavesessions.append(in_context_behavesession)
        return in_context_mssessions,in_context_behavesessions

    def calculate_in_context_MeanFr_mssessions(self):
        """
        condition: each session, in_context
        计算 每个神经元在“in_context”的平均发放率MeanFr for each session 
        return in_context_MeanFr_mssessions
        """
        in_context_mssessions,_ = self.generate_in_context_mssessionsAbehavesessions()
        temp = [i.drop(columns=["ms_ts"]).mean().values for i in in_context_mssessions]
        in_context_MeanFr_mssessions = pd.DataFrame(temp,columns=in_context_mssessions[0].columns.drop("ms_ts"))
        return in_context_MeanFr_mssessions


    def calculate_in_context_LoRAtrialnum_MeanFr_mssessions(self):
        """
        condition 
        结果是每一个trial的MeanFr,同时含有每一个Trial是left还是的信息‘in_context_LoRsLoRs’
        """
        in_context_LoRAtrialnum_MeanFr_mssessions=[]
        in_context_mssessions,_ = self.generate_in_context_mssessionsAbehavesessions()

        for in_context_mssession,aligned2ms_behavesession in zip(in_context_mssessions,self.ana_result["aligned2ms_behavesessions"]):
            # 根据Body_x和时间的线性拟合斜率来判断小鼠往左还是往右
            LoRs = []
            for in_context_trialnum in pd.unique(aligned2ms_behavesession["in_context_trialnum"].dropna()):
                x= aligned2ms_behavesession[aligned2ms_behavesession["in_context_trialnum"]==in_context_trialnum]["ms_ts"]
                y = aligned2ms_behavesession[aligned2ms_behavesession["in_context_trialnum"]==in_context_trialnum]["Body_x"]
                k = np.polyfit(x.tolist(),y.tolist(),1)[0] #做线性拟合取斜率，判断小鼠往左还是往右
                if k>0:
                    LoRs.append("right")
                else:
                    LoRs.append("left")
                    
            in_context_trialnum_mssession = pd.merge(in_context_mssession,aligned2ms_behavesession[['in_context_trialnum','ms_ts']],on="ms_ts",how="inner")            
            
            in_context_LoRAtrialnum_MeanFr_mssession = in_context_trialnum_mssession.groupby("in_context_trialnum",as_index=False).mean()
            in_context_LoRAtrialnum_MeanFr_mssession["in_context_LoRs"] = LoRs
            in_context_LoRAtrialnum_MeanFr_mssessions.append(in_context_LoRAtrialnum_MeanFr_mssession)
        return in_context_LoRAtrialnum_MeanFr_mssessions

    def calculate_in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock(self):
        """
        增加了block_num
        firing rate is normalized by block, each block in exp 'lick water' has 2 continuous sessions
        如果某个session中，某个神经元的发放一直为0，那么Normalization之后可能赋值为NaNs
        """
        in_context_LoRAtrialnum_MeanFr_mssessions = self.calculate_in_context_LoRAtrialnum_MeanFr_mssessions()
        block_nums = self.mouse_info.lick_water["block_nums"]
        context_orders = self.mouse_info.lick_water["context_orders"]
        context_angles = self.mouse_info.lick_water["context_angles"]
        for block_num,context_order,context_angle,in_context_LoRAtrialnum_MeanFr_mssession in zip(block_nums,context_orders,context_angles,in_context_LoRAtrialnum_MeanFr_mssessions):
            in_context_LoRAtrialnum_MeanFr_mssession["context_order"]=context_order
            in_context_LoRAtrialnum_MeanFr_mssession["context_angle"]=context_angle
            in_context_LoRAtrialnum_MeanFr_mssession["block_num"]=block_num

        temp_blocks = pd.concat(in_context_LoRAtrialnum_MeanFr_mssessions)
        #对block_num相等的sessions 进行normalization
        temp_blocks2Normals=[]
        for block_num in set(block_nums):
            temp_blocks2Normal = temp_blocks.loc[temp_blocks["block_num"]==block_num][self.neuron_ids]
            # 注意，这里的Normalize_df 有可能会产生NaNs
            temp_blocks2Normal = Normalize_df(temp_blocks2Normal)
            temp_blocks2Normals.append(temp_blocks2Normal)

        temp_blocks[self.neuron_ids]=pd.concat(temp_blocks2Normals)
        in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock = temp_blocks
        return in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock

    def calculate_in_context_placebin_num_MeanFr_mssessions(self):
        #产生in_context_mssessions_placebins,in_context_behavesessions_placebins
        #计算 in_context_MeanFr_mssessions_placebins,in_context_MeanBehave_mssessions_placebins
        in_context_placebin_num_MeanFr_mssessions=[]
        in_context_mssessions,_ = self.generate_in_context_mssessionsAbehavesessions()
        for in_context_mssession,aligned2ms_behavesession in zip(in_context_mssessions,self.ana_result["aligned2ms_behavesessions"]):
            in_context_placebin_num_mssession = pd.merge(in_context_mssession,aligned2ms_behavesession[['in_context_placebin_num','ms_ts']],on="ms_ts",how="outer")
            in_context_placebin_num_MeanFr_mssession = in_context_placebin_num_mssession.groupby(["in_context_placebin_num"],as_index=False).mean().dropna().drop(columns=["ms_ts"])
            in_context_placebin_num_MeanFr_mssessions.append(in_context_placebin_num_MeanFr_mssession)
        return in_context_placebin_num_MeanFr_mssessions


    def gf_eachneuron_Fig_in_context_MeanFr_each_session_each_trial(self):
        """
        闭包，产生一个根据neuron_id来分别产生对应neuron的图
        subplot 121
        横坐标是每个session,纵坐标是Fr
        每个点表示每个session中每个trial的平均发放
        subplot 122
        横坐标是四个context,纵坐标是Fr
        每个点同上
        """
        in_context_LoRAtrialnum_MeanFr_mssessions = self.calculate_in_context_LoRAtrialnum_MeanFr_mssessions()
        # neuron_ids = in_context_LoRAtrialnum_MeanFr_mssessions[0].columns.drop(["in_context_trialnum","in_context_LoRs"])
        context_orders = self.mouse_info.lick_water["context_orders"]

        def Fig_in_context_MeanFr_each_session_each_trial(neuron_id):
            plt.figure(figsize=(10,5))
            plt.subplot(1,2,1)
            plt.title("%s-each_session-each_trial MeanFr"%neuron_id)
            for i,context in enumerate(context_orders,1):
                try:
                    sns.regplot(x=[i]*len(in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id]),y=in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id],fit_reg = False,x_jitter = 0.2, scatter_kws = {'alpha' : 1/3})
                except:
                    print("neuron_id %s is not exist"%neuron_id)
                    break
            plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12],context_orders)
            plt.xlabel("context orders")
            plt.ylabel("MeaFr/trial")

            plt.subplot(1,2,2)
            plt.title("%s-each_trial MeanFr in diff_contexts"%neuron_id)
            for context in context_orders:
                if context == "A":
                    sns.regplot(x=[1]*len(in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id]),y=in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id],fit_reg = False,x_jitter = 0.2, scatter_kws = {'alpha' : 1/3})
                elif context == "B":
                    sns.regplot(x=[2]*len(in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id]),y=in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id],fit_reg = False,x_jitter = 0.2, scatter_kws = {'alpha' : 1/3})
                elif context == "A1":
                    sns.regplot(x=[3]*len(in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id]),y=in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id],fit_reg = False,x_jitter = 0.2, scatter_kws = {'alpha' : 1/3})
                elif context == "B1":
                    sns.regplot(x=[4]*len(in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id]),y=in_context_LoRAtrialnum_MeanFr_mssessions[i-1][neuron_id],fit_reg = False,x_jitter = 0.2, scatter_kws = {'alpha' : 1/3})
                else:
                    pass
            plt.xticks([1,2,3,4],["A","B","A1","B1"])
            plt.xlabel("contexts")
            plt.ylabel("MeaFr/trial")
            plt.show()

        return Fig_MeanFr_each_session_each_trial

    def idx_ContextCells(self):
        """
        输出 allblocks (idx_ContextACells,idx_ContextBCells,idx_Cells_no_firing);eachblock (idx_ContextACells,idx_ContextBCells,idx_Cells_disappear)
        有可能会报"NaNs"的错误
        """
        in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock = self.calculate_in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock()
        #按列dropna 是否需要？ 在某个block不反应起始也符合预期
        temp = in_context_LoRAtrialnum_MeanFr_mssession_NormalizedByBlock.set_index(["context_angle","context_order","in_context_trialnum","block_num"]) #.dropna(axis=1)
        #将NaN都换成0
        # temp =temp.fillna(0)
        #提取全部的contextA或者contextB中的trial，
        temp_ctxA_allblocks = temp.xs(("A"),level=("context_order"))
        temp_ctxB_allblocks = temp.xs(("B"),level=("context_order"))


        idx_ContextCells_tempallblocks=[]
        neuron_ids = [i for i in temp_ctxA_allblocks.columns.intersection(temp_ctxB_allblocks.columns) if i in self.neuron_ids]
        for neuron_id in neuron_ids:   
            ranksumtest = Wilcoxon_unpaired_ranksumstest(temp_ctxA_allblocks[neuron_id],temp_ctxB_allblocks[neuron_id])
            if ranksumtest[1]<0.05:
                try:
                    csi = ContextSelectivityIndex(np.mean(temp_ctxA_allblocks[neuron_id]),np.mean(temp_ctxB_allblocks[neuron_id]))
                except:
                    csi=0
                if csi < 0:
                    idx_ContextCells_tempallblocks.append(("A",neuron_id,ranksumtest[1],csi))
                elif csi>0:
                    idx_ContextCells_tempallblocks.append(("B",neuron_id,ranksumtest[1],csi))
                else:
                    idx_ContextCells_tempallblocks.append(("Null",neuron_id,0,csi))
        # print(idx_ContextCells_tempallblocks)
        idx_ContextACells_allblocks = [i[1] for i in idx_ContextCells_tempallblocks if i[3]>0]
        idx_ContextBCells_allblocks = [i[1] for i in idx_ContextCells_tempallblocks if i[3]<0]
        idx_Cells_no_firing = [i[1] for i in idx_ContextCells_tempallblocks if "Null" in i]
        # print(idx_ContextACells_allblocks)
        # print(idx_ContextBCells_allblocks)
        # print(idx_ContextACells_allblocks+idx_ContextBCells_allblocks)

        # 提取第i个block的contextA或者ContextB中的trials
        idx_ContextCells_eachblock={}
        for block_num in set(self.mouse_info.lick_water["block_nums"]):
            print("-----%s block-----"%block_num  )  
            try:
                temp_ctxA_tempblock = temp.xs((block_num,"A"),level=("block_num","context_order"))
                temp_ctxB_tempblock = temp.xs((block_num,"B"),level=("block_num","context_order"))
                if len(temp_ctxA_tempblock)==0:
                    temp_ctxA_tempblock = temp.xs((block_num,"A1"),level=("block_num","context_order"))
                if len(temp_ctxB_tempblock)==0:
                    temp_ctxB_tempblock = temp.xs((block_num,"B1"),level=("block_num","context_order"))
            except:
                print("index according to block_num and context_order wrong")

            idx_ContextCells_tempblock=[]
            neuron_ids = [i for i in temp_ctxA_tempblock.columns.intersection(temp_ctxB_tempblock.columns) if i in self.neuron_ids]
            for neuron_id in neuron_ids:   
                ranksumtest = Wilcoxon_unpaired_ranksumstest(temp_ctxA_tempblock[neuron_id],temp_ctxB_tempblock[neuron_id])
                if ranksumtest[1]<0.05:
                    try:
                        csi = ContextSelectivityIndex(np.mean(temp_ctxA_tempblock[neuron_id]),np.mean(temp_ctxB_tempblock[neuron_id]))
                    except:
                        print("分母为0")
                        csi=0
                    if csi < 0:
                        idx_ContextCells_tempblock.append(("A",neuron_id,ranksumtest[1],csi))
                    elif csi>0:
                        idx_ContextCells_tempblock.append(("B",neuron_id,ranksumtest[1],csi))
                    else:
                        idx_ContextCells_tempblock.append(("Null",neuron_id,0,csi))

            idx_ContextACells = [i[1] for i in idx_ContextCells_tempblock if i[3]>0]
            idx_ContextBCells = [i[1] for i in idx_ContextCells_tempblock if i[3]<0]
            idx_Cells_disappear =  [i[1] for i in idx_ContextCells_tempblock if "Null" in i]
            idx_ContextCells_eachblock[block_num]={"idx_ContextACells":idx_ContextACells,"idx_ContextBCells":idx_ContextBCells,"idx_Cells_disappear":idx_Cells_disappear}

        
        value = {"idx_ContextCells_allblocks":{"idx_ContextACells_allblocks":idx_ContextACells_allblocks,"idx_ContextBCells_allblocks":idx_ContextBCells_allblocks,"idx_Cells_no_firing":idx_Cells_no_firing},
            "idx_ContextCells_eachblock":idx_ContextCells_eachblock}

        if "idx_ContextCells" not in self.keys:
            self.add(key="idx_ContextCells",value= value)
        else:
            self.update(key="idx_ContextCells",value= value)

        self.save
        return value

    @staticmethod
    def _generate_bin_num(N_trials,length):
        num = int(np.trunc(length/N_trials))
        last_num = length%N_trials
        bin_num = []
        for i in range(num):
            bin_num = bin_num + [i]*num
        if last_num:
            bin_num = bin_num + [i+1]*last_num
        return bin_num

    def gf_neuronids_Fig_in_context_MeanFr_Each_N_Trials_in_session(self): 

        in_context_LoRAtrialnum_MeanFr_mssessions = self.calculate_in_context_LoRAtrialnum_MeanFr_mssessions().set_index(["block_num","context_order"])
        # neuron_ids = in_context_LoRAtrialnum_MeanFr_mssessions[0].columns.drop(["in_context_trialnum","in_context_LoRs"])
        context_orders = self.mouse_info.lick_water["context_orders"]

        def Fig_in_context_MeanFr_Each_N_Trials_in_session(neuron_ids,N_trials,block_num,context_order):
            temp = in_context_LoRAtrialnum_MeanFr_mssessions.xs((block_num,context_order),level=("block_num,context_order"))[neuron_ids]
            temp["temp_bin_num"] = self._generate_bin_num(N_trials,temp.shape()[0])
            temp = temp.groupby(["temp_bin_num"]).mean() #每个neuronid 每N_trials 的平均发放率
            x = list(temp.index)
            y_mean = temp.mean(axis=1)
            y_std = temp.std(axis=1)
            plt.scatter(x,y_mean,color='black')
            sns.regplot(list(x),y_mean.values)

        return Fig_in_context_MeanFr_Each_N_Trials_in_session

    def GoDirectionCell_idxes(self):
        pass
    def ContextDirectionCell_idxes(self):
        """
        """
        pass

    def PlaceCell_idxes(self):
        """
        """
        pass

    def Fig_in_context_CSI_MeanFr_mssessions(self):
        in_context_MeanFr_mssessions = self.calculate_in_context_MeanFr_mssessions()
        
        in_context_MeanFr_mssessions["context_orders"] = self.mouse_info.lick_water["context_orders"]
        in_context_MeanFr_mssessions["context_angles"] = self.mouse_info.lick_water["context_angles"]

        #对所有角度的CSI
        FR_allangles = in_context_MeanFr_mssessions.groupby(["context_orders"]).mean()
        FR_differentangles = in_context_MeanFr_mssessions.groupby(["context_orders","context_angles"]).mean()
        
        CSI_allangles = (FR_allangles.loc["A"]-FR_allangles.loc["B"])/(FR_allangles.loc["A"]+FR_allangles.loc["B"])
        CSI_changedfloor = (FR_allangles.loc["A1"]-FR_allangles.loc["B1"])/(FR_allangles.loc["A1"]+FR_allangles.loc["B1"])
    
        CSI_allangles_CtxA = CSI_allangles[CSI_allangles>0]
        CSI_allangles_CtxB = CSI_allangles[CSI_allangles<0] 
        in_context_id_CtxA_by_CSI_allangles_bysessions = CSI_allangles_CtxA.index
        in_context_id_CtxB_by_CSI_allangles_bysessions = CSI_allangles_CtxB.index   
        
        #all angles
        ## Fig 1
        ## CSI-neuron_id
        plt.figure() 
        plt.subplot(121)
        plt.scatter(CSI_allangles_CtxA.index,CSI_allangles_CtxA,c="red")
        plt.scatter(CSI_allangles_CtxB.index,CSI_allangles_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.title("In_context_CSI_bysessions-all_angles")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")        
        ## CSI-paired_ctx
        plt.subplot(122)
        paired_AB   = [(1,i,"red") if i>0 else (1,i,"green") for i in CSI_allangles]
        color = [i[2] for i in paired_AB]
        paired_A1B1 = [(2,i) for i in CSI_changedfloor]
        plt.scatter([i[0] for i in paired_AB],[i[1] for i in paired_AB],c=color,s=4)
        plt.scatter([i[0] for i in paired_A1B1],[i[1] for i in paired_A1B1],c=color,s=4)
        for ab, a1b1 in zip(paired_AB,paired_A1B1):
            x = [ab[0],a1b1[0]]
            y = [ab[1],a1b1[1]]
            if np.isnan(y).any():
                continue # 如果两个中有任何一个csi 为零说明，细胞在这个pair 中应该没有信号，因此丢弃
            if y[0]*y[1] > 0:
                plt.plot(x,y,'--',color="black")
            else:
                plt.plot(x,y,'--',color="orange")   
        plt.xticks([1,2],["A/B","A1/B1"])
        plt.xlim([0.5,2.5])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.title("CSI-change when floor changed")
        plt.xlabel("paired_context")
        plt.ylabel("CSI")
        
        ## 所有的细胞 在不同angle上的分布,根据 MeanFr 画出热图
        ## Figure 2
        ##归一化 FR所占百分比
        CtxA_all_cells  = FR_differentangles.loc["A"]/FR_differentangles.groupby(["context_orders"]).sum().loc["A"]
        CtxB_all_cells  = FR_differentangles.loc["B"]/FR_differentangles.groupby(["context_orders"]).sum().loc["B"]
        ##都有的neuron
        common_neuron_id = list(set(CtxA_all_cells.T.dropna().index).intersection(CtxB_all_cells.T.dropna().index))
        ### refer to CtxA, align CtxB
        plt.figure(figsize=[10,10])
        plt.subplot(221)
        heatmap = CtxA_all_cells.T.dropna().loc[common_neuron_id]
        heatmap["max_fr_angle"]=heatmap.apply(lambda x: int(x.nlargest(1).idxmin()),axis=1)
        heatmap["max_fr"]=heatmap[["45","90","135"]].max(axis=1)
        heatmap = heatmap.sort_values(by=["max_fr_angle","max_fr"],ascending=True)
        in_context_id_CtxA_45_CSI_allangles_bysessions = heatmap.index[heatmap["max_fr_angle"]==45]
        in_context_id_CtxA_90_CSI_allangles_bysessions = heatmap.index[heatmap["max_fr_angle"]==90]
        in_context_id_CtxA_135_CSI_allangles_bysessions = heatmap.index[heatmap["max_fr_angle"]==135]
        sns.heatmap(heatmap[["45","90","135"]])
        plt.title("CtxA_angle_distribution")
        plt.ylabel("neuron_id")
        plt.subplot(222)
        heatmap2 = CtxB_all_cells.T.dropna().loc[heatmap.index]
        sns.heatmap(heatmap2[["45","90","135"]])
        plt.title("CtxB_align2CtxA_angle_distribution")
        ### refer to CtxB, align CtxA  
        plt.subplot(223)
        heatmap = CtxB_all_cells.T.dropna().loc[common_neuron_id]
        heatmap["max_fr_angle"]=heatmap.apply(lambda x: int(x.nlargest(1).idxmin()),axis=1)
        heatmap["max_fr"]=heatmap[["45","90","135"]].max(axis=1)
        heatmap = heatmap.sort_values(by=["max_fr_angle","max_fr"],ascending=True)
        in_context_id_CtxB_45_CSI_allangles_bysessions = heatmap.index[heatmap["max_fr_angle"]==45]
        in_context_id_CtxB_90_CSI_allangles_bysessions = heatmap.index[heatmap["max_fr_angle"]==90]
        in_context_id_CtxB_135_CSI_allangles_bysessions = heatmap.index[heatmap["max_fr_angle"]==135]
        sns.heatmap(heatmap[["45","90","135"]])
        plt.title("CtxB_angle_distribution")
        plt.ylabel("neuron_id")
        plt.subplot(224)
        heatmap2 = CtxA_all_cells.T.dropna().loc[heatmap.index]
        sns.heatmap(heatmap2[["45","90","135"]])
        plt.title("CtxA_align2CtxB_angle_distribution")
        
        ## 画出无论在哪个 context, context direction selection  一致的细胞平均发放热图
        ## Fig 3
        ### intersection of cells prefering 45 in ctxA and ctxB
        in_context_id_45_CSI_allangles_bysessions = in_context_id_CtxA_45_CSI_allangles_bysessions.intersection(in_context_id_CtxB_45_CSI_allangles_bysessions)
        in_context_id_90_CSI_allangles_bysessions = in_context_id_CtxA_90_CSI_allangles_bysessions.intersection(in_context_id_CtxB_90_CSI_allangles_bysessions)
        in_context_id_135_CSI_allangles_bysessions = in_context_id_CtxA_135_CSI_allangles_bysessions.intersection(in_context_id_CtxB_135_CSI_allangles_bysessions)
        temp=in_context_id_45_CSI_allangles_bysessions.append(in_context_id_90_CSI_allangles_bysessions).append(in_context_id_135_CSI_allangles_bysessions)
        
        plt.figure(figsize=[10,6])
        ### align to ctxA
        plt.subplot(121)
        heatmap = CtxA_all_cells.T.dropna().loc[common_neuron_id].loc[temp]
        heatmap["max_fr_angle"]=heatmap.apply(lambda x: int(x.nlargest(1).idxmin()),axis=1)
        heatmap["max_fr"]=heatmap[["45","90","135"]].max(axis=1)
        heatmap = heatmap.sort_values(by=["max_fr_angle","max_fr"],ascending=True)
        # print(heatmap)
        sns.heatmap(heatmap[["45","90","135"]])
        plt.ylabel("neuron_id")
        plt.title("CtxA-angle-distribution")
        ### align to ctxB
        plt.subplot(122)
        heatmap2 = CtxB_all_cells.T.dropna().loc[common_neuron_id].loc[heatmap.index]
        sns.heatmap(heatmap2[["45","90","135"]])
        plt.title("CtxB-angle-distribution")
        
        ##### ctxs_45 cells
        ####intersection of cells prefering 90 in ctxA and ctxB
        ####intersection of cells prefering 135 in ctxA and ctxB
        ## prefer CtxA 的细胞， 在不同angle上的分布
        
        CtxA_in_context_id_CtxA_by_CSI_allangles_bysessions_cells = CtxA_all_cells.loc[:,in_context_id_CtxA_by_CSI_allangles_bysessions]
        CtxA_in_context_id_CtxB_by_CSI_allangles_bysessions_cells = CtxA_all_cells.loc[:,in_context_id_CtxB_by_CSI_allangles_bysessions]
        CtxB_in_context_id_CtxA_by_CSI_allangles_bysessions_cells = CtxB_all_cells.loc[:,in_context_id_CtxA_by_CSI_allangles_bysessions]
        CtxB_in_context_id_CtxB_by_CSI_allangles_bysessions_cells = CtxB_all_cells.loc[:,in_context_id_CtxB_by_CSI_allangles_bysessions]
                                 
    def wait(self):
        #对不同角度的CSI或者说不同天
        FR_differentangles = lw_ana.ana_result["in_context_MeanFr_mssessions"].groupby(["context_orders","context_angles"]).mean()
        
        CSI_angle45 = (FR_differentangles.loc[("A","45")]-FR_differentangles.loc[("B","45")])/(FR_differentangles.loc[("A","45")]+FR_differentangles.loc[("B","45")])
        CSI_angle45_CtxA = CSI_angle45[CSI_angle45>0]
        CSI_angle45_CtxB = CSI_angle45[CSI_angle45<0]
        in_context_id_CtxA_by_CSI_angle45_bysessions = CSI_angle45_CtxA.index
        in_context_id_CtxB_by_CSI_angle45_bysessions = CSI_angle45_CtxB.index

        CSI_angle90 = (FR_differentangles.loc[("A","90")]-FR_differentangles.loc[("B","90")])/(FR_differentangles.loc[("A","90")]+FR_differentangles.loc[("B","90")])
        CSI_angle90_CtxA = CSI_angle90[CSI_angle90>0]
        CSI_angle90_CtxB = CSI_angle90[CSI_angle90<0]
        in_context_id_CtxA_by_CSI_angle90_bysessions = CSI_angle90_CtxA.index
        in_context_id_CtxB_by_CSI_angle90_bysessions = CSI_angle90_CtxB.index
        
        CSI_angle135 = (FR_differentangles.loc[("A","135")]-FR_differentangles.loc[("B","135")])/(FR_differentangles.loc[("A","135")]+FR_differentangles.loc[("B","135")])
        CSI_angle135_CtxA = CSI_angle135[CSI_angle135>0]
        CSI_angle135_CtxB = CSI_angle135[CSI_angle135<0]
        in_context_id_CtxA_by_CSI_angle135_bysessions = CSI_angle135_CtxA.index
        in_context_id_CtxB_by_CSI_angle135_bysessions = CSI_angle135_CtxB.index

        in_context_id_CtxA_by_CSI_anyangle_bysessions = list(set(in_context_id_CtxA_by_CSI_angle45_bysessions).intersection(in_context_id_CtxA_by_CSI_angle90_bysessions,in_context_id_CtxA_by_CSI_angle135_bysessions))
        in_context_id_CtxB_by_CSI_anyangle_bysessions = list(set(in_context_id_CtxB_by_CSI_angle45_bysessions).intersection(in_context_id_CtxB_by_CSI_angle90_bysessions,in_context_id_CtxB_by_CSI_angle135_bysessions))

        #45
        plt.figure()        
        plt.scatter(CSI_angle45_CtxA.index,CSI_angle45_CtxA,c="red")
        plt.scatter(CSI_angle45_CtxB.index,CSI_angle45_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.vlines(in_context_id_CtxA_by_CSI_anyangle_bysessions,ymin=0,ymax=1,linestyle='--',color='red')
        plt.vlines(in_context_id_CtxB_by_CSI_anyangle_bysessions,ymin=-1,ymax=0,linestyle='--',color='green')
        plt.title("In_context_CSI_bysessions-angle45")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")
        #90
        plt.figure()        
        plt.scatter(CSI_angle90_CtxA.index,CSI_angle90_CtxA,c="red")
        plt.scatter(CSI_angle90_CtxB.index,CSI_angle90_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.vlines(in_context_id_CtxA_by_CSI_anyangle_bysessions,ymin=0,ymax=1,linestyle='--',color='red')
        plt.vlines(in_context_id_CtxB_by_CSI_anyangle_bysessions,ymin=-1,ymax=0,linestyle='--',color='green')
        plt.title("In_context_CSI_bysessions-angle90")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")
        #135
        plt.figure()        
        plt.scatter(CSI_angle135_CtxA.index,CSI_angle135_CtxA,c="red")
        plt.scatter(CSI_angle135_CtxB.index,CSI_angle135_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.vlines(in_context_id_CtxA_by_CSI_anyangle_bysessions,ymin=0,ymax=1,linestyle='--',color='red')
        plt.vlines(in_context_id_CtxB_by_CSI_anyangle_bysessions,ymin=-1,ymax=0,linestyle='--',color='green')
        plt.title("In_context_CSI_bysessions-angle135")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")
if __name__ == "__main__":
    mouse_info_path = r"Z:\QiuShou\mouse_info\191173_info.txt"
    cnmf_result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all"
    lw_ana = MiniLWAna(mouse_info_path,cnmf_result_dir)
    lw_ana.select_in_context()
    lw_ana.Fig_in_context_CSI_MeanFr_mssessions()
    # lw_ana.save