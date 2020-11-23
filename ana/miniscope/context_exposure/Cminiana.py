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
from mylab.ana.miniscope.Cminiana import MiniAna as MA
from mylab.ana.miniscope.Mca_transient_detection import detect_ca_transients
from mylab.ana.miniscope.Mplacecells import *
import logging 


# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# sh = logging.StreamHandler(sys.stdout) #stream handler
# sh.setLevel(logging.INFO)
# logger.addHandler(sh)

class MiniAna(MA):
    def __init__(self,session_path):
        super().__init__(session_path)

        # self.logfile =self.session_path.replace('.pkl','_log.txt')
        # fh = logging.FileHandler(self.logfile,mode="a")
        # formatter = logging.Formatter("  %(asctime)s %(message)s")
        # fh.setFormatter(formatter)
        # fh.setLevel(logging.INFO)
        # logger.addHandler(fh)

    #%% add behavioral proverties to aligned_behave2ms
    def add_Trial_Num_Process(self,hc_trial_bin=5000):
        """
        in case some data was genereated by older verfion of function "align_behave_ms"
        , we need to regenereate "Trial_Num" and "Porcess" for each session
        and save them in pkl file
        """
        print("FUN:: add_Trial_Num_Process")

        if self.exp=="hc":
            print("this session was recorded in homecage")
            Trial_Num = []
            process = []
            for ts in self.result["ms_ts"]:
                Trial_Num.append(int(np.ceil(ts/hc_trial_bin)))
                process.append(-1)
            self.result["Trial_Num"] = pd.Series(Trial_Num,name="Trial_Num")
            self.result["process"] = pd.Series(process,name="process")

        else: # self.exp=="task"
            if not "aligned_behave2ms" in self.result.keys():
                self.aligned_behave2ms()
            self.result["Trial_Num"] = self.result["aligned_behave2ms"]["Trial_Num"]
            self.result["process"] = self.result["aligned_behave2ms"]["process"]

        print("'Trial_Num' and 'process' were added")
        # self.savesession("Trial_Num","process")
        

    def add_Context(self,context_map=None):
        """
        the same size as df.
        """
        print("FUN::add_Context")
        Context = (pd.merge(self.result["Trial_Num"],self.result["behavelog_info"][["Trial_Num","Enter_ctx"]],how="left",on=["Trial_Num"])["Enter_ctx"]).fillna(-1)# 将NaN置换成-1
        print("'Contex' came frome 'Enter_ctx'")
        self.result["Context"] = pd.Series([int(i) for i in Context],name="Context")
        print("'Context' has been added")

        if not context_map == None:
            self.result["Context"] = pd.Series([context_map[i] for i in self.Context],name="Context")
            print("'Context' was represented as A,B,C or ON")
        else:
            print("'Context' was represented as 0,1,2 or -1")

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

    def add_c_all_track_points(self,):
        """
        """
        print("FUN:: add_c_all_track_points")
        if self.exp == "task":
            if not "all_track_points" in self.result.keys():
                behavevideo = self.result["behavevideo"][0] if behavevideo == None else behavevideo
                coords = LT_Videos(behavevideo).draw_midline_of_whole_track_for_each_day(aim="midline_of_track",count=7)
                self.result["all_track_points"] = coords
                self.savesession("all_track_points")
            else:
                print("all_track_points has been there")


    def add_Body_speed(self,scale=0.2339021309714166):

        print("FUN::add_Body_speed")

        if self.exp == "task":
            Body_speed,Body_speed_angle = speed(X=self.result["aligned_behave2ms"]["Body_x"]
                                                    ,Y=self.result["aligned_behave2ms"]["Body_y"]
                                                    ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                    ,s=scale)
            print("Body_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
            self.result["Body_speed"]=speed_optimize(Body_speed,method="gaussian_filter1d",sigma=3)
            self.result["Body_speed_angle"]=Body_speed_angle
            print("Body_speed and Body_speed_angle have been added")

        else:
            print("homecage session has no 'Body_speed'")

    def add_Head_speed(self,scale=0.2339021309714166):
        print("FUN::add_Head_speed")

        if self.exp == "task":
            Head_speed,Head_speed_angle = speed(X=self.result["aligned_behave2ms"]["Head_x"]
                                                    ,Y=self.result["aligned_behave2ms"]["Head_y"]
                                                    ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                    ,s=scale)
            print("Head_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
            self.result["Head_speed"]=speed_optimize(Head_speed,method="gaussian_filter1d",sigma=3)
            self.result["Head_speed_angle"]=Head_speed_angle
            print("Head_speed and Head_speed_angle have been added")

        else:
            print("homecage session has no 'Head_speed'")



    def add_running_direction(self,according="Body"):
        print("FUN::add_running_direction")

        if self.exp == "task":
            running_direction = []
            key = "%s_speed_angle"%according
            if not key in ["Body","Head"]:
                print("no %s_speed_angle"%according)
                according = "Body"
            for speed_angle in self.result[key]:
                if speed_angle > 90 and speed_angle < 280 :
                    running_direction.append(0)
                else:
                    running_direction.append(1)
            self.result["running_direction"]=pd.Series(running_direction,name="running_direction")
            print("running_direction has been added")
        else:
            print("homecage session has no 'running_direction'")



    def add_alltrack_placebin_num(self,according = "Head",place_bin_nums=[4,4,40,4,4,4],behavevideo=None):
        """
        need to draw line in behavevideo, so save the coords of these lines.
        """
        print("FUN::add_alltrack_placebin_num")

        if self.exp == "task":

            if "all_track_points" in self.result.keys():
                coords = self.result["all_track_points"]
            else:
                behavevideo = self.result["behavevideo"][0] if behavevideo == None else behavevideo
                coords = LT_Videos(behavevideo).draw_midline_of_whole_track_for_each_day(aim="midline_of_track",count=7)
                self.result["all_track_points"] = coords
                self.savesession("all_track_points")

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
                    if len(place_bin_No)>1:
                        place_bin_No.append(place_bin_No[-1])
                    else:
                        place_bin_No.append(0) # 如果是第一帧就tracking出错，那么默认就是 第0 个placebin

            self.result["place_bin_No"] = pd.Series(place_bin_No,name="place_bin_No")

            print("'place_bin_No' has been added")

        else:
            print("homecage session has no 'place_bin_No'")

#%% which are about to discrete
    def add_is_in_context2(self):
        """
        which is about to discrete
        """
        print("FUN::add_is_in_context")
        if self.exp == "task":
            mask = self.result["in_context_mask"]
            is_in_context=[]
            for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                if 255 in mask[int(y),int(x)]:
                    is_in_context.append(0)
                else:
                    is_in_context.append(1)
            self.result["is_in_context"]=pd.Series(is_in_context,name="is_in_context")
            print("'is_in_context' has been added")

        else:
            print("homecage session has no 'is_in_context'")

    def add_is_in_context(self):
        """
        which is about to discrete
        """
        print("FUN::add_is_in_context")
        if self.exp == "task":
            is_in_context=[]
            for x in self.result["aligned_behave2ms"]["Body_x"]:
                if x>=self.result["all_track_points"][2][0] and x<=self.result["all_track_points"][3][0]:
                    is_in_context.append(1)
                else:
                    is_in_context.append(0)
            self.result["is_in_context"] = pd.Series(is_in_context,name="is_in_context")
            print("'is_in_context' has been added")
        else:
            print("homecage session has no 'is_in_context'")

    def add_is_in_lineartrack(self):

        print("FUN::add_is_in_lineartrack")
        if self.exp == "task":
            mask = self.result["in_lineartrack_mask"]
            is_in_lineartrack=[]
            for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                if 255 in mask[int(y),int(x)]:
                    is_in_lineartrack.append(0)
                else:
                    is_in_lineartrack.append(1)
            self.result["is_in_lineartrack"]=pd.Series(is_in_lineartrack,name="is_in_lineartrack")
            print("'is_in_lineartrack' has been added")

        else:
            print("homecage session has no 'is_in_lineartrack'")

    def add_incontext_placebin_num(self,according="Head",placebin_number=40):
        print("FUN::add_incontext_placebin_num")

        if self.exp == "task":
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
                            print("%s is in context but not in any place bin"%x)
            self.result["in_context_placebin_num"] = pd.Series(in_context_placebin_num,name="in_context_placebin_num")
            print("in_context_placebin_num has been added, which should start from 1, 0 means out of context")
        else:
            print("homecage session has no 'in_context_placebin_num'")

    def add_zone2result(self,zone="in_lineartrack"):
        """
        need mannually draw zone in behavevideo, save the coordinates
        """
        print("FUN:: add_zone2result at zone %s"%zone)

        print("FUN:: add_zone2result at zone %s"%zone)
        mask = zone+"_mask"
        coords = zone+"_coords"
        if not mask in self.result.keys():
            if os.path.exists(self.result["behavevideo"]):
                try:
                    temp_mask,temp_coords=Video(self.result["behavevideo"]).draw_rois(aim=zone,count = 1)
                except Exception as e:
                    print(e)
                    sys.exit()
            else:
                print("DON'T EXIST: %s "%self.result["behavevideo"])
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
        print("FUN:: add_info2aligned_behave2ms scale: %scm/pixel ; placebin_number: %s"%(scale,placebin_number))

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
                print("'in_context' has been added")
                update = 1
            else:
                print("'in_context' has been there")

            #2 添加“Body_speed" "Body_speed_angle"
            if not "Body_speed" in self.result.keys():
                Body_speed,Body_speed_angle = Video.speed(X=self.result["aligned_behave2ms"]["Body_x"]
                                                        ,Y=self.result["aligned_behave2ms"]["Body_y"]
                                                        ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                        ,s=scale)
                print("Body_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
                self.result["Body_speed"]=speed_optimize(Body_speed,method="gaussian_filter1d",sigma=3)
                self.result["Body_speed_angle"]=Body_speed_angle
                print("Body_speed and Body_speed_angle have been added")
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
                print("in_context_running_direction has been added")
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
                                print("%s is in context but not in any place bin"%x)

                print("in_context_placebin_num should start from 1, 0 means out of context")
                        
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

#%%

    def add_behave_choice_side(self,):
        print("FUN::add_behave_choice_side")

        behave_choice_side = []
        if self.result["behavelog_info"]["Left_choice"][0]>self.result["behavelog_info"]["Right_choice"][0]:
            behave_choice_side.append("left")
        else:
            behave_choice_side.append("right")

        for i in np.diff(self.result["behavelog_info"]["Left_choice"]):
            if i == 0:
                behave_choice_side.append("right")
            else:
                behave_choice_side.append("left")

        self.result["behave_choice_side"] = pd.Series(behave_choice_side,name="behave_choice_side")
        print("'behave_choice_side' was added.")


    def add_behave_forward_context(self,according="Enter_ctx"):
        print("FUN::add_behave_forward_context")

        self.result["behave_forward_context"] = self.result["behavelog_info"][according]
        print("'behave_forward_context' was added according to %s."%according)

    def add_behave_forward_noise(self,according="Enter_ctx"):
        print("FUN::add_behave_forward_noise")
        behave_forward_noise=[]
        if not "behave_forward_context" in self.result.keys():
            self.add_behave_forward_context(according=according)
        context = self.result["behave_forward_context"]
        if context[0]==1:
            behave_forward_noise.append(0)
        else:
            behave_forward_noise.append(1)

        for context_change in np.diff(context):
            if context_change == 0:
                behave_forward_noise.append(0)
            else:
                behave_forward_noise.append(1)

        self.result["behave_forward_noise"] = behave_forward_noise
        print("'behave_forward_noise' was added according to %s."%according)


    def add_behave_Trial_duration(self):
        """
        """
        print("FUN::add_behave_Trial_duration")
        durations = np.diff(self.result["behavelog_time"],axis=1)
        behave_Trial_durations = pd.DataFrame(durations,columns=["process1","process2","processs3","process4","process5"])
        behave_Trial_durations["Trial"] = np.sum(behave_Trial_durations,axis=1)
        
        self.result["behave_Trial_durations"] = behave_Trial_durations
        print("'behave_Trial_durations' was added.")

    def add_behave_reward(self):
        """
        """
        print("FUN::add_behave_reward")
        self.result["behave_reward"] = self.result["behavelog_info"]["Choice_class"]
        print("'behave_reward' was added")



    def trim_df(self,*args,**kwargs):
        """
        code is excuted along the order of inputted args and kwargs arguments. the order of kwargs generating a DataFrame of trimed_index doesn't affect the result, however the order of args does.
        """
        self.trim_index = pd.DataFrame()
        self.trim_index["Trial_Num"] = self.result["Trial_Num"]>0
        print("trim_index was initialed by Trial_Num>=0")

        for key,value in kwargs.items():
            if key == "Body_speed":
                self._trim_Body_speed(min_speed=value)

            if key == "Head_speed":
                self._trim_Head_speed(min_speed=value)

            if key == "process":
                self._trim_process(process_list=value)

            if key=="Trial":
                self._trim_trial(trial_list=value)

            if key == "placebin":
                self._trim_placebin(placebin_list=value)

            if key == "in_context":
                self._trim_in_context(value=value)


        for arg in args:
            if arg =="S_dff":
                try:
                    self.df = pd.DataFrame(self.result["S_dff"],columns=self.result["idx_accepted"])
                    self.shape = self.df.shape
                    print("'S_dff' is taken as original self.df")
                except:
                    self.df = self.df
                    print("S_dff doesn't exist, sigraw is used.")

            if arg == "sigraw":
                self.df = pd.DataFrame(self.result["sigraw"],columns=self.result["idx_accepted"])
                self.shape = self.df.shape
                print("'sigraw' is taken as original self.df")

            if arg=="detect_ca_transient":
                _,self.df,_= self.detect_ca_transients()
                print("trim_df : calcium transients are detected and ")

            if arg=="force_neg2zero":                
                self.df[self.df<0]=0
                print("trim_df : negative values are forced to be zero")

            if arg == "Normalization":
                pass

            if arg== "Standarization":
                pass

        print("trim_df : df was trimmed.")

        return self.df,self.trim_index.all(axis=1)

    def _trim_Body_speed(self,min_speed=3):
        self.trim_index["Body_speed"] = self.result["Body_speed"]>min_speed
        print("trim_index : Body_speed>%s cm/s"%min_speed)

    def _trim_Head_speed(self,min_speed=None):
        self.trim_index["Head_speed"] = self.result["Head_speed"]>min_speed
        print("trim_index : Head_speed>%s cm/s"%min_speed)

    def _trim_process(self,process_list):
        self.trim_index["process"] = self.result["process"].isin(process_list)
        print("trim_index : process are limited in %s"%min_speed)

    def _trim_trial(self,trial_list):
        self.trim_index["Trial"] = self.result["Trial_Num"].isin(trial_list)
        print("trim_index : trial are limited in %s"%trial_list)

    def _trim_placebin(self,placebin_list):
        self.trim_index["placebin"] = self.result["place_bin_No"].isin(placebin_list)
        print("trim_index : placebins are limited in %s"%placebin_list)

    def _trim_in_context(self,value):
        if value:
            self.trim_index["in_context"] = self.result["is_in_context"]
            

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