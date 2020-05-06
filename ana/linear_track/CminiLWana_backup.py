from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
from mylab.Cmouseinfo import MouseInfo
from mylab.ana.linear_track.Cminiana import MiniAna as MA
import os,sys
import seaborn as sns
from MminiLWana import *
class MiniLWAna(MA):
    def __init__(self,mouse_info_path,cnmf_result_dir):
        super().__init__(mouse_info_path,cnmf_result_dir)
        # self.mouse_info = self.mouse_info.lick_water

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
            
            
        #aligned2ms_behaveblocks增加“in_context”
        if not "in_context" in self.ana_result["aligned2ms_behaveblocks"][0].columns:
            new_aligned2ms_behaveblocks = []
            for aligned2ms_behaveblock,in_context_contextcoord in zip(self.ana_result["aligned2ms_behaveblocks"],self.ana_result["in_context_contextcoords"]):
                masks =in_context_contextcoord[0][0]
                in_context = []
                for x,y in zip(aligned2ms_behaveblock['Body_x'],aligned2ms_behaveblock['Body_y']):
                    if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                        in_context.append(0)
                    else:
                        in_context.append(1)
                aligned2ms_behaveblock['in_context'] = in_context
                new_aligned2ms_behaveblocks.append(aligned2ms_behaveblock)
            self.update("aligned2ms_behaveblocks", new_aligned2ms_behaveblocks)
            del new_aligned2ms_behaveblocks
            print("add condition 'in_context' in aligned2ms_behaveblocks")
        else:
            print("'in_context' is already in aligned2ms_behaveblocks")


        #产生in_context_msblocks,in_context_behaveblocks
        if not "in_context_msblocks" in self.keys:
            in_context_msblocks=[]
            in_context_behaveblocks=[]
            for msblock, aligned2ms_behaveblock in zip(self.ana_result["msblocks"],self.ana_result["aligned2ms_behaveblocks"]):
                in_context = aligned2ms_behaveblock['in_context']
                in_context_msblock = msblock.iloc[(in_context==1).values]
                in_context_behaveblock=aligned2ms_behaveblock.iloc[(in_context==1).values]

                in_context_msblocks.append(in_context_msblock)
                in_context_behaveblocks.append(in_context_behaveblock)
            self.add("in_context_msblocks", in_context_msblocks)
            self.add("in_context_behaveblocks",in_context_behaveblocks)
        else:
            print("'in_context_msblocks' and 'in_context_behaveblocks' are already in ana_result")

        #产生in_context_MeanFr_msblocks
        if not "in_context_MeanFr_msblocks" in self.keys:
            temp = [i.drop(columns=["ms_ts"]).mean().values for i in in_context_msblocks]
            in_context_MeanFr_msblocks = pd.DataFrame(temp,index=self.mouse_info.lick_water["behave_blocknames"],columns=in_context_msblocks[0].columns.drop("ms_ts"))
            self.add("in_context_MeanFr_msblocks", in_context_MeanFr_msblocks)
        else:
            print("'in_context_MeanFr_msblocks' are already in ana_result")

        #aligned2ms_behaveblocks增加"in_context_placebin_num"
        if not "placebin_num" in self.ana_result["aligned2ms_behaveblocks"][0].columns:
            new_aligned2ms_behaveblocks = []
            for aligned2ms_behaveblock,in_context_contextcoord in zip(self.ana_result["aligned2ms_behaveblocks"],self.ana_result["in_context_contextcoords"]):
                Cx_max = max(in_context_contextcoord[1][0][:,0])
                Cx_min = min(in_context_contextcoord[1][0][:,0])
                placebin_number = 10
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给其他区域
                for n in range(placebin_number):
                    placebins.append((n+1,[Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth]))
                in_context_placebin_num = []
                for in_context,x in zip(aligned2ms_behaveblock['in_context'],aligned2ms_behaveblock['Body_x']):
                    if in_context:
                        in_context_placebin_num.append(0)
                    else:
                        for placebin in placebins:
                            if x>=palcebin[1][0] and x<palcebin[1][1]:
                                in_context_placebin_num.append(placebin[0])
                            else:
                                in_context_placebin_num.append(placebin_number)
                                print("小鼠刚好在第%s个placebin的右边界处，特此提醒"%placebin_number)
                new_aligned2ms_behaveblocks.append(aligned2ms_behaveblock)
            self.update(key="aligned2ms_behaveblocks",value=new_aligned2ms_behaveblocks)
            del new_aligned2ms_behaveblocks
            print("add condition 'in_context_placebin_num' in aligned2ms_behaveblocks")
        else:
            print("'in_context_placebin_num' is already in aligned2ms_behaveblocks")
        #产生in_context_msblocks_placebins,in_context_behaveblocks_placebins
        #计算 in_context_MeanFr_msblocks_placebins

        #aligned2ms_behaveblocks增加"in_context_trialnum"
        #产生in_context_msblocks_trials,in_context_behaveblocks_trials,
        #计算 in_context_MeanFr_msblocks_trials
        if not "in_context_MeanFr_msblocks_trials" in self.keys:
            new_aligned2ms_behaveblocks=[]
            in_context_MeanFr_msblocks_trials = []
            for aligned2ms_behaveblock, in_context_msblock,in_context_contextcoord in zip(self.ana_result["aligned2ms_behaveblocks"],self.ana_result["in_context_msblocks"],self.ana_result["in_context_contextcoords"]):
                df = rlc2(aligned2ms_behaveblock['in_context'])
                mstrials=pd.DataFrame(columns=in_context_msblock.columns)
                behavetrials=pd.DataFrame(columns=aligned2ms_behaveblock.columns)
                Cx_max = max(in_context_contextcoord[1][0][:,0])
                Cx_min = min(in_context_contextcoord[1][0][:,0])

                trial_num= 1
                temp_block=pd.DataFrame(columns=["in_context_trialnum","placebin_number","ms_ts"])                
                for index,row in df.iterrows():
                    if row['name'] == 1 and row['idx_min']<row['idx_max']:
                        Bx = aligned2ms_behaveblock["Body_x"][row['idx_min']:row['idx_max']]
                        Bx_max=max(Bx)
                        Bx_min=min(Bx)
                        if (Bx_max-Bx_min)>0.5*(Cx_max-Cx_min):#轨迹要大于一半的context长度
                            temp_behavetrial = aligned2ms_behaveblock.iloc[row['idx_min']:row['idx_max']]
                            temp_trial = pd.DataFrame(columns=["in_context_trialnum","ms_ts"])
                            temp_trial["ms_ts"]=temp_behavetrial["ms_ts"].astype("int64")
                            temp_trial["in_context_trialnum"] = trial_num
                            temp_block = temp_block.append(temp_trial)
                            # print(temp_block)
                            trial_num = trial_num+1

                aligned2ms_behaveblock = pd.merge(aligned2ms_behaveblock,temp_block,on="ms_ts",how="outer")

                #添加'LoR':0 for left, 1 for right
                
                #添加placebin
                new_aligned2ms_behaveblocks.append(aligned2ms_behaveblock)
                in_context_msblock = pd.merge(in_context_msblock,temp_block,on="ms_ts",how="outer")
                in_context_MeanFr_msblock_trials = in_context_msblock.groupby("in_context_trialnum",as_index=False).mean()
                in_context_MeanFr_msblocks_trials.append(in_context_MeanFr_msblock_trials)
                
            self.update(key="aligned2ms_behaveblocks",value=new_aligned2ms_behaveblocks)
            del new_aligned2ms_behaveblocks
            print("add condition 'in_context_trialnum' in aligned2ms_behaveblocks")
            self.add(key="in_context_MeanFr_msblocks_trials",value=in_context_MeanFr_msblocks_trials)
        else:
            print("'aligned2ms_behaveblocks',in_context_MeanFr_msblocks_trials'")


    def in_context_CSI_allangles_byblocks(self):
        """利用'in_context_MeanFr_msblocks'来计算context selectivity index(CSI)"""
        self.ana_result["in_context_MeanFr_msblocks"]["context_orders"] = lw_ana.mouse_info.lick_water["context_orders"]
        self.ana_result["in_context_MeanFr_msblocks"]["context_angles"] = lw_ana.mouse_info.lick_water["context_angles"]
        #对所有角度的CSI
        FR_allangles = lw_ana.ana_result["in_context_MeanFr_msblocks"].groupby(["context_orders"]).mean()

        CSI_allangles = (FR_allangles.loc["A"]-FR_allangles.loc["B"])/(FR_allangles.loc["A"]+FR_allangles.loc["B"])
        CSI_changedfloor = (FR_allangles.loc["A1"]-FR_allangles.loc["B1"])/(FR_allangles.loc["A1"]+FR_allangles.loc["B1"])
        
        CSI_allangles_CtxA = CSI_allangles[CSI_allangles>0]
        CSI_allangles_CtxB = CSI_allangles[CSI_allangles<0] 
        in_context_id_CtxA_by_CSI_allangles_byblocks = CSI_allangles_CtxA.index
        in_context_id_CtxB_by_CSI_allangles_byblocks = CSI_allangles_CtxB.index   
        
        #all angles
        ## CSI-neuron_id
        plt.figure() 
        plt.subplot(121)
        plt.scatter(CSI_allangles_CtxA.index,CSI_allangles_CtxA,c="red")
        plt.scatter(CSI_allangles_CtxB.index,CSI_allangles_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.title("In_context_CSI_byblocks-all_angles")
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
            count = count+1

        plt.xticks([1,2],["A/B","A1/B1"])
        plt.xlim([0.5,2.5])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.title("CSI-change when floor changed")
        plt.xlabel("paired_context")
        plt.ylabel("CSI")
        
        ## 所有的细胞 在不同angle上的分布
        ###归一化 FR所占百分比
        CtxA_all_cells  = FR_differentangles.loc["A"]/FR_differentangles.groupby(["context_orders"]).sum().loc["A"]
        CtxB_all_cells  = FR_differentangles.loc["B"]/FR_differentangles.groupby(["context_orders"]).sum().loc["B"]
        ###都有的neuron
        common_neuron_id = list(set(CtxA_all_cells.T.dropna().index).intersection(CtxB_all_cells.T.dropna().index))
        ####refer to CtxA, align CtxB
        plt.figure(figsize=[10,10])
        plt.subplot(221)
        heatmap = CtxA_all_cells.T.dropna().loc[common_neuron_id]
        heatmap["max_fr_angle"]=heatmap.apply(lambda x: int(x.nlargest(1).idxmin()),axis=1)
        heatmap = heatmap.sort_values(by=["max_fr_angle"],ascending=True)
        in_context_id_CtxA_45_CSI_allangles_byblocks = heatmap.index[heatmap["max_fr_angle"]==45]
        in_context_id_CtxA_90_CSI_allangles_byblocks = heatmap.index[heatmap["max_fr_angle"]==90]
        in_context_id_CtxA_135_CSI_allangles_byblocks = heatmap.index[heatmap["max_fr_angle"]==135]
        sns.heatmap(heatmap[["45","90","135"]])
        plt.title("CtxA_angle_distribution")
        plt.ylabel("neuron_id")
        plt.subplot(222)
        heatmap2 = CtxB_all_cells.T.dropna().loc[heatmap.index]
        sns.heatmap(heatmap2[["45","90","135"]])
        plt.title("CtxB_align2CtxA_angle_distribution")
        ####refer to CtxB, align CtxA  
        plt.subplot(223)
        heatmap = CtxB_all_cells.T.dropna().loc[common_neuron_id]
        heatmap["max_fr_angle"]=heatmap.apply(lambda x: int(x.nlargest(1).idxmin()),axis=1)
        heatmap = heatmap.sort_values(by=["max_fr_angle"],ascending=True)
        in_context_id_CtxB_45_CSI_allangles_byblocks = heatmap.index[heatmap["max_fr_angle"]==45]
        in_context_id_CtxB_90_CSI_allangles_byblocks = heatmap.index[heatmap["max_fr_angle"]==90]
        in_context_id_CtxB_135_CSI_allangles_byblocks = heatmap.index[heatmap["max_fr_angle"]==135]
        sns.heatmap(heatmap[["45","90","135"]])
        plt.title("CtxB_angle_distribution")
        plt.ylabel("neuron_id")
        plt.subplot(224)
        heatmap2 = CtxA_all_cells.T.dropna().loc[heatmap.index]
        sns.heatmap(heatmap2[["45","90","135"]])
        plt.title("CtxA_align2CtxB_angle_distribution")
        
        ####intersection of cells prefering 45 in ctxA and ctxB
        in_context_id_45_CSI_allangles_byblocks = in_context_id_CtxA_45_CSI_allangles_byblocks.intersection(in_context_id_CtxB_45_CSI_allangles_byblocks)
        in_context_id_90_CSI_allangles_byblocks = in_context_id_CtxA_90_CSI_allangles_byblocks.intersection(in_context_id_CtxB_90_CSI_allangles_byblocks)
        in_context_id_135_CSI_allangles_byblocks = in_context_id_CtxA_135_CSI_allangles_byblocks.intersection(in_context_id_CtxB_135_CSI_allangles_byblocks)
        temp=in_context_id_45_CSI_allangles_byblocks.append(in_context_id_90_CSI_allangles_byblocks).append(in_context_id_135_CSI_allangles_byblocks)
        plt.figure(figsize=[10,8])
        ##### align to ctxA
        plt.subplot(121)
        heatmap = CtxA_all_cells_heatmap.loc[temp]
        sns.heatmap(heatmap[["45","90","135"]])
        plt.ylabel("neuron_id")
        plt.title("CtxA-angle-distribution")
        ##### align to ctxB
        plt.subplot(122)
        heatmap2 = CtxB_all_cells_heatmap.loc[temp]
        sns.heatmap(heatmap2[["45","90","135"]])
        plt.title("CtxB-angle-distribution")
        ##### ctxs_45 cells
        ####intersection of cells prefering 90 in ctxA and ctxB
        ####intersection of cells prefering 135 in ctxA and ctxB
        ## prefer CtxA 的细胞， 在不同angle上的分布
        
        CtxA_in_context_id_CtxA_by_CSI_allangles_byblocks_cells = CtxA_all_cells.loc[:,in_context_id_CtxA_by_CSI_allangles_byblocks]
        CtxA_in_context_id_CtxB_by_CSI_allangles_byblocks_cells = CtxA_all_cells.loc[:,in_context_id_CtxB_by_CSI_allangles_byblocks]
        CtxB_in_context_id_CtxA_by_CSI_allangles_byblocks_cells = CtxB_all_cells.loc[:,in_context_id_CtxA_by_CSI_allangles_byblocks]
        CtxB_in_context_id_CtxB_by_CSI_allangles_byblocks_cells = CtxB_all_cells.loc[:,in_context_id_CtxB_by_CSI_allangles_byblocks]
                                 
    def wait(self):
        #对不同角度的CSI或者说不同天
        FR_differentangles = lw_ana.ana_result["in_context_MeanFr_msblocks"].groupby(["context_orders","context_angles"]).mean()
        
        CSI_angle45 = (FR_differentangles.loc[("A","45")]-FR_differentangles.loc[("B","45")])/(FR_differentangles.loc[("A","45")]+FR_differentangles.loc[("B","45")])
        CSI_angle45_CtxA = CSI_angle45[CSI_angle45>0]
        CSI_angle45_CtxB = CSI_angle45[CSI_angle45<0]
        in_context_id_CtxA_by_CSI_angle45_byblocks = CSI_angle45_CtxA.index
        in_context_id_CtxB_by_CSI_angle45_byblocks = CSI_angle45_CtxB.index

        CSI_angle90 = (FR_differentangles.loc[("A","90")]-FR_differentangles.loc[("B","90")])/(FR_differentangles.loc[("A","90")]+FR_differentangles.loc[("B","90")])
        CSI_angle90_CtxA = CSI_angle90[CSI_angle90>0]
        CSI_angle90_CtxB = CSI_angle90[CSI_angle90<0]
        in_context_id_CtxA_by_CSI_angle90_byblocks = CSI_angle90_CtxA.index
        in_context_id_CtxB_by_CSI_angle90_byblocks = CSI_angle90_CtxB.index
        
        CSI_angle135 = (FR_differentangles.loc[("A","135")]-FR_differentangles.loc[("B","135")])/(FR_differentangles.loc[("A","135")]+FR_differentangles.loc[("B","135")])
        CSI_angle135_CtxA = CSI_angle135[CSI_angle135>0]
        CSI_angle135_CtxB = CSI_angle135[CSI_angle135<0]
        in_context_id_CtxA_by_CSI_angle135_byblocks = CSI_angle135_CtxA.index
        in_context_id_CtxB_by_CSI_angle135_byblocks = CSI_angle135_CtxB.index

        in_context_id_CtxA_by_CSI_anyangle_byblocks = list(set(in_context_id_CtxA_by_CSI_angle45_byblocks).intersection(in_context_id_CtxA_by_CSI_angle90_byblocks,in_context_id_CtxA_by_CSI_angle135_byblocks))
        in_context_id_CtxB_by_CSI_anyangle_byblocks = list(set(in_context_id_CtxB_by_CSI_angle45_byblocks).intersection(in_context_id_CtxB_by_CSI_angle90_byblocks,in_context_id_CtxB_by_CSI_angle135_byblocks))

        #45
        plt.figure()        
        plt.scatter(CSI_angle45_CtxA.index,CSI_angle45_CtxA,c="red")
        plt.scatter(CSI_angle45_CtxB.index,CSI_angle45_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.vlines(in_context_id_CtxA_by_CSI_anyangle_byblocks,ymin=0,ymax=1,linestyle='--',color='red')
        plt.vlines(in_context_id_CtxB_by_CSI_anyangle_byblocks,ymin=-1,ymax=0,linestyle='--',color='green')
        plt.title("In_context_CSI_byblocks-angle45")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")
        #90
        plt.figure()        
        plt.scatter(CSI_angle90_CtxA.index,CSI_angle90_CtxA,c="red")
        plt.scatter(CSI_angle90_CtxB.index,CSI_angle90_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.vlines(in_context_id_CtxA_by_CSI_anyangle_byblocks,ymin=0,ymax=1,linestyle='--',color='red')
        plt.vlines(in_context_id_CtxB_by_CSI_anyangle_byblocks,ymin=-1,ymax=0,linestyle='--',color='green')
        plt.title("In_context_CSI_byblocks-angle90")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")
        #135
        plt.figure()        
        plt.scatter(CSI_angle135_CtxA.index,CSI_angle135_CtxA,c="red")
        plt.scatter(CSI_angle135_CtxB.index,CSI_angle135_CtxB,c="green")
        plt.legend(["CtxA","CtxB"])
        plt.axhline(y=0,linestyle='--',c="gray")
        plt.vlines(in_context_id_CtxA_by_CSI_anyangle_byblocks,ymin=0,ymax=1,linestyle='--',color='red')
        plt.vlines(in_context_id_CtxB_by_CSI_anyangle_byblocks,ymin=-1,ymax=0,linestyle='--',color='green')
        plt.title("In_context_CSI_byblocks-angle135")
        plt.xlabel("neuron_id")
        plt.ylabel("CSI")
if __name__ == "__main__":
    mouse_info_path = r"Z:\QiuShou\mouse_info\191173_info.txt"
    cnmf_result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all"
    lw_ana = MiniLWAna(mouse_info_path,cnmf_result_dir)
    lw_ana.select_in_context()
    # lw_ana.save