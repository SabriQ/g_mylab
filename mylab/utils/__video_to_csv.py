'''
author: qiushou
data: 2018/12/16
module name: video_to_csv
aim
    input %video_path% output a csv named with video_name containing
        Frame_No, ts(ms),Num(changed_pixel),percentage(changed_pixel)
global arguments 
    1 %video_path%: video captured in grayscale model
    2 %Interval_number%: between two frame to compare the pixel
    2 %diff_gray_value%:, difference between two pixels less than which is defined the same
    
procedure
    1 load the *_ts.txt file as a dataframe containing all the timestamps and relative Frame_No
    2 read video, save interleaved frames in gray value, and Frame_No picked out
    3 calculate the changed pixel number and percentage and set Frame_No, changed_pixel_num and changed_pixel_percentage as dataframe
    4 merge two dataframes on 'Frame_No' and sort them by the Frame_No as ascending
    5 output a csv named with video_name
    
'''
import cv2
import pandas as pd

def video_to_csv (video_path,Interval_number=3,diff_gray_value=25):
    
    ts = pd.read_csv(video_path.replace('.asf','_ts.txt'), sep=" ",encoding = "utf-16",header='infer',names=['ts(ms)'])

    frame_index = pd.DataFrame({'Frame_No':list(range(1,len(ts)+1))})
    ts.insert(0,'Frame_No',frame_index.pop('Frame_No'))
    print(video_path.replace('.asf','_ts.txt')+'Frame Number & timestamps are loaded sucessfully \nvideo is processing frame by frame')

    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_No = []
    frame_count = 1
    
    while(1):
        ret,frame = cap.read()
        if ret == True:
            if frame_count%Interval_number == 1:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_No.append(frame_count)
                frames.append(frame_gray)
                #print(f'the {frame_count}th frame is picked out')
            frame_count = frame_count +1
        else :
            break
    #print('end')

    cap.release()
    reverse_changed_pixel_num = []
    reverse_changed_pixel_percentage = []
    
    width, height = frames[1].shape
    total_pixel_num = width*height
    
    for i in range(len(frames),1,-1):
       
        judge = cv2.absdiff(frames[i-1],frames[i-2])
        changed_pixel = sum(sum(judge > diff_gray_value )) 
        changed_pixel_percentage = changed_pixel*100/total_pixel_num
        #print(f'reverse changed_pixel,changed_pixel_percentage are {changed_pixel},{changed_pixel_percentage}')
        reverse_changed_pixel_num.append(changed_pixel)
        reverse_changed_pixel_percentage.append(changed_pixel_percentage)
    reverse_changed_pixel_num.append(0)
    reverse_changed_pixel_percentage.append(0)
    
    changed_pixel_num = reverse_changed_pixel_num[::-1]
    changed_pixel_percentage = reverse_changed_pixel_percentage[::-1]
    #print(len(changed_pixel_num),len(changed_pixel_percentage))
    
    dataframe = pd.DataFrame({'Frame_No':frame_No,'Num':changed_pixel_num,'percentage':changed_pixel_percentage})
        
    dataframe = pd.merge(ts,dataframe,on = 'Frame_No',how="outer").sort_values(by="Frame_No",ascending = True)
    
    
    dataframe.to_csv(video_path.replace(video_path.split('.')[-1],'csv'),index = False,sep = ',')

    print(video_path+' finish processing \nand saving of Frame_number, timestamps, chaged pixel number and percentage.')
    return 0    


#video_path = r'C:\Users\Sabri\Desktop\video_analyze\181108191701Cam-1.asf'
video_path = r'Y:\GUEST\czh\1130\181130205250Cam-1.asf'

video_to_csv(video_path)

