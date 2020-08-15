import os,sys,cv2
from mylab.Functions import *
import matplotlib.pyplot as plt
from mylab.process.miniscope.Mfunctions import *
from mylab.ana.miniscope.Mfunctions import *
import logging 
import pandas as pd
import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler(sys.stdout) #stream handler
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)


class MiniAna():
    def __init__(self,mssession_path,besession_path):
        self.session_path=mssession_path
        self.behave_path=besession_path

        self.logfile =self.session_path.replace('.pkl','_log.txt')
        fh = logging.FileHandler(self.logfile,mode="w")
        formatter = logging.Formatter("  %(asctime)s --> %(message)s")
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        self._load_session()

    def _load_session(self):
        logger.info("loading %s and %s"%(self.session_path,self.behave_path))
        with open(self.session_path,"rb") as f:
            self.result = pickle.load(f)
        with open(self.behave_path,"rb") as f:
            self.behave = pickle.load(f)
        logger.debug("loaded %s and %s"%(self.session_path,self.behave_path))

    def play_movie_segment(self,miniscope_movie_path,ms_ts,behave_movie_path,be_ts,events
        ,event_duration=2,event_name="event",pre_event=5,post_event=7):
        """
        ms_ts: miniscope timestamps
        be_ts: behavioral video timestamps that aligned to miniscope timestamps
        events: list in seconds
        pre_event,post_event: in seconds
        """
        miniscope_cap = cv2.VideoCapture(miniscope_movie_path)
        behave_cap = cv2.VideoCapture(behave_movie_path)

        ms_ts = list(self.result["ms_ts"]/1000)
        be_ts = list(self.behave["behave_track"]["be_ts"])

        font = cv2.FONT_ITALIC
        for event in events:
            # video_save_path = os.path.join(os.path.dirname(self.session_path),event_name+str(event)+'.mp4')
            # videoWriter = cv2.videoWriter(video_save_path,cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),)
                print("indexing corresponding behave_movie according to miniscope_movie...")
                # 先找到每一个事件的 时长 pre_event+post_event 的所有miniscope 视频对应的帧数列表
                mini_frame_num_start = find_close_fast(ms_ts,event-pre_event)
                mini_event_start = find_close_fast(ms_ts,event)
                mini_event_stop = find_close_fast(ms_ts,event+event_duration)
                mini_frame_num_end = find_close_fast(ms_ts,event+post_event)
                # 再找每一个miniscope视频帧的行为学视频对应帧，以及每一帧的状态stat
                behave_frames_num=[]
                stats=[] # 1 for pre_event, 2 for during event, 3 for post event
                for frame in range(mini_frame_num_start,mini_frame_num_end):
                    behave_frames_num.append(find_close_fast(be_ts,ms_ts[frame]))
                    if frame < mini_event_start:
                        stats.append(1)
                    elif frame >= mini_event_start and frame <= mini_event_stop:
                        stats.append(2)
                    else:
                        stats.append(3)
                print("begin playing")
                for mini_frame,behave_frame,stat in zip(range(mini_frame_num_start,mini_frame_num_end),behave_frames_num,stats):
                    miniscope_cap.set(cv2.CAP_PROP_POS_FRAMES,mini_frame)
                    behave_cap.set(cv2.CAP_PROP_POS_FRAMES,behave_frame)
                    # print(mini_frame,behave_frame,stat)
                    mini_ret,mi_frame = miniscope_cap.read()
                    beha_ret,be_frame = behave_cap.read()
                    # print(mini_ret)
                    if mini_ret:
                    # cv2.putText(mini_frame,"shock %.1f s"%ms_ts[mini_frame]-event,(10,15),font,0.5,(255,255,255))
                        cv2.imshow("mini_frame",mi_frame)
                        cv2.imshow("beha_frame",be_frame)
                    # delt_t = int((ms_ts[mini_frame]-ms_ts[mini_frame-1])*1000)
                    key = cv2.waitKey(30) & 0xFF

                    if key == ord("q"):
                        print("quit playing")
                        miniscope_cap.release()
                        behave_cap.release()
                        cv2.destroyAllWindows()
                        sys.exit()
                    if key == ord("n"):
                        print("next event")
                        continue

        miniscope_cap.release()
        behave_cap.release()
        cv2.destroyAllWindows()

    def plot_all_trace(self,df,idxes,vlines=None,figsize=(10,10),save=False,show=True):
        """
        df
        idxes: result["idx_accepted"]
        vlines: list in seconds
        """
        plt.figure(figsize=figsize)
        for i, idx in enumerate(idxes):
            x=self.result["ms_ts"]/1000 # in seconds
            y=df[idx]+i*2*max(df.std(axis=0)) # maximum std of all the trace as the height of each trace
            plt.plot(x,y,linewidth=0.5,color="black")
        if not vlines==None:
            for vline in vlines:
                plt.axvline(x=vline,linestyle="--",color="black")
        plt.yticks([])
        plt.ylabel("Cells")
        plt.xlabel("Time/s")
        if save:
            save_path = os.path.join(os.path.dirname(self.session_path),"all_trace.png")
            plt.savefig(save_path,dpi=300,format="png",bbox_inches="tight")
            logger.info("%s saved"%save_path)
        if show:
            plt.show()


    def plot_PSTH(self,df,idxes,events,pre_duration,post_duration,event_duration,event_name="event",save=False,show=True):
        """
        df
        idxes
        pre_duration: in seconds
        post_duration: in seconds
        events: in seconds
        event_duration: in seconds
        """
        num_e = len(events)
        plt.figure(figsize=(5*num_e,10))
        ts = self.result["ms_ts"]/1000 # transfer milliseconds to seconds

        for i,event in enumerate(events,1):
            plt.subplot(1,num_e,i)
            start_time = event-pre_duration
            event_on_time = event
            event_off_time = event+event_duration
            end_time = event+post_duration

            start_frame = find_close_fast(ts,start_time)
            end_frame = find_close_fast(ts,end_time)
            x = ts[start_frame:end_frame]

            multi_coefficient = 2*max(df.std(axis=0))

            for j, idx in enumerate(idxes):
                y = df[idx][start_frame:end_frame] + j*multi_coefficient
                plt.plot(x,y,linewidth=0.5,color="black")
            if event_duration !=0:
                plt.axvspan(xmin=event_on_time,xmax=event_off_time,alpha=0.4,facecolor="blue")
                plt.yticks([])
                plt.xlabel("Time/s")
                plt.title("%s %s"%(event_name,i))
                if i==1:
                    plt.ylabel("Cells")

        if save:
            save_path = os.path.join(os.path.dirname(self.session_path),"PSTH-%s.png"%event_name)
            plt.savefig(save_path,dpi=300,format="png",bbox_inches="tight")
            logger.info("%s saved"%save_path)
        if show:
            plt.show()

    def cellids_event_response(self,df,idxes,events,pre_duration=5,post_duration=5,event_duration=0.5,timebin=0.5,event_name="event"):
        """
        idxes: all cell ids
        df:
        events: list, in seconds
        pre_duration,post_duration, event_duration,timebin are all in seconds
        """
        result={
            "pre_duration":pre_duration,
            "post_duration":post_duration,
            "event_duration":event_duration
        }
        ts = self.result["ms_ts"]/1000 # transfer milliseconds to seconds
        for i, event in enumerate(events,1):
            start_time = event-pre_duration
            event_on_time = event
            event_off_time = event+event_duration
            end_time = event+post_duration

            start_frame = find_close_fast(ts,start_time)
            event_on_frame = find_close_fast(ts,event_on_time)
            end_frame = find_close_fast(ts,end_time)

            baseline_mean = df[start_frame:event_on_frame].mean()
            baseline_std = df[start_frame:event_on_frame].std()

            post_event_mean = df[event_on_frame:end_frame].mean()
            post_event_zscore = (post_event_mean-baseline_mean)/baseline_std

            idx_activated = post_event_zscore[post_event_zscore > 1.96];idx_activated.column=["z-score"]
            idx_inhibited = post_event_zscore[post_event_zscore < -1.96];idx_inhibited.column=["z-score"]
            logger.info("%s were activated %ss after %s. According to z-score>1.96"%(list(idx_activated.index),post_duration,event_name))
            logger.info("%s were inhibited %ss after %s. According to z-score<-1.96"%(list(idx_inhibited.index),post_duration,event_name))
            result[i]={
                "idx_activated":idx_activated,
                "idx_inhibited":idx_inhibited,
                "each_bin_response":{
                    "timebin":timebin }
            }
            bin_num = int(np.ceil(post_duration/timebin))
            for j in range(bin_num):
                logger.info("The %s %ss-bin after the %s %s"%(j,timebin,i,event_name))
                bin_start_frame = find_close_fast(ts,timebin*i+event_on_time)
                bin_end_frame = find_close_fast(ts,timebin*(i+1)+event_on_time)
                bin_mean = df[bin_start_frame:bin_end_frame].mean()
                bin_zscore = (bin_mean-baseline_mean)/baseline_std
                bin_idx_activated = bin_zscore[bin_zscore>1.96];bin_idx_activated.column=["z-score"]
                bin_idx_inhibited = bin_zscore[bin_zscore<-1.96];bin_idx_inhibited.column=["z-score"]
                logger.info("%s were activated. According to z-score>1.96"%list(idx_activated.index))
                logger.info("%s were inhibited. According to z-score<-1.96"%list(idx_inhibited.index))
                result[i]["each_bin_response"][j]={
                    "bin_idx_activated":bin_idx_activated,
                    "bin_idx_inhibited":bin_idx_inhibited
                }
        # print(result)
        return result


