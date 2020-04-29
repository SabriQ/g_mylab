# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 16:07:26 2019

@author: Sabri
"""
import os,re
from mylab.Cvideo import Video
import scipy.io as spio
import glob
import pickle
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

    def copy2(self,dst):
        if os.path.exists(self.file_path):
            from shutil import copyfile
            newname = os.path.join(dst,self.file_name)
            copyfile(self.file_path,newname)
            print(f"Transfer {self.file_path} successfully")
        else:
            print("{self.file_path} does not exists.")
            

#        if isinstance(variable,str) or isinstance(variable,int),or isinstance(variable,float):
            
        
def save_pkl(result,result_path):
    with open(result_path,'wb') as f:
        pickle.dump(result,f)
    print("%s is saved."%result_path)
def load_pkl(result_path):
    with open(result_path,'rb') as f:
        result = pickle.load(f)
    print("%s is loaded."%result_path)
    return result

def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict


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
