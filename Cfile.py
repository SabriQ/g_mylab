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
                from shutil import copyfile
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
            from shutil import copyfile
            newname = os.path.join(dst,self.file_name)
            copyfile(self.file_path,newname)
            print(f"Transfer {self.file_path} successfully")
        else:
            print("{self.file_path} does not exists.")
            



class TrackFile(File):
    def __init__(self,file_path):
        super().__init__(file_path)
        self.trackvideo_path = os.path.join(self.dirname,self.file_name_noextension+'_labeled.mp4')
        self.trackfile_path = os.path.join(self.dirname,self.file_name_noextension+'h5')
        self._load_file()

    def _load_file(self):
        track = pd.read_hdf(self.trackfile_path)
        self.behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                     columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])


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


if __name__ == "__main__":
    #%%
    pnglists= glob.glob(r"C:\Users\Sabri\Desktop\test\results\sum01\*145304*.png")
    for pnglist in pnglists:    
        File(pnglist).add_prefixAsuffix(prefix="6_90_",suffix="",keep_origin=True)
#%%
#    File(r"C:\Users\Sabri\Desktop\test\test_180228160127Cam-1_Test.asf").add_prefixAsuffix(prefix="test",suffix="Test",keep_origin=False)
#    File(r"C:\Users\Sabri\Desktop\test\test_test_180228160127Cam-1_Test_Test.asf").copy2(r"C:\Users\Sabri\Desktop\test\tt")
#    TrackFile(r"C:\Users\Sabri\Desktop\test\trackfiles\191174A-20191110-221945DeepCut_resnet50_linear_track_40cm_ABSep26shuffle1_500000.h5").restrict_area()
#%%
    #    import glob
#    videolists = glob.glob(r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_CFC\RawData\201910*\*\*\*1000000.csv")
#
#    for video in videolists:
#        File(video).add_prefixAsuffix(prefix = "behave_video_",suffix ="",keep_origin=True)
#%%
    print()
