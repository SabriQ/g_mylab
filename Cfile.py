# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 16:07:26 2019

@author: Sabri
"""
import os
from Cvideo import Video
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
            newname = os.path.join(self.dirname,prefix+'_'+self.file_name_noextension+"_"+suffix+self.extension)
            if keep_origin:
                from shutil import copyfile
                copyfile(self.file_path,newname)
                print("Rename file successfully with original file kept")
            else:
                os.rename(self.file_path, newname)
                print("Rename file successfully with original file deleted")
        else:
            print(f"{self.file_path} does not exists.")

    def copy2(self,dst):
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
    def restrict_area(self):
        Video(self.trackvideo_path).draw_rois(aim="restrict",count = 1)
if __name__ == "__main__":
#    File(r"C:\Users\Sabri\Desktop\test\test_180228160127Cam-1_Test.asf").add_prefixAsuffix(prefix="test",suffix="Test",keep_origin=False)
#    File(r"C:\Users\Sabri\Desktop\test\test_test_180228160127Cam-1_Test_Test.asf").copy2(r"C:\Users\Sabri\Desktop\test\tt")
    TrackFile(r"C:\Users\Sabri\Desktop\test\trackfiles\191174A-20191110-221945DeepCut_resnet50_linear_track_40cm_ABSep26shuffle1_500000.h5").restrict_area()


