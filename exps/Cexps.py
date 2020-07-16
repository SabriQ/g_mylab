import serial
import serial.tools.list_ports
import subprocess
import time
import os
import sys
from mylab.sys_camera import video_online_play
from mylab.sys_camera import video_recording

import cv2
import threading
import numpy as np
import datetime
import pandas as pd


class Exp():
    frames_info =[]
    is_record = 0
    is_stop = 0
    def __init__(self,port,data_dir):
        self.port = port
        self.data_dir = os.path.join(data_dir,time.strftime("%Y%m%d", time.localtime()))
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print("%s is created"%self.data_dir)
        if not self.port == None:
            try:
              self.ser = serial.Serial(self.port,baudrate=9600,timeout=0.1)   
              self.countdown(3) 
            except Exception as e:
              print(e)
              ports = [i.device for i in serial.tools.list_ports.comports()]
              print("choose port from %s"% ports)
              sys.exit()
        else:
            print("only camera is available")


    @staticmethod
    def countdown(seconds):
        i=0
        while True:
            sys.stdout.write("%.1is in total %ss"%(i,seconds))
            sys.stdout.write("\r")
            time.sleep(1)
            i += 1
            if i >= seconds:
                #sys.stdout.write("%s countdown finished"%seconds)
                break
            if Exp.is_stop == 1:
                break

    def record_camera(self,video_path):
        print("----start camera recording----")
        p = video_recording(video_path)
        time.sleep(3)
        return p
    def play_camera(self):
        print("----start camera playing----")
        p = video_online_play()
        return p
    def stop_record_camera(self,p):
        print("----stop camera----")
        time.sleep(1)
        try:
            p.kill()                  
        except Exception as e:
            print(e)
            
    def opencv_is_record(self):
        Exp.is_record = 1 - Exp.is_record
    def opencv_is_stop(self):
        Exp.is_stop = 1 - Exp.is_stop
        
    @staticmethod
    def add_recording_marker(img):
        cv2.circle(img,(10,10),5,(0,0,255),-1)
        cv2.putText(img, "Recording", (20,15) ,cv2.FONT_HERSHEY_SIMPLEX ,0.5, (0,0,255) ,1)
        return img
    
    @staticmethod
    def add_timestr(img):
        now = datetime.datetime.now()
        time_str= now.strftime("%Y-%m-%d %H:%M:%S.%f")
        cv2.putText(img, time_str, (400,15) ,cv2.FONT_HERSHEY_SIMPLEX ,0.4, (0,200,0) ,1)
        return img
    
    @staticmethod
    def current_time():
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        return now,time_str


    def path(self,camera_index):
        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        videoname = self.mouse_id +'_'+str(camera_index)+'_'+time_str+'.avi'
        tsname = self.mouse_id +'_'+str(camera_index)+"_"+time_str+'_ts.txt'
        videopath = os.path.join(self.data_dir,videoname)
        tspath=os.path.join(self.data_dir,tsname)
        return videopath,tspath

    def play_video(self,camera_index):
        print("camera_index: %s"%camera_index)
        cap = cv2.VideoCapture(camera_index)
        while True:
            ok,frame = cap.read()
            now,ts = self.current_time()
            mask = 255*np.zeros_like(frame)
            key = cv2.waitKey(1) & 0xff

            if key == ord('q'):
                Exp.is_stop= 1
                Exp.is_record = 0

            if key == ord('s'):
                Exp.is_record = 1 - Exp.is_record

            Exp.frames_info.append([Exp.is_record,Exp.is_stop,frame,ts])

            if Exp.is_stop==1:
                break

            if Exp.is_record == 1:
                self.add_recording_marker(mask)
            self.add_timestr(mask)
            
            cv2.imshow('%s'%camera_index,cv2.addWeighted(frame,1,mask,1,0))
        cap.release()
        cv2.destroyAllWindows()
        print("finish record")



    def save_video(self,camera_index,fourcc,fps,sz):
        timestamps = []
        while True:
            key = cv2.waitKey(1) & 0xff
            if key == ord("q"):
                Exp.is_stop = 1
            if len(Exp.frames_info)>0:
                Exp.is_record,Exp.is_stop,frame,ts = Exp.frames_info.pop(0)
                if Exp.is_stop:
                    Exp.is_record = 0
                if Exp.is_record: # is_record ==1
                    if len(timestamps)>0:
                        out.write(frame)
                        timestamps.append(ts)
                    else:
                        videosavepath,tspath = self.path(camera_index)
                        print(videosavepath)
                        timestamps=[]
                        out = cv2.VideoWriter()

                        out.open(videosavepath,fourcc,fps,sz,True)
                        out.write(frame)
                        timestamps.append(ts)

                else: # is_record == 0
                    if len(timestamps)>0:
                        out.release()
                        # savestamps in tspath
                        pd.DataFrame(data = timestamps).to_csv(tspath,index_label="frame_No")
                        # clear timestamps
                        timestamps = []
                    else:
                        pass
                if Exp.is_stop:
                    break
            elif len(Exp.frames_info) > 100:
                print(len(Exp.frames_info))
                Exp.frames_info.pop(0)
            else:
                pass
            
    def __del__(self):
        if not self.port == None:
            self.close()

    def close(self):
        if not self.port == None:
            self.ser.close()
            print('PORT:%s get closed'%self.port)
if __name__ == "__main__":
    exp = Exp("test")
    p = exp.play_camera()
    exp.countdown(4)
    exp.stop_record_camera(p)
