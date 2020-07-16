
import cv2
import time
import threading
import numpy as np
import datetime
import os
import pandas as pd



frames_info =[]
is_record = 0
is_stop = 0



def add_recording_marker(img):
    cv2.circle(img,(10,10),5,(0,0,255),-1)
    cv2.putText(img, "Recording", (20,15) ,cv2.FONT_HERSHEY_SIMPLEX ,0.5, (0,0,255) ,1)
    return img

def add_timestr(img):
    now = datetime.datetime.now()
    time_str= now.strftime("%Y-%m-%d %H:%M:%S.%f")
    cv2.putText(img, time_str, (400,15) ,cv2.FONT_HERSHEY_SIMPLEX ,0.4, (0,200,0) ,1)
    return img

def current_time():
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    return now,time_str


def path(camera_index):
    time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    videoname = str(camera_index)+'_'+time_str+'.avi'
    tsname = str(camera_index)+"_"+time_str+'.txt'
    videopath = os.path.join(r'C:\Users\Sabri\Desktop\new_method_to_record',videoname)
    tspath=os.path.join(r'C:\Users\Sabri\Desktop\new_method_to_record',tsname)
    return videopath,tspath

def play_video(camera_index):
    print("camera_index: %s"%camera_index)
    global frames_info,is_record,is_stop
    cap = cv2.VideoCapture(camera_index)
    while True:
        ok,frame = cap.read()
        now,ts = current_time()
        mask = 255*np.zeros_like(frame)
        key = cv2.waitKey(1) & 0xff

        if key == ord('q'):
            is_stop=1
            is_record = 0

        if key == ord('s'):
            is_record = 1 - is_record

        frames_info.append([is_record,is_stop,frame,ts])

        if is_stop==1:
            break

        if is_record == 1:
            add_recording_marker(mask)
        add_timestr(mask)
            
        

        cv2.imshow('%s'%camera_index,cv2.addWeighted(frame,1,mask,1,0))
    cap.release()
    cv2.destroyAllWindows()
    print("finish record")



def save_video(camera_index,fourcc,fps,sz):
    timestamps = []
    while True:
        key = cv2.waitKey(1) & 0xff
        if key == ord("q"):
            is_stop = 1
        if len(frames_info)>0:
            is_record,is_stop,frame,ts = frames_info.pop(0)
            if is_stop:
                is_record = 0
            if is_record: # is_record ==1
                if len(timestamps)>0:
                    out.write(frame)
                    timestamps.append(ts)
                else:
                    videosavepath,tspath = path(camera_index)
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
        elif len(frames_info) > 100:
            print(len(frames_info))
            frames_info.pop(0)
        else:
            pass

def main_miniscope():
    mini_fourcc = cv2.VideoWriter_fourcc(*'mpeg')
    camera_mini = threading.Thread(target=play_video,args=(1,))
    camera_mini_save = threading.Thread(target=save_video,args=(1,mini_fourcc,30,(640,480),))

    behave_fourcc = cv2.VideoWriter_fourcc(*'mpeg')
    camera_behave = threading.Thread(target=play_video,args=(0,))
    camera_behave_save = threading.Thread(target=save_video,args=(0,behave_fourcc,20,(640,480),))

    # camera_mini.start()
    # camera_mini_save.start()
    camera_behave.start()
    camera_behave_save.start()

    # camera_mini.join()
    # camera_mini_save.join()
    # camera_behave.join()
    # camera_behave_save.join()

    print("main process Done")
def main_CFC():
    behave_fourcc = cv2.VideoWriter_fourcc(*'mpeg')
    camera_behave = threading.Thread(target=play_video,args=(0,))
    camera_behave_save = threading.Thread(target=save_video,args=(0,behave_fourcc,20,(640,480),))
    CFC = threading.Thread(target=cfc,args=(,))
    
    camera_behave.start()
    camera_behave_save.start()
    CFC.start() #实现循环

if __name__ == "__main__":
    main()
