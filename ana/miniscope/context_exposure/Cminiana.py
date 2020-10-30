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
from mylab.ana.miniscope.context_exposure.Mplacecells import *
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

    def savesession(self,):
        with open(self.session_path,"wb") as f:
            pickle.dump(self.result,f)
        logger.info("self.result is saved at %s"%self.session_path)


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

    def align_behave_ms(self,hc_trial_bin=5000):
        """
        产生 aligned_behave2ms
        注意 有的是行为学视频比较长，有的是miniscope视频比较长，一般是行为学视频比较长
        hc_trial_bin: in ms, default 5000ms
        """
        logger.info("FUN:: aligned_behave2ms")
        
        if "behave_track" in self.result.keys():
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
                self.result["Trial_Num"] = self.result["aligned_behave2ms"]["Trial_Num"]
                self.result["process"] = self.result["aligned_behave2ms"]["process"]
                self.savesession()
                logger.debug("aligned_behave2ms is saved %s" %self.session_path)
            else:
                logger.debug("behaveiroal timestamps were aligned to ms")


        else:
            logger.debug("this session was recorded in homecage")

            Trial_Num = []
            process = []
            for ts in self.result["ms_ts"]:
                Trial_Num.append(int(np.ceil(ts/hc_trial_bin)))
                process.append(-1)
            self.result["Trial_Num"] = pd.Series(Trial_Num,name="Trial_Num")
            self.result["process"] = pd.Series(process,name="process")
            self.savesession()

    def align_behave_ms_2_del(self,hc_trial_bin=5000):
        """
        产生 aligned_behave2ms
        注意 有的是行为学视频比较长，有的是miniscope视频比较长，一般是行为学视频比较长
        hc_trial_bin: in ms, default 5000ms
        """
        logger.info("FUN:: aligned_behave2ms")
        
        if "behave_track" in self.result.keys():
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
                with open(self.session_path,'wb') as f:
                    pickle.dump(self.result,f)
                logger.debug("aligned_behave2ms is saved %s" %self.session_path)
            else:
                logger.debug("behaveiroal timestamps were aligned to ms")

            try:
                self.result["Trial_Num"] = self.result["aligned_behave2ms"]["Trial_Num"]
                self.result["process"] = self.result["aligned_behave2ms"]["process"]
            except:
                del self.result["aligned_behave2ms"]
                logger.debug("add Trial_Num and process failed, del aligned_behave2ms")
                with open(self.session_path,"wb") as f:
                    pickle.dump(self.result,f)
                return self.aligned_behave2ms(hc_trial_bin=hc_trial_bin)
        else:
            logger.debug("this session was recorded in homecage")

            Trial_Num = []
            process = []
            for ts in self.result["ms_ts"]:
                Trial_Num.append(int(np.ceil(ts/hc_trial_bin)))
                process.append(-1)
            self.result["Trial_Num"] = pd.Series(Trial_Num)
            self.result["process"] = pd.Series(process)

    def show_behaveframe(self,tracking=True):
        """
        show all the tracking traectory in a behavioral video frame.
        """
        self.add_behavevideoframe()
        plt.imshow(self.result["behavevideoframe"])
        plt.xticks([])
        plt.yticks([])
        # plt.plot(s.result[])
        plt.plot([i[0] for i in self.result["all_track_points"]],[i[1] for i in self.result["all_track_points"]],"ro",markersize=2)
        if tracking :
            plt.plot(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"],markersize=1)
        plt.show()

        
    #%% add behavioral proverties to aligned_behave2ms

    def add_Context(self,context_map=None):
        """
        the same size as df.
        """
        if not "Context" in self.result.keys():
            Context = (pd.merge(self.result["Trial_Num"],self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])["Enter_ctx"]).fillna(-1)# 将NaN置换成-1
            logger.info("'Contex' came frome 'Enter_ctx'")
            self.result["Context"] = pd.Series([int(i) for i in Context],name="Context")
            logger.info("'Context' has been added")
        else:
            logger.debug("'Context' was there")
        if not context_map == None:
            self.result["Context"] = pd.Series([context_map[i] for i in self.Context],name="Context")
            logger.info("'Context' was represented as A,B,C or ON")
        else:
            logger.info("'Context' was represented as 0,1,2 or -1")

    def add_behavevideoframe(self,behavevideo=None,frame=999):
        """
        """
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
            logger.debug("behavevideoframe was saved")
        else:
            logger.debug("behavevideoframe has been there.")

    def add_is_in_context(self):
        if self.exp == "task":
            if not "is_in_context" in self.result.keys():
                mask = self.result["in_context_mask"]
                is_in_context=[]
                for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        is_in_context.append(0)
                    else:
                        is_in_context.append(1)
                self.result["is_in_context"]=pd.Series(is_in_context,name="is_in_context")
                logger.info("'is_in_context' has been added")
            else:
                logger.info("'is_in_context' has been there")
        else:
            logger.info("homecage session has no 'is_in_context'")

    def add_is_in_lineartrack(self):
        if self.exp == "task":
            if not "is_in_lineartrack" in self.result.keys():
                mask = self.result["in_lineartrack_mask"]
                is_in_lineartrack=[]
                for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        is_in_lineartrack.append(0)
                    else:
                        is_in_lineartrack.append(1)
                self.result["is_in_lineartrack"]=pd.Series(is_in_lineartrack,name="is_in_lineartrack")
                logger.info("'is_in_lineartrack' has been added")
            else:
                logger.info("'is_in_lineartrack' has been there")
        else:
            logger.info("homecage session has no 'is_in_lineartrack'")

    def add_Body_speed(self,scale=0.2339021309714166):
        if self.exp == "task":
            if not "Body_speed" in self.result.keys():
                Body_speed,Body_speed_angle = speed(X=self.result["aligned_behave2ms"]["Body_x"]
                                                        ,Y=self.result["aligned_behave2ms"]["Body_y"]
                                                        ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                        ,s=scale)
                logger.info("Body_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
                self.result["Body_speed"]=speed_optimize(Body_speed,method="gaussian_filter1d",sigma=3)
                self.result["Body_speed_angle"]=Body_speed_angle
                logger.info("Body_speed and Body_speed_angle have been added")
            else:
                logger.info("Body_speed has been there")
        else:
            logger.info("homecage session has no 'Body_speed'")

    def add_Head_speed(self,scale=0.2339021309714166):
        if self.exp == "task":
            if not "Head_speed" in self.result.keys():
                Head_speed,Head_speed_angle = speed(X=self.result["aligned_behave2ms"]["Head_x"]
                                                        ,Y=self.result["aligned_behave2ms"]["Head_y"]
                                                        ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                        ,s=scale)
                logger.info("Head_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
                self.result["Head_speed"]=speed_optimize(Head_speed,method="gaussian_filter1d",sigma=3)
                self.result["Head_speed_angle"]=Head_speed_angle
                logger.info("Head_speed and Head_speed_angle have been added")
            else:
                logger.info("Head_speed has been there")
        else:
            logger.info("homecage session has no 'Head_speed'")


    def add_in_context_running_direction_Body(self):
        if self.exp == "task":
            if not "in_context_running_direction_Body" in self.result.keys():
                in_context_running_direction_Body=[]

                for Trial, in_context,Body_speed,Body_speed_angle in zip(self.result["Trial_Num"],self.result["is_in_context"],self.result["Body_speed"],self.result["Body_speed_angle"]):
                    if Trial == -1:
                        in_context_running_direction_Body.append(-1)
                    else:
                        if in_context == 0:
                            in_context_running_direction_Body.append(-1)
                        else:
                            if Body_speed_angle > 90 and Body_speed_angle < 280 :
                                in_context_running_direction_Body.append(0)
                            else:
                                in_context_running_direction_Body.append(1)
                self.result["in_context_running_direction_Body"]=pd.Series(in_context_running_direction_Body,name="in_context_running_direction_Body")
                logger.info("in_context_running_direction_Body has been added")
            else:
                logger.info("'in_context_running_direction_Body' has been there")
        else:
            logger.info("homecage session has no 'in_context_running_direction_Body'")

    def add_in_context_running_direction_Head(self):
        if self.exp == "task":
            if not "in_context_running_direction_Head" in self.result.keys():
                in_context_running_direction_Head=[]

                for Trial, in_context,Head_speed,Head_speed_angle in zip(self.result["Trial_Num"],self.result["is_in_context"],self.result["Head_speed"],self.result["Head_speed_angle"]):
                    if Trial == -1:
                        in_context_running_direction_Head.append(-1)
                    else:
                        if in_context == 0:
                            in_context_running_direction_Head.append(-1)
                        else:
                            if Head_speed_angle > 90 and Head_speed_angle < 280 :
                                in_context_running_direction_Head.append(0)
                            else:
                                in_context_running_direction_Head.append(1)
                self.result["in_context_running_direction_Head"]=pd.Series(in_context_running_direction_Head,name="in_context_running_direction_Head")
                logger.info("in_context_running_direction_Head has been added")
            else:
                logger.info("'in_context_running_direction_Head' has been there")
        else:
            logger.info("homecage session has no 'in_context_running_direction_Head'")


    def add_alltrack_placebin_num(self,according = "Head",place_bin_nums=[4,4,40,4,4,4],behavevideo=None):
        if self.exp == "task":
            if not "place_bin_No" in self.result.keys():

                if "all_track_points" in self.result.keys():
                    coords = self.result["all_track_points"]
                else:
                    behavevideo = self.result["behavevideo"][0] if behavevideo == None else behavevideo
                    coords = LT_Videos(behavevideo).draw_midline_of_whole_track_for_each_day(aim="midline_of_track",count=7)
                    self.result["all_track_points"] = coords
                    self.savesession()

                lines = [(coords[i],coords[i+1]) for i in range(len(coords)-2)]
                lines.append((coords[-3],coords[-1]))
                place_bin_mids=[] # 每个placebin 的中点坐标
                for line, place_bin_num in zip(lines,place_bin_nums):
                    #计算每个placebin中点的坐标。
                    #首先 计算每个placebin边界点的坐标
                    xs = np.linspace(line[0][0],line[1][0],place_bin_num+1)
                    ys = np.linspace(line[0][1],line[1][1],place_bin_num+1)
                    #然后计算 每个placebin的中点坐标
                    xs_mid = [np.mean([xs[i],xs[i+1]]) for i in range(len(xs)-1)]
                    ys_mid = [np.mean([ys[i],ys[i+1]]) for i in range(len(ys)-1)]
                    place_bin_mids.extend([(x,y) for x,y in zip(xs_mid,ys_mid)])

                if according == "Head":
                    X = self.result["aligned_behave2ms"]["Head_x"]
                    Y = self.result["aligned_behave2ms"]["Head_y"]
                elif according == "Body":
                    X = self.result["aligned_behave2ms"]["Body_x"]
                    Y = self.result["aligned_behave2ms"]["Body_y"]
                else:
                    sys.exit("no %s"%according)

                place_bin_No=[]
                for x,y in zip(X,Y):
                    distances=[]
                    for place_bin_mid in place_bin_mids:
                        distance = np.sqrt((x-place_bin_mid[0])**2+(y-place_bin_mid[1])**2)
                        distances.append(distance)
                    # print(distances)
                    # sys.exit()  
                    #有一些 点会tracking到 很远的地方去，用像素点为15 作为距离来筛选错误的点，然后用上一个值替代这个值
                    if np.min(distances) < 20:
                        place_bin_No.append(np.argmin(distances))
                    else:
                        place_bin_No.append(place_bin_No[-1])

                self.result["place_bin_No"] = pd.Series(place_bin_No,name="place_bin_No")

                logger.info("'place_bin_No' has been added")
            else:
                logger.info("'place_bin_No' has been there")
        else:
            logger.info("homecage session has no 'place_bin_No'")

    def add_incontext_placebin_num(self,according="Head",placebin_number=40):
        if self.exp == "task":
            if not "in_context_placebin_num" in self.result.keys():
                Cx_min = np.min(np.array(self.result["in_context_coords"])[:,0])
                Cx_max = np.max(np.array(self.result["in_context_coords"])[:,0])
    
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                if according=="Head":
                    X = self.result["aligned_behave2ms"]['Head_x']
                elif according == "Body":
                    X = self.result["aligned_behave2ms"]['Body_x']
                else:
                    print("only ['Head','Bpdy'] are available")
                for in_context,x in zip(self.result['is_in_context'],X):
                    # x = int(x)
                    if not in_context:
                        in_context_placebin_num.append(0)
                    else:   
                        if x == placebins[0][0]:
                            in_context_placebin_num.append(1)
                        else:
                            for i,placebin in enumerate(placebins,0):
                                # print(x,placebin[0],placebin[1],end="|")
                                if x>placebin[0] and x <= placebin[1]:
                                    temp=i+1
                                    break                                    
                                else:
                                    pass
                            try:
                                in_context_placebin_num.append(temp)
                            except:
                                logger.warning("%s is in context but not in any place bin"%x)
                self.result["in_context_placebin_num"] = pd.Series(in_context_placebin_num,name="in_context_placebin_num")
                logger.info("in_context_placebin_num has been added, which should start from 1, 0 means out of context")
            else:
                logger.info("'in_context_placebin_num' has been there")
        else:
            logger.info("homecage session has no 'in_context_placebin_num'")

    def add_zone2result(self,zone="in_lineartrack"):
        logger.info("FUN:: add_zone2result at zone %s"%zone)
        mask = zone+"_mask"
        coords = zone+"_coords"
        if not mask in self.result.keys():
            if os.path.exists(self.result["behavevideo"]):
                try:
                    temp_mask,temp_coords=Video(self.result["behavevideo"]).draw_rois(aim=zone,count = 1)
                except Exception as e:
                    logger.info(e)
                    sys.exit()
            else:
                logger.info("DON'T EXIST: %s "%self.result["behavevideo"])
                sys.exit()

            self.result[mask]=temp_mask
            self.result[coords]=temp_coords

            with open(self.session_path,'wb') as f:
                pickle.dump(self.result,f)
            print("%s coords and mask is saved"%zone)
        else:
            print("%s coords and mask are already there"%zone)


    def add_info2aligned_behave2ms(self,scale=0.2339021309714166,placebin_number=10):
        """
        which is about to discrete
        """
        #     scale = 0.2339021309714166 #cm/pixel 40cm的台子，202016，202017.202019适用
        logger.info("FUN:: add_info2aligned_behave2ms scale: %scm/pixel ; placebin_number: %s"%(scale,placebin_number))
        update = 0
            
        if "aligned_behave2ms" in self.result.keys():
            #1 添加 "in_context" in behave_track
            mask = self.result["in_context_mask"]
            if not "in_context" in self.result.keys():
                in_context=[]
                for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        in_context.append(0)
                    else:
                        in_context.append(1)
                self.result["in_context"]=pd.Series(in_context,name="in_context")
                logger.info("'in_context' has been added")
                update = 1
            else:
                print("'in_context' has been there")

            #2 添加“Body_speed" "Body_speed_angle"
            if not "Body_speed" in self.result.keys():
                Body_speed,Body_speed_angle = Video.speed(X=self.result["aligned_behave2ms"]["Body_x"]
                                                        ,Y=self.result["aligned_behave2ms"]["Body_y"]
                                                        ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                        ,s=scale)
                logger.info("Body_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
                self.result["Body_speed"]=speed_optimize(Body_speed,method="gaussian_filter1d",sigma=3)
                self.result["Body_speed_angle"]=Body_speed_angle
                logger.info("Body_speed and Body_speed_angle have been added")
                update = 1
            else:
                print("'Body_speed'and'Body_speed_angle' has been there")
            
            #3 添加"in_context_running_direction"
            if not "in_context_running_direction" in self.result.keys():
                in_context_running_direction=[]

                for Trial, in_context,Body_speed,Body_speed_angle in zip(self.result["Trial_Num"],self.result["in_context"],self.result["Body_speed"],self.result["Body_speed_angle"]):
                    if Trial == -1:
                        in_context_running_direction.append(-1)
                    else:
                        if in_context == 0:
                            in_context_running_direction.append(-1)
                        else:
                            if Body_speed_angle > 90 and Body_speed_angle < 280 :
                                in_context_running_direction.append(0)
                            else:
                                in_context_running_direction.append(1)
                self.result["in_context_running_direction"]=pd.Series(in_context_running_direction,name="in_context_running_direction")
                logger.info("in_context_running_direction has been added")
                update = 1
            else:
                print("in_context_running_direction has been there")

            #4 添加 in_context_placebin_num"
            if not "in_context_placebin_num" in self.result.keys():
                # print(self.result["in_context_coords"])
                Cx_min = np.min(np.array(self.result["in_context_coords"])[:,0])
                Cx_max = np.max(np.array(self.result["in_context_coords"])[:,0])
    
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                print(placebins)
                for in_context,x in zip(self.result['in_context'],self.result["aligned_behave2ms"]['Body_x']):
                    # x = int(x)
                    if not in_context:
                        in_context_placebin_num.append(0)
                    else:   
                        if x == placebins[0][0]:
                            in_context_placebin_num.append(1)
                        else:
                            for i,placebin in enumerate(placebins,0):
                                # print(x,placebin[0],placebin[1],end="|")
                                if x>placebin[0] and x <= placebin[1]:
                                    temp=i+1
                                    break                                    
                                else:
                                    pass
                            try:
                                in_context_placebin_num.append(temp)
                            except:
                                logger.warning("%s is in context but not in any place bin"%x)

                logger.info("in_context_placebin_num should start from 1, 0 means out of context")
                        
                print(len(in_context_placebin_num),self.result["aligned_behave2ms"].shape)
                self.result["in_context_placebin_num"] = pd.Series(in_context_placebin_num,name="in_context_placebin_num")
                update = 1
            else:
                print("'in_context_placebin_num' has been there")
            
        else:
            print("you haven't align behave to ms or it's homecage session")

        if update:
            with open(self.session_path,'wb') as f:
                pickle.dump(self.result,f)
            print("aligned_behave2ms is updated and saved %s" %self.session_path)


    def detect_ca_transients(self,thresh=1.5,baseline=0.8,t_half=0.2,FR=30):
        """
        return ca_transients,celldata_detect, single_cell_detected_transiend. 
        celldata_detect have the same size with df
        """
        logger.debug("detecting calcium transients for each cell")
        self.result["ca_transients"],self.result["ca_transient_detect"],self.result["single_cell_detected_transient"]=detect_ca_transients(self.result["idx_accepted"],self.df.values,thresh,baseline,t_half,FR)
        logger.info("calcium tansients are detected... ")

    ## trim* ret

    def trim_df(self,force_neg2zero=True,detect_ca_transient =False,Normalize=False,standarize=False):
        if detect_ca_transient:
            _,self.df,_= self.detect_ca_transients()

    def trim_speed(self,min=None):
        pass

    def trim_Trial_Num(self,):
        pass

    def trim_process(self,):
        pass


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

class Cellid(MiniAna):
    def __init__(self,session_path):
        super().__init__(session_path)

        # self.add_info2aligned_behave2ms(scale=0.2339021309714166,placebin_number=10) 
        # self.result["in_context"],self.result["Body_speed"],self.result["Body_speed_angle"],self.result["“in_context_place_bin"]
        self.add_is_in_context()
        self.add_Body_speed(scale=0.33)
        self.add_in_context_running_direction_Body()

        self.add_Context()
        self.add_incontext_placebin_num()

        self.Context = self.result["Context"]
        self.in_context_running_direction = self.result["in_context_running_direction_Body"]
        self.Body_speed = self.result["Body_speed"]
        self.in_context_placebin_num=self.result["in_context_placebin_num"]
        self.process = self.result["process"]

    def cellids_HCTrack_Context(self,idx_accept,df):
        """
        df 合并了HC session 和 non-HC session的
        df 必须具备 Trial_Num Enter_ctx 和 Exit_ctx
        """
        #重置Trial_Num
        df["Trial_Num"][df["Enter_ctx"]!=-1] = [i+1 for i in range(len(df["Trial_Num"][df["Enter_ctx"]!=-1]))]
        df = df.sort_values(by=["Enter_ctx","Trial_Num"])
        df[idx_accept],_,_ = Normalization(df[idx_accept])
        
        familiar_cells = []
        familiar_ctxA_cells = []
        familiar_ctxB_cells =[]
        familiar_nonctx_cells = []
        novel_cells =[]
        novel_ctxA_cells=[]
        novel_ctxB_cells=[]
        novel_nonctx_cells = []
        nothing_cells=[]
        
        strange_cells = []
        
        for idx in idx_accept:
            hc_fr = df[idx][df["Enter_ctx"]==-1]
            ctxA_fr = df[idx][df["Enter_ctx"]==0]
            ctxB_fr = df[idx][df["Enter_ctx"]==1]
            hc_meanfr =np.mean(hc_fr)
            hc_std = np.std(hc_fr)
            ctxA_meanfr =np.mean(ctxA_fr)
            ctxA_std =np.std(ctxA_fr)
            ctxB_meanfr =np.mean(ctxB_fr)
            ctxB_std  =np.std(ctxB_fr)
            hc_ctxA_p = stats.ranksums(hc_fr,ctxA_fr)[1]
            hc_ctxB_p = stats.ranksums(hc_fr,ctxB_fr)[1]
            ctxA_ctxB_p = stats.ranksums(ctxA_fr,ctxB_fr)[1]
            

            #首先判定 是否是某种cells
            if hc_ctxA_p < 0.05 or hc_ctxB_p < 0.05 or ctxA_ctxB_p < 0.05:
                #判定是familair cells 
                if hc_ctxA_p < 0.05 and hc_ctxB_p<0.05 and hc_meanfr>ctxA_meanfr and hc_meanfr>ctxB_meanfr:
                    familiar_cells.append(idx)
                    #判定是familiar_ctxA_cell / familiar_ctxB_cell/familiar_nonctx_cell
                    if ctxA_ctxB_p < 0.05:
                        if ctxA_meanfr > ctxB_meanfr:
                            familiar_ctxA_cells.append(idx)
                        else:
                            familiar_ctxB_cells.append(idx)
                    else:
                        familiar_nonctx_cells.append(idx)
                #判定是novel cells
                elif (hc_ctxA_p < 0.05 and hc_meanfr < ctxA_meanfr) or (hc_ctxB_p<0.05 and hc_meanfr < ctxB_meanfr):
                    novel_cells.append(idx)
                    #判定是novel_ctxA_cell / novel_ctxB_cell / novel_nonctx_cells
                    if ctxA_ctxB_p < 0.05:
                        if ctxA_meanfr > ctxB_meanfr:
                            novel_ctxA_cells.append(idx)
                        else:
                            novel_ctxB_cells.append(idx)
                    else:
                        novel_nonctx_cells.append(idx)
                else:
                    strange_cells.append(idx)
            else:
                nothing_cells.append(idx)
        """
        通过rank sum test判断其在home cage中发放的比较高还是在Track A or B中发放的比较高
        输出HC A B None 的 cell ID
        """
        return  {"familiar_cells":familiar_cells
                 ,"familiar_ctxA_cells":familiar_ctxA_cells
                 ,"familiar_ctxB_cells":familiar_ctxB_cells
                 ,"familiar_nonctx_cells":familiar_nonctx_cells
                 ,"novel_cells":novel_cells
                 ,"novel_ctxA_cells":novel_ctxA_cells
                 ,"novel_ctxB_cells":novel_ctxB_cells
                 ,"novel_nonctx_cells":novel_nonctx_cells
                 ,"nothing_cells":nothing_cells
                 ,"strange_cells":strange_cells}


    def cellids_Context(self,idxes,meanfr_df=None,Context=None,context_map=["A","B","C","N"]):
        """
        which is about to discrete
        输入应该全是 in_context==1的数据
        idxes: the ids of all the cell that you're concerned.
        meanfr_df: meanfr in each trial only in context
        context_list:contains ["Trial_Num","context_list"],existed in self.result["behavelog_info"]
                     two available contexts represented by A or B.N means out of all the context. each trial have a exposured context
        context_map: 0 means context A, 1 means context B, 2 means context C.
        standarization to make data of differnet batch compatable
        """
        logger.info("FUN:: cellids_Context")
        logger.info("Context 0,1,2,-1 means %s."%context_map)
        #序列化in_context_list
        if meanfr_df is None:
            logger.info("Default :: meanfr_df = self.meanfr_by_trial(Normalize=False,standarize=False,in_context=True) ")
            df,index = self.trim_df2(df = None,force_neg2zero=True
                ,Normalize=False,standarize=False,in_context=True)

            meanfr_df = df[index].groupby(self.result["Trial_Num"][index]).mean().reset_index(drop=False)

        try:
            if Context is None:
                logger.info("""Default:: pd.merge(self.result["Trial_Num"][index],self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])[Enter_ctx]""")
                temp = pd.merge(meanfr_df,self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])
                Context = temp["Enter_ctx"]
            # 将0，1对应的context信息根据context_map置换成A B
            Context = pd.Series([context_map[i] for i in Context])
        except:
            logger.info("homecage session, no context cells")
            sys.exit()

        ctx_pvalue = meanfr_df[idxes].apply(func=lambda x: stats.ranksums(x[Context=="A"],x[Context=="B"])[1],axis=0)
        # ctx_pvalue.columns=["ranksum_p_value"]
        ctx_meanfr = meanfr_df[idxes].groupby(Context).mean().T
        ctx_meanfr["ranksums_p_value"] = ctx_pvalue
        ctx_meanfr["CSI"] = (ctx_meanfr["A"]-ctx_meanfr["B"])/(ctx_meanfr["A"]+ctx_meanfr["B"])
        ContextA_cells=[]
        ContextB_cells=[]
        non_context_cells=[]

        for cellid,a, b, p in zip(ctx_meanfr.index,ctx_meanfr["A"],ctx_meanfr["B"],ctx_meanfr["ranksums_p_value"]):
            if p>=0.05:
                non_context_cells.append(cellid)
            else:
                if a>b:
                    ContextA_cells.append(cellid)
                elif a<b:
                    ContextB_cells.append(cellid)
                else:
                    logger.warning("meanfr of cell % is equal in Context A and Context B"%cellid)
                    non_context_cells.append(cellid)

        return{
        "meanfr_df":meanfr_df,
        "ctx_meanfr":ctx_meanfr, # meanfr in context A and B, rank_sum_pvalue,CSI
        "ContextA_cells":ContextA_cells,
        "ContextB_cells":ContextB_cells,
        "non_context_cells":non_context_cells
        }


    def cellids_RD_incontext(self,idxes,mean_df=None,Context=None,in_context_running_direction=None
        ,context_map=["A","B","C","N"],rd_map=["left","right","None"]):
        """
        which is about to discrete
        输入应该全是 in_context==1的数据. in_context_running_direction is -1 when out of context
        idxes: the ids of all the cell that you're concerned.
        meanfr_df: meanfr in each trial only in context
        in_context_running_direction: in_context_running_direction order which is as long as the frame length
        rd_map: 0 means left, 1 means right, -1 means None.
        standarization to make data of differnet batch compatable
        """

        logger.info("FUN:: cellids_RD_incontext")
        logger.info("context 0,1,2,-1 means%s."%context_map)
        logger.info("in_context_running_direction 0,1,-1 means%s."%rd_map)

        if mean_df is None:
            logger.info("Normalize=False,standarize=False,in_context=True")
            df,index = self.trim_df2(force_neg2zero=True
                ,Normalize=False,standarize=False,in_context=True)

        if in_context_running_direction is None:
            in_context_running_direction=self.result["in_context_running_direction"]
        in_context_running_direction = pd.Series([rd_map[i] for i in in_context_running_direction])

        meanfr_df = df[index].groupby([self.result["Trial_Num"][index],in_context_running_direction[index]]).mean().reset_index(drop=False).rename(columns={"level_1":"rd"})
        # meanfr_df = df[index].groupby([self.result["Trial_Num"][index],in_context_running_direction[index]]).mean().reset_index(drop=False)
        try:
            if Context is None:
                temp = pd.merge(meanfr_df,self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])
                Context = temp["Enter_ctx"]
            # 将0，1对应的context信息根据context_map置换成A B
            Context = pd.Series([context_map[i] for i in Context])
            meanfr_df["Context"]=Context
        except:
            logger.info("homecage session, no context cells")
            sys.exit()

        # print(meanfr_df)
        #meanfr context 
        # #context A rd 0
        # A_left = meanfr_df[(meanfr_df["Context"]=="A") & (meanfr_df['rd']=="left")]
        # #context A rd 1
        # A_right = meanfr_df[(meanfr_df["Context"]=="A") & (meanfr_df['rd']=="right")]
        # #context B rd 0
        # B_left = meanfr_df[(meanfr_df["Context"]=="B") & (meanfr_df['rd']=="left")]
        # #context B rd 1
        # B_right = meanfr_df[(meanfr_df["Context"]=="B") & (meanfr_df['rd']=="right")]
        # #rd 0
        # left = meanfr_df[meanfr_df['rd']=="left"]
        # #rd 1
        # right = meanfr_df[meanfr_df['rd']=="right"]

        rd_meanfr = meanfr_df[idxes].groupby(meanfr_df["rd"]).mean().T 
        rd_meanfr["rd_pvalue"] = meanfr_df[idxes].apply(func=lambda x: stats.ranksums(x[meanfr_df['rd']=="left"],x[meanfr_df['rd']=="right"])[1],axis=0)
        rd_meanfr["RDSI"] = (rd_meanfr["left"]-rd_meanfr["right"])/(rd_meanfr["left"]+rd_meanfr["right"])
        left_cells = rd_meanfr[(rd_meanfr["rd_pvalue"]<0.05) & (rd_meanfr["left"]>rd_meanfr["right"])].index
        right_cells = rd_meanfr[(rd_meanfr["rd_pvalue"]<0.05) & (rd_meanfr["left"]<rd_meanfr["right"])].index
        non_rd_cells = rd_meanfr[rd_meanfr["rd_pvalue"]>0.05].index
        # print(non_rd_cells)

        rd_ctx_meanfr = meanfr_df[idxes].groupby([meanfr_df["Context"],meanfr_df["rd"]]).mean()
        rd_A_meanfr = rd_ctx_meanfr.xs("A").T
        rd_A_meanfr["rd_pvalue"] = meanfr_df[idxes].apply(func=lambda x: stats.ranksums(x[(meanfr_df["Context"]=="A") & (meanfr_df['rd']=="left")]
            ,x[(meanfr_df["Context"]=="A") & (meanfr_df['rd']=="right")])[1],axis=0)
        rd_A_meanfr["RDSI"] = (rd_A_meanfr["left"]-rd_A_meanfr["right"])/(rd_A_meanfr["left"]+rd_A_meanfr["right"])


        A_left_cells = rd_meanfr[(rd_A_meanfr["rd_pvalue"]<0.05) & (rd_A_meanfr["left"]>rd_A_meanfr["right"])].index
        A_right_cells = rd_meanfr[(rd_A_meanfr["rd_pvalue"]<0.05) & (rd_A_meanfr["left"]<rd_A_meanfr["right"])].index
        A_non_rd_cells = rd_meanfr[rd_A_meanfr["rd_pvalue"]>0.05].index
        # print(A_non_rd_cells)

        rd_B_meanfr = rd_ctx_meanfr.xs("B").T
        rd_B_meanfr["rd_pvalue"] = meanfr_df[idxes].apply(func=lambda x: stats.ranksums(x[(meanfr_df["Context"]=="B") & (meanfr_df['rd']=="left")]
            ,x[(meanfr_df["Context"]=="B") & (meanfr_df['rd']=="right")])[1],axis=0)
        rd_B_meanfr["RDSI"] = (rd_B_meanfr["left"]-rd_B_meanfr["right"])/(rd_B_meanfr["left"]+rd_B_meanfr["right"])

        B_left_cells = rd_B_meanfr[(rd_meanfr["rd_pvalue"]<0.05) & (rd_B_meanfr["left"]>rd_B_meanfr["right"])].index
        B_right_cells = rd_B_meanfr[(rd_meanfr["rd_pvalue"]<0.05) & (rd_B_meanfr["left"]<rd_B_meanfr["right"])].index
        B_non_rd_cells = rd_B_meanfr[rd_meanfr["rd_pvalue"]>0.05].index
        # print(B_non_rd_cells)

        return {
        "meanfr_df":meanfr_df,
        "rd_meanfr":rd_meanfr,# meanfr in running direction o and 1, rank_sum_pvalue,RDSI
        "left_cells":left_cells,
        "right_cells":right_cells,
        "non_rd_cells":non_rd_cells,

        "rd_A_meanfr":rd_A_meanfr,
        "A_left_cells":A_left_cells,
        "A_right_cells":A_right_cells,
        "A_non_rd_cells":A_non_rd_cells,

        "rd_B_meanfr":rd_B_meanfr,
        "B_left_cells":B_left_cells,
        "B_right_cells":B_right_cells,
        "B_non_rd_cells":B_non_rd_cells
        }

    def cellids_PC_incontext(self,idxes,df=None,Context=None,in_context_placebin_num=None
        ,in_process=True,process=[0,1,2,3],scale=0.2339021309714166,placebin_number=10
        ,context_map=["A","B","C","N"],shuffle_times=1000):
        """
        which is about to discrete
        df 必须具备 place_bin_num
        输入df包括分好的place bin 
        """
        logger.info("FUN:: cellids_PC_incontext")
        logger.info("context 0,1,2,-1 means%s."%context_map)
        logger.info("in_context_placebin_num start from 1.")

        # self.add_info2aligned_behave2ms(scale=scale,place_bin_num=placebin_number)

        if df is None:
            logger.info("force_neg2zero=True,Normalize=False,standarize=False,in_context=True,speed_min=3")
            df,index = self.trim_df2(force_neg2zero=True,in_process=in_process,process=process
                ,Normalize=False,standarize=False,in_context=True,speed_min=3)
            df=df[index]
        logger.info("indexed shape of df %s"%df.shape[0])

        if in_context_placebin_num is None:
            in_context_placebin_num=self.result["in_context_placebin_num"]
        in_context_placebin_num = pd.Series(in_context_placebin_num)[index]
        logger.info("indexed shape of in_context_placebin_num %s"%in_context_placebin_num.shape)

        if Context ==None:
            Context = self.Context
        Context = pd.Series([context_map[int(i)] for i in Context])[index]
        logger.info("indexed shape of Context %s"%Context.shape)


        observed_SIs_A = Cal_SIs(df[Context=="A"],in_context_placebin_num[Context=="A"])
        shuffle_A = bootstrap_Cal_SIs(df[Context=="A"],in_context_placebin_num[Context=="A"])
        shuffle_SIs_A=[]

        observed_SIs_B = Cal_SIs(df[Context=="B"],in_context_placebin_num[Context=="B"])
        shuffle_B = bootstrap_Cal_SIs(df[Context=="B"],in_context_placebin_num[Context=="B"])
        shuffle_SIs_B=[]
        # print(observed_SIs_A)
        try:
            if df[Context=="C"].shape[0] != 0:
                observed_SIs_C = Cal_SIs(df[Context=="C"],in_context_placebin_num[Context=="C"])
                shuffle_C = bootstrap_Cal_SIs(df[Context=="C"],in_context_placebin_num[Context=="C"])
                shuffle_SIs_C=[]
                C = True
            else:
                C = False
        except:
            logger.info("No context C")
            C = False
        logger.info("we shuffle mean firing rate in each place bin")
        
        
        for i in range(shuffle_times):
            sys.stdout.write("%s/%s"%(i+1,shuffle_times))
            sys.stdout.write("\r")
            shuffle_SIs_A.append(shuffle_A().values)
            shuffle_SIs_B.append(shuffle_B().values)
            if C:
                shuffle_SIs_C.append(shuffle_C().values)


        shuffle_SIs_A = pd.DataFrame(shuffle_SIs_A,columns=idxes)
        shuffle_SIs_B = pd.DataFrame(shuffle_SIs_B,columns=idxes)
        if C:
            shuffle_SIs_C = pd.DataFrame(shuffle_SIs_C,columns=idxes)

        logger.info("we define spatial information zscore of cell larger than 1.96 as place cell")
        zscores_A = (observed_SIs_A-shuffle_SIs_A.mean())/shuffle_SIs_A.std()
        place_cells_A = (zscores_A[zscores_A>1.96]).index.tolist()
        zscores_B = (observed_SIs_B-shuffle_SIs_B.mean())/shuffle_SIs_B.std()
        place_cells_B = (zscores_B[zscores_B>1.96]).index.tolist()
        if C:
            zscores_C = (observed_SIs_C-shuffle_SIs_C.mean())/shuffle_SIs_C.std()
            place_cells_C = (zscores_C[zscores_C>1.96]).index.tolist()



        if C:
            return{
            "observed_SIs_A":observed_SIs_A,
            "place_cells_A":place_cells_A,
            "observed_SIs_B":observed_SIs_B,
            "place_cells_B":place_cells_B,
            "observed_SIs_C":observed_SIs_C,
            "place_cells_C":place_cells_C
            }
        else:
            return{
            "observed_SIs_A":observed_SIs_A,
            "place_cells_A":place_cells_A,
            "observed_SIs_B":observed_SIs_B,
            "place_cells_B":place_cells_B
            }
        
    def plot_in_context_placefield(self,df=None,Trial_Num=None,in_process=True,process=[0,1,2,3,4,5],
        Context=None,in_context_placebin_num=None,context_map=["A","B","C","N"]):
        logger.info("FUN:: plot_in_context_placefield")
        logger.info("context 0,1,2,-1 means%s."%context_map)
        logger.info("in_context_placebin_num start from 1.")

        if df is None:
            logger.info("force_neg2zero=True,Normalize=False,standarize=False,in_context=True,speed_min=3")
            df,index = self.trim_df2(force_neg2zero=True,in_process=in_process,process=process
                ,Normalize=False,standarize=False,in_context=True)
            df=df[index]
        logger.info("indexed shape of 'df' %s"%df.shape[0])

        if Trial_Num is None:
            Trial_Num=self.result["Trial_Num"].values
        Trial_Num=pd.Series(Trial_Num)[index]
        logger.info("indexed shape of 'Trial_Num' %s"%Trial_Num.shape)

        if Context is None:
            Context = self.Context
        Context = pd.Series([context_map[int(i)] for i in Context])[index]
        logger.info("indexed shape of 'Context' %s"%Context.shape)

        if in_context_placebin_num is None:
            in_context_placebin_num=self.result["in_context_placebin_num"]
        in_context_placebin_num = pd.Series(in_context_placebin_num)[index]
        logger.info("indexed shape of 'in_context_placebin_num' %s"%in_context_placebin_num.shape)



        meanfr = df.groupby([Trial_Num,Context,in_context_placebin_num]).mean()
        
        try:
            meanfr = meanfr.drop(index=(0,-1),level=0)
            logger.info("remove Trial_Num '0' or '-1'")
        except:
            logger.debug("Trial_Num doesn't contain '-1' or '0'")

        try:
            meanfr = meanfr.drop(index="N",level=1)
            logger.info("remove Context 'N'")
        except:
            logger.debug("Context doesn't contain 'N'")

        try:
            meanfr = meanfr.drop(index=0,level=2)
            logger.info("remove in_context_placebin_num '0'")
        except:
            logger.debug("in_context_placebin_num,does'n contain '0'")

        meanfr.index.names=(["Trial_Num","Context","in_context_placebin_num"])

        def plot_Meanfr_trace_along_Placebin(idx,legend=True):
            mean = meanfr.groupby(["Context","in_context_placebin_num"]).mean()
            sem = meanfr.groupby(["Context","in_context_placebin_num"]).sem()
            x = meanfr.index.levels[2]

            y_A = mean.xs("A")[idx].values
            y_B = mean.xs("B")[idx].values
            sem_A = sem.xs("A")[idx].values
            sem_B = sem.xs("B")[idx].values
            plt.plot(x,y_A,color="red")
            plt.plot(x,y_B,color="green")
            plt.fill_between(x,y_A-sem_A,y_A+sem_A,facecolor="red",alpha=.3)
            plt.fill_between(x,y_B-sem_B,y_B+sem_B,alpha=.3,facecolor="green")
            if legend:
                plt.legend(["CtxA","CtxB"])
            plt.yticks([])
            plt.xlabel("place bin numbers")

        def plot_Meanfr_heatmap_along_Placebin(idxes,figsize=(8,8),**kwargs):
            plt.figure(figsize=figsize)
            
            df_A = meanfr.xs("A",level="Context").groupby(["in_context_placebin_num"]).mean()
            norm_df_A = df_A.apply(lambda x:(x-np.mean(x))/np.std(x,ddof=1)).T
            norm_df_A = norm_df_A.loc[idxes,:]

            df_B = meanfr.xs("B",level="Context").groupby(["in_context_placebin_num"]).mean()
            norm_df_B = df_B.apply(lambda x:(x-np.mean(x))/np.std(x,ddof=1)).T
            norm_df_B = norm_df_B.loc[idxes,:]

            plt.subplot(221)
            sorted_df_A = norm_df_A.loc[norm_df_A.idxmax(axis=1).sort_values().index,:]
            plt.imshow(sorted_df_A,aspect="auto",**kwargs)
            plt.yticks([])
            plt.title("pc-cells in Context A sorted in Context A")

            plt.subplot(222)
            sorted_df_B = norm_df_B.loc[norm_df_A.idxmax(axis=1).sort_values().index,:]
            plt.imshow(sorted_df_B,aspect="auto",**kwargs)
            plt.yticks([])
            plt.title("pc-cells in Context B sorted in Context A")

            plt.subplot(223)
            sorted_df_B = norm_df_B.loc[norm_df_B.idxmax(axis=1).sort_values().index,:]
            plt.imshow(sorted_df_B,aspect="auto",**kwargs)
            plt.yticks([])
            plt.title("pc-cells in Context B sorted in Context B")
            plt.tight_layout() 

            plt.subplot(224)
            sorted_df_A = norm_df_A.loc[norm_df_B.idxmax(axis=1).sort_values().index,:]
            plt.imshow(sorted_df_A,aspect="auto",**kwargs)
            plt.yticks([])
            plt.title("pc-cells in Context A sorted in Context B")

            plt.tight_layout() 
            plt.show()

        def plot_Fr_in_SingleTrial_along_Placebin(idx,norm=True,colorbar=True
            ,xlabel=True,ylabel=True,**kwargs):            
            try:
                #将整个1d trace按照place_bin的个数变成一个2d 的matrix
                heatmap_matrix_A = np.reshape(meanfr.xs(("A"),level=("Context"))[idx].values,(-1,max(meanfr.index.levels[2])))
                heatmap_matrix_B = np.reshape(meanfr.xs(("B"),level=("Context"))[idx].values,(-1,max(meanfr.index.levels[2])))
            except:
                print("some trial didn't have %s place bins"%max(meanfr.index.levels[2]))
            if norm:
                heatmap_matrix_A = np.apply_along_axis(lambda x:(x-np.mean(x))/np.std(x,ddof=1),axis=1,arr=heatmap_matrix_A)
                heatmap_matrix_B = np.apply_along_axis(lambda x:(x-np.mean(x))/np.std(x,ddof=1),axis=1,arr=heatmap_matrix_B)
            plt.subplot(211)
            plt.imshow(heatmap_matrix_A,aspect='auto',**kwargs)
            plt.title("CtxA")
            if colorbar:
                plt.colorbar(shrink=1)
            if ylabel:
                plt.ylabel("Trials")
            if xlabel:
                plt.xlabel("Place bins")

            plt.subplot(212)
            plt.imshow(heatmap_matrix_B,aspect='auto',**kwargs)
            plt.title("CtxB")
            if colorbar:
                plt.colorbar(shrink=1)
            if ylabel:
                plt.ylabel("Trials")
            if xlabel:
                plt.xlabel("Place bins")
            plt.tight_layout() 

        return meanfr,plot_Meanfr_trace_along_Placebin,plot_Meanfr_heatmap_along_Placebin,plot_Fr_in_SingleTrial_along_Placebin



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