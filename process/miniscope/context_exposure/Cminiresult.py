import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob,csv,re
import json,cv2
import scipy.io as spio
import pickle
from mylab.process.miniscope.context_exposure.Mfunctions import *  # starts_firstnp_stops
from mylab.Functions import *
from mylab.process.miniscope.Cminiresult import *

import logging 





class MiniResult(MiniResult):
    """
    to generate file such as "behave_20200509-160744.pkl",session*.pkl"
    This father class is to 
        1.load MiniResult through reading pkl,mat or hdf5 file 
        2.load/save mouseinfo
    """
    def __init__(self,Result_dir):
        super().__init__(Result_dir)




    def save_behave_session(self,behavevideo,logfilepath = r"C:\Users\qiushou\OneDrive\miniscope_2\202016\starts_firstnp_stops.csv"):
        """
        save log, track, timestamp as behavesession according to behavevideo, 
        and add Trial_Num and process to each frame of the track according to behave log
        """

        print("FUN:: save_behave_session")


        key = str(re.findall('\d{8}-\d{6}',behavevideo)[0])
        mark = starts_firstnp_stops(logfilepath)

        _,start_frame,first_np_frame,mark_point,stop_frame = mark(behavevideo)

        #save a frame of behavioral video
        cap = cv2.VideoCapture(behavevideo)
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES,1000-1)
        except:
            print("video is less than 100 frame")

        ret,frame = cap.read()
        cap.release()

    
        # index log file
        behave_log =[i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*log*")) if key in i][0]
        log = pd.read_csv(behave_log,skiprows=3)
        behavelog_time = log.iloc[:,12:]-min(log["P_nose_poke"])
        behavelog_info = log.iloc[:,:6]
        print("correct 'behavelog_time' when the first_np as 0")

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
            delta_t = ts[0][first_np_frame-1]-behavelog_time["P_nose_poke"][0]
        
        ## 这里有时候因为first-np的灯刚好被手遮住，所以用第二个点的信号代替，即第一次enter_ctx的时间
        if mark_point == 2:
            delta_t = ts[0][first_np_frame-1]-behavelog_time["P_enter"][0]

        behave_track['be_ts']=ts[0]-delta_t

        print("correct 'be_ts' when the first_np as 0")

        # add Trial_Num and process
        # np.diff(np.insert(temp.values.reshape(1,-1),0,0)).reshape(10,6).shape
        starts = np.insert(behavelog_time.values.reshape(1,-1),0,0)[0:-1]
        stops = behavelog_time.values.reshape(1,-1)[0]
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
        for i in behave_track["be_ts"]:
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

        behave_track["Trial_Num"]=Trial_Num
        behave_track["process"]=process
        print("Trial_Num and process has been added to behave_track")

        # index in_context
        in_context_mask,in_context_coords=Video(behavevideo).draw_rois(aim="in_context",count = 1)

        # index in_lineartrack
        in_lineartrack_mask,in_lineartrack_coords=Video(behavevideo).draw_rois(aim="in_lineartrack",count = 1)

        result = {"behavevideo":[behavevideo,key,start_frame,first_np_frame,mark_point,stop_frame]
                  ,"behavevideoframe":frame
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



    def save_aligned_session_pkl(self,session_tasks= ['hc','test','hc','test','train']):
        """
        产生 corrected_ms_ts,integrate behave session into miniscope session
        """
        # index behave*.pkl
        print("FUN:: save_alinged_session_pkl")
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

        if not len(behave_infos) == len(task_ms_infos):
            print("non-hc-task is not the same length to bahavioral session")
            sys.exit()

        ## 产生“corrected_ms_ts”
        nonhc_session_tasks = [i for i in session_tasks if i!="hc"]
        for behave_info, task_ms_info,task in zip(behave_infos,task_ms_infos,nonhc_session_tasks):
            ## 读取行为学beha_session
            with open(behave_info,'rb') as f:
                behave_result = pickle.load(f)

            behavevideo,key,start,first_np,mark_point,stop = behave_result["behavevideo"]

            ## 读取有行为学的ms_session
            with open(task_ms_info,'rb') as f:
                ms_result = pickle.load(f)
                ms_result["exp"] = task

            #行为学中miniscope亮灯的总时长和 miniscope记录的总时长
            print("total time elaspse in 'behavioral video' and 'miniscope video': ****ATTENTION****")
            t1 = behave_result["behave_track"]["be_ts"][stop-1]-behave_result["behave_track"]["be_ts"][start-1]
            print(t1)
            print(max(ms_result["ms_ts"])/1000) #这部分不能相差太多

            # 以行为学视频中，miniscope-led灯亮(或其后的100ms)为起始0点
            delta_t = 0-(behave_result["behave_track"]["be_ts"][start-1]) 

            ms_result["corrected_ms_ts"] = ms_result["ms_ts"]-delta_t*1000
            print("corrected ms_ts and behavioral result are saved %s"%task_ms_info)


            #=================================


            #提取每一个trial的start和stop ，并产生对应的Trial_Num ,process
            temp = behave_result["behavelog_time"]
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
            for i in behave_result["behave_track"]["be_ts"]:
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

            behave_result["behave_track"]["Trial_Num"]=Trial_Num
            behave_result["behave_track"]["process"]=process
            print("Trial_Num,process here are the same length as behavioral data,not the final version")

            #%%===========align_behave_ms========================

            # 为每一帧miniscope数据找到对应的行为学数据并保存  为 aligned_behave2ms
            print("aligninging behavioral frame to each ms frame...")
            print("looking for behave frame for each corrected_ms_ts...")
            aligned_behave2ms=pd.DataFrame({"corrected_ms_ts": ms_result["corrected_ms_ts"]
                                            ,"ms_behaveframe":[find_close_fast(arr=behave_result["behave_track"]["be_ts"]*1000,e=k) for k in ms_result["corrected_ms_ts"]]})
            _,length = rlc(aligned_behave2ms["ms_behaveframe"])
            # print(length)
            print("for one miniscope frame, there are at most %s behavioral frames "%max(length))

            if max(length)>10:
                print("********ATTENTION when align_behave_ms**********")
                print("miniscope video is longer than behavioral video, please check")
                print("********ATTENTION when align_behave_ms**********")

            aligned_behave2ms = aligned_behave2ms.join(behave_result["behave_track"],on="ms_behaveframe")
            
            ms_result["aligned_behave2ms"]=aligned_behave2ms

            # quality info is saved in case of later use
            ms_result["quality"]={
            "behave_duration":t1,
            "mini_duration":max(ms_result["ms_ts"])/1000,
            "delta_t":delta_t,
            "max_lenth":max(length)
            }


            #jiang behave_result中的数据全部整合到 ms_session
            with open(task_ms_info,'wb') as f:
                try:
                    pickle.dump(dict(ms_result,**behave_result),f)
                except:
                    pickle.dump(dict(ms_result,**behave_result),f,protocol=4)
        
            print("------------------------------------------")





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