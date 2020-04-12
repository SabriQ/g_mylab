import numpy as np


import matplotlib.pyplot as plt

class ResultHdf5():
	def __init__(self,hdf5Path):
		try:
			from caiman.source_extraction.cnmf.cnmf import load_CNMF
		except:
			print("please activate env caiman")
			sys.exit()
		print("loading hdf5Path...")
		self.cnm = load_CNMF(hdf5Path)
		print("successfully loaded")

	def keys():
		return self.cnm.keys()
	def save_mat():
		pass
	def plot_SFP():
		pass
	def plot_demo_traces():
		pass
def plot_demo(filepath):
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