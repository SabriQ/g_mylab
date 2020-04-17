from mylab.process.miniscope.Cminiresult import MiniResult as MR

class MiniLTResult(MR):
	def __init__(self,result_dir,mouse_info):
		super().__init__(result_dir,mouse_info)
		self.stage = "lick_water"

	def load_msts(self):
		# attention to check whether frames of ms_ts are equal to that of traces
		pass
	def msblocks(self):
		pass
	def crop_video(self):
		pass
	def scale_video(self):
		pass

	def msblocks(self):
		pass
	def behaveblocks(self):
		pass
	def aligned_behaveblocks(self):
		pass