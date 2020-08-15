import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys,glob,csv
import json
import scipy.io as spio
import pickle

from mylab.process.miniscope.Mfunctions import *
from mylab.ana.miniscope.Mfunctions import *
import logging 


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler(sys.stdout) #stream handler
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

class MiniAna():
    def __init__(self,session_path):
        self.session_path=session_path

        self.logfile =self.session_path.replace('.pkl','_log.txt')
        fh = logging.FileHandler(self.logfile,mode="w")
        formatter = logging.Formatter("  %(asctime)s %(message)s")
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        self._load_session()

    def _load_session(self):
        logger.info("loading %s"%self.session_path)
        with open(self.session_path,"rb") as f:
            self.result = pickle.load(f)
        if not "aligned_behave2ms" in self.result.keys():
            self.exp = "hc"
        else:
            self.exp = "task"
        logger.debug("loaded %s"%self.session_path)

    def _dataframe2nparray(self,df):
        if isinstance(df,dict):
            for key in list(df.keys()):
                if isinstance(df[key],pd.core.frame.DataFrame):
                    df[str(key)+"_column"]=np.array(df[key].columns)
                    df[key]=df[key].values                    
                    print("%s has transferred to numpy array"%key)
                if isinstance(df[key],dict):
                    return dataframe2nparray(df[key])
        else:
            print("df is not a dict")
        return df

    def savepkl2mat(self,):
        savematname = self.session_path.replace("pkl","mat")
        spio.savemat(savematname,self._dataframe2nparray(self.result))
        logger.info("saved %s"%savematname)


    def align_behave_ms(self):
        """
        产生 aligned_behave2ms
        注意 有的是行为学视频比较长，有的是miniscope视频比较长，一般是行为学视频比较长
        """
        if not "aligned_behave2ms" in self.result.keys():
            if "behave_track" in self.result.keys():

                # 为每一帧miniscope数据找到对应的行为学数据并保存  为 aligned_behave2ms
                logger.debug("aligninging behavioral frame to each ms frame...")
                aligned_behave2ms=pd.DataFrame({"corrected_ms_ts": self.result["corrected_ms_ts"]
                                                ,"ms_behaveframe":[find_close_fast(arr=self.result["behave_track"]["be_ts"]*1000,e=k) for k in self.result["corrected_ms_ts"]]})

                _,length = rlc(aligned_behave2ms["ms_behaveframe"])
                logger.info("max length of the same behave frame in one mini frame: %s"%max(length))

                if max(length)>10:
                    logger.info("********ATTENTION when align_behave_ms**********")
                    logger.info("miniscope frame is longer than behavioral video, please check")
                    logger.info("********ATTENTION when align_behave_ms**********")

                aligned_behave2ms = aligned_behave2ms.join(self.result["behave_track"],on="ms_behaveframe")
                self.result["aligned_behave2ms"]=aligned_behave2ms
                with open(self.session_path,'wb') as f:
                    pickle.dump(self.result,f)
                logger.debug("aligned_behave2ms is saved %s" %self.session_path)

            else:
                logger.debug("this session was recorded in homecage")
        else:
            logger.debug("behaveiroal timestamps were aligned to ms")


    def add_zone2result(self,zone="in_lineartrack"):

        mask = zone+"_mask"
        coords = zone+"_coords"
        if not mask in self.result.keys():
            if os.path.exists(self.result["behavevideo"]):
                try:
                    temp_mask,temp_coords=Video(self.result["behavevideo"]).draw_rois(aim=zone,count = 1)
                except Exception as e:
                    logger.info(e)
                    sys.exit()
            else:
                logger.info("DON'T EXIST: %s "%self.result["behavevideo"])
                sys.exit()

            self.result[mask]=temp_mask
            self.result[coords]=temp_coords

            with open(self.session_path,'wb') as f:
                pickle.dump(self.result,f)
            print("%s coords and mask is saved"%zone)
        else:
            print("%s coords and mask are already there"%zone)


    def add_info2aligned_behave2ms(self,scale=0.2339021309714166,placebin_number=10):
        #     scale = 0.2339021309714166 #cm/pixel 40cm的台子，202016，202017.202019适用
        update = 0
            
        if "aligned_behave2ms" in self.result.keys():
            #1 添加 "in_context" in behave_track
            mask = self.result[""]
            if not "in_context" in self.result["aligned_behave2ms"].columns:
                in_context=[]
                for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        in_context.append(0)
                    else:
                        in_context.append(1)
                self.result["aligned_behave2ms"]["in_context"]=in_context
                print("'in_context' has added")
                update = 1
            else:
                print("'in_context' has been there")

            #2 添加“Body_speed" "Body_speed_angle"
            if not "Body_speed" in self.result["aligned_behave2ms"].columns:
                Body_speed,Body_speed_angle = Video.speed(X=self.result["aligned_behave2ms"]["Body_x"],Y=self.result["aligned_behave2ms"]["Body_y"],T=self.result["aligned_behave2ms"]["be_ts"],s=scale)
                self.result["aligned_behave2ms"]["Body_speed"]=list(Body_speed)
                self.result["aligned_behave2ms"]["Body_speed_angle"]=list(Body_speed_angle)
                update = 1
            else:
                print("'Body_speed'and'Body_speed_angle' has been there")
            
            #3 添加 “in_context_place_bin"
            if not "in_context_placebin_num" in self.result["aligned_behave2ms"].columns:
                Cx_min = np.min(self.result["in_context_coords"][:,0])
                Cx_max = np.max(self.result["in_context_coords"][:,0])
    
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                print(placebins)
                for in_context,x in zip(self.result["aligned_behave2ms"]['in_context'],self.result["aligned_behave2ms"]['Body_x']):
                    x = int(x)
                    if not in_context:
                        in_context_placebin_num.append(0)
                    else:   
                        for i in range(placebin_number):
                            if i == 0 :
                                if x<placebins[i][1]:
                                    in_context_placebin_num.append(i+1)
                                else:
                                    pass
                            elif not i == placebin_number-1:
                                if x>=placebins[i][0] and x<placebins[i][1]:
                                    in_context_placebin_num.append(i+1)
                                else:             
                                    pass
                            else:
                                if x>=placebins[i][0]:
                                    in_context_placebin_num.append(i+1)
                                else:
                                    pass
                        
                print(len(in_context_placebin_num),self.result["aligned_behave2ms"].shape)
                self.result["aligned_behave2ms"]["in_context_placebin_num"] = in_context_placebin_num
                update = 1
            else:
                print("'in_context_placebin_num' has been there")
            
        else:
            print("you haven't align behave to ms or it's homecage session")

        if update:
            with open(ms_session,'wb') as f:
                pickle.dump(self.result,f)
            print("aligned_behave2ms is updated and saved %s" %ms_session)

    def hc_meanfr(self,by = ["Trial_Num"],maxTrialNum=60):   
        """
        homecage session:
            regard every 5000ms as ONE Trial
        """
        Trial_Num = []
        for ts in self.result["ms_ts"]:
            Trial_Num.append(int(np.ceil(ts/5000)))

        temp_sigraw = pd.DataFrame(result["sigraw"][:,result["idx_accepted"]],columns=result["idx_accepted"])
        temp_sigraw["Trial_Num"] = Trial_Num
        temp_sigraw = temp_sigraw.loc[temp_sigraw["Trial_Num"]<=maxTrialNum]
        temp_mean = temp_sigraw.groupby(by).mean().reset_index()
        temp_mean["Enter_ctx"] = -1
        temp_mean["Exit_ctx"] = -1
        return 

    def task_meanfr(self,by=["Trial_Num"],**kwargs):
        """
        非"hc" self.session_path， 
            索引result["aligned_behave2ms"] 指定columns指定values的每个trial的平均发放率
        **kwargs 作为筛选条件
        输出 按Trial_Num groupby的平均发放率
        """
        with open(self.session_path,'rb') as f:
            self.result = pickle.load(f)

        if "aligned_behave2ms" in self.result.keys():
            #索引指定的columns中指定值的帧,新增"index"列，用于索引“sigraw"中的值
            temp = self.result["aligned_behave2ms"].reset_index(drop=False)
            keys = self.result["aligned_behave2ms"].keys()

            # **kwargs 作为筛选条件
            for key,value in kwargs.items():
                print("%s is limited to %s"%(key,value),end=":  ")
                print(temp.shape,end=">>>")
                if key in keys:
                    if key == "Body_speed":                
                        temp = temp.loc[temp["Body_speed"]>3]
        #                 print(temp["Body_speed"])
                    else:
                        temp = temp.loc[temp[key].isin(value)]
                    print(temp.shape)
                else:
                    print("%s does not exist")
                    sys.exit()
                
            temp = temp.reset_index()

            temp_sigraw = pd.DataFrame(result["sigraw"][:,result["idx_accepted"]][temp["index"],:],columns=result["idx_accepted"])
            temp_sigraw["Trial_Num"] = temp["Trial_Num"]
            return temp_sigraw.groupby(by).mean().reset_index().join(result["behavelog_info"].set_index("Trial_Num")[["Enter_ctx","Exit_ctx"]],on="Trial_Num")

    def shuffle(self,df,times=1000):
        for i in range(times):
            new_df = df.sample(frac=1).reset_index(drop=True)
            yield new_df

    def cellids_HCTrack_Context(self,idx_accept,df):
        """
        df 合并了HC session 和 non-HC session的
        df 必须具备 Trial_Num Enter_ctx 和 Exit_ctx
        """
        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Enter_ctx","Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])
        
        familiar_cells = []
        familiar_ctxA_cells = []
        familiar_ctxB_cells =[]
        familiar_nonctx_cells = []
        novel_cells =[]
        novel_ctxA_cells=[]
        novel_ctxB_cells=[]
        novel_nonctx_cells = []
        nothing_cells=[]
        
        strange_cells = []
        
        for idx in idx_accept:
            hc_fr = df[idx][df["Enter_ctx"]==-1]
            ctxA_fr = df[idx][df["Enter_ctx"]==0]
            ctxB_fr = df[idx][df["Enter_ctx"]==1]
            hc_meanfr =np.mean(hc_fr)
            hc_std = np.std(hc_fr)
            ctxA_meanfr =np.mean(ctxA_fr)
            ctxA_std =np.std(ctxA_fr)
            ctxB_meanfr =np.mean(ctxB_fr)
            ctxB_std  =np.std(ctxB_fr)
            hc_ctxA_p = stats.ranksums(hc_fr,ctxA_fr)[1]
            hc_ctxB_p = stats.ranksums(hc_fr,ctxB_fr)[1]
            ctxA_ctxB_p = stats.ranksums(ctxA_fr,ctxB_fr)[1]
            

            #首先判定 是否是某种cells
            if hc_ctxA_p < 0.05 or hc_ctxB_p < 0.05 or ctxA_ctxB_p < 0.05:
                #判定是familair cells 
                if hc_ctxA_p < 0.05 and hc_ctxB_p<0.05 and hc_meanfr>ctxA_meanfr and hc_meanfr>ctxB_meanfr:
                    familiar_cells.append(idx)
                    #判定是familiar_ctxA_cell / familiar_ctxB_cell/familiar_nonctx_cell
                    if ctxA_ctxB_p < 0.05:
                        if ctxA_meanfr > ctxB_meanfr:
                            familiar_ctxA_cells.append(idx)
                        else:
                            familiar_ctxB_cells.append(idx)
                    else:
                        familiar_nonctx_cells.append(idx)
                #判定是novel cells
                elif (hc_ctxA_p < 0.05 and hc_meanfr < ctxA_meanfr) or (hc_ctxB_p<0.05 and hc_meanfr < ctxB_meanfr):
                    novel_cells.append(idx)
                    #判定是novel_ctxA_cell / novel_ctxB_cell / novel_nonctx_cells
                    if ctxA_ctxB_p < 0.05:
                        if ctxA_meanfr > ctxB_meanfr:
                            novel_ctxA_cells.append(idx)
                        else:
                            novel_ctxB_cells.append(idx)
                    else:
                        novel_nonctx_cells.append(idx)
                else:
                    strange_cells.append(idx)
            else:
                nothing_cells.append(idx)
        """
        通过rank sum test判断其在home cage中发放的比较高还是在Track A or B中发放的比较高
        输出HC A B None 的 cell ID
        """
        return  {"familiar_cells":familiar_cells
                 ,"familiar_ctxA_cells":familiar_ctxA_cells
                 ,"familiar_ctxB_cells":familiar_ctxB_cells
                 ,"familiar_nonctx_cells":familiar_nonctx_cells
                 ,"novel_cells":novel_cells
                 ,"novel_ctxA_cells":novel_ctxA_cells
                 ,"novel_ctxB_cells":novel_ctxB_cells
                 ,"novel_nonctx_cells":novel_nonctx_cells
                 ,"nothing_cells":nothing_cells
                 ,"strange_cells":strange_cells}


    def cellids_Context(self,idx_accept,df,method="ranksum"):
        """
        df 必须具备 Trial_Num Enter_ctx 和 Exit_ctx

        输入df包括在contextA和在contextB中的两种trial
        输出在A B cell ID
        """

        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])

        ContextA_cells=[]
        ContextB_cells=[]
        CDIs=[]
        Noncontext_cells=[]

        if method == "ranksums":
            for idx in idx_accept:
                ctxA_fr = df[idx][df["Enter_ctx"]==0]
                ctxB_fr = df[idx][df["Enter_ctx"]==1]
                ctxA_meanfr =np.mean(ctxA_fr)
                ctxA_std =np.std(ctxA_fr)
                ctxB_meanfr =np.mean(ctxB_fr)
                ctxB_std  =np.std(ctxB_fr)
                ctxA_ctxB_p = stats.ranksums(ctxA_fr,ctxB_fr)[1]
                CDI= (ctxA_meanfr-ctxB_meanfr)/(ctxA_meanfr+ctxB_meanfr)
                CIDs.append(CDI)


                #判定是novel_ctxA_cell / novel_ctxB_cell / novel_nonctx_cells
                if ctxA_ctxB_p < 0.05:
                    if ctxA_meanfr > ctxB_meanfr:
                        ContextA_cells.append(idx)
                    else:
                        ContextB_cells.append(idx)
                else:
                    Noncontext_cells.append(idx)

            return [ContextA_cells,ContextB_cells,CDIs]
        if method == "shuffle":
            pass



    def cellids_RD_incontext(self,df):
        """
        df 必须具备  Trial_Num Enter_ctx, Exit_ctx  和 running direction
        输入df包括 两种不同running direction 的 区分
        """

        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])

        ContextA_RD0_cells=[]
        ContextA_RD1_cells=[]
        ContextB_RD0_cells=[]
        ContextB_RD1_cells=[]

        ContextA_NonRD_cells=[]
        ContextB_NonRD_cells=[]

        for idx in idx_accept:
            ctxA_RD0_fr = df[idx][df["Enter_ctx"]==0][df["rd"]==0]
            ctxA_RD0_meanfr=np.mean(ctxA_RD0_fr)
            ctxA_RD0_std=np.std(ctxA_RD0_fr)

            ctxA_RD1_fr = df[idx][df["Enter_ctx"]==0][df["rd"]==1]
            ctxA_RD1_meanfr=np.mean(ctxA_RD1_fr)
            ctxA_RD1_std=np.std(ctxA_RD1_fr)

            ctxB_RD0_fr = df[idx][df["Enter_ctx"]==1][df["rd"]==0]
            ctxB_RD0_meanfr=np.mean(ctxB_RD0_fr)
            ctxB_RD0_std=np.std(ctxB_RD0_fr)

            ctxB_RD1_fr = df[idx][df["Enter_ctx"]==1][df["rd"]==1]
            ctxB_RD1_meanfr=np.mean(ctxB_RD1_fr)
            ctxB_RD1_std=np.std(ctxB_RD1_fr)


            ctxA_ctxB_p = stats.ranksums(ctxA_fr,ctxB_fr)[1]
            CDI= (ctxA_meanfr-ctxB_meanfr)/(ctxA_meanfr+ctxB_meanfr)
            CIDs.append(CDI)


            #判定是novel_ctxA_cell / novel_ctxB_cell / novel_nonctx_cells
            if ctxA_ctxB_p < 0.05:
                if ctxA_meanfr > ctxB_meanfr:
                    ContextA_cells.append(idx)
                else:
                    ContextB_cells.append(idx)
            else:
                Noncontext_cells.append(idx)

        # return [ContextA_cells,ContextB_cells,CDIs]

    def cellids_PC_incontext(self,df):
        """
        df 必须具备 place_bin_num
        输入df包括分好的place bin 
        """
        pass


    def cellids_NovelFamiliar_incontext(self,df):
        """
        df 必须具备 Trial_Num Enter_ctx, Exit_ctx
        这是同一个session在时间尺度上的分析
        将单个session的df分为前后两个半段，前半段为novel context session ,后半段为familair context session
        比较两个半段的session，输出Novel context /  Familiar contxt cell ID
        """
        pass
if __name__ == "__main__":
    sessions = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\Results_202016\20200531_165342_0509-0511-Context-Discrimination-30fps\session*.pkl")
    for session in sessions:
        S = MiniAna(session)
        S.savepkl2mat()
