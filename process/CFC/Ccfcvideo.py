from mylab.Cvideo import Video
import os,sys,glob
import cv2
from mylab.Cfile import TimestampsFile 
from mylab.process.CFC.Ccfcfile import FreezingFile as FF
import pandas as pd
from mylab.Cdecs import *
import csv
from mylab.Cdecs import *
class CFCvideo(Video):
    def __init__(self,video_path):
        super().__init__(video_path)
        self.videofreezing_path = self.abs_prefix + '_freezing.csv'

    def show_masks(self):
        mask = self.draw_rois(aim="freezing",count=1)[0][0]
        cv2.imshow("mask",mask)

    def __video2csv(self,Interval_number=1,show = True):

        mask= self.draw_rois(aim="freezing",count=1)[0][0]

        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        cap = cv2.VideoCapture(self.video_path)
        frame_count =0
        font = cv2.FONT_HERSHEY_COMPLEX
        while(1):
            frame_count += 1
            ret,frame = cap.read()        
            if ret == True:
    ##            print(frame_count)
                if (frame_count-1)%Interval_number == 0:
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame_gray = cv2.add(mask,frame_gray)
                    if show:
                        if frame_count <=100:
                            cv2.putText(frame_gray,f'frame_No:{frame_count}',(10,15), font, 0.5, (0,0,0))
                            cv2.imshow("video",frame_gray)                    
                            cv2.waitKey(30)     
                    yield (frame_count,frame_gray)
            else :
                break
        cap.release()
        cv2.destroyAllWindows()
        
    def video2csv(self,timestamp_method = "ffmpeg",Interval_number=3,diff_gray_value=30,show = True):
        """calculate the change in fixed roi"""
        if not os.path.exists(self.videots_path):
            try:
                self.generate_ts_txt()
            except:
                print("fail to extract tiemstamps of %s by ffprobe"%self.video_name)
                sys.exit()
        ts = pd.DataFrame(TimestampsFile(self.videots_path,method=timestamp_method).ts)
        # print(type(ts))
        print("==timestamps==")
        ts['Frame_No'] = list(range(1,len(ts)+1)) # Frame_No start from 1
        print(ts)
        print("==============")
        frame_grays = self.__video2csv(Interval_number = Interval_number,show = show)
        
        print(self.video_name+' Frame Number & timestamps are loaded successfully \nvideo is processing frame by frame...')
        changed_pixel_percentages = []
        Frame_No = []

        for item in frame_grays:
            Frame_No.append(item[0])
            if item[0]==1:
                width, height = item[1].shape
                total_pixel = width*height
                changed_pixel_percentages.append(0)
                frame1 = item[1];
            else:
                frame2 = item[1];judge = cv2.absdiff(frame2,frame1) > diff_gray_value
                changed_pixel_percentage = sum(sum(judge))/total_pixel*100
                changed_pixel_percentages.append(changed_pixel_percentage)
                frame1=frame2

        df= pd.DataFrame({'Frame_No':Frame_No,'percentage':changed_pixel_percentages},index=None)
        df = pd.merge(ts,df,on = 'Frame_No',how="outer").sort_values(by="Frame_No",ascending = True)    
        df.to_csv(self.videofreezing_path,index = False,sep = ',')

        print(self.video_path+' finish processing.')
        return df
      

    def video2csv2(self,Interval_number=3,roi_radius = 10,diff_gray_value_in=30,show = True):
        """according to tracked coordinates, calculted the change in dynamic roi"""
        if not os.path.exists(self.videots_path):
            try:
                print("generating timestamps by ffmpeg")
                self.generate_ts_txt()
            except:
                print("fail to generate timestamps by ffprobe")
                sys.exit()
        else:
            ts = pd.read_table(self.videots_path,sep='\n',header=None,encoding="utf-16")

        if not os.path.exists(self.video_track_path):
            print("you haven't done deeplabcut tracking")
            sys.exit()
        else:
            track = pd.read_hdf(self.video_track_path)

    def video2csv3(self):
        """according to tracked coordinates, calculted the chage in dynamic mouse contours"""
        if not os.path.exists(self.videots_path):
            try:
                print("generating timestamps by ffmpeg")
                self.generate_ts_txt()
            except:
                print("fail to generate timestamps by ffprobe")
                sys.exit()
        else:
            ts = pd.read_table(self.videots_path,sep='\n',header=None,encoding="utf-16")

        if not os.path.exists(self.video_track_path):
            print("you haven't done deeplabcut tracking")
            sys.exit()
        else:
            track = pd.read_hdf(self.video_track_path)

    def freezing_percentage(self,timestamp_method = "ffmpeg",Interval_number=3,diff_gray_value=30,show = True
        ,threshold = 0.005, start = 0, stop = 300,show_detail=False,percent =True,save_epoch=True):
        """
        Syntax:
            CFCvideo(video).freezing_percentage(*args)
        Args:
            Interval_number=3,
            diff_gray_value=30,
            show = True,
            threshold = 0.005,
            start = 0,
            stop = 300,
            show_detail=True,
            percent =True,
            save_epoch=True
        """
        if not os.path.exists(self.videofreezing_path):
            self.video2csv(timestamp_method = timestamp_method,Interval_number=Interval_number
                ,diff_gray_value=diff_gray_value,show = show)

        return FF(self.videofreezing_path).freezing_percentage(threshold=threshold, start = start, stop = stop
            ,show_detail=show_detail,percent =percent,save_epoch=save_epoch)

    
    @classmethod
    @timeit
    def freezing_percentages(cls,videolists,timestamp_method="ffmpeg",Interval_number=3,diff_gray_value=30,show = True,
        threshold = 0.5, start = 0, stop = 300,show_detail=True,percent =True,save_epoch=True):
        """
        syntax:
            confirm the *args with `CFCvideo(video).freezing_percentage(*args)`, then,
            CFCvideo.freezing_percentage(videolists,*args).
            result will be saved named as `freezing_stat.csv` at the same directory
        Args:
            videolists: a list of video to calculate freezing 
            Interval_number=3,
            diff_gray_value=30,
            show = True,
            threshold = 0.005,
            start = 0,
            stop = 300,
            show_detail=True,
            percent =True,
            save_epoch=True
        """
        freezing_stat_path = os.path.join(os.path.dirname(videolists[0]),'freezing_stat.csv')

        with open(freezing_stat_path,'w',newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['diff_gray_value',diff_gray_value])
            writer.writerow(['threshold',threshold])
            writer.writerow(["Interval_number",Interval_number])
            writer.writerow(['start',start,"stop",stop])
            writer.writerow(['video','freezing%'])
            for video in videolists:
                freezing = cls(video).freezing_percentage(timestamp_method=timestamp_method,Interval_number=Interval_number,diff_gray_value=diff_gray_value,show = show,threshold=threshold, start = start, stop = stop,show_detail=show_detail,percent =percent,save_epoch=save_epoch)
                writer.writerow([video,freezing])
if __name__ == "__main__":
    # help(CFCvideo.freezing_percentage)
    videolists=glob.glob(r"C:\Users\qiushou\Desktop\CFC\*.avi")
    # for video in videolists:
    CFCvideo.freezing_percentages(videolists)
        # CFCvideo(video).freezing_percentage(Interval_number=1,diff_gray_value=30,show = True
        #   ,threshold = 0.005, start = 0, stop = 100,show_detail=True,percent =True,save_epoch=True)