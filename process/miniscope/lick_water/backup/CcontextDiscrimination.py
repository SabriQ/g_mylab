from Canimal import Mouse
from mylab.miniscope.utils.TimeStamps import msCam_sort_key,make_ms_ts,check_ts_video_frame
import glob
class ContextDiscrimination(Mouse):
	def __init__(self,mouse_id,owner="qs",gender="M",enter_date="20200000"
		,enter_age="56d",gene_type="C57",experiments=list()
		,dictkey="ContextDiscrimination"
		,params={
		#fixed info
			"experimentor":"qs"
			,"record_method":"miniscope_chs"
		#exps info
			,"data_dir":r"W:\qiushou\miniscope"
		#pre_processing info, mannuly input
			,"ms_starts":[]
			,"context_orders":[]
			,"context_angles":[]
		#pre_processing by caiman, ffmpeg,
			,"CNMF_result_dir":r"G:\data\miniscope"
		#pre_processing output:
			,"in_context_result_dir":r"G:\data\miniscope\LinearTrackAll"}		
		):		

		# self._mouse_id = mouse_id
		# self._owner = owner
		# self._gender = gender 
		# self._enter_date=enter_date
		# self._enter_age = enter_age
		# self._gene_type=gene_type
		# self._experiments=experiments
		# self._dictkey = dictkey
		# self._params = params


		# super(ContextDiscrimination,self).__init__(mouse_id=self._mouse_id
		# 	,owner=self._owner,gender=self._gender,enter_date=self._enter_date
		# 	,enter_age=self._enter_age,gene_type=self._gene_type,experiments=self._experiments
		# 	,dictkey=self._dictkey,params=self._params)
		super().__init__(mouse_id)

	def ms_ts(self,):
		pass
	def check_ts_video_frame(self,):
		pass
	def be_ts(self,):
		pass
	def concatenate_msCams(self):
		pass
	def Motioncorrection_Sourceextraction(self):
		pass	
if __name__ == "__main__":
	m1 = ContextDiscrimination(191173)
	print("-----1-----")
	print(m1.info)
	print("-----2-----")
	m1["test"]="test"
	print("-----3----")
	print(m1.info)
	print("-----4----")
	del m1["test"]
	print("-----5----")