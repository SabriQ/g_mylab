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
import seaborn as sns



class File():
    def __init__ (self,file_path):
        
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            print("%s does not exist."%self.file_path)
            sys.exit()
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
            data.columns = ["frame_No","ts"]
            start = datetime.datetime.strptime(data["ts"][0], '%Y-%m-%d %H:%M:%S.%f')
            data["ts"]=data["ts"].apply(self.datetime2minisceconds,args=[start,])

            return pd.Series(data["ts"]/1000,name="datetime_ms")
        if self.method  == "ffmpeg":
            try:
                ts = pd.read_csv(self.file_path,encoding="utf-16",header=None,sep=" ",names=["ts"])
            except :
                try:
                    ts = pd.read_csv(self.file_path,header=None,sep=" ",names=["ts"])
                except:
                    print("default method is ffmpeg, try 'datetime'")
                    sys.exit()
            return ts
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



class TrackFile(File):
    """
    Cminiresult 因为内容高度保守，并没有用到 TrackFile 这个类
    """
    def __init__(self,file_path,parts=None):
        super().__init__(file_path)

        self.parts = parts

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

        if not self.file_path.endswith(".h5"):
            print("track file is not end with h5")
        else:
            track = pd.read_hdf(self.file_path)

        parts = ["Head","Body","Tail"] if self.parts == None else self.parts

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

        print("track file is loaded")


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


if __name__ == "__main__":
    pass




    
