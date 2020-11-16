import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os,sys,glob,csv
import json
import scipy.io as spio
import pickle
import scipy.stats as stats
from mylab.Cvideo import *
from mylab.Functions import *
from mylab.process.miniscope.Mfunctions import *
from mylab.ana.miniscope.Mca_transient_detection import detect_ca_transients
from mylab.ana.miniscope.Mplacecells import *
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
        fh = logging.FileHandler(self.logfile,mode="a")
        formatter = logging.Formatter("  %(asctime)s %(message)s")
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        self._load_session()
        # self.align_behave_ms() # self.result["Trial_Num"], self.process
        logger.info("'sigraw' is taken as original self.df")
        self.df = pd.DataFrame(self.result["sigraw"][:,self.result["idx_accepted"]],columns=self.result["idx_accepted"])
        self.shape = self.df.shape

    def _load_session(self):
        logger.info("FUN:: _load_session")
        print("loading %s"%self.session_path)
        with open(self.session_path,"rb") as f:
            self.result = pickle.load(f)
        if not "behavelog_info" in self.result.keys():
            self.exp = "hc"
        else:
            self.exp = "task"
        logger.debug("loaded")
        print(self.result.keys())


    def _dataframe2nparray(self,df):
        if isinstance(df,dict):
            print("df is a dict")
            for key in list(df.keys()):
                if isinstance(df[key],pd.core.frame.DataFrame):
                    df[str(key)+"_column"]=np.array(df[key].columns)
                    df[key]=df[key].values                    
                    # print("%s has transferred to numpy array"%key)
                if isinstance(df[key],pd.core.series.Series):
                    df[key]=df[key].values
                if isinstance(df[key],dict):
                    return self._dataframe2nparray(df[key])
            return df
        elif isinstance(df,pd.core.frame.DataFrame):
            print("df is a DataFrame")
            return {"df":df.values,"df_columns":np.array(df.columns)}
        else:
            print("%s can not be transferred to nparray"%type(df))

    def savepkl2mat(self,):
        logger.info("FUN:: savepkl2mat")
        savematname = self.session_path.replace("pkl","mat")
        spio.savemat(savematname,self._dataframe2nparray(self.result))
        logger.info("saved %s"%savematname)

    def savesession(self,*args):

        with open(self.session_path,"wb") as f:
            pickle.dump(self.result,f)
        if len(args)==0:
            logger.debug("%s self.result is saved at %s"%self.session_path)
        else:
            logger.info("%s is saved at %s"%(args,self.session_path))


    def generate_timebin(self,timebin=1000):
        self.result["timebin"] = pd.Series([int(np.ceil(i/1000)) for i in self.result["ms_ts"]])
        logger.info("timebin is binned into %s ms"%timebin)
        return self.result["timebin"]

    def play_events_in_behavioral_video(self,):
        """
        we define 'nosepoke,ctx_enter,ctx_exit,choice,r_ctx_enter,r_ctx_exit' as event_points,
        this function help us to quickly check the relative behavioral frame
        """
        if self.exp=="task":
            event_points = np.reshape(self.result["behavelog_time"].to_numpy(),(1,-1))[0]
            be_ts = self.result["behave_track"]["be_ts"].to_numpy()
            frame_points=[find_close_fast(be_ts,i)+1 for i in event_points ]

            Video(self.result["behavevideo"][0]).check_frames(*frame_points)
        else:
            print("homecage session doesn't have behaviral video")

    def play_events_in_miniscope_video(self,miniscope_video_path,forwardframe_num=1):
        """
        miniscope_video_path: batter to te mp4
        forwardframe_num:frames.num to play forward. default to be 1. because 'check_frames' play 1 frame backward
        """
        event_points = np.reshape(self.result["behavelog_time"].to_numpy(),(1,-1))[0]
        be_ts = self.result["aligned_behave2ms"]["be_ts"].to_numpy()
        frame_points=[find_close_fast(be_ts,i)+forwardframe_num for i in event_points ]
        Video(miniscope_video_path).check_frames(*frame_points)




    def align_behave_ms(self,):
        """
        产生 aligned_behave2ms
        注意 有的是行为学视频比较长，有的是miniscope视频比较长，一般是行为学视频比较长
        """
        logger.info("FUN:: aligned_behave2ms")
        if self.exp=="task":
            if not "aligned_behave2ms" in self.result.keys():
                # 为每一帧miniscope数据找到对应的行为学数据并保存  为 aligned_behave2ms
                logger.debug("aligninging behavioral frame to each ms frame...")
                logger.info("looking for behave frame for each corrected_ms_ts...")
                aligned_behave2ms=pd.DataFrame({"corrected_ms_ts": self.result["corrected_ms_ts"]
                                                ,"ms_behaveframe":[find_close_fast(arr=self.result["behave_track"]["be_ts"]*1000,e=k) for k in self.result["corrected_ms_ts"]]})
                _,length = rlc(aligned_behave2ms["ms_behaveframe"])
                # print(length)
                logger.info("for one miniscope frame, there are at most %s behavioral frames "%max(length))

                if max(length)>10:
                    logger.info("********ATTENTION when align_behave_ms**********")
                    logger.info("miniscope video is longer than behavioral video, please check")
                    logger.info("********ATTENTION when align_behave_ms**********")

                aligned_behave2ms = aligned_behave2ms.join(self.result["behave_track"],on="ms_behaveframe")
                
                self.result["aligned_behave2ms"]=aligned_behave2ms

                self.savesession("aligned_behave2ms")

            else:
                logger.debug("behaveiroal timestamps were aligned to ms")

        else:
            logger.debug("this session was recorded in homecage")


    def detect_ca_transients(self,thresh=1.5,baseline=0.8,t_half=0.2,FR=30):
        """
        return ca_transients,celldata_detect, single_cell_detected_transiend. 
        celldata_detect have the same size with df
        """
        logger.debug("detecting calcium transients for each cell")
        self.result["ca_transients"],self.result["ca_transient_detect"],self.result["single_cell_detected_transient"]=detect_ca_transients(self.result["idx_accepted"],self.df.values,thresh,baseline,t_half,FR)
        logger.info("calcium tansients are detected... ")




    def trim_df2(self,df=None,force_neg2zero=True,Normalize=False,standarize=False
        ,Trial_Num=None
        ,in_process=False,process=None
        ,in_context=False,in_lineartrack=False
        ,speed_min = False):
        """
        is about to discrete
        process: list process, for example [0,1,2]
        """
        logger.info("FUN:: trim_df")

        df = self.df if df == None else df
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
            Trial_Num = self.result["Trial_Num"]


        index=pd.DataFrame()
        index["Trial_Num"] = Trial_Num>=0
        logger.info("Trial_Num start from 1")

        if in_process:
            if not process ==None:
                index["in_process"] = self.process.isin(process)
                logger.info("process is limited in %s"%process)
            else:
                logger.warning("process is [None], please specify.")

        if in_context:
            try:
                index["in_context"] = self.result["is_in_context"]
                logger.info("interested zone are restricted 'is_in_context'")
            except:
                logger.warning("is_in_context does not exist")
        if in_lineartrack:
            try:
                index["in_lineartrack"] = self.result["is_in_lineartrack"]
                logger.info("interested zone are restricted 'is_in_lineartrack'")
            except:
                logger.warning("is_in_lineartrack does not exist")

        if speed_min:
            try:
                index["speed_min"] = self.result["Body_speed"]>speed_min
                logger.info("minimum speed are restricted to at least %s cm/s"%speed_min)
            except:
                logger.warning("Body_speed>%s is problemic"%speed_min)
                


        # df = df[index.all(axis=1)]
        # print(index.all(axis=1))
        
        return df, index.all(axis=1)




# if __name__ == "__main__":
#     sessions = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\Results_202016\20200531_165342_0509-0511-Context-Discrimination-30fps\session*.pkl")
#     for session in sessions:
#         S = MiniAna(session)
#         S.savepkl2mat()
if __name__ == "__main__":
    s3 = Cellid(r"C:\Users\Sabri\Desktop\20200531_165342_0509-0511-Context-Discrimination-30fps\session3.pkl")
    print("----")
    print(s3.cellids_Context(s3.result["idx_accepted"]))
    print(s3.cellids_RD_incontext(s3.result["idx_accepted"]))
    print(s3.cellids_PC_incontext(s3.result["idx_accepted"]))