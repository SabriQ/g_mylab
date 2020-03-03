# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:30:51 2019

@author: Sabri
"""

from mylab.Cvideo import Video
import glob,os
video = glob.glob(r"W:\qiushou\miniscope\*\191174\191174A1-20191102-153327.mp4")
print(video)
#%%
Video(video[0]).check_frames_trackbar()
#%%