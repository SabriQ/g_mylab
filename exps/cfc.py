from mylab.video.Cvideo import Video
import time
import os
import sys
import concurrent.futures
import glob
import pandas as pd
import cv2

sys.path.append(r'C:/Users/Sabri/OneDrive/Document/python/decorator')

##dir_path = sys.argv[1] # 接收系统传参的时候可以用，一般是在bash或者powershell中执行命令的时候使用


##freezing_analysis_for_videos(dir_path,'.asf')



def _video_to_csv(videoPath,Interval_number=1,show = True):
    video = Video(videoPath)
    mask= video.mask_generate()
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    cap = cv2.VideoCapture(video.video_path)
    frame_count =0
    font = cv2.FONT_HERSHEY_COMPLEX
    while(1):
        frame_count += 1
        ret,frame = cap.read()        
        if ret == True:
##            print(frame_count)
            if (frame_count-1)%Interval_number == 0:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_gray = cv2.add(mask,frame_gray)
##                    if frame_count ==1:                    
##                        cv2.imwrite(video.masked_path,frame_gray)
                if show:
                    if frame_count <=100:
                        cv2.putText(frame_gray,f'frame_No:{frame_count}',(10,15), font, 0.5, (0,0,0))
                        cv2.imshow(video.masked_path,frame_gray)                    
                        cv2.waitKey(1)
                        
##                    frames.append(frame_gray)
                
                yield frame_gray
                #print(f'the {frame_count}th frame is picked out')               
        else :
            break
        
        
    cap.release()
    cv2.destroyAllWindows()
    
def video_to_csv(videoPath,Interval_number=3,diff_gray_value=30,show = True):
    video = Video(videoPath)
    if os.path.exists(video.videots_path):
        ts = pd.read_csv(video.videots_path, sep=" ",encoding = "utf-16",header =None,names=['ts(s)'])
        ts['Frame_No'] = list(range(1,len(ts)+1))
    else:
        print(video.videots_path)
        sys.exit('there is no timestamp file')
    

    frame_grays = _video_to_csv(videoPath,Interval_number = Interval_number,show = show)
    
    print(video.video_name+' Frame Number & timestamps are loaded sucessfully \nvideo is processing frame by frame...')
    changed_pixel_percentages = []
    Frame_No = []
    for index,frame_gray in enumerate(frame_grays,1):
        Frame_No.append(1+(index-1)*Interval_number)
        if index == 1:
            width, height = frame_gray.shape
            total_pixel = width*height
            temp1 = frame_gray
            changed_pixel_percentages.append(0)
        else :
            temp2 = frame_gray
            judge = cv2.absdiff(temp2,temp1) > diff_gray_value
            changed_pixel_percentage = sum(sum(judge))/total_pixel*100
            changed_pixel_percentages.append(changed_pixel_percentage)                
            temp1 = temp2

    dataframe = pd.DataFrame({'Frame_No':Frame_No,'percentage':changed_pixel_percentages},index=None)
    dataframe = pd.merge(ts,dataframe,on = 'Frame_No',how="outer").sort_values(by="Frame_No",ascending = True)    
    dataframe.to_csv(video.videofreezing_path,index = False,sep = ',')
    print(video.video_path+r' finish processing \nand saving of Frame_number, timestamps, chaged pixel number and percentage(%).')




    
    

if __name__ == '__main__':
    
##    videolists = glob.glob(r'Y:\ChenHaoshan\11. fiber photometry\video\*\*.AVI',recursive = False)
####    freezing_analysis(videolists[1])
##    videolists = [i for i in videolists if '20181020' not in i]
##    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
##        for i,_ in enumerate(executor.map(video_to_cvs,videolists),1):
##            print (f'{i}/{len(videolists)} is done')

    video_to_csv(r'Y:\zhangna\vgat-gain_function_acquisition\20190718\Video\20190718\196535_190718130808Cam-1.asf')
