
import cv2
import time
import threading
import numpy as np
import datetime
import os,sys
import pandas as pd

is_record = 0
is_stop = 0

def eye_on_signal():
    global is_record, is_stop
    while True:
        time.sleep(5)
        
        for i in range(100):
        # print(is_record)
            is_record=1
            time.sleep(100)
        # print(is_stop)
            is_record=0
            time.sleep(10)
        is_stop=1
        # print(is_stop)
        break

def add_recording_marker(img):
    cv2.circle(img,(10,10),5,(0,0,255),-1)
    cv2.putText(img, "Recording", (20,15) ,cv2.FONT_HERSHEY_SIMPLEX ,0.5, (0,0,255) ,1)
    return img

def add_timestr(img):
    now = datetime.datetime.now()
    time_str= now.strftime("%Y-%m-%d %H:%M:%S.%f")
    cv2.putText(img, time_str, (400,15) ,cv2.FONT_HERSHEY_SIMPLEX ,0.4, (0,200,0) ,1)
    return img,now

def path(camera_index,mouse_id):
    time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    videoname = str(camera_index)+"_"+str(mouse_id)+"_"+time_str+'.avi'
    tsname = str(camera_index)+"_"+str(mouse_id)+"_"+time_str+'.txt'
    videopath = os.path.join(r'D:',videoname)
    tspath=os.path.join(r'D:',tsname)
    return videopath,tspath

def record_video(camera_index,fourcc,fps,w,h,mouse_id):
    
    videosavepath,tspath = path(camera_index,mouse_id)
    
    timestamps = []
    print("----")
    cap = cv2.VideoCapture(camera_index)
    cap.set(3,w)
    cap.set(4,h)
    sz = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    ## to save the video
    global is_record,is_stop
    fourcc =fourcc
    fps=fps
    out = cv2.VideoWriter()
    out.open(videosavepath,fourcc,fps,sz,True)
    while True:
        ok,frame = cap.read()
        
        key = cv2.waitKey(5) & 0xff
        
        if key == ord('q'):
            is_stop =1 - is_stop

        elif key == ord('s'):
            is_record = 1 - is_record

        elif key == ord('t'):
            self.is_track = 1 - self.is_track
            self.diff_frame(frame)
        else:
            pass
        
        if is_stop:
            break
        if is_record == 1:
            timestamps.append(ts)
            out.write(frame)
            add_recording_marker(frame)
            
        frame,ts = add_timestr(frame)
        cv2.imshow('%s'%camera_index,frame)
        
    ts = pd.DataFrame(data = timestamps)
    ts.to_csv(tspath,index_label="frame_No")

    out.release()
    cap.release()
    cv2.destroyAllWindows()
    print(f"{videosavepath}  finish record")




if __name__ == "__main__":
    mouse_id = sys.argv[1]
    fourcc_mini = cv2.VideoWriter_fourcc(*'mpeg')
##    fourcc_beha = cv2.VideoWriter_fourcc(*'mpeg')
##    fourcc_mini = cv2.VideoWriter_fourcc(*'mp4v')
##    fourcc_beha = cv2.VideoWriter_fourcc(*'mp4v')
    camera_mini = threading.Thread(target=record_video,args=(0,fourcc_mini,30,752,480,mouse_id))
##    camera_beha = threading.Thread(target=record_video,args=(1,fourcc_beha,30,640,480,mouse_id))
##    eye_on_behave = threading.Thread(target=eye_on_signal)

    camera_mini.start()
    time.sleep(5)
##    camera_beha.start()
##    eye_on_behave.start()

##    eye_on_behave.join()
    print("main process done")
