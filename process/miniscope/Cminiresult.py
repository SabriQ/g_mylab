import numpy as np
import matplotlib.pyplot as plt
import os,sys
import json
class MiniResult():
	def __init__(self,result_dir,mouse_info_path):

		self.hdf5Path=
		self.ms_tsPath=
		self.result_matpath=
		self.result_pklpath=
		self.mouse_info_path = mouse_info_path
		f = open(self.mouse_info_path, encoding='utf-8')
		self.mouse_info=json.load(f)


	def save_mouseinfo(self):
		with open(self.mouse_info_path,'a') as f:
			json.dump(self.mouse_info,f)
			print("update %s" %os.base.name(self.mouse_info_path))
			
	def load_hdf5(self):
		try:
			from caiman.source_extraction.cnmf.cnmf import load_CNMF
		except:
			print("please activate env caiman")
			sys.exit()
		print("loading hdf5Path...")
		self.cnm = load_CNMF(hdf5Path)
		print("successfully loaded")

	def load_result(self):
		if os.path.exists(self.result_pklpath):
			pass
		else:
			self.load_hdf5


	def savepkl(self):
		pass
	def savemat(self):
		pass

	def plot_demo(self,self.filepath):
		print("loading results...")
		cnm = load_CNMF(filepath,n_processes=4,dview=dview)
		print("successful loading")
		DeconvTraces = cnm.estimates.S
		RawTraces = cnm.estimates.C
		SFP = cnm.estimates.A 
		print(cnm.dims)
		plt.figure()
		plt.imshow(np.reshape(SFP[:,4].toarray(),cnm.dims,order="F"))




if __name__ == "__main__":
	filepath = r"G:\data\miniscope\Results_191172\20191218_111624_20191028-1102all_30fps\result.hdf5"
	plot_demo(filepath)