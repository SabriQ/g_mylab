import numpy as np
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import os,sys
import scipy.io as scio

def mimictrack(ts_dir):
    for i in os.listdir(ts_dir):
        if str(i).endswith('_ts.txt'):
            ts_path = os.path.join(ts_dir,i)
            Time = pd.read_csv(ts_path, sep=" ",encoding = "utf-16",header =None,names=['ts(s)'])
            #matlab tracing results
            
            matfile = os.path.join(ts_dir,('result_'+ i.replace('_ts.txt','.mat')))
            
            if os.path.exists(matfile):
                data = scio.loadmat(matfile)
                X = [i[0] for i in data['result'][0][0][-2]]
                Y = [i[1] for i in data['result'][0][0][-2]]
                if not len(Time) == len(X):
                    print(f'matlab tracking lost {abs(len(Time)-len(X))} frames')
                while not len(Time) == len(X):
                    X.append(X[-1])
                    Y.append(Y[-1])
            else:
                X = Y = [100 for i in range(len(Time))]
            
            Frame_No = np.linspace(1,len(X),len(X),dtype=int)
            
                               
            dataframe = pd.DataFrame({'Frame':Frame_No,'time':Time['ts(s)'],'X':X,'Y':Y})                
            if not os.path.exists(ts_path.replace('_ts.txt','_tracking.csv')):                
                dataframe.to_csv(ts_path.replace('_ts.txt','_tracking.csv'),index = None)
                print(f'{i} tracking file is created')
            else:
                print(f'{i}tracking file alread exists.')
              

def detect(Frame_No,Time,X,Y):
    
    distances = (np.diff(X)**2 + np.diff(Y) ** 2)**0.5
    speeds = np.divide(distances,np.diff(Time))
    distances = np.insert(distances,0,0)
    speeds = np.insert(speeds,0,0)

    mean_speed = np.mean(speeds)
    std_speed = np.std(speeds,ddof =1)

    lost_object = []
    wrong_object = []
    
    for frame_No,x,y,speed in zip(Frame_No,X,Y,speeds):
       
        if x+y < 0 or x*y< 0:
            lost_object.append(frame_No)
            continue
        if abs(speed-mean_speed)/std_speed > 2.33: #z_score = (distance-mean)/std
            wrong_object.append(frame_No)
            
##    print(f'{len(lost_object)},{len(wrong_object)}')
##    print(f'{wrong_object}')
    start = end =0
    for frame in lost_object:
        if frame < end:
            continue
        else:
            def start_frame(frame):
                if X[frame-1]+Y[frame-1]<0 or X[frame-1]*Y[frame-1]<0:
                    frame = frame-1
                    return start_frame(frame)
                else:
                    return frame
            def end_frame(frame):
                if X[frame-1]+Y[frame-1]<0 or X[frame-1]*Y[frame-1]<0:
                    frame = frame+1
                    return end_frame(frame)
                else:
                    return frame

            start = start_frame(frame)
            end = end_frame(frame)        

            X[(start-1):end] = np.linspace(X[start-1],X[end+1],end-start+1)
            Y[(start-1):end] = np.linspace(Y[start-1],Y[end+1],end-start+1)
    return wrong_object,X,Y
    
