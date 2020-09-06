from mylab.Cvideo import Video
import os,sys,glob
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mylab.Cdecs import *
import csv
from mylab.Cfile import TrackFile

class OFvideo(Video):
    def __init__(self,video_path):  
        super().__init__(video_path)
        self.videoAreaStay_path = self.abs_prefix + '_areas.csv'
        

    def show_masks(self):
        masks = self.draw_of_masks(ratio=6)[0] 
        cv2.imshow("whole_area",masks[0])
        cv2.imshow("center",masks[1])
        cv2.waitKey(0)

    def show_track_fig(self,frame_as_bg=False,save_fig = True):
        masks,coords = self.draw_of_masks()
        mask = masks[0]
        mask_center = mask[1]
        coord = np.array(coords[0])
        coord_center = coords[1]
        try:
            Track = TrackFile(self.video_track_path)
        except:
            print("no track file")
            sys.exit()

        X=[]
        Y=[]
        count = 1
        for x,y in zip(Track.behave_track["Body_x"],Track.behave_track["Body_y"]):
            if x<min(coord[:,0]) or x > max(coord[:,0]) or y < min(coord[:,1]) or y>max(coord[:,1]):
                # print("abort")
                count=count+1
            else:
                X.append(x)
                Y.append(y)

        if count>10:
            print("you have about %s points"%count )

        cap = cv2.VideoCapture(self.video_path)
        ret,frame = cap.read()
        white_bg = np.ones_like(frame)*255
        if frame_as_bg:
            bg = frame
        else:
            bg = white_bg
        cv2.polylines(bg,[coord],True,(0,0,255),2)
        cv2.polylines(bg,[coord_center],True,(0,255,0),2)
        for i in range(len(X)-1):
            pts1=(int(X[i]),int(Y[i]))
            pts2=(int(X[i+1]),int(Y[i+1]))
            cv2.line(bg,pts1,pts2,(255,0,0),1,lineType = cv2.LINE_AA)

        M = cv2.getPerspectiveTransform(np.float32(coord),np.float32([[100,100],[100,600],[600,600],[600,100]]))
        dst = cv2.warpPerspective(bg,M,(700,700))
        plt.xticks([])
        plt.yticks([])
        plt.axis('off')
        plt.title(self.video_name)
        plt.imshow(dst)
        if save_fig:
            plt.savefig(self.abs_prefix+'_track_fig.png',dpi=600,bbox_inches="tight")

    @staticmethod
    def find_close_fast(arr,e):
        min_value = min(np.abs(np.add(arr,e*-1)))
        locations = np.where(np.abs(np.add(arr,e*-1))==min_value)
        # print(locations[0][0])
        return locations[0][0]

    def draw_of_masks(self,ratio=6):
        """
        ratio : the area of center zone / the area of the whole zone 
        """
        mask,coord = self.draw_rois(aim="of",count=1)
        # print(coord)
        coords_xs = np.array(coord)[0][:,0]
        coords_ys = np.array(coord)[0][:,1]
        delt_x1  = abs(coords_xs[0]-coords_xs[2])*(1-1/np.sqrt(ratio))/2
        delt_x2  = abs(coords_xs[1]-coords_xs[3])*(1-1/np.sqrt(ratio))/2
        delt_y1 = abs(coords_ys[0]-coords_ys[2])*(1-1/np.sqrt(ratio))/2
        delt_y2 = abs(coords_ys[1]-coords_ys[3])*(1-1/np.sqrt(ratio))/2

        if coords_xs[0]<coords_xs[2]:
            nx0 = coords_xs[0]+delt_x1
            nx2 = coords_xs[2]-delt_x1
        else:
            nx0 = coords_xs[0]-delt_x1
            nx2 = coords_xs[2]+delt_x1

        if coords_xs[1]<coords_xs[3]:
            nx1 = coords_xs[1]+delt_x2
            nx3 = coords_xs[3]-delt_x2
        else:
            nx1 = coords_xs[1]-delt_x2
            nx3 = coords_xs[3]+delt_x2

        if coords_ys[0]<coords_ys[2]:
            ny0 = coords_ys[0]+delt_y1
            ny2 = coords_ys[2]-delt_y1
        else:
            ny0 = coords_ys[0]-delt_y1
            ny2 = coords_ys[2]+delt_y1

        if coords_ys[1]<coords_ys[3]:
            ny1 = coords_ys[1]+delt_y2
            ny3 = coords_ys[3]-delt_y2
        else:
            ny1 = coords_ys[1]-delt_y2
            ny3 = coords_ys[3]+delt_y2

        center_coord = np.array([[nx0,ny0],[nx1,ny1],[nx2,ny2],[nx3,ny3]],np.int32)
        # print(center_coord)
        # cv2.imshow("mask",mask[0])
        center_mask = 255*np.ones_like(mask[0])
        cv2.fillPoly(center_mask,[center_coord],0)
        # cv2.imshow(mask[0])
        # cv2.imshow("center",center)
        # cv2.waitKey(0)
        return [mask[0],center_mask], [coord[0],center_coord]

    @timeit
    def oftimer(self,start=None,stop=None,start_index=None,stop_index=None
        ,Interval_number=1,according="Body"):
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
            print("loading track")
            track = pd.read_hdf(self.video_track_path)
            print("loaded track")
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
        # masks = self.draw_rois(aim="of",count=2)[0]
        masks = self.draw_of_masks(ratio=6)[0]

        in_mask = [];t_in_mask=[]
        # print(masks[0][479,639])
        print("calculate cumulative time frame by frame: ...")
        for index,row in behaveblock.iterrows():
            # print(index)
            if index==0:
                delta_t = 0
            else:
                delta_t = behaveblock['be_ts'][index]-behaveblock['be_ts'][index-1]

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
        print(pd.DataFrame(t_in_mask))
        print("Context","Center","others")
        print("frame numbers: ",end="")
        print(np.sum(in_mask,axis=0))
        print("time longs: ",end="")
        print(list(np.round(np.sum(np.array(t_in_mask),axis=0),2)))
        print("----------------------")
        return list(np.round(np.sum(np.array(t_in_mask),axis=0),2))

    @classmethod
    def oftimers(cls,videolists,starts=None,stops=None,start_indexes=None,stop_indexes =None,Interval_number=1,according="Body"):
        areatime_path = os.path.join(os.path.dirname(videolists[0]),'areatime_stat.csv')
        with open(areatime_path,'w',newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Interval_number",Interval_number])
            writer.writerow(['videos','start','stop','start_index','start_index','area1','area2','other'])
            for video in videolists:
                print(video)
                if start_indexes==None and start_indexes==None:
                    for start,stop in zip(starts,stops):
                        area_time = cls(video).oftimer(start=start,stop=stop,Interval_number=Interval_number,according=according)
                        writer.writerow([video,start,stop,"",""]+area_time)
                else:
                    for start_index,stop_index in zip(start_indexes,stop_indexes):
                        area_time = cls(video).oftimer(start_index=start_index,stop=stop_index,Interval_number=Interval_number,according=according)
                        writer.writerow([video,"","",start_index,stop_index]+area_time)


if __name__=="__main__":



    file = r"C:\Users\Sabri\Desktop\program\Data\video\epm\192093-20190807-102117.mp4"
    OFvideo(file).show_masks()
    