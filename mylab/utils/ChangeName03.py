import glob
import os

zdat_names = glob.glob(r'Y:\zhangna\vgat-gain_function_acquisition\20190718\*\*.zdat')
video_names = glob.glob(r'Y:\zhangna\vgat-gain_function_acquisition\20190718\Video\*.asf')

for zdat_name in zdat_names:
    mouse_id = zdat_name.split('\\')[-2]    
    recording_name = os.path.basename(zdat_name).split('.')[-2]
    
    for video_name in video_names:
        if recording_name[0:-1] in video_name:
            newvideoname = video_name.replace(recording_name,mouse_id+'_'+recording_name)
            os.rename(video_name,newvideoname)