def correct(video_path,scale = 0.11,mannual =True,detection = True):
    videotrack_path = os.path.splitext(video_path)[-2] + '_tracking.csv'
    try:
        track = pd.read_table(videotrack_path,sep=',')
    except:
        print(f"{videotrack_path} \n路径中不要含有中文，空格等奇怪符号")
        sys.exit()
    
    Frame_No = list(track['Frame'])
    Time = list(track['time'])
    X = list(track['X'])
    Y = list(track['Y'])
    if detection == True:        
        wrong_frames,X,Y=detect(Frame_No,Time,X,Y)
    else:        
        wrong_frames = Frame_No      
   
    if mannual == True:
        font = cv2.FONT_HERSHEY_COMPLEX
        cv2.namedWindow('correct_coordination',0)
        cap = cv2.VideoCapture(video_path)
        
        temp_Frame_No = []
        temp_X = []
        temp_Y = []

        def choose_frame(event,x,y,flags,param):            
            if event == cv2.EVENT_LBUTTONDOWN:
                nonlocal temp_Frame_No,temp_X,temp_Y
                temp_Frame_No.append(frame_No)
                temp_X.append(x*scale)
                temp_Y.append(y*scale)
                cv2.circle(frame,(x,y),5,(255,0,0),2)
                if len(temp_Frame_No) == 1:
                    print('it is the 1st poind')                                       
                if len(temp_Frame_No) == 2:
                    print("it is the 2nd point")
                    if temp_Frame_No[1]<temp_Frame_No[0]:
                        temp_Frame_No.reverse()
                        temp_X.reverse()
                        temp_Y.reverse()
                        
                    X[(temp_Frame_No[0]-1):(temp_Frame_No[1])] = np.linspace(temp_X[0],temp_X[1],abs(temp_Frame_No[1]-temp_Frame_No[0])+1)
                    Y[(temp_Frame_No[0]-1):(temp_Frame_No[1])] = np.linspace(temp_Y[0],temp_Y[1],abs(temp_Frame_No[1]-temp_Frame_No[0])+1)      
                    
                        
                    print('correction is implemented between these two points')
                    temp_Frame_No = []
                    temp_X = []
                    temp_Y = []
                    
        def drow_roi(event,x,y,flags,param):
            img = np.zeros_like(param['frame'])
            if event == cv2.EVENT_LBUTTONDOWN:
                temp_X.append(x*scale)
                temp_Y.append(y*scale)
                
            if event == cv2.EVENT_MOUSEMOVE and len(temp_X) > 2:
                temp_X[-1] = x
                temp_Y[-1] = y
                pts = np.array([i for i in zip(temp_X,temp_Y)])
                print(pts)
                cv2.fillPoly(img,[pts],255,2)
                img = cv2.addWeighted(frame,1.0,img,0.5,0.)
                cv2.imshow("roi",img)

        frame_No = 1
        for wrong_frame in wrong_frames:
            if frame_No >= wrong_frame:
                continue
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES,wrong_frame-1)
                ret,frame = cap.read()
                frame_No = wrong_frame
                cv2.putText(frame,f'{frame_No}',(20,30), font, 1, (255,255,255))
                x_pos = int(round(X[frame_No-1]/scale))
                y_pos = int(round(Y[frame_No-1]/scale))
                cv2.circle(frame,(x_pos,y_pos),5,(0,0,255),2)
                cv2.imshow('correct_coordination',frame)
                
                while 1:
                    key = cv2.waitKey(30) & 0xFF

                    if key == ord('f'):
                        frame_No += 10
                        cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No)
                        ret,frame=cap.read()                
                        if ret:
                            cv2.putText(frame,f'{frame_No}',(20,30), font, 1, (255,255,255))
                            x_pos = int(round(X[frame_No-1]/scale))
                            y_pos = int(round(Y[frame_No-1]/scale))
                            cv2.circle(frame,(x_pos,y_pos),5,(0,0,255),2)
                            cv2.imshow('correct_coordination',frame)         
                        else:
                            break
                    if key == ord('a'):
                        if frame_No <=1:
                            frame_No = 1
                            print('it is the first frame!')
                        else:
                            frame_No = frame_No -1
                        
                        cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No)
                        ret,frame=cap.read()
                        if ret:
                            cv2.putText(frame,f'{frame_No}',(20,30), font, 1, (255,255,255))
                            x_pos = int(round(X[frame_No-1]/scale))
                            y_pos = int(round(Y[frame_No-1]/scale))
                            cv2.circle(frame,(x_pos,y_pos),5,(0,0,255),2)
                            cv2.imshow('correct_coordination',frame)
                        else:
                            break
                    if key == ord('n'):
                        break
                    if key == ord('q'):
                        print(len(X))
                        print(len(track['X']))
                        try:
                            track['X'] = X
                            track['Y'] = Y
                        except:
                            print("X or Y is longer or shorter")
                        track.to_csv(videotrack_path,mode = 'w',index = False)
                        print('corrected coordinates have been saved')
                        cap.release()
                        cv2.destroyAllWindows()
                        return
                    cv2.setMouseCallback("correct_coordination",drow_roi,
                                         {"frame":frame})

        cap.release()
        cv2.destroyAllWindows()
    else:
         print(f"{os.path.basename(videotrack_path)}auto-correction finish")       
    track['X'] = X
    track['Y'] = Y
    track.to_csv(videotrack_path,mode='w',index = False)
    print('corrected coordinates have been saved')

                
   
    
if __name__ == '__main__':
##    ts_dir = r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\matfile\asf'
##    mimictrack(ts_dir)

##    ts_dir = r'Y:\吴近泥\# miniscope\RAW_DATA\CTX_CFC_6mice\M181078_DPCA1\20190404_shock\H1_M2_S14'
##    mimictrack(ts_dir)
##    video_path = r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\matfile\asf\#10186-day1.asf'
    video_path=r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\2019031100002.AVI'
    correct(video_path,scale = 1,mannual = True,detection = True)

