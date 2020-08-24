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
        self.align_behave_ms() # self.Trial_Num, self.process
        self.add_info2aligned_behave2ms() # self.result["in_context"],self.result["Body_speed"],self.result["Body_speed_angle"],self.result["“in_context_place_bin"]
        self.df = pd.DataFrame(self.result["sigraw"][:,self.result["idx_accepted"]],columns=self.result["idx_accepted"])
        self.length = self.df.shape[0]

    def _load_session(self):
        logger.info("FUN:: _load_session")
        logger.debug("loading %s"%self.session_path)
        with open(self.session_path,"rb") as f:
            self.result = pickle.load(f)
        if not "aligned_behave2ms" in self.result.keys():
            self.exp = "hc"
        else:
            self.exp = "task"
        logger.debug("loaded %s"%self.session_path)



    def _dataframe2nparray(self,df):
        if isinstance(df,dict):
            print("df is a dict")
            for key in list(df.keys()):
                if isinstance(df[key],pd.core.frame.DataFrame):
                    df[str(key)+"_column"]=np.array(df[key].columns)
                    df[key]=df[key].values                    
                    print("%s has transferred to numpy array"%key)
                if isinstance(df[key],dict):
                    return dataframe2nparray(df[key])
            return df
        elif isinstance(df,pd.core.frame.DataFrame):
            print("df is a DataFrame")
            return {"df":df.values,"df_columns":np.array(df.columns)}

    def savepkl2mat(self,):
        logger.info("FUN:: savepkl2mat")
        savematname = self.session_path.replace("pkl","mat")
        spio.savemat(savematname,self._dataframe2nparray(self.result))
        logger.info("saved %s"%savematname)


    def align_behave_ms(self,hc_trial_bin=5000):
        """
        产生 aligned_behave2ms
        注意 有的是行为学视频比较长，有的是miniscope视频比较长，一般是行为学视频比较长
        hc_trial_bin: in ms, default 5000ms
        """
        logger.info("FUN:: aligned_behave2ms,hc_trial_bin=%s"%hc_trial_bin)
        
        if "behave_track" in self.result.keys():
            if not "aligned_behave2ms" in self.result.keys():
                # 为每一帧miniscope数据找到对应的行为学数据并保存  为 aligned_behave2ms
                logger.debug("aligninging behavioral frame to each ms frame...")
                logger.info("looking for behave frame for each corrected_ms_ts...")
                aligned_behave2ms=pd.DataFrame({"corrected_ms_ts": self.result["corrected_ms_ts"]
                                                ,"ms_behaveframe":[find_close_fast(arr=self.result["behave_track"]["be_ts"]*1000,e=k) for k in self.result["corrected_ms_ts"]]})

                _,length = rlc(aligned_behave2ms["ms_behaveframe"])
                logger.info("for one miniscope frame, there are at most %s behavioral frames "%max(length))

                if max(length)>10:
                    logger.info("********ATTENTION when align_behave_ms**********")
                    logger.info("miniscope video is longer than behavioral video, please check")
                    logger.info("********ATTENTION when align_behave_ms**********")

                aligned_behave2ms = aligned_behave2ms.join(self.result["behave_track"],on="ms_behaveframe")
                self.result["aligned_behave2ms"]=aligned_behave2ms
                with open(self.session_path,'wb') as f:
                    pickle.dump(self.result,f)
                logger.debug("aligned_behave2ms is saved %s" %self.session_path)
            else:
                logger.debug("behaveiroal timestamps were aligned to ms")


            self.Trial_Num = self.result["aligned_behave2ms"]["Trial_Num"]
            self.process = self.result["aligned_behave2ms"]["process"]

        else:
            logger.debug("this session was recorded in homecage")

            Trial_Num = []
            process = []
            for ts in self.result["ms_ts"]:
                Trial_Num.append(int(np.ceil(ts/hc_trial_bin)))
                process.append(-1)
            self.Trial_Num = pd.Series(Trial_Num)
            self.process = pd.Series(process)

    def add_zone2result(self,zone="in_lineartrack"):
        logger.info("FUN:: add_zone2result at zone %s"%zone)
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
        logger.info("FUN:: add_info2aligned_behave2ms scale: %scm/pixel ; placebin_number: %s"%(scale,placebin_number))
        update = 0
            
        if "aligned_behave2ms" in self.result.keys():
            #1 添加 "in_context" in behave_track
            mask = self.result["in_context_mask"]
            if not "in_context" in self.result.keys():
                in_context=[]
                for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        in_context.append(0)
                    else:
                        in_context.append(1)
                self.result["in_context"]=pd.Series(in_context)
                logger.info("'in_context' has been added")
                update = 1
            else:
                print("'in_context' has been there")

            #2 添加“Body_speed" "Body_speed_angle"
            if not "Body_speed" in self.result.keys():
                Body_speed,Body_speed_angle = Video.speed(X=self.result["aligned_behave2ms"]["Body_x"]
                                                        ,Y=self.result["aligned_behave2ms"]["Body_y"]
                                                        ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                        ,s=scale)
                self.result["Body_speed"]=Body_speed
                self.result["Body_speed_angle"]=Body_speed_angle
                logger.info("Body_speed and Body_speed_angle have been added")
                update = 1
            else:
                print("'Body_speed'and'Body_speed_angle' has been there")
            
            #3 添加"in_context_running_direction"
            if not "in_context_running_direction" in self.result.keys():
                in_context_running_direction=[]

                for Trial, in_context,Body_speed,Body_speed_angle in zip(self.Trial_Num,self.result["in_context"],self.result["Body_speed"],self.result["Body_speed_angle"]):
                    if Trial == -1:
                        in_context_running_direction.append(-1)
                    else:
                        if in_context == 0:
                            in_context_running_direction.append(-1)
                        else:
                            if Body_speed_angle > 90 and Body_speed_angle < 280 :
                                in_context_running_direction.append(0)
                            else:
                                in_context_running_direction.append(1)
                self.result["in_context_running_direction"]=pd.Series(in_context_running_direction)
                logger.info("in_context_running_direction has been added")
                update = 1
            else:
                print("in_context_running_direction has been there")

            #4 添加 in_context_placebin_num"
            if not "in_context_placebin_num" in self.result.keys():
                Cx_min = np.min(self.result["in_context_coords"][:,0])
                Cx_max = np.max(self.result["in_context_coords"][:,0])
    
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                print(placebins)
                for in_context,x in zip(self.result['in_context'],self.result["aligned_behave2ms"]['Body_x']):
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
                self.result["in_context_placebin_num"] = in_context_placebin_num
                update = 1
            else:
                print("'in_context_placebin_num' has been there")
            
        else:
            print("you haven't align behave to ms or it's homecage session")

        if update:
            with open(self.session_path,'wb') as f:
                pickle.dump(self.result,f)
            print("aligned_behave2ms is updated and saved %s" %self.session_path)





    def trim_df(self,df=None,force_neg2zero=True,Normalize=False,standarize=False
        ,Trial_Num=None
        ,in_process=False,process=None
        ,in_context=False,in_lineartrack=False):
        """
        process: list process, for example [0,1,2]
        """
        logger.info("FUN:: trim_df")

        if df == None:
            df = self.df
        if force_neg2zero:
            logger.info("negative values are forced to be zero")
            df[df<0]=0

        if Normalize:
            df,_,_ = Normalization(df)
            logger.info("NORMALIZED sigraw trace")
        if standarize:
            df,_,_ = Standarization(df)
            logger.info("STANDARIZED sigraw trace")

        if Trial_Num==None:
            Trial_Num = self.Trial_Num


        index=pd.DataFrame()
        index["Trial_Num"] = Trial_Num>=0
        
        if in_process:
            if not process ==None:
                indes["in_process"] = self.process.isin(process)
            else:
                logger.warning("process is [None], please specify.")

        if in_context:
            try:
                index["in_context"] = self.result["in_context"]
            except:
                logger.warning("in_context does not exist")
        if in_lineartrack:
            try:
                index["in_lineartrack"] = self.result["in_lineartrack"]
            except:
                logger.warning("in_lineartrack does not exist")


        # df = df[index.all(axis=1)]
        # print(index.all(axis=1))
        
        return df, index.all(axis=1)

    def shuffle(self,df):
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




    def cellids_Context(self,idxes,meanfr_df=None,Context=None,context_map=["A","B","C","N"]):
        """
        输入应该全是 in_context==1的数据
        idxes: the ids of all the cell that you're concerned.
        meanfr_df: meanfr in each trial only in context
        context_list:contains ["Trial_Num","context_list"],existed in self.result["behavelog_info"]
                     two available contexts represented by A or B.N means out of all the context. each trial have a exposured context
        context_map: 0 means context A, 1 means context B, 2 means context C.
        standarization to make data of differnet batch compatable
        """
        logger.info("FUN:: cellids_Context")
        logger.info("Context 0,1,2,-1 means %s."%context_map)
        #序列化in_context_list
        if meanfr_df == None:
            logger.info("Default :: meanfr_df = self.meanfr_by_trial(Normalize=False,standarize=False,in_context=True) ")
            df,index = self.trim_df(force_neg2zero=True
                ,Normalize=False,standarize=False,in_context=True)

            meanfr_df = df[index].groupby(self.Trial_Num[index]).mean().reset_index(drop=False)

        if Context == None:
            logger.info("""Default:: pd.merge(self.Trial_Num[index],self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])[Enter_ctx]""")
            temp = pd.merge(meanfr_df,self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])
            Context = temp["Enter_ctx"]
        # 将0，1对应的context信息根据context_map置换成A B
        Context = pd.Series([context_map[i] for i in Context])

        ctx_pvalue = meanfr_df[idxes].apply(func=lambda x: stats.ranksums(x[Context=="A"],x[Context=="B"])[1],axis=0)
        # ctx_pvalue.columns=["ranksum_p_value"]
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
        "ctx_meanfr":ctx_meanfr, # meanfr in context A and B, rank_sum_pvalue,CSI
        "ContextA_cells":ContextA_cells,
        "ContextB_cells":ContextB_cells,
        "non_context_cells":non_context_cells
        }



    def cellids_RD_incontext(self,idxes,mean_df=None,Context=None,in_context_running_direction=None,in_context_placebin_num=None,context_map=["A","B","C","N"],rd_map=["left","right","None"]):
        """
        输入应该全是 in_context==1的数据. in_context_running_direction is -1 when out of context
        idxes: the ids of all the cell that you're concerned.
        meanfr_df: meanfr in each trial only in context
        in_context_running_direction: in_context_running_direction order which is as long as the frame length
        rd_map: 0 means left, 1 means right, -1 means None.
        standarization to make data of differnet batch compatable
        """

        logger.info("FUN:: cellids_RD_incontext")
        logger.info("in_context_running_direction 0,1,-1 means%s."%rd_map)


        if mean_df == None:
            logger.info("Default :: meanfr_df = self.meanfr_by_trial(Normalize=False,standarize=False,in_context=True) ")
            df,index = self.trim_df(force_neg2zero=True
                ,Normalize=False,standarize=False,in_context=True)


        if in_context_running_direction == None:
            logger.info("Default ::")
            in_context_running_direction=self.result["in_context_running_direction"]
        in_context_running_direction = pd.Series([rd_map[i] for i in in_context_running_direction])

        meanfr_df = df[index].groupby([self.Trial_Num[index],in_context_running_direction[index]]).mean().reset_index(drop=False).rename(columns={"level_1":"rd"})
        # meanfr_df = df[index].groupby([self.Trial_Num[index],in_context_running_direction[index]]).mean().reset_index(drop=False)
        if Context == None:
            logger.info("""Default:: pd.merge(self.Trial_Num[index],self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])[Enter_ctx]""")
            temp = pd.merge(meanfr_df,self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])
            Context = temp["Enter_ctx"]
        # 将0，1对应的context信息根据context_map置换成A B
        Context = pd.Series([context_map[i] for i in Context])
        #meanfr context 
        #context A rd 0
        print(meanfr_df)
        print(meanfr_df[(Context=="A") & (meanfr_df['rd']=="left")])
        #context A rd 1
        #context B rd 0
        #context B rd 1
        #rd 0
        #rd 1



        # return {
        # "rd_meanfr":rd_meanfr# meanfr in running direction o and 1, rank_sum_pvalue,RDSI
        # "rd_0_cells":rd_0_cells,
        # "rd_1_cells":rd_1_cells,
        # "non_rd_cells":non_rd_cells
        # }

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
# if __name__ == "__main__":
#     sessions = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\Results_202016\20200531_165342_0509-0511-Context-Discrimination-30fps\session*.pkl")
#     for session in sessions:
#         S = MiniAna(session)
#         S.savepkl2mat()
if __name__ == "__main__":
    s3 = MiniAna(r"C:\Users\Sabri\Desktop\20200531_165342_0509-0511-Context-Discrimination-30fps\session3.pkl")

    print(s3.cellids_RD_incontext(s3.result["idx_accepted"]))