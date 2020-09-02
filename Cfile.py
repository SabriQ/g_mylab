# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 16:07:26 2019

@author: Sabri
"""
import os,re
from mylab.Cvideo import Video
import scipy.io as spio
import glob
import numpy as np
import pandas as pd
from shutil import copyfile
import datetime

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

        self.ts=self.read_timestamp(method=self.method)
        if self.ts.isnull().any()[0]:
            print(self.ts)
            print("ATTENTION: therea are 'NaN' in timestamps !!")

    def datetime2minisceconds(self,x,start):    
        # print(x,end = " " )
        delta_time = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')-start
        return int(delta_time.seconds*1000+delta_time.microseconds/1000)

    def read_timestamp(self,method = "datetime"):
        if method == "datetime":
            data = pd.read_csv(self.file_path,sep=",")
            start = datetime.datetime.strptime(data["0"][0], '%Y-%m-%d %H:%M:%S.%f')
            data["0"]=data["0"].apply(self.datetime2minisceconds,args=[start,])
            return data["0"]
        if method  == "ffmpeg":
            return pd.read_csv(self.file_path,encoding="utf-16",header=None,sep=" ",names=["0"])
        if method == "miniscope":
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

            ts = pd.DataFrame(temp['sysClock'].values)
            return ts

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
        self.behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                     columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
        print("trackfile is loaded.")

    def _dataframe2nparray(self,df):
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
        savematname = self.file_path.replace("h5","mat")
        spio.savemat(savematname,self._dataframe2nparray(self.behave_track))
        print("save mat as %s"%savematname)

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

    @classmethod
    def speed(cls,X,Y,T,s,sigma=3):
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
            speed_angles.append(cls._angle(1,0,delta_x,delta_y))
        return pd.Series(speeds),pd.Series(speed_angles) # in cm/s

class Free2pFile(File):
    def __init__(self,file_path):
        super().__init__(file_path)

class LinearTrackBehaviorFile(File):
    def __init__(self,file_path,context_map=["A","B","C","N"]):
        super().__init__(file_path)

        self.context_map = ["A","B","C","N"]
        print("context map is %s"%self.context_map)
        self.date = re.findall(r"\d{8}-\d{6}",self.file_path)[0]
        self.mouse_id = re.findall(r"(\d+)-\d{8}-\d{6}",self.file_path)[0]
        self.data = pd.read_csv(self.file_path ,skiprows=3)

        self.Enter_Context = pd.Series ([self.context_map[i] for i in self.data["Enter_ctx"]])
        self.Exit_Context = pd.Series ([self.context_map[i] for i in self.data["Exit_ctx"]] )

        Choice = []
        if self.data["Left_choice"][0]==1:
            Choice.append("left")
        else:
            Choice.append("right")
            
        for choice in (self.data["Left_choice"].diff()[1:]-self.data["Right_choice"].diff()[1:]):
            if choice == 1:
                Choice.append("left")
            else:
                Choice.append("right")
        self.data["Choice_side"] = Choice
    


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
        print(len(data['ts(s)']),"time points ;",len(data['Frame_No']),"frames")
##        if not (len(data['ts(s)']) == len(data['Frame_No'])):
##            warnings.warn("the number of timestamp is not consistent with frame number")
        # na.omit    
        data = data.dropna(axis=0)             
        #print(f"{self.file_path}")
        data = data.reset_index()
        # slice (start->stop)
        
        #start_index
        if start>stop:
            start,stop = stop,start
            warning.warn("start time is later than stop time")
        if start >=max(data['ts(s)']):
            warnings.warn("the selected period start is later than the end of experiment")
            sys.exit()
        elif start <=min(data['ts(s)']):            
            start_index = 0
        else:
            start_index = [i for i in range(len(data['ts(s)'])) if data['ts(s)'][i]<=start and  data['ts(s)'][i+1]>start][0]+1

        #stop_index
        if stop >= max(data['ts(s)']):
            stop_index = len(data['ts(s)'])-1
            warnings.warn("the selected period exceed the record time, automatically change to the end time.")
        elif stop <=min(data['ts(s)']):
            warnings.warn("the selected period stop is earlier than the start of experiment")
            sys.exit()
        else:            
            stop_index = [i for i in range(len(data['ts(s)'])) if data['ts(s)'][i]<=stop and  data['ts(s)'][i+1]>stop][0]
##            print(data)
        selected_data = data.iloc[start_index:stop_index+1]
##        print(selected_data)
        # freezing
        #values,lengthes = self._rlc(np.int64(np.array(selected_data.iloc[:,2].tolist())<=threshold))
        values,lengthes = self._rlc(np.int64(np.array(selected_data['percentage'].tolist())<=threshold))

##        print(values)
##        print(lengthes)
        
        sum_freezing_time = 0
        if save_epoch:
            with open(self.freezingEpochPath,'w+',newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["start","stop"])
        for i,value in enumerate(values,0):
            if value ==1:              
                begin = sum(lengthes[0:i])
                end = sum(lengthes[0:i+1])
                if end > len(selected_data['ts(s)'])-1:
                    end = len(selected_data['ts(s)'])-1
##                print(begin,end,end=' ')
##                print(selected_data['ts(s)'].iat[begin],selected_data['ts(s)'].iat[end])
                condition = selected_data['ts(s)'].iat[end]-selected_data['ts(s)'].iat[begin]
                if condition >=1:
                    if show_detail:
                        print(f"{round(selected_data['ts(s)'].iat[begin],1)}s--{round(selected_data['ts(s)'].iat[end],1)}s,duration is {round(condition,1)}s".rjust(35,'-'))
                    if save_epoch:
                        with open(self.freezingEpochPath,'a+',newline="") as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow([selected_data['ts(s)'].iat[begin],selected_data['ts(s)'].iat[end]])
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

if __name__ == "__main__":
    file = r"C:\Users\Sabri\Desktop\new_method_to_record\behave\LickWater-test-201033-20200825-130238_log.csv"
    data = LinearTrackBehaviorFile(file)
    print(data.Right_Accuracy)
    print(data.Context_A_Accuracy)
    print(data.Context_B_Accuracy)