import os
video_path = r'Y:\Qiushou\2_Novel-context recognition\20180706_chs\avi'
for i in os.listdir(video_path):    
    if '0706' in i:
        newname = os.path.join(video_path,i.replace('_','_day1_'))
        os.rename(os.path.join(video_path,i),newname)
    
    elif '0707' in i:
        newname = os.path.join(video_path,i.replace('_','_day2_'))
        os.rename(os.path.join(video_path,i),newname)
##    elif '190507' in i:
##        newname = os.path.join(video_path,i.replace('_','_day3_'))
##        os.rename(os.path.join(video_path,i),newname)
##    elif '190508' in i:
##        newname = os.path.join(video_path,i.replace('_','_day4_'))
##        os.rename(os.path.join(video_path,i),newname)
##    elif '190509' in i:
##        newname = os.path.join(video_path,i.replace('_','_day5_'))
##        os.rename(os.path.join(video_path,i),newname)
##    elif '190510' in i:
##        newname = os.path.join(video_path,i.replace('_','_day6_'))
##        os.rename(os.path.join(video_path,i),newname)
##    elif '190511' in i:
##        newname = os.path.join(video_path,i.replace('_','_day7_'))
##        os.rename(os.path.join(video_path,i),newname)
