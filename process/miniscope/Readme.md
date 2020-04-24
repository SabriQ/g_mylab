# miniscope 分析流程
lick_water
	分为behave_data和cnmf_data
	class Mini_CNMF_data()
		def __init__()
		def load_hdf5
			self.cnm
				self.cnm.estimates
		def load_mat
		def load_pkl
		def make_ms_ts
		def check_ts_msframe
	class Mini_Behave_data()
		def __init__()
		def behave_info()
# class MiniResult
	`Args: mouse_info_path,cnmf_result_dir`
	最初的想法是实验对ana_result.pkl实现插入式的修改，不需要每次都要重新跑一遍脚本文件
	整合由CNMF产生的数据、mouse_info的实验信息，在同文件夹下生成ana_result.pkl的文件
		#### __init__
		#### @property info
		#### @property keys
		#### _load_hdf5
		#### _load_mat
		#### __check_keys()
		#### __check_keys()
		#### __todict()
		#### _load_pkl
		#### load_cnmf_result
		#### load_ana_result
		#### __del__
		#### save_ana_result_pkl
		#### save_ana_result_mat

### contents of `ana_result`
	blocknames 每一个单独的文件名一个blockname

	msblocks 每一个单独的视频一个block
	behaveblocks 每一个单独个视频一个behave block
	logblocks 每一个单独的logfile一个logblock

	aligned_behaveblocks, 每一天的行为学数据和miniscope数据对其之之后，合并一个aligned_behaveblock,
	contextcoords 每天的视频一个坐标，每天可能有多个
	video_scale

lick water
# class MiniLWResult
	`Args: mouse_info_path,cnmf_result_dir,behave_dir`
	继承class MiniResult，针对"lick_water"这部分实验,增加behavedir,索引得到所有的行为学信息，增加至mouse_info中
		#### __init__
		#### @property expinfo
		#### @property expkeys
		#### __add_behave_info()
		#### __add_video_scale()
		#### __check_behave_info()
		#### _equal_frames()
		#### load_msts()
		#### sigraw2msblocks()
		#### dlctrack2behaveblocks()
		#### _speed()
		#### align_msblocks_behaveblocks()
		#### select_in_context()
		#### extract_trials_in_context()
		#### TrackinZoneView()
		#### select_in_track()
		#### run()


### structure of `result_dir`
`
	result.hdf5
	ms.mat
		post_processed.mat
			in_context_191172.py
			in_context_191172.mat
			in_track_191172.py
			in_track_191172.mat
`


