import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob,csv,re
import json,cv2
import scipy.io as spio
from scipy.io import savemat
import pickle
from mylab.process.miniscope.Mfunctions import * #load/save pkl/mat/hdf5


# import logging 


# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# sh = logging.StreamHandler(sys.stdout) #stream handler
# sh.setLevel(logging.DEBUG)
# logger.addHandler(sh)

def concatenate_sessions(session1,session2):
    """
    仅限于记录时有多个sessions但是只有一个behavioral video的情况
    """
    with open(session1,"rb") as f:
        s1 = pickle.load(f)
    with open(session2,"rb") as f:
        s2 = pickle.load(f)


    if (s1["idx_accepted"]==s2["idx_accepted"]).all():
        s1["ms_ts"] = np.concatenate((s1["ms_ts"],s2["ms_ts"]+s1["ms_ts"].max()+33),axis=0)
        s1["S_dff"] = np.vstack((s1.get("S_dff"),s2.get("S_dff")))
        s1["sigraw"] = np.vstack((s1.get("sigraw"),s2.get("sigraw")))
        s1["idx_accepted"] = s1["idx_accepted"]

        with open(session1,"wb") as f:
            pickle.dump(s1,f)
        print("%s has been merged in %s"%(session2,session1))
        print("you should remove %s"%session2)
        os.remove(session2)
    else:
        print("%s is not connected to %s"%(session2,session1))


def ms_tses2ms_ts(dirpath):
    """
    将每天的ms_ts.pkl合并成一个ms_ts.mat/ms_ts.pkl
    """
    ms_tses = glob.glob(os.path.join(dirpath,"*[0-9]/ms_ts.pkl"))
    [print(i) for i in ms_tses]
    mss = []
    for ms_ts in ms_tses:
        with open(ms_ts,"rb") as f:
            ms = pickle.load(f)
        print(len(ms))
        [mss.append(i) for i in ms]
    print(len(mss))
    pklpath=os.path.join(dirpath,"ms_ts.pkl")
    matpath=os.path.join(dirpath,"ms_ts.mat")

    savemat(matpath,{'ms_ts':np.array(mss)})

    with open(pklpath,"wb") as output:
        pickle.dump(mss,output)

    print("concate all the ms_ts and saved")

class MiniResult():
    """
    to generate file such as "behave_20200509-160744.pkl",session*.pkl"
    This father class is to 
        1.load MiniResult through reading pkl,mat or hdf5 file 
        2.load/save mouseinfo
    """
    def __init__(self,Result_dir):
        self.Result_dir = Result_dir

        self.ms_mat_path = os.path.join(self.Result_dir,"ms.mat")
        self.ms_mat_path2 = os.path.join(self.Result_dir,"ms.pkl")
        self.ms_ts_path = os.path.join(self.Result_dir,"ms_ts.pkl")
        self.resulthdf5 =  os.path.join(self.Result_dir,"result.hdf5")

        self.ms_mc_path = os.path.join(self.Result_dir,"ms_mc.mp4")
        self.S_dff_path = os.path.join(self.Result_dir,"S_dff.pkl")

        # fh = logging.FileHandler(self.logfile,mode="a")
        # formatter = logging.Formatter("  %(asctime)s %(message)s")
        # fh.setFormatter(formatter)
        # fh.setLevel(logging.INFO)
        # logger.addHandler(fh)
    @property
    def sessions(self):
        sessions = glob.glob(os.path.join(self.Result_dir,"session*.pkl"))
        sessions.sort(key=lambda x:int(re.findall(r"session(\d+).pkl",x)[0]))
        return sessions

    def frame_num(self):
        if os.path.exists(self.ms_mc_path):
            videoframe_num = int(cv2.VideoCapture(self.ms_mc_path).get(7))
            print("the length of miniscope video is %d"%videoframe_num)
        else:
            print("there is no %s"%self.ms_mc_path)
            sys.exit()

        with open(self.ms_ts_path,'rb') as f:
            ms_tss = pickle.load(f)
        ms_ts_num = int(sum([len(i) for i in ms_tss]))
        print("the length of ms_ts is %d"%ms_ts_num)

        if videoframe_num == ms_ts_num:
            return 1
        else:
            return 0 



    def save_miniscope_session_pkl(self,orders=None,jump=False):
        """

        """
        print("FUN:: save_miniscope_session_pkl")
        try:
            print("loading %s"%self.ms_mat_path)
            ms = load_mat(self.ms_mat_path)
            print("loaded %s"%self.ms_mat_path)
        except:
            print("loading %s"%self.ms_mat_path2)
            ms = load_pkl(self.ms_mat_path2)
            print("loaded %s"%self.ms_mat_path2)

        sigraw = ms['ms']['sigraw'] #默认为sigraw
        try:            
            S_dff = ms['ms']['S_dff']
        except:            
            try:
                S_dff = load_pkl(self.S_dff_path)
            except:
                print("saving S_dff problem,is there S_dff.pkl in directory?")
                sys.exit()

        idx_accepted = ms['ms']['idx_accepted']
        idx_deleeted = ms['ms']['idx_deleted']

        with open(self.ms_ts_path,'rb') as f:
            timestamps = pickle.load(f)
        [print(len(i)) for i in timestamps]

        if not sum([len(i) for i in timestamps]) == sigraw.shape[0]:
            print("timestamps length:%s, sigraw shape:%s"%(sum([len(i) for i in timestamps]),sigraw.shape))
            print("not equal")
            if not jump:
                return -1
            else:
                print("jump")
        

        # 对不同session的分析先后顺序排序
        orders = list(np.arange(1,len(timestamps)+1)) if orders == None else orders

        timestamps_order = np.array([timestamps[i] for i in np.array(orders)-1])
        # [print(len(i)) for i in timestamps_order]
        print("timestamps are sorted by %s"%orders)

        #根据timestamps将dff切成对应的session
        slice = []
        for i,timestamp in enumerate(timestamps_order):
            if i == 0:
                start = 0
                stop = len(timestamp)
                slice.append((start,stop))
            else:
                start = slice[i-1][1]
                stop = start+len(timestamp)
        #         if i == len(timestamps)-1:
        #             stop = -1
                slice.append((start,stop))
        # print(slice)

        for s,i in zip(slice,orders):
            name = "session"+str(i)+".pkl"
            result = {
                "ms_ts":timestamps[i-1],
                "S_dff":np.transpose(S_dff)[s[0]:s[1]],
                "sigraw":sigraw[s[0]:s[1]],
                "idx_accepted":idx_accepted
            }

            with open(os.path.join(self.Result_dir,name),'wb') as f:
                pickle.dump(result,f)
            print("%s is saved"%name)







if __name__ == "__main__":
    pass