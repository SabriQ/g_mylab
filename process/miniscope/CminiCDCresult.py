from mylab.process.miniscope.Cminiresult import MiniResult as MR
from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as pyplot
from mylab.Cvideo import Video
from mylab.Cmouseinfo import MouseInfo
import glob,os,sys
import math
class MiniCDCResult(MR):
    """
    将行为学和miniscope的数据结合在一块
    每个behave video分开跑
    """
    def __init__(self,mouse_info_path,cnmf_result_dir,behave_dir):
        super().__init__(mouse_info_path,cnmf_result_dir)
        self.exp_name = "CDC"

        if not self.exp_name in self.mouse_info.keys:
            self.mouse_info.add_exp(exp=self.exp_name)
            print("add json %s"%self.exp_name)

        self.behave_dir = behave_dir
        print(self.behave_dir)
        self.mouse_info.save
        # here are all the possible format of self.genesulted by CNMF
        self.ms_ts_Path=glob.glob(os.path.join(self.cnmf_result_dir,'ms_ts.pkl'))


        self.check_behave_info()

    def dlctrack2behavesessions(self,behave_trackfiles,behave_timestamps,behave_logfiles)


if __name__ == "__main__":
    lw_result = MiniLWResult(mouse_info_path=r"Z:\QiuShou\mouse_info\202016_info.txt"
        ,cnmf_result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191086\20191016_102454_all"
        ,behave_dir= r"X:\miniscope\2020*\*202016*")
    lw_result.run()