from mylab.Cvideo import Video
import pandas as pd
import glob
import numpy as np
import h5py
import os
import csv

def detect(Frame_No,Time,X,Y,L):
    
    distances = (np.diff(X)**2 + np.diff(Y) ** 2)**0.5
    speeds = np.divide(distances,np.diff(Time))
    distances = np.insert(distances,0,0)
    
    speeds = np.insert(speeds,0,0)
   
    mean_distance = np.mean(distances)
    std_distance = np.std(distances,ddof=1)
    median_distance = np.median(distances)
    max_distance = 1.96*std_distance+mean_distance

##    max_distance = 4
    print("distance:",mean_distance,max_distance)
    
    mean_speed = np.mean(speeds)
    std_speed = np.std(speeds,ddof =1)
    max_speed = 2.33*std_speed+mean_speed #99%    
    print("speed:",mean_speed,max_speed)
  
    lost_object = []
    wrong_object = []
    
    for frame_No,l in zip(Frame_No,L):       
        if l<0.8:
            lost_object.append(frame_No)
            continue
    for i in range(20):
        for frame_No,distance,speed in zip(Frame_No,distances,speeds):
            if  distance > max_distance:
        ##            wrong_object.append(frame_No)                
                lost_object.append(frame_No)
##        print(len(lost_object),end="\n")
        
        start = end =0
        for frame in sorted(lost_object):
            start = frame-2
            end = frame            
            if not end == max(Frame_No):
                X[start:end] = np.linspace(X[start],X[end],end-start)
                Y[start:end] = np.linspace(Y[start],Y[end],end-start)
##            print(X[end-1],Y[end-1],end="\n")
            
    distances = (np.diff(X)**2 + np.diff(Y) ** 2)**0.5
    speeds = np.divide(distances,np.diff(Time))
    for frame_No,distance,speed in zip(Frame_No,distances,speeds):
        if  distance > max_distance: #z_score = (distance-mean)/std
            wrong_object.append(frame_No)
    return wrong_object,X,Y

def count(up,down,T):
    up_t =0
    mid_t = 0
    down_t = 0
    i = 0
    for t,y in zip(T,Y):
        if i>0:
            delt = T[i]-T[i-1]
            if y >up:
                up_t = up_t+delt
            elif y < down:
                 down_t = down_t+delt
            else:
                mid_t = mid_t+delt
        i = i+1
    return up_t,mid_t,down_t

########

videolists = glob.glob(r"C:\Users\Sabri\Desktop\program\video\CPA\*asf")
##print(videolists)
h5lists = glob.glob(r"C:\Users\Sabri\Desktop\program\video\CPA\*h5")
##print(h5lists)
ts_lists = glob.glob(r"C:\Users\Sabri\Desktop\program\video\CPA\*txt")
##print(ts_lists)
no_video = []
for h5list in h5lists:
    f = pd.read_hdf(h5list)   
    
    X =np.array(f.DeepCut_resnet50_CPAMay5shuffle1_20000.Body['x'])
    Y =np.array(f.DeepCut_resnet50_CPAMay5shuffle1_20000.Body['y'])
    L = np.array(f.DeepCut_resnet50_CPAMay5shuffle1_20000.Body['likelihood'])
    ts_list = [i for i in ts_lists if os.path.basename(h5list)[0:12] in i]
    print(ts_list)
    T = np.array(pd.read_csv(ts_list[0],sep='\n',encoding='utf-16',header=None)[0])
    Frame_No = np.linspace(1,len(T),len(T),dtype=np.int16)


    wrong_object,_,_=detect(Frame_No,T,X,Y,L)
    videolist = [i for i in videolists if os.path.basename(h5list)[0:12] in i]
    if videolist:
        video = Video(videolist[0])
    else:
        no_video.append(os.path.basename(h5list)[0:12])
        print(f'{os.path.basename(h5list)[0:12]} does not have a video')
    _,pts =video.draw_roi()
  
    
    up = max([i[1] for i in pts])
    down = min([i[1] for i in pts])
    white,gray,black=count(up,down,T)
    output = [os.path.basename(videolist[0]),black,gray,white]
    with open(r"C:\Users\Sabri\Desktop\program\video\CPA\output.csv",'a') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(output)
    print(f'{os.path.basename(videolist[0])} gets finished! ')
    if len(no_video):
        print(f'{no_video} get no videos')

            
        
    
