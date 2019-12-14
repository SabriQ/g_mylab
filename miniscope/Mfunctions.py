import scipy.io as spio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle 
import os
import glob
import datetime
import math
from mylab.Cvideo import Video

def save_result(result,result_path):
    with open(result_path,'wb') as f:
        pickle.dump(result,f)
    print("result is saved.")
def load_result(result_path):
    with open(result_path,'rb') as f:
        result = pickle.load(f)
    print("result is loaded")
    return result
def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict

level = 0
def view_variable_structure(variable):       
    global level   
    level=level+1        
    if isinstance(variable,dict):
        for key in variable.keys():
            print(2*(level-1)*" ","--",key)
            view_variable_structure(variable[key])
            level = level -1
    if isinstance(variable,list):
        if isinstance(variable[0],int) or isinstance(variable[0],str) or isinstance(variable[0],tuple):
            print(2*(level-1)*" ","--",len(variable),'lists of int/str/tuples')
        else: 
            print(2*(level-1)*" ","--",len(variable),'lists','for each list there are')
            view_variable_structure(variable[0])
            level = level-1

    if isinstance(variable,pd.core.frame.DataFrame):
        print(2*(level-1)*" ",level*" ","--",len(variable.columns),"columns |",variable.columns[0],'...',variable.columns[-1],"|")
    else:
        pass
    


def generate_tsFileList(dateDir=r"X:\miniscope\20191028\191172"):    
    tsFileList = glob.glob(os.path.join(dateDir,"H*/timestamp.dat"))
#    tsFileList = [i for i in tsFileList if "2019111" not in i]
    def sort_key(s):     
        if s:            
            try:         
                date = re.findall('\d{8}', s)[0]
            except:      
                date = -1            
            try:         
                H = re.findall('H(\d+)',s)[0]
            except:      
                H = -1            
            try:         
                M = re.findall('M(\d+)',s)[0]
            except:      
                M = -1            
            try:         
                S = re.findall('S(\d+)',s)[0]
            except:      
                S = -1            
            try:         
                ms = re.findall('msCam(\d+)',s)[0]
            except:      
                ms = -1  
            return [int(date),int(H),int(M),int(S),int(ms)]
    tsFileList.sort(key=sort_key)
    print(f"get {len(tsFileList)} timestamps files")
    return tsFileList

def generate_ms_ts(tsFileList,save_path,temporal_downsampling=3):
    if not os.path.exists(save_path):
        ts_sessions=[]       
        for tsFile in tsFileList:
            datatemp=pd.read_csv(tsFile,sep = "\t", header = 0)
            ts_sessions.append(datatemp['sysClock'].values) 
        #         print(len((datatemp['sysClock'].values)))
        if len(tsFileList)>1:
            ts_all=np.hstack(ts_sessions)[::temporal_downsampling]#downsampled timestamps of all the blocks
            # remporally downsample for each video
            # [i[::3] for i in ts_sessions][0]
            ts_breakpoints=(np.where(np.diff(ts_all)<0)[0]).tolist()# ts_breakpoints means the location of the lagest timepoint of each session
    #        print(ts_breakpoints)
            ends = np.add(ts_breakpoints,1)
            starts = np.insert(ends,0,0)
            ts_blocks=[]
            for start,end in zip(starts,ends):
                ts_blocks.append(ts_all[start:end])            
            ts_blocks.append(ts_all[ts_breakpoints[-1]+1:])# append the last block[:]
        elif len(tsFileList)==1:
            ts_blocks = ts_sessions            
        ms_ts=np.array(ts_blocks)
        with open(save_path,'wb') as output:
            pickle.dump(ms_ts,output,pickle.HIGHEST_PROTOCOL)
    else:
        with open(save_path,'rb') as f:
            ms_ts = pickle.load(f)                             
    print(f'concatenated timestamp of miniscope_video is located at {save_path}')
def add_ms_ts2mat(ms_ts_path,mat_path):
    with open(ms_ts_path,"rb") as f:
        ms_ts = pickle.load(f)
    ms_mat = loadmat(mat_path)
    ms_mat['ms']['ms_ts']=ms_ts
    spio.savemat(mat_path,{"ms":ms_mat["ms"]})
    del ms_mat
    del ms_ts
