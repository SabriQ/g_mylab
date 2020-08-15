import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob,csv
import json
import scipy.io as spio
import pickle
from mylab.Cmouseinfo import MouseInfo
from mylab.process.miniscope.context_exposure.Mfunctions import *
from mylab.process.miniscope.Mfunctions import *

import logging 
import sys,os

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
        self.ms_ts_path = os.path.join(self.Result_dir,"ms_ts.pkl")
        self.resulthdf5 =  os.path.join(self.Result_dir,"result.hdf5")
        self.logfile = os.path.join(self.Result_dir,"pre-process_log.txt")

        fh = logging.FileHandler(self.logfile,mode="a")
        formatter = logging.Formatter("  %(asctime)s --> %(message)s")
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)


    def save_session_pkl(self):
        ms = load_mat(self.ms_mat_path)
        logger.debug("load %s"%self.ms_mat_path)
        dff = ms['ms']['dff']
        sigraw = ms['ms']['sigraw'] #默认为sigraw
        idx_accepted = ms['ms']['idx_accepted']
        idx_deleeted = ms['ms']['idx_deleted']

        with open(self.ms_ts_path,'rb') as f:
            timestamps = pickle.load(f)

        logger.info("timestamps length:%s, dff shape:%s"%(sum([len(i) for i in timestamps]),dff.shape))

        #根据timestamps讲dff切成对应的session
        slice = []
        for i,timestamp in enumerate(timestamps):
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

        for i,s in enumerate(slice,1):
            name = "session"+str(i)+".pkl"
            result = {
                "ms_ts":timestamps[i-1],
                "dff":np.transpose(dff)[s[0]:s[1]],
                "sigraw":sigraw[s[0]:s[1]],
                "idx_accepted":idx_accepted
            }

            with open(os.path.join(self.Result_dir,name),'wb') as f:
                pickle.dump(result,f)
            logger.info("%s is saved"%name)

    def save_behave_pkl(self,behavevideo,miniscope_start_frame,session_name,delta_t=0.1):
        """
        behavevideo
        miniscope_start_frame
        session_name
        delta_t: we think miniscope on was 0.1s later than led on
        """
        key = str(re.findall('(\d{13}).AVI',behavevideo)[0])


        # index track file
        behave_track = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*DLC*h5")) if key in i][0]    
        track = pd.read_hdf(behave_track)
        behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                     columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
        
        
        # index timestamps file
        behave_ts = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*_ts.txt*")) if key in i][0]
        ts = pd.read_table(behave_ts,sep='\n',header=None,encoding='utf-16-le')
        logger.info("led suggesting start of miniscope was turned on at %s frame"%miniscope_start_frame)
        
        behave_track['be_ts']=ts[0]-ts[0][miniscope_start_frame]-delta_t
        logger.info("we set the timestamp when miniscope started to record as 0,'be_ts' was the behavioral timestamps which had beed aligned to miniscope timestamps")
        logger.info("delta_t is %s"%delta_t)
        result = {"behavevideo":[behavevideo]
                  ,"session_name":session_name
                  ,"miniscope_start_frame":miniscope_start_frame
                  ,"behave_track":behave_track}

        savename = os.path.join(self.Result_dir,"behave_"+str(key)+".pkl")
        with open(savename,'wb') as f:
            pickle.dump(result,f)
        logger.info("%s get saved"%savename)




    def savepkl2mat(self,session):
        with open(session,'rb') as f:
            result = pickle.load(f)
        savematname = session.replace("pkl","mat")
        spio.savemat(savematname,result)
        print("saved %s"%savematname)






