import cv2
import numpy as np
import pandas as pd
import os
import re
from correct_videotrack import correct


class Video():

    def __init__(self,video_path):
        self.video_path = video_path		 
        self.video_name = os.path.basename(self.video_path)
        
        extension = os.path.splitext(self.video_path)[-1]
        abs_prefix = os.path.splitext(self.video_path)[-2]
        
        self.xy = os.path.dirname(self.video_path)+'\\'+'xy.txt'
        self.led_xy = os.path.dirname(self.video_path)+'\\'+'led_xy.txt'
        
##        if os.path.splitext(self.video_path)[-1] == '.asf':
        self.mask_path = abs_prefix + '_mask.png'
        self.masked_path = abs_prefix + '_masked.png'
        self.maskedvideo_path = abs_prefix + 'masked.asf'
        self.videots_path = abs_prefix + '_ts.txt'
        self.videotrack_path = abs_prefix+'_tracking.csv'
        self.videofreezing_path = abs_prefix + '_freezing.csv'

        self.sum_path = abs_prefix + '_sum.csv'            
              
    def correct(self):
##        try:
##            from correct_videotrack import correct
##        except:
##            print("please add module 'correct_videotrack' to your PATH")
##
        correct(self.video_path)
    def play (self):
        print(
            '''
            请注意使用英文输入法！
            "q":退出播放
            "f":快速播放，不丢帧
            "d":慢速播放，不丢帧

            ''')
        cap = cv2.VideoCapture(self.video_path)
        wait= 30
        step = 1
        while (1):
            ret,frame = cap.read()
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            cv2.imshow('video',gray)
            if cv2.waitKey(wait) & 0xFF == ord('q'):
                break
            if cv2.waitKey(wait) & 0xFF == ord('f'):
                if wait > 1:
                    wait = wait -step
                else:
                    print("it has played at the fast speed without dropping any frame")
            if cv2.waitKey(wait) & 0xFF == ord('d'):
                wait = wait + step
        cap.release()
        cv2.destroyAllWindows()
        

            
    def draw_roi(self,img,event = 0):
        print("event = 0 for freezing ,event = 1 for led-on mark")
        ix = []
        iy = []
        rows,cols = img.shape
        black_bg = np.zeros((rows,cols),np.uint8)
        
        def draw_polygon(event,x,y,flags,param):
            if event == cv2.EVENT_LBUTTONDOWN:
                ix.append(x)
                iy.append(y)
            if len(ix) == 2:
                cv2.line(img,(ix[0],iy[0]),(ix[1],iy[1]),255,2)
                #cv2.line(img,(ix[1],iy[1]),(x,y),255,4)
            elif len(ix) == 3:
                cv2.line(img,(ix[0],iy[0]),(ix[1],iy[1]),255,2)
                cv2.line(img,(ix[1],iy[1]),(ix[2],iy[2]),255,2)
            elif len(ix) == 4:
                pts=np.array([[ix[0],iy[0]],[ix[1],iy[1]],[ix[2],iy[2]],[ix[3],iy[3]]],np.int32)
                cv2.fillPoly(img,[pts],255)
                cv2.fillPoly(black_bg,[pts],255)           

        def draw_rectangle(event,x,y,flags,param):
