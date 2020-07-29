

class MiniAna():
    def __init__(self,Result_dir):
        self.Result_dir=Result_dir


    def hc_meanfr(self,ms_session,by = ["Trial_Num"],maxTrialNum=60):   
        """
        homecage session:
            regard every 5000ms as ONE Trial
        """
        with open(ms_session,'rb') as f:
            result = pickle.load(f)
        Trial_Num = []
        for ts in result["ms_ts"]:
            Trial_Num.append(int(np.ceil(ts/5000)))

        temp_sigraw = pd.DataFrame(result["sigraw"][:,result["idx_accepted"]],columns=result["idx_accepted"])
        temp_sigraw["Trial_Num"] = Trial_Num
        temp_sigraw = temp_sigraw.loc[temp_sigraw["Trial_Num"]<=maxTrialNum]
        temp_mean = temp_sigraw.groupby(by).mean().reset_index()
        temp_mean["Enter_ctx"] = -1
        temp_mean["Exit_ctx"] = -1
        return 

    def task_meanfr(self,ms_session,by=["Trial_Num"],**kwargs):
        """
        非"hc" ms_session， 
            索引result["aligned_behave2ms"] 指定columns指定values的每个trial的平均发放率
        **kwargs 作为筛选条件
        输出 按Trial_Num groupby的平均发放率
        """
        with open(ms_session,'rb') as f:
            result = pickle.load(f)

        if "aligned_behave2ms" in result.keys():
            #索引指定的columns中指定值的帧,新增"index"列，用于索引“sigraw"中的值
            temp = result["aligned_behave2ms"].reset_index(drop=False)
            keys = result["aligned_behave2ms"].keys()

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


    def cellids_Context(self,idx_accept,df):
        """
        df 必须具备 Trial_Num Enter_ctx 和 Exit_ctx

        输入df包括在contextA和在contextB中的两种trial
        输出在A B cell ID
        """

        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Enter_ctx","Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])

        ContextA_cells=[]
        ContextB_cells=[]
        CDIs=[]
        Noncontext_cells=[]

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



    def cellids_RD_incontext(self,df):
        """
        df 必须具备  Trial_Num Enter_ctx, Exit_ctx  和 running direction
        输入df包括 两种不同running direction 的 区分
        """
        pass

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