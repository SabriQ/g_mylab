from mylab.Cvideo import Video
import csv
import re,os
import pandas as pd
import numpy as np

def starts_firstnp_stops(logfilepath):

    if not os.path.exists(logfilepath):
        with open(logfilepath,'w',newline="",encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["video","start","first-np","mark_point","stop"])

    def mark_start_firstnp_stop(video):
        videoname = video

        key = str(re.findall('\d{8}-\d{6}',video)[0])
        print(key)
        led_log = pd.read_csv(logfilepath)
        keys = led_log["video"].apply(lambda x:re.findall('\d{8}-\d{6}',x)[0])
        
        if not key in list(keys):
            start,first_np,stop = Video(video).check_frames()
            with open(logfilepath,'a',newline='\n',encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([videoname,start,first_np[0],1,stop]) # 可能会手动修改mark_point 1 为 2
            return videoname,start,first_np,mark_point,stop
        else:
            index = keys[keys.values==key].index[0]
            print(index)
            return list(led_log.iloc[index])
            print("%s has marked start first_np and stop" %video)
    
    return mark_start_firstnp_stop

