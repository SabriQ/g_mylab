#!/usr/bin/env python
# coding: utf-8

# # <center>索引所要分析的数据并排序</center>

# In[2]:


import glob
import re
import os

def sort_key(s):
    """
    fit for video recorded by miniscope.exe
    sort fixed pattern: YYYYMMDD/H*M*S*/msCam*.avi
    """
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
    
def index_videos(animal_id,date = '20190930',recorded_method="miniscope",
                 rawdataDir = r'/run/user/1000/gvfs/smb-share:server=10.10.46.135,share=data_archive/qiushou/miniscope'):
    """
    index_videos: index miniscope videos recorded  by different recorded_method
    animal_id
    date: the day you did the experiment and also the name of the folder you save your raw data
    recorded_method: "miniscope" or "script". script is established by Qiushou. it will generate two files for each experiment.
                    formats are like these:
                        0_201034_20200703-191143.avi   0 means miniscope camera
                        0_201034_20200703-191143.txt   miniscppe camera timestamps
                        1_201034_20200703-191143.avi   1 means behavoiral camera
                        0_201034_20200703-191143.txt   behavoiral camera timestamps
    rawdataDir: the folder you save your rawdata, usually fixed.
    """
    if recorded_method=="miniscope":
        msFileList = glob.glob(os.path.join(rawdataDir,date,animal_id,"H*/msCam*.avi"))
        tsFileList = glob.glob(os.path.join(rawdataDir,date,animal_id,"H*/timestamp.dat"))
        msFileList.sort(key=sort_key)
        tsFileList.sort(key=sort_key)
        
    elif recorded_method=="script":
        msFileList = glob.glob(os.path.join(rawdataDir,str(date),"0_"+str(animal_id)+"*.avi"))
        tsFileList = glob.glob(os.path.join(rawdataDir,str(date),"0_"+str(animal_id)+"*.txt"))
    else:
        print("wrong recorded_method")
        return 0
    
    
    return msFileList, tsFileList


def index_videos_wjn(animal_id,date = '20190930',recorded_method="miniscope",
                 rawdataDir = r'/run/user/1000/gvfs/smb-share:server=10.10.46.135,share=data_archive/qiushou/miniscope'):
    """
    index_videos: index miniscope videos recorded  by different recorded_method
    animal_id
    date: the day you did the experiment and also the name of the folder you save your raw data
    recorded_method: "miniscope" or "script". script is established by Qiushou. it will generate two files for each experiment.
                    formats are like these:
                        0_201034_20200703-191143.avi   0 means miniscope camera
                        0_201034_20200703-191143.txt   miniscppe camera timestamps
                        1_201034_20200703-191143.avi   1 means behavoiral camera
                        0_201034_20200703-191143.txt   behavoiral camera timestamps
    rawdataDir: the folder you save your rawdata, usually fixed.
    """
    if recorded_method=="miniscope":
        msFileList = glob.glob(os.path.join(rawdataDir,animal_id,date,"H*/msCam*.avi"))
        tsFileList = glob.glob(os.path.join(rawdataDir,animal_id,date,"H*/timestamp.dat"))
        msFileList.sort(key=sort_key)
        tsFileList.sort(key=sort_key)
        
    elif recorded_method=="script":
        msFileList = glob.glob(os.path.join(rawdataDir,str(date),"0_"+str(animal_id)+"*.avi"))
        tsFileList = glob.glob(os.path.join(rawdataDir,str(date),"0_"+str(animal_id)+"*.txt"))
    else:
        print("wrong recorded_method")
        return 0
    
    
    return msFileList, tsFileList

import moviepy.video as mpv
from moviepy.editor import *
import matplotlib as mpl
import cv2
import pickle
import datetime
import numpy as np
import pandas as pd
import pickle
from scipy.io import savemat


def datetime2minisceconds(x,start):    
    delta_time = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')-start
    return int(delta_time.seconds*1000+delta_time.microseconds/1000)
    
def read_timestamp(tsFile):
    data = pd.read_csv(tsFile,sep=",")
    start = datetime.datetime.strptime(data["0"][0], '%Y-%m-%d %H:%M:%S.%f')
    data["0"]=data["0"].apply(datetime2minisceconds,args=[start,])
    return data["0"]

def coordnates2crop_datavideo(video,cropfilename):
    
    """
    generate the coordinates of ROI. return x1,x2,y1,y2
    """    
    clip = VideoFileClip(video) #
    im=clip.get_frame(1)

    if not os.path.exists(cropfilename):
        r=cv2.selectROI(im,fromCenter=False) # r = (x,y,w,h)
        cv2.destroyAllWindows()
        x1=int(r[0])
        x2=int(r[0]+r[2])
        y1=int(r[1])
        y2=int(r[1]+r[3])
        crop_coord=[x1,x2,y1,y2]
        print(crop_coord)
        
        with open(cropfilename,'wb') as output:
            pickle.dump(crop_coord,output)
    else:
        with open(cropfilename, "rb") as f:
            crop_coord= pickle.load(f) 
    #     print(r)
        x1=crop_coord[0]
        x2=crop_coord[1]
        y1=crop_coord[2]
        y2=crop_coord[3]
    return x1,x2,y1,y2