##            print(x,y)
            if event == cv2.EVENT_LBUTTONDOWN:
                ix.append(x)
                iy.append(y)
            
                cv2.rectangle(img,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                
        if event == 0: # 0 for freezing
            if os.path.exists(self.xy):
                print('xy.txt existed')
                f = open(self.xy)
                coord = f.read()
                f.close()
                coord_x = coord.split('\n')[0]
                coord_y = coord.split('\n')[1]
    ##            print(coord_x.split(',')[3].replace(']',''))

                ix.append(int(coord_x.split(',')[0][3:6]))
                ix.append(int(coord_x.split(',')[1]))
                ix.append(int(coord_x.split(',')[2]))
                ix.append(int(coord_x.split(',')[3].replace(']','')))

                iy.append(int(coord_y.split(',')[0][3:6]))
                iy.append(int(coord_y.split(',')[1]))
                iy.append(int(coord_y.split(',')[2]))
                iy.append(int(coord_y.split(',')[3].replace(']','')))
##                f.close()
    ##            print(ix,iy)
                pts = np.array([[ix[0],iy[0]],[ix[1],iy[1]],[ix[2],iy[2]],[ix[3],iy[3]]],np.int32)
##                cv2.fillPoly(img,[pts],255)
                cv2.fillPoly(black_bg,[pts],255)                
                return cv2.bitwise_not(black_bg)
            else:
                print("xy.txt does not existed")     
                    
                cv2.namedWindow('drawRoi')                
                cv2.setMouseCallback('drawRoi',draw_polygon,)
                while(1):
                    cv2.imshow('drawRoi',img)
                    key = cv2.waitKey(10) & 0xFF
                    if key == ord('s'):
                        
                        black_bg_inv = cv2.bitwise_not(black_bg)
                        #cv2.imwrite(self.mask_path,black_bg_inv)
                        
                        cv2.destroyWindow('drawRoi')
                        
                        f = open(self.xy,'w+')
                        f.write(f'x:{ix}\ny:{iy}')
                        f.close()
                        print("xy.txt is created !")
                        return black_bg_inv             
                        
                    elif key == ord('q'):
                        cv2.destroyWindow('drawRoi')
                        break
        if event == 1: # 1 for led on
            if os.path.exists(self.led_xy):
                print('led_xy existed')
                f = open(self.led_xy)
                coord = f.read()
                f.close
                coord_x = re.split('[\n:\[\]xy]',coord)[3]
                coord_y = re.split('[\n:\[\]xy]',coord)[8]
                ix.append(int(coord_x))
                iy.append(int(coord_y))
                return ix,iy
            else:
                print('Find the led location please')
                cv2.namedWindow('drawRoi')
                cv2.setMouseCallback('drawRoi',draw_rectangle)
                
                while(1):
                    cv2.imshow('drawRoi',img)
                    key = cv2.waitKey(10) & 0xFF
                    if key == ord('s'):
                        #cv2.imwrite(self.mask_path,black_bg_inv)
                        cv2.destroyWindow('drawRoi')

                        f = open(self.led_xy,'w+')
                        f.write(f'x:{ix}\ny:{iy}')
                        f.close

                        print('led_xy.txt is created')                        
                        return ix,iy               
                        
                    elif key == ord('q'):
                        cv2.destroyWindow('drawRoi')
                        break
              
       
    
        
    
    def _video_to_csv(self,Interval_number=1,show = True):
        
        cap = cv2.VideoCapture(self.video_path)
        frame_count = 1

        while(1):
            ret,frame = cap.read()
            if frame_count ==1:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                
                mask = self.draw_roi(img,event = 0)   
            frame_count += 1
            if ret == True:
                if (frame_count-1)%Interval_number == 0:
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame_gray = cv2.add(mask,frame_gray)
##                    if frame_count ==1:                    
##                        cv2.imwrite(self.masked_path,frame_gray)
                    if show:
                        if frame_count <=100:
                            frame_count = frame_count +1
                            cv2.imshow(self.masked_path,frame_gray)
                            cv2.waitKey(10)
                            
##                    frames.append(frame_gray)
                    
                    yield frame_gray
                    #print(f'the {frame_count}th frame is picked out')               
            else :
                break
        cap.release()
        cv2.destroyAllWindows()
        
    def video_to_cvs(self,Interval_number=1,diff_gray_value=30,show = True):
        if os.path.exists(self.videots_path):
            ts = pd.read_csv(self.videots_path, sep=" ",encoding = "utf-16",header =None,names=['ts(s)'])
            ts['Frame_No'] = list(range(1,len(ts)+1))
        else:
            print ('there is no timestamp file')

        print(self.video_name+' Frame Number & timestamps are loaded sucessfully \nvideo is processing frame by frame...')

        frame_grays = self._video_to_csv(Interval_number = Interval_number,show = show)       

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
        dataframe.to_csv(self.videofreezing_path,index = False,sep = ',')
        print(self.video_path+r' finish processing \nand saving of Frame_number, timestamps, chaged pixel number and percentage(%).')



    def mark_led_on (self,*args,threshold1 = 240,threshold2 = 50):
        '''
        两种模式
        第一种是无输入，video.mark_led_on()，会自动识别 roi内的led,像素值阈值（threshold1）为240，
        达到像素阈值的个数阈值（threshold2）为50,return a list of "led_on_frame"
        第二种为有输入，video.mark_led_on(61,355,700),程序会自动跳到数字指定的帧，然后mannually confirm
        'a':后退一帧
        'f':前进一帧
        's':保存当前帧数到结果中
        'n':下一个指定帧
        '''
        font = cv2.FONT_HERSHEY_COMPLEX
        cap = cv2.VideoCapture(self.video_path)
        frame_No = 1
        led_ons = args
##        threshold1 = 240 #判断像素为led_on的像素阈值
##        threshold2 = 50 # 判断led on 的 roi 内像素值大于 threshold1 的像素个数的阈值
        ret,frame = cap.read()
        frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        ix,iy = self.draw_roi(frame_gray,event = 1)
        print('Got the led location')
  
##        pixel_sum_base = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)]))
##        def show_frame (frame_No,frame):
##            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
##            frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
##            cv2.imshow('led location',frame_gray)
        led_on_frame = []
        if len(led_ons):
            print("please press 'a' or 'f' to confirm the first led_on frame, and 's' to save the frame_No!")
            for i in np.arange(1,len(led_ons)+1):
                frame_No = led_ons[i-1]
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)  
                ret,frame = cap.read()
                frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))
                cv2.rectangle(frame_gray,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                cv2.putText(frame_gray,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
                cv2.imshow('led location',frame_gray)
                while 1:
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('f'):                        
                        frame_No +=1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                        ret,frame = cap.read()
                        if ret:
                            frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                            judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))                      
                                                    
                            cv2.rectangle(frame_gray,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                            cv2.putText(frame_gray,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
                            cv2.imshow('led location',frame_gray)
                            print(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)])
                        else:
                            frame_No = frame_No-1
                            print(f'frame_No {frame_No} is the last frame')
                        
                    if key == ord('a'):
                        frame_No = frame_No - 1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-2)
                        ret,frame = cap.read()
                        frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                        judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))
                        
                        cv2.rectangle(frame_gray,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                        cv2.putText(frame_gray,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
                        cv2.imshow('led location',frame_gray)
                        print(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)])
                        
                    if key == ord('s'):
                        led_on_frame.append(frame_No)
                        print(f'{frame_No} frame is saved')              
                        break
                    if key == ord('n'):
                        led_ons.pop(i-1)
                        print(f'{frame_No} frame is thrown')
                        break
        else:
            print('finding the first frame where led on...')
            while(1):
                ret,frame = cap.read()
                if ret:
                    frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                    judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))
                    if judge > threshold2:
                        led_on_frame.append(frame_No)
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No+99)
                        frame_No = frame_No + 99
                    else:                    
                        frame_No = frame_No+1
                
                
##                    cv2.rectangle(frame_gray,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
##                    cv2.putText(frame_gray,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
##                    cv2.imshow('led location',frame_gray)                                             
##    ##            
##                    if cv2.waitKey(1) & 0xFF == ord('q'):
##                        break
                else:
                    print(f'it has totally {frame_No-1} frame')
                    break
        return led_on_frame
        cap.release()
        cv2.destroyAllWindows()
                
                
               
if __name__ == '__main__':

    video = Video (r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\2019031100002.AVI')
    video.video_to_cvs()
    

