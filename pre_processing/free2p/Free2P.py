# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 11:00:43 2019

@author: Sabri
"""
import os,re
import datetime
import subprocess
import sys
#from Cfile import Free2pFile
def sort_key(s):
    if s:
        try:
            order = re.findall('^(\d+)', s)[0]
        except:
            order = -1
        return [int(order)]
#dir_path = r"Y:\Qiushou\13_twophoto\2019-11-15\wjn\192574A1"
dir_path = sys.argv[1]
filenames = [i for i in os.listdir(dir_path) if "concat" not in i]
filenames.sort(key=sort_key)

def date2seconds(s):
    if s:
        try:
            S = int(datetime.datetime.strptime(re.findall('\d{4}-\d+-\d+ \d+-\d+-\d+',s)[0],"%Y-%m-%d %H-%M-%S").timestamp())
            MS = int(re.findall('\d{4}-\d+-\d+ \d+-\d+-\d+\.(\d+)',s)[0])
        except:
            print(f"{s} has wrong format")
        return S+(MS/1000)

#time_points = [datetime.datetime.strptime(re.findall('\d{4}-\d+-\d+ \d+-\d+-\d+\.\d+',i)[0],"%Y-%m-%d %H-%M-%S") for i in filenames]
time_points = [date2seconds(i) for i in filenames]

durations = [time_points[i+1]-time_points[i] for i in range(len(time_points)-1)]
concat_txt = os.path.join(dir_path,'concat.txt')
concat_video = os.path.join(dir_path,"concat.mp4")

i=0
for filename,duration in zip(filenames[0:-1],durations):
    info1 = "file "+f"'{os.path.join(dir_path,filename)}'"
    info2 = duration
    i=i+1
    with open(concat_txt,'a+') as f:
        f.write(f"{info1}\nduration {info2}\n")
    print(f"\r{i}/{len(durations)} frames.",end=" ")

last_info = "file "+f"'{os.path.join(dir_path,filenames[-1])}'"
with open(concat_txt,'a+') as f:
        f.write(f"{last_info}\n")
        f.write(f"duration {durations[-1]}\n")
        f.write(f"{last_info}\n")

print("concat.txt is generated!")

"""
this is for concatenating tifs to video by ffmpeg
    ffmpeg -f concat -safe 0 -i Desktop/input.txt -vsync vfr -pix_fmt yuv420p Desktop/output.mp4
"""
command=["ffmpeg"
        ,"-f","concat"
        ,"-safe","0"
        ,"-i",concat_txt
        ,"-vsync","vfr"
        ,"-pix_fmt","yuv420p"
        ,concat_video]
child = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
out = child.communicate()[1]
print(f"\r{out}",end=" ")
child.wait()
print("concatenation finished!")