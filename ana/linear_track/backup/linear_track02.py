
import glob
from mylab.exps.linear_track import *

behavior_readout = save_behavior_readout(result_file=r"C:\Users\Sabri\Desktop\program\data\linear_track_training\result.csv")
filelists = glob.glob(r"C:\Users\Sabri\Desktop\program\data\linear_track_training\*\*192232*")
filelists.sort(key=sort_key) 
for i in filelists:
    print(i)
    behavior_readout(i)