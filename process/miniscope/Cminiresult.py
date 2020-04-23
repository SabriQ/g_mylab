import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob
import json
import scipy.io as spio
import pickle
from mylab.Cmouseinfo import MouseInfo
class MiniResult():
    """
    to generate file such as "191172_in_context.mat"
    This father class is to 
        1.load MiniResult through reading pkl,mat or hdf5 file 
        2.load/save mouseinfo
    """
    def __init__(self,mouse_info_path,cnmf_result_dir):
        self.cnmf_result_dir = cnmf_result_dir
        self.ana_result_path = os.path.join(self.cnmf_result_dir,"ana_result.pkl")

        # here is the txt file containing all the info
        self._info = MouseInfo(mouse_info_path)

        self.mspkl_Path=glob.glob(os.path.join(self.cnmf_result_dir,'ms.pkl'))
        self.msmat_Path=glob.glob(os.path.join(self.cnmf_result_dir,'ms.mat'))
        self.hdf5_Path=glob.glob(os.path.join(self.cnmf_result_dir,'*/hdf5'))

        self.load_cnmf_result()
        self.load_ana_result()
        


    @property
    def info(self):
        return self._info

    @property
    def keys(self):
        return self.ana_result.keys()

    @property
    def save(self):
        return self.save_ana_result_pkl()

    def _load_hdf5(self):
        try:
            from caiman.source_extraction.cnmf.cnmf import load_CNMF
        except:
            print("please activate env caiman")
            sys.exit()
        print("loading hdf5Path...")
        self.cnm = load_CNMF(self.hdf5_Path[0])
        print("result.hdf5 is successfully loaded.")

    def _load_mat(self):
        '''
        this function should be called instead of direct spio.loadmat
        as it cures the problem of not properly recovering python dictionaries
        from mat files. It calls the function check keys to cure all entries
        which are still mat-objects
        '''
        data = spio.loadmat(self.msmat_Path[0], struct_as_record=False, squeeze_me=True)
        return self.__check_keys(data)

    def __check_keys(self,dict):
        '''
        checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        '''
        for key in dict:
            if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
                dict[key] = self.__todict(dict[key])
        return dict

    def __todict(self,matobj):
        '''
        A recursive function which constructs from matobjects nested dictionaries
        '''
        dict = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, spio.matlab.mio5_params.mat_struct):
                dict[strg] = self.__todict(elem)
            else:
                dict[strg] = elem
        return dict

    def _load_pkl(self):
        with open(self.mspkl_Path[0],'r') as f:
            return pickle.load(f)

    def load_cnmf_result(self):
        print("loading cnmf_result...")
        if self.mspkl_Path:
            self.cnmf_result = self._load_pkl()
        elif self.msmat_Path:
            self.cnmf_result = self._load_mat()
        elif self.hdf5_Path:
            self.cnmf_result = self._load_hdf5()
        else:
            print("cnmf_result generated by CNMF is inexistence.")
            sys.exit()
        print("loaded cnmf_result")
            
    def load_ana_result(self):
        if os.path.exists(self.ana_result_path):
            with open(self.ana_result_path,'rb') as f:
                self.ana_result =  pickle.load(f)
        else:
            self.ana_result = {}
        
    def __del__(self):
        pass

    def save_ana_result_pkl(self):
        with open(self.ana_result_path,'wb') as f:
            pickle.dump(self.ana_result,f)        
        print("ana_result is saved as %s."%self.ana_result_path)

    def save_ana_result_mat(self):
        pass



if __name__ == "__main__":
    mr = MiniResult(mouse_info_path=r"X:\QiuShou\mouse_info\191173_info.txt",
        cnmf_result_dir = r"X:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all")
    print(mr.keys)
