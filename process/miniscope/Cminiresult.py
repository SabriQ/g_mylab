import numpy as np
import matplotlib.pyplot as plt
import os
class MiniResult():
	def __init__(self,result_dir,mouse_info):

		self.hdf5Path=
		self.ms_tsPath=
		self.result_matpath=
		self.result_pklpath=
		self.mouse_info=

	def keys():
		return self.cnm.keys()
	def save_mat():
		pass
	def plot_SFP():
		pass
	def load_mouseinfo(self):
		pass
	def load_hdf5(self):
		try:
			from caiman.source_extraction.cnmf.cnmf import load_CNMF
		except:
			print("please activate env caiman")
			sys.exit()
		print("loading hdf5Path...")
		self.cnm = load_CNMF(hdf5Path)
		print("successfully loaded")
	def load_msts(self):
		# attention to check whether frames of ms_ts are equal to that of traces
		pass

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