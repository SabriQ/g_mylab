from mylab.Cvideo import Video
import os,sys,glob
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mylab.Cdecs import *
import csv
class OFvideo(Video):
	def __init__(self,video_path):	
		super().__init__(video_path)

	def show_masks(self,show = True):
		masks = self.draw_rois(aim="epm",count=5)[0]
		for mask in masks:
			plt.imshow(mask)
			plt.show()

	@staticmethod
	def find_close_fast(arr,e):
		min_value = min(np.abs(np.add(arr,e*-1)))
		locations = np.where(np.abs(np.add(arr,e*-1))==min_value)
		# print(locations[0][0])
		return locations[0][0]

	@staticmethod
	def distance(X,Y,T,s):
	    distance=[0]
	    for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
	        distances.append(np.sqrt(delta_x**2+delta_y**2))	        
	    return pd.Series(distances) # in cm/s




	@timeit
	def oftimer(self,start=None,stop=None,start_index=None,stop_index=None,Interval_number=1,according="Body"):
		"""
		Args:
			start. start time in seconds
			stop. stop time in seconds
			start_index. start frame in frame Number
			stop_index. stop frame in frame Number
			according="Body". string in "Head" and "Body"
		"""
		# read self.videots_path
		print(self.video_path)
		if not os.path.exists(self.videots_path):
		    try:
		        print("generating timestamps by ffmpeg")
		        self.generate_ts_txt()
		    except:
		        print("fail to generate timestamps by ffprobe")
		        sys.exit()
		else:
			ts = pd.read_table(self.videots_path,sep='\n',header=None,encoding="utf-16")
		# read self.video_track_path
		if not os.path.exists(self.video_track_path):
		    print("you haven't done deeplabcut tracking")
		    sys.exit()
		else:
		    track = pd.read_hdf(self.video_track_path)

		# extract coordinates of Head and Body
		try:
			behaveblock=pd.DataFrame(track[track.columns[0:9]].values,columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
			print("get track of head, body and tail")
		except:
			behaveblock=pd.DataFrame(track[track.columns[0:6]].values,columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh'])
			print("get track of head and body")
		# extract timestamps of each frame
		behaveblock['be_ts'] = ts[0]

		behaveblock=behaveblock[0::Interval_number].reset_index(drop=True)

		if start_index==None:
			start_index = self.find_close_fast(behaveblock['be_ts'],start)
		else:
			start_index = start_index

		if stop_index==None:
			stop_index = self.find_close_fast(behaveblock['be_ts'],stop)
		else:
			stop_index = stop_index

		if start_index>stop_index:
			start_index,stop_index =stop_index,start_index
			print("corrention: start:%ds,stop: %ds"%(start_index,stop_index))

		print("align start at %f, stop at %f"%(behaveblock['be_ts'][start_index],behaveblock['be_ts'][stop_index]))
		behaveblock = behaveblock.iloc[start_index:stop_index+1].reset_index(drop=True)

		
		# extract masks of video 
		masks = self.draw_rois(aim="of",count=1)[0]


		in_mask = [];t_in_mask=[];distances_in_mask=[]
		# print(masks[0][479,639])
		print("calculate cumulative time frame by frame: ...")
		for index,row in behaveblock.iterrows():
			# print(index)
			if index==0:
				delta_d = 0
				delta_t = 0
			else:
				delta_t = behaveblock['be_ts'][index]-behaveblock['be_ts'][index-1]
				delta_x = behaveblock['Body_x'][index]-behaveblock['Body_x'][index-1]
				delta_y = behaveblock['Body_y'][index]-behaveblock['Body_y'][index-1]
				delta_d = np.sqrt(delta_x**2+delta_y**2)

			# print(">>>>>>%d>>>>>>"%behaveblock['be_ts'][index])
			
			temp_in_mask=[]
			for mask in masks:				
				if mask[int(row['Body_y']),int(row['Body_x']),0] == 0:
					temp_in_mask.append(1)
				else:
					temp_in_mask.append(0)
			if sum(temp_in_mask)==0:
				temp_in_mask.append(1)
			else:
				temp_in_mask.append(0)

			in_mask.append(np.array(temp_in_mask))
			t_in_mask.append(np.array(temp_in_mask)*delta_t)
			distances_in_mask.append(np.array(temp_in_mask)*delta_d)


		print("frame numbers: ",end="")
		print(np.sum(in_mask,axis=0))
		print("time longs: ",end="")
		print(list(np.round(np.sum(np.array(t_in_mask),axis=0),2)))
		print("distances(in cm): ",end="")
		print(list(np.round(np.sum(np.array(distances_in_mask),axis=0),2)))
		print("----------------------")
		return list(np.round(np.sum(np.array(distances_in_mask),axis=0),2))

	@classmethod
	def oftimers(cls,videolists,starts=None,stops=None,start_indexes=None,stop_indexes =None,scale_distance=40,Interval_number=1,according="Body"):
		areatime_path = os.path.join(os.path.dirname(videolists[0]),'of_stat.csv')

		s=cls(videolists[0]).scale(scale_distance)
		

		with open(areatime_path,'w',newline="") as csv_file:
			writer = csv.writer(csv_file)
			writer.writerow(["Interval_number",Interval_number])
			writer.writerow(["scale",s])
			writer.writerow(['videos','start','stop','start_index','start_index','area1(cm)','other(cm)'])
			for video in videolists:
				if start_indexes==None and start_indexes==None:
					for start,stop in zip(starts,stops):
						of_distance = cls(video).oftimer(start=start,stop=stop,Interval_number=Interval_number,according=according)
						writer.writerow([video,start,stop,"",""]+list(np.multiply(of_distance,s)))
				else:
					for start_index,stop_index in zip(start_indexes,stop_indexes):
						of_distance = cls(video).oftimer(start_index=start_index,stop=stop_index,Interval_number=Interval_number,according=according)
						writer.writerow([video,"","",start_index,stop_index]+list(np.multiply(of_distance,s)))


if __name__=="__main__":
	video_path = r"C:\Users\Sabri\Desktop\program\data\video\epm\192093-20190807-102117.mp4"
	# EPMvideo(video_path).play_with_track(show="Head")
	# EPMvideo(video_path).oftimer(start=0,stop=300)
	OFvideo.oftimers([video_path],starts=[0,300],stops=[300,500],scale_distance=70,Interval_number=1)
	