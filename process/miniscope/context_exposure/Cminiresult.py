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
        self.ms_ts_path = os.path.join(self.Result_dir,"ms_ts.pkl")
        self.resulthdf5 =  os.path.join(self.Result_dir,"result.hdf5")
        self.logfile = os.path.join(self.Result_dir,"pre-process_log.txt")

        fh = logging.FileHandler(self.logfile,mode="w")
        formatter = logging.Formatter("  %(asctime)s %(message)s")
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
            logger.debug("%s is saved"%name)

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
        logger.debug("%s get saved"%savename)



    def save_alinged_session_pkl(self,session_tasks= ['hc','test','hc','test','train']):
        """
        产生 corrected_ms_ts
        """
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
            logger.info("total time elaspse in 'behavioral video' and 'miniscope vidoe': ****ATTENTION****")
            logger.info(behave_result["behave_track"]["be_ts"][stop-1]-behave_result["behave_track"]["be_ts"][start-1],end=" ")
            logger.info(max(task_ms_result["ms_ts"])) #这部分不能相差太多

            # 以行为学视频中，miniscope-led灯亮后的100ms为起始0点
            delta_t = 0-behave_result["behave_track"]["be_ts"][start-1]-0.1 # 这个0.1大约是启动时间
            logger.info("miniscope timestamps delta_t:%s"%delta_t)
            task_ms_result["corrected_ms_ts"] = task_ms_result["ms_ts"]-delta_t*1000

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
    #                         continue #2020-07-16 13:16:00 更改为break,应该会节省一些时间
                            break
                        else:
                            pass

            ms_result["behave_track"]["Trial_Num"]=Trial_Num
            ms_result["behave_track"]["process"]=process

            with open(session,'wb') as f:
                pickle.dump(ms_result,f)
            print("%s is updated and saved"%session)
        else:
            print("%s is recorded in homecage"%session)


    def align_behave_ms(self,ms_session,scale=0.2339021309714166):
        """
        产生 aligned_behave2ms
        注意 有的是行为学视频比较长，有的是miniscope视频比较长，一般是行为学视频比较长
        """
    #     scale = 0.2339021309714166 #cm/pixel 40cm的台子，202016，202017.202019适用
        with open(ms_session,'rb') as f:
            result = pickle.load(f)
        if "behave_track" in result.keys():

            # 为每一帧miniscope数据找到对应的行为学数据并保存  为 aligned_behave2ms
            print("aligninging behavioral frame to each ms frame...")
            aligned_behave2ms=pd.DataFrame({"corrected_ms_ts":result["corrected_ms_ts"]
                                            ,"ms_behaveframe":[find_close_fast(arr=result["behave_track"]["be_ts"]*1000,e=k) for k in result["corrected_ms_ts"]]})

            _,length = rlc(aligned_behave2ms["aligned_behave2ms"])
            print("max length of the same behave frame in one mini frame: %s"%max(length))
            if max(length)>10:
                print("********ATTENTION**********")
                print("miniscope frame is longer than behavioral video, please check")
                print("********ATTENTION**********")
            aligned_behave2ms = aligned_behave2ms.join(result["behave_track"],on="ms_behaveframe")
            result["aligned_behave2ms"]=aligned_behave2ms
            with open(ms_session,'wb') as f:
                pickle.dump(result,f)
            print("aligned_behave2ms is saved %s" %ms_session)

        else:
            print("this session was recorded in homecage")


    def add_zone2result(self,ms_session,zone="in_lineartrack"):
        with open(ms_session,'rb') as f:
            result = pickle.load(f)
        mask = zone+"_mask"
        coords = zone+"_coords"
        if not mask in result.keys():
            temp_mask,temp_coords=Video(behavevideo).draw_rois(aim=zone,count = 1)

            result[mask]=temp_mask
            result[coords]=temp_coords

            with open(ms_session,'wb') as f:
                pickle.dump(result,f)
            print("%s is saved"%zone)
        else:
            print("%s is already there"%zone)

    def savepkl2mat(self,session):
        with open(session,'rb') as f:
            result = pickle.load(f)
        savematname = session.replace("pkl","mat")
        spio.savemat(savematname,result)
        print("saved %s"%savematname)

