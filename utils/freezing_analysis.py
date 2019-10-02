from mylab.video.Cvideo import Video 
from mylab.exps.cfc import video_to_csv as v2c
from mylab.csvs.Ccsv import Csv
import glob,os,sys
import concurrent.futures
import subprocess
import csv

videolists = glob.glob(r'C:\Users\Sabri\Desktop\test\*.mp4')
coordinates = os.path.join(os.path.dirname(videolists[0]),'xy.txt')

powershell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
##print(sys.argv[0])
extract_ts = os.path.join(os.path.dirname(sys.argv[0]),'extract_ts.ps1')

if len(videolists)==0:
    print("there are no video choosed")
    sys.exit()
elif not os.path.exists(coordinates):
    print("please draw the travel region.")
    _,_ = Video(videolists[0]).draw_roi()
else:
    pass

freezing_stat = {}
threshold = 0.02
for video in videolists:
    ts_video = os.path.splitext(video)[0]+'_ts.txt'
    extension = os.path.splitext(video)[1]
    csv_video = os.path.splitext(video)[0]+'_freezing.csv'
    print(csv_video)
    if not os.path.exists(ts_video):
        subprocess.call([powershell,"-ExecutionPolicy","Unrestricted","-File",extract_ts,video,extension])
        print("we are extracting timestamps")
    if not os.path.exists(csv_video):
        v2c(video,Interval_number=2,diff_gray_value=30,show = True)
        print("we are caclulating the pixel change percentage frame by frame")
    
    freezing_stat[os.path.basename(video)]=Csv(csv_video).freezing_percentage(threshold=threshold,start=0,stop=300,show_detail=True)
        

with open(os.path.join(os.path.dirname(videolists[0]),'freezing_stat.csv'),'w',newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['video_id','freezing%',threshold])
    for row in freezing_stat.items():
        writer.writerow(row)
        print("threshold is:",threshold,row)







