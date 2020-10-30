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
import seaborn as sns
from scipy.ndimage import gaussian_filter1d

def save_pkl(result,result_path):
    with open(result_path,'wb') as f:
        pickle.dump(result,f)
    print("result is saved at %s"% result_path)

def load_pkl(result_path):
    with open(result_path,'rb') as f:
        result = pickle.load(f)
    print("result is loaded")
    return result
    
def load_mat(filename):
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

def load_hdf5_cnmf(hdf5_Path):
    try:
        from caiman.source_extraction.cnmf.cnmf import load_CNMF
    except:
        print("please activate env caiman")
        sys.exit()
    print("loading hdf5 file...")
    cnm = load_CNMF(hdf5_Path)
    print("%s is successfully loaded."% hdf5_Path)
    return cnm


def generate_tsFileList(dateDir=r"X:\miniscope\20191028\191172"):
    """
    for a specified miniscope data directory, generate a sorted list of timestamp file name
    """
    tsFileList = glob.glob(os.path.join(dateDir,"H*/timestamp.dat"))
    #tsFileList = [i for i in tsFileList if "2019111" not in i]
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
    """
    concatenate several timestamp files as one ms_ts.pkl
    """
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

def angle(dx1,dy1,dx2,dy2):
#def angle(v1,v2)    #v1 = [0,1,1,1] v2 = [x1,y1,x2,y2]
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

def scale(video_path,distance):
    print("the line you draw are as long as %s cm"%distance)
    _,coords_in_pixel = Video(video_path).draw_rois(aim='scale')
    print(coords_in_pixel[0][1],coords_in_pixel[0][0])
    distance_in_pixel = np.sqrt(np.sum(np.square(np.array(coords_in_pixel[0][1])-np.array(coords_in_pixel[0][0]))))
    distance_in_cm = distance #int(input("直线长(in cm)： "))
    s = distance_in_cm/distance_in_pixel
    print(f"{s} cm/pixel")
    return s

def speed(X,Y,T,s):
    speeds=[0]
    speed_angles=[0]
    for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
        distance = np.sqrt(delta_x**2+delta_y**2)
        if not delta_t==0:
            speeds.append(distance*s/delta_t)
        else:
            speeds.append(0)
        speed_angles.append(angle(1,0,delta_x,delta_y))
    return pd.Series(speeds),pd.Series(speed_angles) # in cm/s

def speed_optimize(speeds,method="gaussian_filter1d",sigma=3,length=12):
    """speeds: an iterable items
    """
    if method == "gaussian_filter1d": # default
        speeds = gaussian_filter1d(speeds,sigma)
        print("speed filter sigma is default to be 3")
    elif method == "slider":
        print("Slider length default to be 12. About 0.4s in 30fps behavioral video")
    elif method == "temporal_bin":
        print("bin_length default to be 12, meaning 12 frames in each temporal_bin")
    else:
        print("This is a warning because method is only available in ['gaussian_filter1d','slider','temporal_bin'].",
              " Here default to return gaussian_filter1d with sigma =3")
        return speed_optimize(X,Y,T,s,method="gaussian_filter1d",sigma=3)
        
    return speeds # in cm/s

def direction(Head_X,Head_Y,Body_X,Body_Y,Tail_X,Tail_Y):
    headdirections=[] # head_c - body_c
    taildirections=[]
    arch_angles=[]
    for x1,y1,x2,y2,x3,y3 in zip(Head_X,Head_Y,Body_X,Body_Y,Tail_X,Tail_Y):
        hb_delta_x = x1-x2 # hb means head to body
        hb_delta_y = y1-y2
        headdirection = angle(1,0,hb_delta_x,hb_delta_y)
        headdirections.append(headdirection)
        tb_delta_x = x3-x2
        tb_delta_y = y3-y2
        taildirection = angle(1,0,tb_delta_x,tb_delta_y)
        taildirections.append(taildirection)
        arch_angle = abs(headdirection - taildirection)
        if arch_angle>180:
            arch_angle = 360-arch_angle
        arch_angles.append(arch_angle)
    return pd.Series(headdirections), pd.Series(taildirections), pd.Series(arch_angles)
    
def rlc(x):
    name=[]
    length=[]
    
    for i,c in enumerate(x,0):
        if i ==0:
            name.append(x[0])
            count=1
        elif i>0 and x[i] == name[-1]:
            count += 1
        elif i>0 and x[i] != name[-1]:
            name.append(x[i])
            length.append(count)
            count = 1
    length.append(count)
    return name,length   

def rlc2(X):
    name=[]
    length=[]
    idx_min=[]
    idx_max=[]
    for i,x in enumerate(X,0):
        if i == 0:
            name.append(x)
            idx_min.append(i)
            count =1
        elif i>0 and x==name[-1]:
            count = count +1
        elif i>0 and x!=name[-1]:
            idx_max.append(i)
            idx_min.append(i)
            name.append(x)
            length.append(count)
            count=1
    length.append(count)
    idx_max.append(i)
    df = {"name":name,"length":length,"idx_min":idx_min,"idx_max":idx_max}
    return pd.DataFrame(df)         
    
def Standarization(df):
    """
    对matrix中的所有值一块进行standarization
    """
    temp_mean = np.mean(np.reshape(df.values,(1,-1))[0])
    temp_std = np.std(np.reshape(df.values,(1,-1))[0],ddof=1)
    Standarized_df = (df-temp_mean)/temp_std
    print("mean and std", temp_mean,temp_std)
    return Standarized_df,temp_mean,temp_std

def Normalization(df):
    """
    对matrix中的所有值一块进行 normalization
    """
    residual = np.max(np.reshape(df.values,(1,-1))[0])-np.min(np.reshape(df.values,(1,-1))[0])
#     residual = df.max().max()-df.min().min()
    minimum = np.min(np.reshape(df.values,(1,-1))[0])
    normalized_df = (df-minimum)/residual
    print("residual and minimum", residual,minimum)
    return normalized_df,residual,minimum

if __name__ == "__main__":
    print("done")
    #%%
#   video_path = r"X:/miniscope/20191028/191172/191172A-20191028-202245DeepCut_resnet50_linear_track_40cm_ABSep26shuffle1_500000_labeled.mp4"
#   s = scale(video_path)
   
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