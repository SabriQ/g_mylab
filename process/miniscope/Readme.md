# miniscope 分析流程
# class MiniResult
	整合由CNMF产生的数据，产生info_mouse_id.txt
## info
	new info
		ms_starts
## load ms.mat from CAIMAN
	hdf5

## output result


# class MiniLTResult
## check whether frames of ms_ts are equal to that of traces
	ms_ts
## construct list blocks each block of which has a DataFrame containing all the traces and ms_ts
	result["msblocks"]
##  output behaveblocks, logblocks,blocknames read track coordinates as lists of dataframe
	result["behaveblocks"]
	result["logblocks"]
	result["blocknames"]
## align timepoint of ms_ts & track/ts,log & track/ts, all are aligned to time of ms_ts
	result['video_scale']
	result["aligned_behaveblocks"]
## crop video get the interested areas
	result["contextcoords"]
## add aligned_behaveblock['Track']    
	result["aligned_behaveblocks"] 
		aligned_behaveblock['in_track']
## for each block(context),calculate the averate trace value of each neuron
	result["in_track_behavetrialblocks"]
	result["in_track_msblocks"]


result.hdf5
	ms.mat
		post_processed.mat
			in_context_191172.py
			in_context_191172.mat
			in_track_191172.py
			in_track_191172.mat

result
	blocknames 每一个单独的文件名一个blockname

	msblocks 每一个单独的视频一个block
	behaveblocks 每一个单独个视频一个behave block
	logblocks 每一个单独的logfile一个logblock

	aligned_behaveblocks, 每一天的行为学数据和miniscope数据对其之之后，合并一个aligned_behaveblock,
	contextcoords 每天的视频一个坐标，每天可能有多个
	video_scale
