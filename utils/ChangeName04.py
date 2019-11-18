import os
import glob
video_pathes =glob.glob(r"Y:\zhangna\3. EPM and open field\open_field\*\*.mp4")
for video in video_pathes:
    newname = os.path.split(video)[0]+"-"+os.path.split(video)[1]
    os.rename(video,newname)