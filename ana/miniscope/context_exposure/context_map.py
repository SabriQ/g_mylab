import os,sys,glob,re
import pandas as pd
import numpy as np
from mylab.ana.miniscope.context_exposure.Cminiana import MiniAna as MA

file_pathes1 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_201033-finish\part*")
file_pathes2 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_201034-finish\part*")
file_pathes3 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_206551-finish\part*")
file_pathes4 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_206552-finish\part*")
file_pathes = file_pathes1+file_pathes2+file_pathes3+file_pathes4
file_pathes

sessions=[]
for file_path in file_pathes:
    print(os.path.dirname(file_path))
    sessions = sessions + glob.glob(os.path.join(file_path,"session*.pkl"))


def show_frame(session):
    mouse_id = re.findall("Results_(\d+)",session)[0]
    part = re.findall("part(\d+)",session)[0]
    session_num = re.findall("session(\d+).pkl",session)[0]
    if mouse_id == sys.argv[2] and part==sys.argv[1]:
        s = MA(session)
        if not s.exp == "hc":
            video_name = s.result["behavevideo"][0]
            if  "all_blank" in video_name :
                aim = re.findall(r"CDC-(.*)-%s"%mouse_id,video_name)[0]
                index=re.findall("\d{8}-\d{6}",video_name)[0]
                print(mouse_id,part,session_num,index)
                s.show_behaveframe(tracking=False)
            else:
                print("session not choosed")

        else:
            print("session not choosed")
    else:
        pass

if __name__ == '__main__':
    for session in sessions:
        show_frame(session)
    