if __name__ == "__main__":
    wd = r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_191082\20191025_161452_all"
    mssession_path = os.path.join(wd,"session4.pkl")
    besession_path = os.path.join(wd,"behave_2019090600003.pkl")
    r_191082 = MiniAna(mssession_path,besession_path)

    df = pd.DataFrame(r_191082.result["sigraw"][:,r_191082.result["idx_accepted"]],columns=r_191082.result["idx_accepted"])
    idxes = r_191082.result["idx_accepted"]

    # r_191082.cellids_event_response(df,idxes,events=[180,240,300],pre_duration=5,post_duration=5,event_duration=0.5,timebin=0.5,event_name="shock")
    # r_191082.plot_all_trace(df,idxes,figsize=(10,10),vlines=[180,240,300],save=True,show=False)
    # r_191082.plot_PSTH(df,idxes,pre_duration=5,post_duration=7,events=[180,240,300]
    # ,event_duration=2,event_name="Shock",save=True,show=False)
    r_191082.play_movie_segment(
        miniscope_movie_path=r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_191082\20200815_192004_10fps_20190906\msCam_concat.avi"
        ,ms_ts=r_191082.result["ms_ts"]
        ,behave_movie_path=r"V:\miniscope\7_Miniscope_CHS\raw_data\2019\201909\20190906\191082\H11_M7_S47\2019090600003.mp4"
        ,be_ts=r_191082.behave["behave_track"]["be_ts"]
        ,events=[180,240,300]
        ,event_duration=2
        ,event_name="shock",pre_event=5,post_event=10)