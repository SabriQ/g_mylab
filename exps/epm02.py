# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 14:57:04 2019

@author: Sabri
"""

from mylab.Cvideo import Video
import pandas as pd
import os
import csv

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


def video_segment(filename = r"C:\Users\Sabri\Desktop\program\data\video\epm\video_segmentations.csv"):  
    def write_rows(video_path,*args):
        if not os.path.exists(filename):
            f = open(filename,'a',newline="")
            writer = csv.writer(f)
            writer.writerow(["video_name","breakpoint1","breakpoint2"])
            f.close()        
        f= open(filename,'a+',newline="")
        writer = csv.writer(f)
        marked_frames = Video(video_path).check_frames_trackbar(*args)
        if marked_frames:
            marked_frames.insert(0,video_path)
            print(marked_frames)
            writer.writerow(marked_frames)
        else:
            print("no marked frames")
        f.close()
    return write_rows

def epm_result(filename,videolists):
    video_segmentations = pd.read_csv(filename)
    for video in videolists:
        pass



# understanding of closure
def func1(a1,a2,a3,a4):
    def func2(b):
        return a1*b+a2**b+(a3-b)+a4/b
    return func2
#under condition of series of a, we manipunate b

## understanding of callback
def Func1(a1,a2,func2):
    func2(a1,a2)
# excute func2 during excuting func1 when reaching condition
if __name__ == "__main__":
    test = video_segment()
    test(r"C:\Users\Sabri\Desktop\program\data\video\epm\192093-20190807-102117.mp4")