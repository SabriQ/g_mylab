import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob,csv,re
import json,cv2
import scipy.io as spio
import pickle
from mylab.process.miniscope.context_exposure.Mfunctions import *
from mylab.process.miniscope.Mfunctions import *

import logging 


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler(sys.stdout) #stream handler
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

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
        s1["dff"] = np.vstack((s1.get("dff"),s2.get("dff")))
        s1["sigraw"] = np.vstack((s1.get("sigraw"),s2.get("sigraw")))
        s1["idx_accepted"] = s1["idx_accepted"]

        with open(session1,"wb") as f:
            pickle.dump(s1,f)
        print("%s has been merged in %s"%(session2,session1))
        print("you should remove %s"%session2)
    else:
        print("%s is not connected to %s"%(session2,session1))


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
        self.ms_mc_path = os.path.join(self.Result_dir,"ms_mc.avi")

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
        if os.path.exists(self.ms_mat_path):        
            logger.debug("loading %s"%self.ms_mat_path)
            ms = load_mat(self.ms_mat_path)
            logger.debug("loaded %s"%self.ms_mat_path)
        else:
            logger.debug("loading %s"%self.ms_mat_path2)
            ms = load_pkl(self.ms_mat_path2)
            logger.debug("loaded %s"%self.ms_mat_path2)

        try:
            # dff = ms['ms']['dff']
            S_dff = ms['ms']['S_dff']
        except:            
            logger.debug("save S_dff or dff problem")

        sigraw = ms['ms']['sigraw'] #默认为sigraw


        idx_accepted = ms['ms']['idx_accepted']
        idx_deleeted = ms['ms']['idx_deleted']

        with open(self.ms_ts_path,'rb') as f:
            timestamps = pickle.load(f)
        [print(len(i)) for i in timestamps]
        logger.info("session lenth:%s, timestamps length:%s, dff shape:%s"%(len(timestamps),sum([len(i) for i in timestamps]),dff.shape))


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
                "dff":np.transpose(dff)[s[0]:s[1]],
                "S_dff":np.transpose(S_dff)[s[0]:s[1]],
                "sigraw":sigraw[s[0]:s[1]],
                "idx_accepted":idx_accepted
            }

            with open(os.path.join(self.Result_dir,name),'wb') as f:
                pickle.dump(result,f)
            logger.debug("%s is saved"%name)


    def save_session_pkl2(self):
        if os.path.exists(self.ms_mat_path):        
            logger.debug("loading %s"%self.ms_mat_path)
            ms = load_mat(self.ms_mat_path)
            logger.debug("loaded %s"%self.ms_mat_path)
        else:
            logger.debug("loading %s"%self.ms_mat_path2)
            ms = load_pkl(self.ms_mat_path2)
            logger.debug("loaded %s"%self.ms_mat_path2)

        try:
            dff = ms['ms']['dff']
        except:
            dff = ms['ms']['S_dff']
            logger.debug("save S_dff as dff")
        sigraw = ms['ms']['sigraw'] #默认为sigraw
        idx_accepted = ms['ms']['idx_accepted']
        idx_deleeted = ms['ms']['idx_deleted']

        with open(self.ms_ts_path,'rb') as f:
            timestamps = pickle.load(f)

        logger.info("timestamps length:%s, dff shape:%s"%(sum([len(i) for i in timestamps]),dff.shape))

        #根据timestamps将dff切成对应的session
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
            logger.debug("%s is saved"%name)

    def show_masks(self,behavevideo,aim="in_context"):
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



    def save_behave_pkl(self,behavevideo
        ,logfilepath = r"C:\Users\qiushou\OneDrive\miniscope_2\202016\starts_firstnp_stops.csv"):
        logger.info("FUN:: save_behave_pkl")
        key = str(re.findall('\d{8}-\d{6}',behavevideo)[0])
        mark = starts_firstnp_stops(logfilepath)

        _,start,first_np,mark_point,stop = mark(behavevideo)
        # index log file
        behave_log =[i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*log*")) if key in i][0]
        log = pd.read_csv(behave_log,skiprows=3)
        behavelog_time = log.iloc[:,12:]-min(log["P_nose_poke"])
        behavelog_info = log.iloc[:,:6]
        logger.info("correct 'behavelog_time' when the first_np as 0")

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
            delta_t = ts[0][first_np-1]-behavelog_time["P_nose_poke"][0]
        
        ## 这里有时候因为first-np的灯刚好被手遮住，所以用第二个点的信号代替，即第一次enter_ctx的时间
        if mark_point == 2:
            delta_t = ts[0][first_np-1]-behavelog_time["P_enter"][0]

        behave_track['be_ts']=ts[0]-delta_t

        logger.info("correct 'be_ts' when the first_np as 0")
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
        logger.debug("%s get saved"%savename)



    def save_alinged_session_pkl(self,session_tasks= ['hc','test','hc','test','train']):
        """
        产生 corrected_ms_ts
        """
        # index behave*.pkl
        logger.info("FUN:: save_alinged_session_pkl")
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

        ## 产生“corrected_ms_ts”
        for behave_info, task_ms_info in zip(behave_infos,task_ms_infos):
            ## 读取行为学beha_session
            with open(behave_info,'rb') as f:
                behave_result = pickle.load(f)

            behavevideo,key,start,first_np,mark_point,stop = behave_result["behavevideo"]

            ## 读取有行为学的ms_session
            with open(task_ms_info,'rb') as f:
                task_ms_result = pickle.load(f)
            #行为学视频中的start,first_np,stop分别是哪一帧，哪一个行为学时间戳
            print("behavevideo %s start at %s,first_np at %s,stop at %s frame, the corresponding timestamps are: " %(key,start,first_np,stop))
            print(behave_result["behave_track"]["be_ts"][start-1],behave_result["behave_track"]["be_ts"][first_np-1],behave_result["behave_track"]["be_ts"][stop-1])

            #行为学中miniscope亮灯的总时长和 miniscope记录的总时长
            logger.info("total time elaspse in 'behavioral video' and 'miniscope video': ****ATTENTION****")
            t1 = behave_result["behave_track"]["be_ts"][stop-1]-behave_result["behave_track"]["be_ts"][start-1]
            logger.info(t1)
            logger.info(max(task_ms_result["ms_ts"])) #这部分不能相差太多

            # 以行为学视频中，miniscope-led灯亮后的100ms为起始0点
            delta_t = 0-(behave_result["behave_track"]["be_ts"][start-1]) # 这个0.1大约是启动时间

            task_ms_result["corrected_ms_ts"] = task_ms_result["ms_ts"]-delta_t*1000
            logger.info("'corrected_ms_ts' corrected 'ms_ts' when first_np as 0")

            with open(task_ms_info,'wb') as f:
                pickle.dump(dict(task_ms_result,**behave_result),f)
        
            logger.debug("corrected ms_ts and behavioral result are saved %s"%task_ms_info)
            print("---------------------")
        #     print(task_ms_result["ms_ts"])
        #     sys.exit()
        print("=========================")


    def add_TrialNum_Process2behave_track(self,session):
        """
        在session*.pkl中的behave_tracek 加上“Trial_Num”,"process"
        """
        logger.info("FUN:: add_TrialNum_Process2behave_track")
        with open(session,'rb') as f:
            ms_result = pickle.load(f)

        if "behavelog_time" in ms_result.keys():
            #提取每一个trial的start和stop ，并产生对应的Trial_Num ,process
            temp = ms_result["behavelog_time"]
            # np.diff(np.insert(temp.values.reshape(1,-1),0,0)).reshape(10,6).shape
            starts = np.insert(temp.values.reshape(1,-1),0,0)[0:-1]
            stops = temp.values.reshape(1,-1)[0]
            startstops=[]
            i=1
            for start,stop in zip(starts,stops):
                # startstops structure:[(Trial,process,start,stop),etc]
                startstops.append((int(np.ceil(i/6)),(i-1)%6,start,stop))
                i = i+1
                #Trial 从1开始，process从0开始
            #将Trial_Num,process 写进behave_track
            Trial_Num = []
            process = []
            for i in ms_result["behave_track"]["be_ts"]:
                if i < startstops[0][2] or i >startstops[-1][3]: # 小于第一个startstop的开始或者大于最后一个startstop的结束
                    Trial_Num.append(-1)
                    process.append(-1)
                else:
                    for startstop in startstops:
                        if i>=startstop[2] and i <startstop[3]:
                            Trial_Num.append(startstop[0])
                            process.append(startstop[1])
                            break
                        else:
                            pass

            ms_result["behave_track"]["Trial_Num"]=Trial_Num
            ms_result["behave_track"]["process"]=process
            logger.info("Trial_Num,process here are the same length as behavioral data,not the final version")
            with open(session,'wb') as f:
                pickle.dump(ms_result,f)
            print("%s is updated and saved"%session)
        else:
            print("%s is recorded in homecage"%session)





if __name__ == "__main__":
    pass