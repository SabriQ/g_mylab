# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 16:07:26 2019

@author: Sabri
"""
import os,re,sys
import scipy.io as spio
import glob
import numpy as np
import pandas as pd
from shutil import copyfile
import datetime
import warnings
import csv
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt

class File():
    def __init__ (self,file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.file_name_noextension = self.file_name.split(".")[0]
        self.extension = os.path.splitext(self.file_path)[-1]
        self.abs_prefix = os.path.splitext(self.file_path)[-2]
        self.dirname = os.path.dirname(self.file_path)
    def add_prefixAsuffix(self,prefix = "prefix", suffix = "suffix",keep_origin=True):
        '''
        会在suffix前或者prefix后自动添加“——”
        keep_origin = True，表示会复制原文件，否则是直接操作源文件
        '''
        if os.path.exists(self.file_path):
            newname = os.path.join(self.dirname,prefix+self.file_name_noextension+suffix+self.extension)
            if keep_origin:
                copyfile(self.file_path,newname)
                print("Rename file successfully with original file kept")
            else:
                os.rename(self.file_path, newname)
                print("Rename file successfully with original file deleted")
        else:
            print(f"{self.file_path} does not exists.")

    def copy2dst(self,dst):
        """
        将文件copy到指定的位置（文件夹，不是文件名）
        dst: path of directory
        """
        if os.path.exists(self.file_path):
            newname = os.path.join(dst,self.file_name)
            copyfile(self.file_path,newname)
            print(f"Transfer {self.file_path} successfully")
        else:
            print("{self.file_path} does not exists.")

class TimestampsFile(File):
    def __init__(self,file_path,method="ffmpeg",camNum=0):
        super().__init__(file_path)
        self.method = method
        self.camNum = camNum
        if not method in ["datetime","ffmpeg","miniscope"]:
            print("method are only available in 'ffmpeg','datetime',")
            sys.exit()

        self.ts=self.read_timestamp()
        # if self.ts.isnull().any():
        #     print(self.ts)
        #     print("ATTENTION: therea are 'NaN' in timestamps !!")

    def datetime2minisceconds(self,x,start):    
        # print(x,end = " " )
        delta_time = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')-start
        return int(delta_time.seconds*1000+delta_time.microseconds/1000)

    def read_timestamp(self):
        if self.method == "datetime":
            data = pd.read_csv(self.file_path,sep=",")
            start = datetime.datetime.strptime(data["0"][0], '%Y-%m-%d %H:%M:%S.%f')
            data["0"]=data["0"].apply(self.datetime2minisceconds,args=[start,])
            return pd.Series(data["0"]/1000,name="datetime_ms")
        if self.method  == "ffmpeg":
            try:
                ts = pd.read_csv(self.file_path,encoding="utf-16",header=None,sep=" ",names=["ffmpeg_ts"])
                return ts
            except:
                print("default method is ffmpeg, try 'datetime'")
                sys.exit()
        if self.method == "miniscope":
            temp=pd.read_csv(self.file_path,sep = "\t", header = 0)
            temp = temp[temp["camNum"]==self.camNum] ## wjn的 case 是1， 其他的scope是0
            print("camNum in miniscope is %s"%self.camNum)
            # incase the first frame of timestamps is not common 比如这里会有一些case的第一帧会出现很大的正/负数
            if np.abs(temp['sysClock'][0])>temp['sysClock'][1]:
                value = temp['sysClock'][1]-13 # 用第2帧的时间减去13，13是大约的一个值
                if value < 0:
                    temp['sysClock'][0]=0
                else:
                    temp['sysClock'][0]=value

            ts = pd.Series(temp['sysClock'].values,name="miniscope_ts")
            return ts

class CPPLedPixelValue(File):
    def __init__(self,file_path):
        super().__init__(file_path)

        if not self.file_path.endswith("_ledvalue_ts.csv"):
            pirnt("wrong file input")

        self.df = pd.read_csv(self.file_path)
    
    def show_change_along_thresholds(self,v1,v2):
        """
        v1: specified the minimum threshold
        v2: specified the maxmum threshold
        """
        threshods = np.arange(v1,v2)
        points1=[]
        points2=[]
        for thre in threshods:
            points1.append(sum([ 1 if i< thre  else 0 for i in self.df["1"]]))
            points2.append(sum([ 1 if i< thre  else 0 for i in self.df["2"]]))

        plt.plot(threshods,points1)
        plt.plot(threshods,points2)
        plt.xlabel("Threshod of ROI pixel value")
        plt.ylabel("Numbers of led-off frames")
        plt.title("For choosing threshold")
        plt.legend(["led1","led2"])
        # plt.axvline(x=930,color="green",linestyle="--")
        plt.show()

    def _led_off_epoch_detection(self,trace,thresh):
        """
        trace: any timeseries data. 
        thresh: the minimum absolute deviation from baseline, which could be negtive.
        """
        trace = np.array(trace)
        points = np.reshape(np.argwhere(trace<thresh),-1)
        epoch_indexes = []
        last_epoch_index=[]
        for i in range(len(points)):
            if i == 0:
                last_epoch_index.append(points[i])
            else:
                if points[i]-points[i-1]==1:
                    last_epoch_index.append(points[i])
                else:
                    epoch_indexes.append(last_epoch_index)
                    last_epoch_index=[]
                    last_epoch_index.append(points[i])        
        return epoch_indexes

    def lick_water(self,thresh,led1_trace,led2_trace,show=False):
        led1_indexes = self._led_off_epoch_detection(led1_trace,thresh)
        led2_indexes= self._led_off_epoch_detection(led2_trace,thresh)

        led1_off = []
        led1_offset = []
        for i in led1_indexes:
            led1_offset.append(i[0])
            for j in i:
                led1_off.append(j)

        led2_off = []
        led2_offset = []
        for i in led2_indexes:
            led2_offset.append(i[0])
            for j in i:
                led2_off.append(j)

        self.df["led1_off"]=0
        self.df["led1_off"][led1_off]=1
        self.df["led1_offset"]=0
        self.df["led1_offset"][led1_offset]=1

        self.df["led2_off"]=0
        self.df["led2_off"][led2_off]=1
        self.df["led2_offset"]=0
        self.df["led2_offset"][led2_offset]=1

        if show:
            plt.figure(figsize=(600,1))
            plt.plot(self.df["ts"],led1_trace,color="orange")
            for epochs_index in led1_indexes:
                if len(epochs_index)==1:
                    plt.scatter(self.df["ts"][epochs_index[0]],led1_trace[epochs_index[0]],s=20,marker="x",c="green")
                else:
                    plt.plot(self.df["ts"][epochs_index[0]:(epochs_index[-1]+1)],led1_trace[epochs_index[0]:(epochs_index[-1]+1)],color="red")

            plt.plot(self.df["ts"],led2_trace+1000,color="blue")
            for epochs_index2 in led2_indexes:
                if len(epochs_index2)==1:
                    plt.scatter(self.df["ts"][epochs_index2[0]],led2_trace[epochs_index2[0]]+1000,s=20,marker="x",c="green")
                else:
                    plt.plot(self.df["ts"][epochs_index2[0]:(epochs_index2[-1]+1)],led2_trace[epochs_index2[0]:(epochs_index2[-1]+1)]+1000,color="red")

        self.df.to_csv(self.file_path,index = False,sep = ',')
        print("lick_water information has been added and saved.")

class TrackFile(File):
    def __init__(self,file_path):
        super().__init__(file_path)

        if not self.file_path.endswith(".h5"):
            print("track file is not end with h5")
        else:
            self._load_file()

    @property
    def key_PLX(self):
        key = re.findall("\d{13}",self.file_name)
        if len(key)>0:
            return key[0]
        else:
            return 0
    @property
    def key_YMDHMS(self):
        key = re.findall("\d{8}-\d{6}",self.file_name)
        if len(key)>0:
            return key[0]
        else:
            return 0
    
    def _load_file(self):
        track = pd.read_hdf(self.file_path)
        # print(track.columns)
        try:
            self.behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                         columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
        except:
            print("you might not mark 'Tail'")
            self.behave_track=pd.DataFrame(track[track.columns[0:6]].values,
                         columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh'])

        print("Trackfile is loaded.")

    def _dataframe2nparray(self,df):
        """
        Transfer dict or pd.DataFrame to np.array
        """
        if isinstance(df,dict):
            print("df is a dict")
            for key in list(df.keys()):
                if isinstance(df[key],pd.core.frame.DataFrame):
                    df[str(key)+"_column"]=np.array(df[key].columns)
                    df[key]=df[key].values                    
                    print("%s has transferred to numpy array"%key)
                if isinstance(df[key],dict):
                    return dataframe2nparray(df[key])
            return df
        elif isinstance(df,pd.core.frame.DataFrame):
            print("df is a DataFrame")
            return {"df":df.values,"df_columns":list(df.columns)}

    def savepkl2mat(self,):
        """
        save pkl file as mat
        """
        savematname = self.file_path.replace("h5","mat")
        spio.savemat(savematname,self._dataframe2nparray(self.behave_track))
        print("save mat as %s"%savematname)

    def extract_behave_track(self,parts=["Head","Body","Tail"]):

        track = pd.read_hdf(self.file_path)

        ispart_available = pd.Series(parts)[~pd.Series(parts).isin(track.columns.get_level_values(1))]
        if len(ispart_available)>0:
            print("%s is not available"%list(ispart_available))
        else:
            print("%s are all available."%parts)

        cols = track.columns.get_level_values(level=1).isin(parts)
        new_columns=[]
        for part in parts:
            new_columns.append(part+"_x")
            new_columns.append(part+"_y")
            new_columns.append(part+"_lh")

        self.behave_track=track.iloc[:,cols]
        self.behave_track.columns=new_columns

        return self.behave_track


    @staticmethod
    def _angle(dx1,dy1,dx2,dy2):
        """
        dx1 = v1[2]-v1[0]
        dy1 = v1[3]-v1[1]
        dx2 = v2[2]-v2[0]
        dy2 = v2[3]-v2[1]
        """
        angle1 = math.atan2(dy1, dx1) * 180/math.pi
        if angle1 <0:
            angle1 = 360+angle1
        # print(angle1)
        angle2 = math.atan2(dy2, dx2) * 180/math.pi
        if angle2<0:
            angle2 = 360+angle2
        # print(angle2)
        return abs(angle1-angle2)

    def speed(self,X,Y,T,s,sigma=3):
        """
        X
        Y
        T
        s
        """
        speeds=[0]
        speed_angles=[0]
        for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
            distance = np.sqrt(delta_x**2+delta_y**2)
            speeds.append(distance*s/delta_t)
            speed_angles.append(self._angle(1,0,delta_x,delta_y))
        if sigma:
            speeds=gaussian_filter1d(speeds)
            print("speeds are filted by gaussian_filter1d with sigma 3")
        return pd.Series(speeds),pd.Series(speed_angles) # in cm/s



# from mylab.ana.miniscope.context_exposure.Cminiana import MiniAna as MA

class LinearTrackBehavioralLogFile(File):
    def __init__(self,file_path,context_map=["B","A","C","N"]):
        super().__init__(file_path)

        self.context_map = context_map
        # print("context map is %s"%self.context_map)
        self.date = re.findall(r"(\d{8})-\d{6}",self.file_path)[0]
        self.mouse_id = re.findall(r"(\d+)-\d{8}-\d{6}",self.file_path)[0]
        self.aim = re.findall(r"LickWater-(.*)-%s"%self.mouse_id,self.file_path)[0]
        self.data = pd.read_csv(self.file_path ,skiprows=3)

        self.Enter_Context = pd.Series ([self.context_map[i] for i in self.data["Enter_ctx"]])
        self.Exit_Context = pd.Series ([self.context_map[i] for i in self.data["Exit_ctx"]] )

    @property
    def choice(self):
    
        Choice = []
        if self.data["Left_choice"][0]==1:
            Choice.append("left")
        else:
            Choice.append("right")
            
        for choice in (np.diff(self.data["Left_choice"])-np.diff(self.data["Right_choice"])):
            if choice == 1:
                Choice.append("left")
            else:
                Choice.append("right")
                
        return pd.Series(Choice,name="choice")
    

    @property
    def noise(self):
        """
        Series contains only 0 and 1, 0 means no motion, 1 means motion
        """
        noisy=[]
        if self.data["Enter_ctx"][0]==1:
            noisy.append(0)
        else:
            noisy.append(1)

        for context_change in np.diff(self.data["Enter_ctx"]):
            if context_change == 0:
                noisy.append(0)
            else:
                noisy.append(1)
                
        return pd.Series(noisy,name="noise")


    @property
    def reward(self):
        return self.data["Choice_class"]
    
    @property
    def Trial_duration(self):        
        durations = np.diff(self.data.iloc[:,-6:],axis=1)
        Trial_duration = pd.DataFrame(durations,columns=["process1","process2","process3","process4","process5"])
        Trial_duration["Trial"] = np.sum(durations,axis=1)
        return Trial_duration


    @property
    def bias(self):
        return  (max(self.data["Left_choice"])-max(self.data["Right_choice"]))/(max(self.data["Left_choice"])+max(self.data["Right_choice"]))

    @property
    def Total_Accuracy(self):
        return  sum(self.data["Choice_class"])/len(self.data["Choice_class"])

    @property
    def Left_Accuracy(self):
        return sum(self.data["Choice_class"][self.data["Choice_side"]=="left"])/len(self.data["Choice_class"][self.data["Choice_side"]=="left"])
    
    @property
    def Right_Accuracy(self):
        return sum(self.data["Choice_class"][self.data["Choice_side"]=="right"])/len(self.data["Choice_class"][self.data["Choice_side"]=="right"])

    @property
    def Context_A_Accuracy(self):
        return  sum(self.data["Choice_class"][self.Enter_Context=="A"])/len(self.data["Choice_class"][self.Enter_Context=="A"])

    @property
    def Context_B_Accuracy(self):
        return sum(self.data["Choice_class"][self.Enter_Context=="B"])/len(self.data["Choice_class"][self.Enter_Context=="B"])
    

class FreezingFile(File):
    def __init__(self,file_path):
        super().__init__(file_path)
        self.freezingEpochPath = os.path.join(self.dirname,'behave_video_'+self.file_name_noextension+'_epoch.csv')
    def _rlc(self,x):
        name=[]
        length=[]
        for i,c in enumerate(x,0):
            if i ==0:
                name.append(x[0])
                count=1
            elif i>0 and x[i] == name[-1]:
                count += 1
            elif i>0 and x[i] != name[-1]:
                name.append(x[i])
                length.append(count)
                count = 1
        length.append(count)
        return name,length

    def freezing_percentage(self,threshold = 0.005, start = 0, stop = 300,show_detail=False,percent =True,save_epoch=True): 
        data = pd.read_csv(self.file_path)
        print(len(data['0']),"time points ;",len(data['Frame_No']),"frames")

        data = data.dropna(axis=0)             
        #print(f"{self.file_path}")
        data = data.reset_index()
        # slice (start->stop)
        
        #start_index
        if start>stop:
            start,stop = stop,start
            warning.warn("start time is later than stop time")
        if start >=max(data['0']):
            warnings.warn("the selected period start is later than the end of experiment")
            sys.exit()
        elif start <=min(data['0']):            
            start_index = 0
        else:
            start_index = [i for i in range(len(data['0'])) if data['0'][i]<=start and  data['0'][i+1]>start][0]+1

        #stop_index
        if stop >= max(data['0']):
            stop_index = len(data['0'])-1
            warnings.warn("the selected period exceed the record time, automatically change to the end time.")
        elif stop <=min(data['0']):
            warnings.warn("the selected period stop is earlier than the start of experiment")
            sys.exit()
        else:            
            stop_index = [i for i in range(len(data['0'])) if data['0'][i]<=stop and  data['0'][i+1]>stop][0]

        selected_data = data.iloc[start_index:stop_index+1]

        values,lengthes = self._rlc(np.int64(np.array(selected_data['percentage'].tolist())<=threshold))


        
        sum_freezing_time = 0
        if save_epoch:
            with open(self.freezingEpochPath,'w+',newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["start","stop"])
        for i,value in enumerate(values,0):
            if value ==1:              
                begin = sum(lengthes[0:i])
                end = sum(lengthes[0:i+1])
                if end > len(selected_data['0'])-1:
                    end = len(selected_data['0'])-1
                condition = selected_data['0'].iat[end]-selected_data['0'].iat[begin]
                if condition >=1:
                    if show_detail:
                        print(f"{round(selected_data['0'].iat[begin],1)}s--{round(selected_data['0'].iat[end],1)}s,duration is {round(condition,1)}s".rjust(35,'-'))
                    if save_epoch:
                        with open(self.freezingEpochPath,'a+',newline="") as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow([selected_data['0'].iat[begin],selected_data['0'].iat[end]])
                    sum_freezing_time = sum_freezing_time + condition
                else:
                    sum_freezing_time = sum_freezing_time
        print(f'the freezing percentage during [{start}s --> {stop}s] is {round(sum_freezing_time*100/(stop-start),2)}% ')
        if save_epoch:
            with open(self.freezingEpochPath,'a+',newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["","",f"{round(sum_freezing_time*100/(stop-start),2)}%"])
        if  percent:
            return sum_freezing_time*100/(stop-start)
        else:
            return sum_freezing_time/(stop-start)

class EpmFile(File):
    pass
    
if __name__ == "__main__":
    file = r"C:\Users\Sabri\Desktop\new_method_to_record\behave\LickWater-test-201033-20200825-130238_log.csv"
    data = LinearTrackBehaviorFile(file)
    print(data.Right_Accuracy)
    print(data.Context_A_Accuracy)
    print(data.Context_B_Accuracy)