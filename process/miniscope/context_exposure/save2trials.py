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


# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# sh = logging.StreamHandler(sys.stdout) #stream handler
# sh.setLevel(logging.INFO)
# logger.addHandler(sh)

class MiniAna():
    def __init__(self,session_path):
        self.session_path=session_path

        # self.logfile =self.session_path.replace('.pkl','_log.txt')
        # fh = logging.FileHandler(self.logfile,mode="a")
        # formatter = logging.Formatter("  %(asctime)s %(message)s")
        # fh.setFormatter(formatter)
        # fh.setLevel(logging.DEBUG)
        # logger.addHandler(fh)

        self._load_session()
        # self.align_behave_ms() # self.result["Trial_Num"], self.process
        print("default 'sigraw' is taken as original self.df")
        self.df = pd.DataFrame(self.result["sigraw"][:,self.result["idx_accepted"]],columns=self.result["idx_accepted"])
        self.shape = self.df.shape

    def _load_session(self):
        print("FUN:: _load_session")
        print("loading %s"%self.session_path)
        with open(self.session_path,"rb") as f:
            self.result = pickle.load(f)

        if not "exp" in self.result.keys():
            self.exp = "hc"
        else:
            self.exp = self.result["exp"]
        print("loaded")
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
        print("FUN:: savepkl2mat")
        savematname = self.session_path.replace("pkl","mat")
        spio.savemat(savematname,self._dataframe2nparray(self.result))
        print("saved %s"%savematname)

    def savesession(self,*args):

        with open(self.session_path,"wb") as f:
            pickle.dump(self.result,f)
        if len(args)==0:
            print("%s self.result is saved at %s"%self.session_path)
        else:
            print("%s is saved at %s"%(args,self.session_path))


    def generate_timebin(self,timebin=1000):
        self.result["timebin"] = pd.Series([int(np.ceil(i/1000)) for i in self.result["ms_ts"]])
        print("timebin is binned into %s ms"%timebin)
        return self.result["timebin"]

    def play_events_in_behavioral_video(self,):
        """
        we define 'nosepoke,ctx_enter,ctx_exit,choice,r_ctx_enter,r_ctx_exit' as event_points,
        this function help us to quickly check the relative behavioral frame
        """
        if not self.exp=="hc":
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



    def add_c_behavevideoframe(self,behavevideo=None,frame=999):
        """
        which is moved to context_exposure/Cminiresult, and is about to discrete
        """
        print("FUN::add_c_behavevideoframe")
        if not "behavevideoframe" in self.result.keys() and frame==999:
            behavevideo = self.result["behavevideo"][0] if behavevideo==None else behavevideo
            cap = cv2.VideoCapture(behavevideo)
            try:
                cap.set(cv2.CAP_PROP_POS_FRAMES,frame)
            except:
                print("video is less than 100 frame")

            ret,frame = cap.read()
            cap.release()
            self.result["behavevideoframe"]=frame
            self.savesession("all_track_points")
            # print("behavevideoframe was saved")
        else:
            print("behavevideoframe has been there.")
            
    def add_c_all_track_points(self,behavevideo=None):
        """
        add 7 ponits with behavevideo frame for generating placebins later
        """
        print("FUN:: add_c_all_track_points")
        if not self.exp == "hc":
            if not "all_track_points" in self.result.keys():
                behavevideo = self.result["behavevideo"][0] if behavevideo == None else behavevideo
                coords = LT_Videos(behavevideo).draw_midline_of_whole_track_for_each_day(aim="midline_of_track",count=7)
                self.result["all_track_points"] = coords
                self.savesession("all_track_points")
            else:
                print("all_track_points has been there")





def divide_sessions_into_trials(session_path
    ,savedir=r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\results\trials"
    ,update=False):
    """
    Arguments:

    session_path: path of each session after aligned. e.g.
        r"...\batch3\Results_201033-finish\part1\session2.pkl"
    savedir:
    update: if True, then regenerate the trials or jump the trial if it was once generated

    Returns:
        save trial as pkl files. No returns.
    """
    mouse_id1 = re.findall("Results_(\d+)",session_path)[0]
    part = re.findall("part(\d+)",session_path)[0]
    session_num = re.findall("session(\d+).pkl",session_path)[0]

    s = MiniAna(session_path)
    if not s.exp == "hc":        

        videoname = s.result["behavevideo"][0]

        mouse_id2 = re.findall("(\d+)-\d{8}-\d{6}.mp4",videoname)[0]
        key_index = s.result["behavevideo"][1]
        aim=s.result["exp"]

        if mouse_id1 == mouse_id2:
            mouse_id = mouse_id1

        tirals = []
        s.add_c_behavevideoframe()
        s.add_c_all_track_points()
        trial_list= [i for i in set(s.result["aligned_behave2ms"]["Trial_Num"]) if not i==-1] 

        for trial in trial_list :
            savepath = os.path.join(savedir,"%s_part%s_index%s_session%s_aim_%s_trial%s.pkl"%(mouse_id,part,key_index,session_num,s.exp,trial))
            if os.path.exists(savepath):
                if update:
                    pass
                else:
                    print("%s exists. JUMP!"%os.path.basename(savepath))
                    break
                
            info={
                "mouse_id":mouse_id,
                "part":part,
                "session_num":session_num,
                "aim":aim,
                "index":key_index,
                "Trial_Num":trial,
                "behavevideoframe":s.result["behavevideoframe"],
                "all_track_points":s.result["all_track_points"]
                }

            index = s.result["aligned_behave2ms"]["Trial_Num"]==trial

            miniscope={
                "idx_accepted":s.result["idx_accepted"],
                "S_dff":s.result["S_dff"][index],
                "sigraw":s.result["sigraw"][index],
                "corrected_ms_ts":s.result["corrected_ms_ts"][index]
                }

            behavior={
                "track":s.result["aligned_behave2ms"][index],
                "loginfo":s.result["behavelog_info"][s.result["behavelog_info"]["Trial_Num"]==trial],
                "logtime":s.result["behavelog_time"].loc[trial-1]}

            quality={
                "quality":s.result["quality"]
            }

            Trial = {
            "info":info,
            "miniscope":miniscope,
            "behavior":behavior,
            "quality":quality
            }

            

            with open(savepath,'wb') as f:
                pickle.dump(Trial,f)
            print("Trial is saved at %s"% savepath)

    else:
        print("homecage session")
        savepath = os.path.join(savedir,"%s_part%s_session%s_hc.pkl"%(mouse_id1,part,session_num))
        if os.path.exists(savepath):
            print("%s exists"%os.path.basename(savepath))
        else:
            with open(savepath,'wb') as f:
                pickle.dump(s.result,f)
            print("homecage session is saved at %s"% savepath)

        

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