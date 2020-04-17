# miniscope 分析流程
#class MiniResult
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

