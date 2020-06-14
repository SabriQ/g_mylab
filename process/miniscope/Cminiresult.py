import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob
import json
import scipy.io as spio
import pickle
from mylab.Cmouseinfo import MouseInfo
from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *

class MiniResult():
    """
    to generate file such as "191172_in_context.mat"
    This father class is to 
        1.load MiniResult through reading pkl,mat or hdf5 file 
        2.load/save mouseinfo
    """
    def __init__(self,mouse_info_path,cnmf_result_dir):
        self.mouse_info_path = mouse_info_path
        self.cnmf_result_dir = cnmf_result_dir
        self.ana_result_path = os.path.join(self.cnmf_result_dir,"ana_result.pkl")
        
        # here is the txt file containing all the info
        self.mouse_info = MouseInfo(self.mouse_info_path)
        
        self.mspkl_Path=glob.glob(os.path.join(self.cnmf_result_dir,'ms.pkl'))
        self.msmat_Path=glob.glob(os.path.join(self.cnmf_result_dir,'*post_processed*.mat'))
        self.hdf5_Path=glob.glob(os.path.join(self.cnmf_result_dir,'*/hdf5'))

        self.load_post_processed_mat()
        self.load_ana_result()
        


    @property
    def keys(self):
        return self.ana_result.keys()

    @property
    def save(self):
        return self.save_ana_result_pkl()


    def load_post_processed_mat(self):
        print("loading cnmf_result...")

        if self.msmat_Path:
            self.cnmf_result = load_mat(self.msmat_Path[0])
            print("load post_processed_mat file")
        else:
            print("cnmf_result generated by CNMF is inexistence.")
            sys.exit()
        print("loaded cnmf_result")
            
    def load_ana_result(self):
        if os.path.exists(self.ana_result_path):
            with open(self.ana_result_path,'rb') as f:
                self.ana_result =  pickle.load(f)
            print("reload %s"% self.ana_result_path)
        else:
            self.ana_result = {}
            print("initialize %s"% self.ana_result_path)


    def save_ana_result_pkl(self):
        with open(self.ana_result_path,'wb') as f:
            pickle.dump(self.ana_result,f)        
        print("ana_result is saved as %s."%self.ana_result_path)


    def _equal_frames(self,l_dff,ms_ts):
        l_ms_ts = sum([len(i) for i in ms_ts])
        print(">>>>>",[l_dff,l_ms_ts])
        if l_dff != l_ms_ts:
            return 0
        else:
            return 1

    def load_msts(self,l_dff):
        # attention to check whether frames of ms_ts are equal to that of traces
        with open(self.ms_ts_Path[0],'rb') as f:
            ms_ts = pickle.load(f)

        if self._equal_frames(l_dff,ms_ts):
            print("frames of timestaps and traces are equal!")
            self.ana_result["ms_ts"] = ms_ts
        else:
            print("please regenerate ms_ts")
            print("ms_ts: %s;frames: %s"%(dff.shape[0],sum([len(i) for i in ms_ts])))


    def Fig_Deconvoluted_neuronal_activity(self):
        """
        Neurons are ranked by peak to noises ratio (PNR)
        Heatmap white to black
        Neuron_id-Time(minitues)
        """
        pass
        
    def Fig_fraction_of_sessions_active(self):
        """
        两幅图
        1 Neurons_activate(%)-session
        2 Neurons-fraction_of_session_active(0-1)
        """
        pass
if __name__ == "__main__":
    mr = MiniResult(mouse_info_path=r"Z:\QiuShou\mouse_info\191173_info.txt",cnmf_result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all")
    print(mr.keys)
