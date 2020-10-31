import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob,csv,re
import json,cv2
import scipy.io as spio
import pickle
from mylab.process.miniscope.Mfunctions import * #load/save pkl/mat/hdf5


import logging 


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler(sys.stdout) #stream handler
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)




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
        self.logfile = os.path.join(self.Result_dir,"pre-process_log.txt")
        self.sessions = glob.glob(os.path.join(self.Result_dir,"session*.pkl"))
        self.sessions.sort(key=lambda x:int(re.findall(r"session(\d+).pkl",x)[0]))
        self.ms_mc_path = os.path.join(self.Result_dir,"ms_mc.mp4")

        fh = logging.FileHandler(self.logfile,mode="a")
        formatter = logging.Formatter("  %(asctime)s %(message)s")
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

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

    def save_session_pkl(self,orders=None):
        """

        """
        if os.path.exists(self.ms_mat_path):        
            logger.debug("loading %s"%self.ms_mat_path)
            ms = load_mat(self.ms_mat_path)
            logger.debug("loaded %s"%self.ms_mat_path)
        else:
            logger.debug("loading %s"%self.ms_mat_path2)
            ms = load_pkl(self.ms_mat_path2)
            logger.debug("loaded %s"%self.ms_mat_path2)

        sigraw = ms['ms']['sigraw'] #默认为sigraw
        try:            
            S_dff = ms['ms']['S_dff']
        except:            
            # read S_dff.pkl
            logger.debug("saving S_dff problem")
            sys.exit(0)


        idx_accepted = ms['ms']['idx_accepted']
        idx_deleeted = ms['ms']['idx_deleted']

        with open(self.ms_ts_path,'rb') as f:
            timestamps = pickle.load(f)
        [print(len(i)) for i in timestamps]
        logger.info("session lenth:%s, timestamps length:%s, sigraw shape:%s"%(len(timestamps),sum([len(i) for i in timestamps]),sigraw.shape))

        # 对不同session的分析先后顺序排序
        if not orders == None:
            timestamps_order = np.array([timestamps[i] for i in np.array(orders)-1])
            [print(len(i)) for i in timestamps_order]
            logger.info("timestamps are sorted by %s"%orders)


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
            logger.debug("%s is saved"%name)



    def show_in_context_masks(self,behavevideo,aim="in_context"):
        mask, coord = Video(behavevideo).draw_rois(aim=aim)

        cap = cv2.VideoCapture(behavevideo)
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES,1000-1)
        except:
            print("video is less than 100 frame")

        ret,frame = cap.read()


        cv2.polylines(frame,coord,True,(0,0,255),2)
        plt.xticks([])
        plt.yticks([])
        plt.axis('off')
        plt.imshow(frame)



if __name__ == "__main__":
    pass