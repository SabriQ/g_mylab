from mylab.Cvideo import Video
import os,sys,glob
import cv2
import pandas as pd
import numpy as pd

class EPMvideo(Video):
	def __init__(self,video_path):
		super().__init__(video_path)
		self.videoAreaStay_path = self.abs_prefix + '_areas.csv'

	def __video2csv(self,Interval_number=1,show = True):
		masks = self.draw_rois(aim="epm",count=5)[0]


if __name__=="__main__":
	EPMvideo(r"G:\data\video\epm\192093-20190807-102117.mp4").draw_rois()