def find_close_fast(arr, e):    
    start_time = datetime.datetime.now()            
    low = 0    
    high = len(arr) - 1    
    idx = -1     
    while low <= high:        
        mid = int((low + high) / 2)        
        if e == arr[mid] or mid == low:            
            idx = mid            
            break        
        elif e > arr[mid]:            
            low = mid        
        elif e < arr[mid]:            
            high = mid     
    if idx + 1 < len(arr) and abs(e - arr[idx]) > abs(e - arr[idx + 1]):        
        idx += 1            
    use_time = datetime.datetime.now() - start_time    
    return idx
def find_close_fast2(arr,e):
    np.add(arr,e*(-1))
    min_value = min(np.abs(np.add(arr,e*-1)))
    locations = np.where(np.abs(np.add(arr,e*-1))==min_value)
    return locations[0][0]
#    return arr[idx],idx, use_time.seconds * 1000 + use_time.microseconds / 1000
def _angle(dx1,dy1,dx2,dy2):
#def _angle(v1,v2)    #v1 = [0,1,1,1] v2 = [x1,y1,x2,y2]
#    dx1 = v1[2]-v1[0]
#    dy1 = v1[3]-v1[1]
#    dx2 = v2[2]-v2[0]
#    dy2 = v2[3]-v2[1]

    angle1 = math.atan2(dy1, dx1) * 180/math.pi
    if angle1 <0:
        angle1 = 360+angle1
    # print(angle1)
    angle2 = math.atan2(dy2, dx2) * 180/math.pi
    if angle2<0:
        angle2 = 360+angle2
    # print(angle2)
    return abs(angle1-angle2)
# dx1 = 1,dy1 = 0,this is sure ,because we always want to know between the varial vector with vector[0,1,1,1]
#%%draw scale
def scale(video_path):    
    _,coords_in_pixel = Video(video_path).draw_rois(aim='scale')
    print(coords_in_pixel[0][1],coords_in_pixel[0][0])
    distance_in_pixel = np.sqrt(np.sum(np.square(coords_in_pixel[0][1]-coords_in_pixel[0][0])))
    distance_in_cm = 40 #int(input("直线长(in cm)： "))
    print(f"{distance_in_pixel} pixels in {distance_in_cm} cm")
    unit = "cm/pixel"
    return (distance_in_cm/distance_in_pixel,unit)
def speed(X,Y,T,s):
    speeds=[0]
    speed_angles=[0]
    for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
        distance = np.sqrt(delta_x**2+delta_y**2)
        speeds.append(distance*s/delta_t)
        speed_angles.append(_angle(1,0,delta_x,delta_y))
    return pd.Series(speeds),pd.Series(speed_angles) # in cm/s

def direction(Head_X,Head_Y,Body_X,Body_Y,Tail_X,Tail_Y):
    headdirections=[] # head_c - body_c
    taildirections=[]
    arch_angles=[]
    for x1,y1,x2,y2,x3,y3 in zip(Head_X,Head_Y,Body_X,Body_Y,Tail_X,Tail_Y):
        hb_delta_x = x1-x2 # hb means head to body
        hb_delta_y = y1-y2
        headdirection = _angle(1,0,hb_delta_x,hb_delta_y)
        headdirections.append(headdirection)
        tb_delta_x = x3-x2
        tb_delta_y = y3-y2
        taildirection = _angle(1,0,tb_delta_x,tb_delta_y)
        taildirections.append(taildirection)
        arch_angle = abs(headdirection - taildirection)
        if arch_angle>180:
            arch_angle = 360-arch_angle
        arch_angles.append(arch_angle)
    return pd.Series(headdirections), pd.Series(taildirections), pd.Series(arch_angles)        
    
        
if __name__ == "__main__":
   video_path = r"X:/miniscope/20191028/191172/191172A-20191028-202245DeepCut_resnet50_linear_track_40cm_ABSep26shuffle1_500000_labeled.mp4"
   s = scale(video_path)
   
    #%% 产生ms_ts2.pkl 是ms_ts.pkl的纠正
#    dateDir=r"X:\miniscope\20191*\191172"
#    save_path=r'Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms_ts2.pkl'
#    tsFileList=generate_tsFileList(dateDir)
#    print(tsFileList)
#    generate_ms_ts(tsFileList,save_path)
    #%% 将产生的ms_ts2.pkl 合并到对应的ms.mat中去
#    ms_ts_path = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms_ts2.pkl"
#    mat_path=r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191172\20191110_160835_all\ms.mat"
#    add_ms_ts2mat(ms_ts_path,mat_path)