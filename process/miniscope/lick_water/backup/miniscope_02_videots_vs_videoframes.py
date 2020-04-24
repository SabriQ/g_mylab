# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 13:32:00 2020

@author: admin
"""

import glob          
import re            
import os
import numpy as np
import pandas as pd
import pickle   
import cv2          
from mylab.miniscope.Mplot import *
#%%
animal_id = "191126"
tsFileList = glob.glob(os.path.join(r'W:\qiushou\miniscope\2019*',animal_id,"H*/timestamp.dat"))   
def sort_key(s):     
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
    
tsFileList.sort(key=sort_key)
msCamFileList.sort(key=sort_key)
ts_lens = []
framenums = []
for tsFile in tsFileList:
    print(tsFile)
    print(">",end="")
    ts = pd.read_csv(tsFile,sep = "\t", header = 0)
    ts_len=ts.shape[0]        
    videoFileList=glob.glob(os.path.dirname(tsFile)+'\msCam*.avi')   
    framenum=[]
    for video in videoFileList:
#         print(video)
        print("<",end="")
        cap = cv2.VideoCapture(video)
        framenum.append(int(cap.get(7)))
        cap.release()
    print([ts_len,sum(framenum)])
    ts_lens.append(ts_len)
    framenums.append(sum(framenum))
print(sum(ts_lens),sum(framenums))
#%%

