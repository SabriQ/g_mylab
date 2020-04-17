import numpy as np
import matplotlib.pyplot as plt
import os,sys,glob
import json
import scipy.io as spio
import pickle
class MiniResult():
	"""
	to generate file such as "191172_in_context.mat"
	This father class is to 
		1.load MiniResult through reading pkl,mat or hdf5 file 
		2.load/save mouseinfo
	"""
	def __init__(self,result_dir,mouse_info_path):
		self.result_dir = result_dir
		# here are all the possible format of result generesulted by CNMF
		self.hdf5_Path=glob.glob(os.path.join(self.result_dir),'*/hdf5')[0]
		self.ms_ts_Path=glob.glob(os.path.join(self.result_dir),'ms_ts.pkl')[0]
		self.msmat_Path=glob.glob(os.path.join(self.result_dir),'ms.mat')[0]
		self.mspkl_Path=glob.glob(os.path.join(self.result_dir),'ms.pkl')[0]
		# here is the txt file containing all the info
		self.mouse_info_path = mouse_info_path

		if os.path.exits(self.mouse_info_path):
			self.mouse_info = self._load_mouseinfo()

	def __del__(self):
		self._save_mouseinfo()

	def _load_mouseinfo(self):
		with open(self.mouse_info_path,'r') as f:
			return json.load(f)

	def _save_mouseinfo(self):		
		with open(self.mouse_info_path,'w') as f:
			f.write(json.dumps(self.mouse_info,indent=4))
		print("update %s" %os.path.basename(self.mouse_info_path))

			
	def _load_hdf5(self):
		try:
			from caiman.source_extraction.cnmf.cnmf import load_CNMF
		except:
			print("please activate env caiman")
			sys.exit()
		print("loading hdf5Path...")
		self.cnm = load_CNMF(self.hdf5_Path)
		print("result.hdf5 is successfully loaded.")

	def _load_mat(self):
	    '''
	    this function should be called instead of direct spio.loadmat
	    as it cures the problem of not properly recovering python dictionaries
	    from mat files. It calls the function check keys to cure all entries
	    which are still mat-objects
	    '''
	    data = spio.loadmat(self.msmat_Path, struct_as_record=False, squeeze_me=True)
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
		with open(self.mspkl_Path,'r') as f:
			return pickle.load(f)

	def load_result(self):

		if os.path.exists(self.mspkl_Path):
			self._load_pkl
		elif os.path.exists(self.msmat_Path):
			self._load_mat
		elif os.path.exists(self.hdf5_Path):
			self._load_hdf5()
		else:
			print("result generated by CNMF is inexistence.")
			sys.exit()




if __name__ == "__main__":
	mr = MiniResult(result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_20191028-1102all"
		,mouse_info_path)