    def cellids_RD_incontext(self,idx_accept,df):
        """
        df 必须具备 Trial_Num Enter_ctx, Exit_ctx running direction(rd,0 or 1) 

        输入df包括在contextA和在contextB中的两种trial
        输出在A B cell ID
        """

        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Enter_ctx","Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])

        ContextA_RD0_cells=[]
        ContextA_RD1_cells=[]
        ContextB_RD0_cells=[]
        ContextB_RD1_cells=[]

        ContextA_NonRD_cells=[]
        ContextB_NonRD_cells=[]

        for idx in idx_accept:
            ctxA_0_fr = df[idx][df["Enter_ctx"]==0]


    def cellids(self,df):
        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])

        result = {
        "HC-ContextAB_cells":{
            familiar_cells = []
            familiar_ctxA_cells = []
            familiar_ctxB_cells =[]
            familiar_nonctx_cells = []
            novel_cells =[]
            novel_ctxA_cells=[]
            novel_ctxB_cells=[]
            novel_nonctx_cells = []
            nothing_cells=[]
            strange_cells=[]
        },

        "ContextAB_cells":{
            ContextA_cells=[]
            ContextB_cells=[]
            Noncontext_cells=[]
        },


        "RuningDirection_cells":{
            ContextA_RD0_cells=[]
            ContextA_RD1_cells=[]
            ContextB_RD0_cells=[]
            ContextB_RD1_cells=[]

            ContextA_NonRD_cells=[]
            ContextB_NonRD_cells=[]
        },

        "Place_Cells":{
            ContextA_placecells=[]
            ContextB_placecells=[]
        }
        }