import serial
import serial.tools.list_ports
import subprocess
import time
import os
import sys
from mylab.sys_camera import video_online_play
from mylab.sys_camera import video_recording

import cv2
from threading import Thread
from multiprocessing import Process,Queue
import numpy as np
import datetime
import pandas as pd
import winsound


class Exp():
    frames_info =[]
    is_record = 0
    is_stop = 0

    is_shock = 0
    is_tone_1 = 0
    is_bluelaser = 0
    is_yellowlaser = 0

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
              print("%s is connected"%self.port)
            except Exception as e:
              print(e)
              ports = [i.device for i in serial.tools.list_ports.comports()]
              print("choose port from %s"% ports)
              sys.exit()
        else:
            print("only camera is available")
            
#%% ===================events==============
    def shock(self,duration=2):
        while not Exp.is_stop:
            cv2.waitKey(2)
            if Exp.is_shock:
                print("shock starts at %s"%self.current_time()[1])
                self.ser.write("0".encode()) # shock on
                time.sleep(duration)
                self.ser.write("1".encode()) # shock off
                print("shock ends at %s"%self.current_time()[1])
                Exp.is_shock = 0

    def tone1(self,frequency=3000,duration=500,latency=0):
        while not Exp.is_stop:
            cv2.waitKey(2)
            if Exp.is_tone_1:
                print("tone starts at %s"%self.current_time()[1],end=" ")
                winsound.Beep(frequency,duration)
                print("tone ends at %s"%self.current_time()[1])
                time.sleep(latency/1000)
                Exp.is_tone_1=0

    def bluelaser(self,duration=180):
        while not Exp.is_stop:
            cv2.waitKey(2)
            if Exp.is_bluelaser:
                print("bluelaser starts at %s"%self.current_time()[1])
                self.ser.write("4".encode()) # blue laser on
                time.sleep(duration)
                self.ser.write("5".encode()) # blue laser off
                print("bluelaser ends at %s"%self.current_time()[1])
                Exp.is_bluelaser = 0

    def yellowlaser(self,duration=5):
        while not Exp.is_stop:
            cv2.waitKey(2)
            if Exp.is_yellowlaser:
                print("yellowlaser starts at %s"%self.current_time()[1])
                self.ser.write("2".encode()) # yellow laser on
                time.sleep(duration)
                self.ser.write("3".encode()) # yellow laser off
                print("yellowlaser ends at %s"%self.current_time()[1])
                Exp.is_yellowlaser = 0

    def do_shock(self):
        Exp.is_shock = 1
    def do_tone(self):
        Exp.is_tone_1 = 1
    def do_bluelaser(self):
        Exp.is_bluelaser = 1
    def do_yellowlaser(self):
        Exp.is_yellowlaser = 1

#%%=========================================

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
    #%% use ffmpeg
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
            
    #%% use opencv
        
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


    def opencv_is_record(self):
        Exp.is_record = 1
        print("start video recording")
    def opencv_is_stop(self):
        Exp.is_record = 0
        print("end video recording")
    def path(self,camera_index):
        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        videoname = self.mouse_id +'_'+str(camera_index)+'_'+time_str+'.avi'
        tsname = self.mouse_id +'_'+str(camera_index)+"_"+time_str+'_ts.txt'
        videopath = os.path.join(self.data_dir,videoname)
        tspath=os.path.join(self.data_dir,tsname)
        return videopath,tspath



    def play_video2(self,camera_index):
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

            # if key == ord('s'):
            #     Exp.is_record = 1 - Exp.is_record

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

    def play_video(self,camera_index):
        print("camera_index: %s"%camera_index)
        cap = cv2.VideoCapture(camera_index,cv2.CAP_DSHOW)
        while True:
            ok,frame = cap.read()
            if ok:
                now,ts = self.current_time()
                mask = 255*np.zeros_like(frame)
                key = cv2.waitKey(1) & 0xff

                if key == ord('q'):
                    Exp.is_stop= 1
                    Exp.is_record = 0

                # if key == ord('s'):
                #     Exp.is_record = 1 - Exp.is_record

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
    def save_video2(self,camera_index,fourcc,fps,sz):
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

    def save_video(self,camera_index,fourcc,fps,sz):
        timestamps = []
        while True:
            key = cv2.waitKey(5) & 0xff

            if len(Exp.frames_info)>0:
                is_record,is_stop,frame,ts = Exp.frames_info.pop(0)
                if is_stop:
                    is_record = 0
                if is_record: # is_record ==1
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
                if is_stop:
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
