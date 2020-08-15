import serial
import serial.tools.list_ports
import subprocess
import time
import os
import sys
from mylab.sys_camera import video_online_play
from mylab.sys_camera import video_recording

import cv2
from multiprocessing import Process,Queue
from threading import Thread
import numpy as np
import datetime
import pandas as pd
import winsound

def current_time():
    now = datetime.datetime.now()
    time_str = now.strftime("%Y%m%d-%H%M%S")
    return now,time_str

def play_video(q):
    is_record = 0
    is_stop = 0
    cap = cv2.VideoCapture(0)
    while True:
        ok,frame = cap.read()
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            is_stop= 1
            is_record = 0

        if key == ord('s'):
            is_record = 1 - is_record

        q.put([is_record,is_stop,frame])

        if is_stop==1:
            break
        if is_record == 1:
            pass

        cv2.imshow('0',frame)
    cap.release()
    cv2.destroyAllWindows()
    print("finish video record")

def save_video(q):
    out = 0
    while True:
        if not q.empty():
            value = q.get()
            is_record,is_stop,frame = value

            if is_stop:
                is_record = 0
            if is_record: # is_record ==1
                if not isinstance(out,cv2.VideoWriter):
                    videosavepath = os.path.join(r"C:\Users\qiushou\Desktop\test",current_time()[1]+".avi")
                    print("new video: %s"%videosavepath)
                    out = cv2.VideoWriter()
                    out.open(videosavepath,cv2.VideoWriter_fourcc(*'XVID'),30,(640,480),True)
                out.write(frame)
            else:                
                if isinstance(out,cv2.VideoWriter):
                    out.release()
                    print("save %s"%videosavepath)
                    out = 0

            if is_stop:
                break
    print("finish video save")
    


if __name__ == "__main__":
    q = Queue()
    behave_video = Process(target=play_video,args=(q,))
    save_behave_video = Process(target=save_video,args=(q,))

    behave_video.start()
    save_behave_video.start()

    print("main process")