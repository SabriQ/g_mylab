import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob,csv
import json
import scipy.io as spio
import pickle
from mylab.Cmouseinfo import MouseInfo
from mylab.process.miniscope.context_exposure.Mfunctions import *
from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.context_exposure.Mplot import *


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

    def save_session_pkl(self):
        ms = load_mat(self.ms_mat_path)
        print("load %s"%self.ms_mat_path)
        dff = ms['ms']['dff']
        sigraw = ms['ms']['sigraw']
        idx_accepted = ms['ms']['idx_accepted']
        idx_deleeted = ms['ms']['idx_deleted']

        with open(self.ms_ts_path,'rb') as f:
            timestamps = pickle.load(f)

        print("timestamps length:%s, dff shape:%s"%(sum([len(i) for i in timestamps]),dff.shape))

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
        print(slice)

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
            print("%s is saved"%name)

    def save_behave_pkl(self,behavevideo,logfilepath = r"C:\Users\Sabri\Desktop\miniscope_1\202016\starts_firstnp_stops.csv"):

        key = str(re.findall('\d{8}-\d{6}',behavevideo)[0])
        mark = starts_firstnp_stops(logfilepath)

        _,start,first_np,mark_point,stop = mark(behavevideo)
        # index log file
        behave_log =[i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*log*")) if key in i][0]
        log = pd.read_csv(behave_log,skiprows=3)
        behavelog_time = log.iloc[:,12:]-min(log["P_nose_poke"])
        behavelog_info = log.iloc[:,:6]


        # index track file
        behave_track = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*DLC*h5")) if key in i][0]    
        track = pd.read_hdf(behave_track)
        behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                     columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
        
        
        # index timestamps file
        behave_ts = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*_ts.txt*")) if key in i][0]
        ts = pd.read_table(behave_ts,sep='\n',header=None,encoding='utf-16-le')
        
        # aligned log_time and behave video_time
        if mark_point  == 1:
            delta_t = ts[0][first_frame-1]-behavelog_time["P_nose_poke"][0]
            
        ## 这里有时候因为first-np的灯刚好被手遮住，所以用第二个点的信号代替，即第一次enter_ctx的时间
        if mark_point == 2:
            delta_t = ts[0][first_frame-1]-behavelog_time["P_enter"][0]
        behave_track['be_ts']=ts[0]-delta_t
        
        # index in_context
        print(behavevideo)
        in_context_mask,in_context_coords=Video(behavevideo).draw_rois(aim="in_context",count = 1)

        # index in_lineartrack
        in_lineartrack_mask,in_lineartrack_coords=Video(behavevideo).draw_rois(aim="in_lineartrack",count = 1)

        result = {"behavevideo":[behavevideo,key,start,first_np,mark_point,stop]
                  ,"behavelog_time":behavelog_time
                  ,"behavelog_info":behavelog_info
                  ,"behave_track":behave_track
                  ,"in_context_mask":in_context_mask[0]
                  ,"in_context_coords":in_context_coords[0]
                 ,"in_lineartrack_mask":in_lineartrack_mask[0]
                 ,"in_lineartrack_coords":in_lineartrack_coords[0]}

        savename = os.path.join(self.Result_dir,"behave_"+str(key)+".pkl")
        with open(savename,'wb') as f:
            pickle.dump(result,f)
        print("%s get saved"%savename)



    def save_alinged_session_pkl(self,session_tasks= ['hc','test','hc','test','train'],logfilepath = r"C:\Users\Sabri\Desktop\miniscope_1\202016\starts_firstnp_stops.csv"):

        # index behave*.pkl
        behave_infos = glob.glob(os.path.join(self.Result_dir,"behave*"))

        # indx session*.pkl
        ms_sessions = glob.glob(os.path.join(self.Result_dir,"session*.pkl"))
        def order(s):
            return int(re.findall('session(\d+)',s)[0])
        ms_sessions.sort(key=order)
        print("all ms sessions:")
        [print(i) for i in ms_sessions]
        ## index non-hc-task
        task_ms_infos = [ms_session  for (session_task,ms_session) in zip(session_tasks,ms_sessions) if session_task != "hc"] 
        print("non-hc-task ms:")
        [print(i) for i in task_ms_infos]

        for behave_info, task_ms_info in zip(behave_infos,task_ms_infos):
            with open(behave_info,'rb') as f:
                behave_result = pickle.load(f)
            behavevideo,key,start,first_np,mark_point,stop = behave_result["behavevideo"]
            with open(task_ms_info,'rb') as f:
                task_ms_result = pickle.load(f)
            #miniscope 的开始帧是行为学的哪一个时间点
            print("frame number of [behavevideo,key,start,first_np,mark_point,stop] in behavioral video is:%s:"%behave_result["behavevideo"])
            print(behave_result["behave_track"]["be_ts"][led_info[1]-1],behave_result["behave_track"]["be_ts"][led_info[2]-1])