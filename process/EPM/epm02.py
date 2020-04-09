# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 14:57:04 2019

@author: Sabri
"""

from mylab.Cvideo import Video
import pandas as pd
import os
import csv
import glob
import matplotlib.pyplot as plt
import numpy as np
import cv2
from mylab.info import *
'''
第一部分：
切割视频：
输入数据：MP4
模式：手动调整视频的帧，通过按键确定几个帧位置
输出：frame_Nos 文件 
'''
'''
第二部分
输入数据： MP4,h5,txt,frame_Nos
不确定的输入： 视频分成几段，最少输入几个点（时间点还是帧数）,这几个点是批量确定，还是临时确定
输出：按几段输出几个distance in pixel(with or withoud scale)
'''

#闭包，首先固定一个写入文件，然后再将不同的信息写入进去
def find_close_fast(arr,e):
    np.add(arr,e*(-1))
    min_value = min(np.abs(np.add(arr,e*-1)))
    locations = np.where(np.abs(np.add(arr,e*-1))==min_value)
    return locations[0][0]
def rlc(x):
    name=[]
    length=[]
    for i,c in enumerate(x,0):
        if i ==0:
            name.append(x[0])
            count=1
        elif i>0 and x[i] == name[-1]:
            count += 1
        elif i>0 and x[i] != name[-1]:
            name.append(x[i])
            length.append(count)
            count = 1
    length.append(count)
    return name,length

def video_segment(filename = r"C:\Users\Sabri\Desktop\program\data\video\epm\video_segmentations.csv"):  
    if not os.path.exists(filename):
        f = open(filename,'a',newline="")
        writer = csv.writer(f)
        writer.writerow(["video_name","breakpoint1","breakpoint2"])
        f.close()        
    f= open(filename,'a+',newline="")
    writer = csv.writer(f)
    def write_rows(video_path,*args):
        marked_frames = Video(video_path).check_frames_trackbar(*args)
        if marked_frames:
            marked_frames.insert(0,video_path)
            print(marked_frames)
            writer.writerow(marked_frames)
        else:
            print("no marked frames")
        f.close()
    return write_rows

def epm_result(video_segmentation_filename=r"C:\Users\Sabri\Desktop\program\data\video\epm\video_segmentations.csv",
               result_dir = r"C:\Users\Sabri\Desktop\program\data\video\epm",               
               temporal_downsample=7):
    result_file  = os.path.join(result_dir,'result.csv')
    video_segmentations = pd.read_csv(video_segmentation_filename)
    
    if not os.path.exists(result_file):
        f = open(result_file,'w',newline="")
        writer = csv.writer(f)
        writer.writerow(["analyze_time",current_timepoint()])
        writer.writerow(["temporal_downsample:",temporal_downsample])
        writer.writerow(["video_name","segmentation","zone_1","zone_2","zone_3","zone_4",
                         "wrong_track","largest wrong consecutive track number"])
        f.close()        
        
    def epm_calculate(video=r'C:\Users\Sabri\Desktop\program\data\video\epm\192093-20190807-102117.mp4',):
        specific_id = os.path.splitext(os.path.basename(video))[0]
        result_fig = os.path.join(result_dir,specific_id+'.png')
        breakpoints=[row[1][1:].tolist() for row in video_segmentations.iterrows() if specific_id in row[1]['video_name']][0]
        print(breakpoints)
        
        dirname = os.path.dirname(video)
        video_track = glob.glob(os.path.join(dirname,'*'+specific_id+'DeepCut*'+'.mp4'))[0]
        h5 = glob.glob(os.path.join(dirname,'*'+specific_id+'*'+'.h5'))[0]
        ts = glob.glob(os.path.join(dirname,'*'+specific_id+'*'+'.txt'))[0]        
        masks_wholezone,coords_whole_zone = Video(video_track).draw_rois(aim="epm_wholezone",count = 1)
        masks,coords = Video(video_track).draw_rois(aim="epm",count = 4)
        #plot whole_zone,zone_1,zone_2,zone_3
        plt.figure(figsize=(10,12))
        plt.subplot2grid((3,2),(0,0))
        plt.title("whole_zone")
        plt.xticks([])
        plt.yticks([])
        plt.imshow(masks_wholezone[0])
        plt.subplot2grid((3,2),(0,1))
        plt.imshow(masks[0])
        plt.title("zone_1")
        plt.xticks([])
        plt.yticks([])
        plt.subplot2grid((3,2),(1,0))
        plt.imshow(masks[1])
        plt.title("zone_2")
        plt.xticks([])
        plt.yticks([])
        plt.subplot2grid((3,2),(1,1))
        plt.imshow(masks[2])
        plt.title("zone_3")
        plt.xticks([])
        plt.yticks([])
        plt.subplot2grid((3,2),(2,0))
        plt.imshow(masks[3])
        plt.title("zone_4")
        plt.xticks([])
        plt.yticks([])    
        
        zones=[]
        for i in range(len(masks)):
            zones.append([])        
             
        f = pd.read_hdf(h5)
        training_set = f.columns[0][0]
        X =f[training_set].Body['x'][::temporal_downsample].reset_index()
        Y =f[training_set].Body['y'][::temporal_downsample].reset_index()
        L = f[training_set].Body['likelihood'][::temporal_downsample].reset_index()
        T = pd.read_csv(ts,sep='\n',encoding='utf-16',header=None)[0][::temporal_downsample].reset_index()
        
        corrected_X=X['x'].tolist()
        corrected_Y=Y['y'].tolist()
        
        break_indexes = [find_close_fast(T['index'],i) for i in breakpoints]
        start_time = T.iloc[break_indexes[0]][0]-180#往前3min
        end_time = T.iloc[break_indexes[1]][0]+180#往后3min
        break_indexes.insert(0,find_close_fast(T[0],start_time))
        break_indexes.append(find_close_fast(T[0],end_time))
#        print(break_indexes)
#        print([T.loc[i][0] for i in break_indexes])
#        print(T)
        
        frame_No = 0
        outs=[]
        for x,y in zip(corrected_X,corrected_Y):
            #如果这个点出现在所有区域的外面，则认为可能是track错误，并仍然重复上一帧对zones[i]的判断
            if 0 not in masks_wholezone[0][int(y),int(x)]:                
                outs.append(frame_No)
                if frame_No != 0 :# 用前一个在whole_zone中的点来代替这个不在whole_zone的点来进行简单的矫正
                    x=corrected_X[frame_No-1]
                    y=corrected_Y[frame_No-1]
                    corrected_X[frame_No]=corrected_X[frame_No-1]
                    corrected_Y[frame_No]=corrected_Y[frame_No-1]    
            #判断在哪一个zone[i],则zone[i].append(1),else zone[i].append(0)
            frame_No = frame_No + 1
            for i,mask in enumerate(masks,0):
                #print(mask[int(y),int(x)])
                if 0 in mask[int(y),int(x)]:
                    zones[i].append(1)                    
                else:
                    zones[i].append(0)          
            
        print(f"In total,there are {len(outs)}/{len(X)} frames out of the whole zone")
        name,length = rlc(np.diff(outs))
        print(f"At most, there are {max(length)} frames consecutively wrong" )
        if max(length)>20:
            print("Optimizing your track is recommended!")     
        #plot real view for specific video in case of unexpected shift of setup
        cap = cv2.VideoCapture(video_track)
        cap.set(cv2.CAP_PROP_POS_FRAMES,1000)
        ret,frame = cap.read()   
        plt.subplot2grid((3,2),(2,1))
        ax = plt.gca()
        ax.imshow(frame)
        ax.xaxis.set_ticks([])
        ax.yaxis.set_ticks([])
        ax.set_title("all points")
        ax.scatter(X['x'][(pd.Series(zones[0])==1).tolist()],Y['y'][(pd.Series(zones[0])==1).tolist()],c='red',s=1)
        ax.scatter(X['x'][(pd.Series(zones[1])==1).tolist()],Y['y'][(pd.Series(zones[1])==1).tolist()],c='green',s=1)
        ax.scatter(X['x'][(pd.Series(zones[2])==1).tolist()],Y['y'][(pd.Series(zones[2])==1).tolist()],c='blue',s=1)
        ax.scatter(X['x'][(pd.Series(zones[3])==1).tolist()],Y['y'][(pd.Series(zones[3])==1).tolist()],c='orange',s=1)
        #查看不在规定区域内的点，用黑色表示
        other_zone =(pd.Series(zones[0])==0)&(pd.Series(zones[1])==0)&(pd.Series(zones[2])==0)&(pd.Series(zones[3])==0)
        out_index = X['x'][other_zone.tolist()].index
    #        print(out_index)
        ax.scatter(X['x'][other_zone.tolist()],Y['y'][other_zone.tolist()],c='black',s=1)
#        ax.scatter(corrected_X,corrected_Y,c='g',s=1)
#        ax.title(label=specific_id )
        plt.show()
        plt.savefig(result_fig,dpi=80)
    #        Video(video_t`rack).check_frames()
    
        
    return epm_calculate
        
        
        

# distance in cm; total time in seconds


if __name__ == "__main__":
    epm_calculate = epm_result()
    epm_calculate(r"C:\Users\Sabri\Desktop\program\data\video\epm\192093-20190807-102117.mp4")
#    test = video_segment()
#    test(r"C:\Users\Sabri\Desktop\program\data\video\epm\192093-20190807-102117.mp4")