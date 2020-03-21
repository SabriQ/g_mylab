import glob,re,os,sys,pickle
import numpy as np
import pandas as pd
import cv2
def msCam_sort_key(s):     
    if s:            
        try:         
            date = re.findall('\d{8}', s)[0]
        except:      
            date = -1            
        try:         
            H = re.findall('H(\d+)',s)[0]
        except:      
            H = -1            
        try:         
            M = re.findall('M(\d+)',s)[0]
        except:      
            M = -1            
        try:         
            S = re.findall('S(\d+)',s)[0]
        except:      
            S = -1            
        try:         
            ms = re.findall('msCam(\d+)',s)[0]
        except:      
            ms = -1  
        return [int(date),int(H),int(M),int(S),int(ms)]

def make_ms_ts(tsFileList,temporal_downsampling=1,is_save=True,savePath=r"C:\Users\admin\Desktop\ms_ts.pkl"):
	"""for make a file concatenating all the timestamps of miniscope file
	tsFileList: a sorted list of timestamp.dat
	temporal_downsampling=1
	savePath: an absolute path of pkl file to save ms_ts
	save: boolen, whether to save ms_ts in savePath
	"""
	if not os.path.exists(savePath):
	    ts_session=[]
	    for tsFile in tsFileList:
	        datatemp=pd.read_csv(tsFile,sep = "\t", header = 0)
	        ts_session.append(datatemp['sysClock'].values)    
	    ttemp=np.hstack(ts_session)[::temporal_downsampling]
	    # remporally downsample for each video
	    # [i[::3] for i in ts_session][0]
	    session_indend=(np.where(np.diff(ttemp)<0)[0]).tolist()
	#    session_indend.append(-1)
	    ts_session_ds=[]
	    i0=0
	    session_indstart=[]
	    if len(session_indend)>0:
	        for i in range(len(session_indend)):
	            session_indstart.append(i0)
	            ts_session_ds.append(ttemp[i0:(session_indend[i]+1)])
	            i0=session_indend[i]+1
	        ts_session_ds.append(ttemp[(session_indend[-1]+1):])
	    else:
	        ts_session_ds.append(ttemp[i0:])
	    
	    ms_ts=np.array(ts_session_ds)   

	    if is_save:
		    with open(savePath,'wb') as output:
		        pickle.dump(ms_ts,output,pickle.HIGHEST_PROTOCOL)
		    print(f"ms_ts is saved at {savePath}")
	    else:print("generate ms_ts: ");print(ms_ts)

	else:
	    with open(savePath, "rb") as f:
	        ms_ts= pickle.load(f)
	    print("loading ms_ts")
		
	return ms_ts

def check_ts_video_frame(tsFileList):
	print("it will take tens of minutes!")
	for tsFile in tsFileList:
		print(tsFile)
		print(">",end="")
		ts = pd.read_csv(tsFile,sep="\t",header=0)
		ts_len=ts.shape[0]# the last raw could be uncomplete
		videoFileList=glob.glob(os.path.dirname(tsFile)+'\*.avi')   
		framenum=[]
		for video in videoFileList:
			print("<",end="")
			cap = cv2.VideoCapture(video)
			framenum.append(int(cap.get(7)))
			cap.release()
		print(f" [timestamp_len: {ts_len};videoframe_len: {sum(framenum)}]")

if __name__=="__main__":

	animal_id='191172'
	tsFileList=glob.glob(os.path.join(r'W:\qiushou\miniscope\2019*',animal_id,r'H*\timestamp.dat'))
	tsFileList.sort(key=msCam_sort_key)
	#print(tsFileList)
	if len(tsFileList) ==0:
		print("there is no timestamp.dat selected")
	else:
		[print(i) for i in tsFileList]
		make_ms_ts(tsFileList,temporal_downsampling=1,is_save=False)
		check_ts_video_frame(tsFileList)
 		
