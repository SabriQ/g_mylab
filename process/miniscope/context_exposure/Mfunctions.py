from mylab.Cvideo import Video
import csv
import re,os
import pickle
import pandas as pd
import numpy as np

def starts_firstnp_stops(logfilepath):
    print("FUN:: starts_firstnp_stops")
    if not os.path.exists(logfilepath):
        with open(logfilepath,'w',newline="",encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["video","start","first-np","mark_point","stop"])

    def mark_start_firstnp_stop(video):
        videoname = video

        key = str(re.findall('\d{8}-\d{6}',video)[0])
        print("video key is %s"%key)
        led_log = pd.read_csv(logfilepath)
        keys = led_log["video"].apply(lambda x:re.findall('\d{8}-\d{6}',x)[0])
        
        if not key in list(keys):
            start,first_np,stop = Video(video).check_frames()
            with open(logfilepath,'a',newline='\n',encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([videoname,start,first_np,1,stop]) # 可能会手动修改mark_point 1 为 2
            return videoname,start,first_np,1,stop
        else:
            index = keys[keys.values==key].index[0]
            print("the %s row of logfilepath" %index)
            return list(led_log.iloc[index])
            print("%s has marked start first_np and stop" %video)
    
    return mark_start_firstnp_stop

def save_behave_pkl(
    behavevideo
    ,Result_dir
    ,logfilepath = r"C:\Users\qiushou\OneDrive\miniscope_2\202016\starts_firstnp_stops.csv"
    ):
    """
    behavebideo
    logfilepath
    Result_dir: the path of CNMFe result directory
    """
    key = str(re.findall('\d{8}-\d{6}',behavevideo)[0])
    mark = starts_firstnp_stops(logfilepath)

    _,start,first_np,mark_point,stop = mark(behavevideo)
    
    # index log file
    behave_log =[i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*log*")) if key in i][0]
    log = pd.read_csv(behave_log,skiprows=3)
    behavelog_time = log.iloc[:,12:]-min(log["P_nose_poke"])
    behavelog_info = log.iloc[:,:6]
    print("correct 'behavelog_time' when the first_np as 0")

    # index track file
    behave_track = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*DLC*h5")) if key in i][0]    
    track = pd.read_hdf(behave_track)
    behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                 columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
    
    
    # index timestamps file
    behave_ts = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*_ts.txt*")) if key in i][0]
    ts = pd.read_table(behave_ts,sep='\n',header=None,encoding='utf-16-le')
    
    # aligned log_time and behave video_time
    if mark_point  == 1:
        delta_t = ts[0][first_np-1]-behavelog_time["P_nose_poke"][0]
    
    ## 这里有时候因为first-np的灯刚好被手遮住，所以用第二个点的信号代替，即第一次enter_ctx的时间
    if mark_point == 2:
        delta_t = ts[0][first_np-1]-behavelog_time["P_enter"][0]

    behave_track['be_ts']=ts[0]-delta_t

    print("correct 'be_ts' when the first_np as 0")
    # index in_context
    print(behavevideo)
    in_context_mask,in_context_coords=Video(behavevideo).draw_rois(aim="in_context",count = 1)

    # index in_lineartrack
    in_lineartrack_mask,in_lineartrack_coords=Video(behavevideo).draw_rois(aim="in_lineartrack",count = 1)

    result = {"behavevideo":[behavevideo,key,start,first_np,mark_point,stop]
              ,"behavelog_time":behavelog_time
              ,"behavelog_info":behavelog_info
              ,"behave_track":behave_track
              ,"in_context_mask":in_context_mask[0]
              ,"in_context_coords":in_context_coords[0]
             ,"in_lineartrack_mask":in_lineartrack_mask[0]
             ,"in_lineartrack_coords":in_lineartrack_coords[0]}

    savename = os.path.join(Result_dir,"behave_"+str(key)+".pkl")
    with open(savename,'wb') as f:
        pickle.dump(result,f)
    print("%s get saved"%savename)