def crop_downsample_concatenate(animal_id
                                ,msFileList
                                ,tsFileList
                                ,note
                                ,resultDir = r'/home/qiushou/Documents/QS_data/miniscope/miniscope_result'
                               ,spatial_downsampling=2
                               ,temporal_downsampling=1
                               ,video_process = True
                               ,camNum=0):
    """
    
    """
    Result_animalid_folderpath=os.path.join(resultDir,'Results'+'_'+animal_id)
    if not os.path.exists(Result_animalid_folderpath):
        os.makedirs(Result_animalid_folderpath)        

    
    Realtime_folderpath=os.path.join(Result_animalid_folderpath,datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+str(note))
    if not os.path.exists(Realtime_folderpath):
        os.makedirs(Realtime_folderpath)
    
    videoconcat=os.path.join(Realtime_folderpath,'msCam_concat.avi')
    ms_ts_name = os.path.join(Realtime_folderpath,'ms_ts.pkl')
    ms_ts_mat_name = os.path.join(Realtime_folderpath,'ms_ts.mat')

    if video_process:
        cropfilename=os.path.join(Result_animalid_folderpath,'crop_param.pkl')
        print(cropfilename)
        x1,x2,y1,y2 =coordnates2crop_datavideo(msFileList[0],cropfilename=cropfilename)

        cropped_clip_list=[]
        iframe=0
        for video in msFileList:
            print('Concatenating '+video)
            clip = VideoFileClip(video)
            cropped_clip=mpv.fx.all.crop(clip,x1=x1,y1=y1,x2=x2,y2=y2)
            
            if spatial_downsampling!=1:
                cropped_clip=cropped_clip.resize(1/spatial_downsampling)
            cropped_clip_list.append(cropped_clip)
            
        final_clip=concatenate_videoclips(cropped_clip_list)

        if temporal_downsampling>1:
            final_clip=mpv.fx.all.speedx(final_clip, factor=temporal_downsampling)
            

        final_clip.write_videofile(videoconcat,codec='rawvideo',audio=False,threads=8)
    ##    final_clip.write_videofile(videoconcat,codec='png',audio=False,threads=8)
    #     final_clip.write_videofile(videoconcat,codec='mpeg4',audio=False,threads=8)

#     help(final_clip.write_videofile)

    if not os.path.exists(ms_ts_name):
        print(ms_ts_name)
        ts_session=[]
        for tsFile in tsFileList:
            if "timestamp.dat" in tsFile: # 如果是miniscope原版软件录制
                datatemp=pd.read_csv(tsFile,sep = "\t", header = 0)
                datatemp = datatemp[datatemp["camNum"]==camNum] ## wjn的 case 是1， 其他的scope是0
                print("camNum in miniscope is %s"%camNum)
                # incase the first frame of timestamps is not common 比如这里会有一些case的第一帧会出现很大的正/负数
                if np.abs(datatemp['sysClock'][0])>datatemp['sysClock'][1]:
                    value = datatemp['sysClock'][1]-13 # 用第2帧的时间减去13，13是大约的一个值
                    if value < 0:
                        datatemp['sysClock'][0]=0
                    else:
                        datatemp['sysClock'][0]=value

                ts = datatemp['sysClock'].values
            elif "txt" in tsFile: # 如果是脚本录制
                ts = read_timestamp(tsFile)
                print(ts)
            else:
                print("no timestamp file found!")
                sys.exit()
                
            ts_session.append(ts)   

        ttemp=np.hstack(ts_session)[::temporal_downsampling]
        session_indend=(np.where(np.diff(ttemp)<0)[0]).tolist()
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
        
        with open(ms_ts_name,'wb') as output:
            pickle.dump(ms_ts,output,pickle.HIGHEST_PROTOCOL)
            
        savemat(ms_ts_mat_name,{'ms_ts':ms_ts})
    else:
        with open(ms_ts_name, "rb") as f:
            ms_ts= pickle.load(f)

    timestamps_frames = sum([len(i) for i in ms_ts])
    cap = cv2.VideoCapture(videoconcat)
    concated_video_frames = int(cap.get(7))
    cap.release()
    if timestamps_frames == concated_video_frames:
        print("concatenated video and timestamps have the same frames")
    else:
        print(f"Attention: concatenated video {concated_video_frames}frames and timestamps {timestamps_frames}frames have different frames")
    print(f'concatenated timestamp of miniscope_video is located at {ms_ts_name}')



# In[163]:

if __name__ == "__main__":
    animal_id = "206550"
    msFileList,tsFileList = index_videos(animal_id=animal_id,date="7_15_2020",recorded_method="miniscope",rawdataDir=r"E:\Miniscope\data")
    crop_downsample_concatenate(animal_id=animal_id,msFileList=msFileList,tsFileList=tsFileList,note="_20200714",resultDir=r'D:\miniscope_results')

