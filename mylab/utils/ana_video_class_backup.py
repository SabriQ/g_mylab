import cv2
import numpy as np
import pandas as pd
import os

class Video():

    def __init__(self,video_path):
        self.video_path = video_path		 
        self.video_name = os.path.basename(self.video_path)
        
        extension = os.path.splitext(self.video_path)[-1]
        abs_prefix = os.path.splitext(self.video_path)[-2]
        
        self.xy = os.path.dirname(self.video_path)+'\\'+'xy.txt'
        
##        if os.path.splitext(self.video_path)[-1] == '.asf':
        self.mask_path = abs_prefix + '_mask.png'
        self.masked_path = abs_prefix + '_masked.png'
        self.maskedvideo_path = abs_prefix + 'masked.asf'
        self.videots_path = abs_prefix + '_ts.txt'
        self.videotrack_path = abs_prefix+'_tracking.csv'
        self.videofreezing_path = abs_prefix + '_freezing.csv'

        self.sum_path = abs_prefix + '_sum.csv'            
              

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
        
    def _draw_polygon(event,x,y,flags,param):
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
    def _draw_rectangle(event,x,y,flags,param):
        print(x,y)
        if event == cv2.EVENT_LBUTTONDOWN:
            ix.append(x)
            iy.append(y)
        if len(ix)==2:
            cv2.rectangle(img,(ix[0],iy[0]),(ix[1],iy[1]),(255,0,0),2)
                
    def draw_roi(self,img,event = 0):
        ix = []
        iy = []

                
        if event == 0: # 0 for freezing
            if os.path.exists(self.xy):
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
                f.close()
    ##            print(ix,iy)
                pts = np.array([[ix[0],iy[0]],[ix[1],iy[1]],[ix[2],iy[2]],[ix[3],iy[3]]],np.int32)
##                cv2.fillPoly(img,[pts],255)
                cv2.fillPoly(black_bg,[pts],255)                
                return cv2.bitwise_not(black_bg)
            else:
                print("xy.txt is not existed")     
                    
                cv2.namedWindow('drawRoi')                
                cv2.setMouseCallback('drawRoi',draw_polygon)
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
            cv2.namedWindow('drawRoi')
            cv2.setMouseCallback('drawRoi',draw_rectangle)
            while(1):
                cv2.imshow('drawRoi',img)
                key = cv2.waitKey(10) & 0xFF
                if key == ord('s'):
                    #cv2.imwrite(self.mask_path,black_bg_inv)
                    cv2.destroyWindow('drawRoi')
                    return ix,iy               
                    
                elif key == ord('q'):
                    cv2.destroyWindow('drawRoi')
                    break

        
    def draw_roi(self,event = 0):
        cap = cv2.VideoCapture(self.video_path)
        ret,frame = cap.read()
        img = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        rows,cols = img.shape
        black_bg = np.zeros((rows,cols),np.uint8) #0 for black, 255 for white
        #####
        ix = []
        iy = []
##        print(self.xy)
        def draw_polygon(event,x,y,flags,param):

            if event == cv2.EVENT_LBUTTONDOWN:
                ix.append(x)
                iy.append(y)
            #print(f'{x},{y} are appended')
            #if len(ix) == 1:
                #cv2.circle(img,(ix[0],iy[0]),255,2)
                #cv2.line(img,(ix[0],iy[0]),(x,y),255,2)
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
            print(x,y)
            if event == cv2.EVENT_LBUTTONDOWN:
                ix.append(x)
                iy.append(y)
            if len(ix)==2:
                cv2.rectangle(img,(ix[0],iy[0]),(ix[1],iy[1]),(255,0,0),2)
           
##                cv2.rectangle(black_bg,(ix[-1]+2,ix[-1]-2),(iy[-1]+2,iy[-1]-2),(255,0,0),-1)
                
        if event == 0: # 0 for freezing
            if os.path.exists(self.xy):
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
                f.close()
    ##            print(ix,iy)
                pts = np.array([[ix[0],iy[0]],[ix[1],iy[1]],[ix[2],iy[2]],[ix[3],iy[3]]],np.int32)
##                cv2.fillPoly(img,[pts],255)
                cv2.fillPoly(black_bg,[pts],255)                
                return cv2.bitwise_not(black_bg)
            else:
                print("xy.txt is not existed")     
                    
                cv2.namedWindow('drawRoi')                
                cv2.setMouseCallback('drawRoi',draw_polygon)
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
            cv2.namedWindow('drawRoi')
            cv2.setMouseCallback('drawRoi',draw_rectangle)
            while(1):
                cv2.imshow('drawRoi',img)
                key = cv2.waitKey(10) & 0xFF
                if key == ord('s'):
                    #cv2.imwrite(self.mask_path,black_bg_inv)
                    cv2.destroyWindow('drawRoi')
                    return ix,iy               
                    
                elif key == ord('q'):
                    cv2.destroyWindow('drawRoi')
                    break


    
    def extract_roi(self):
        mask = self.draw_roi()
        #mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        #frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        
        newvideo = cv2.VideoWriter(self.maskedvideo_path, cv2.VideoWriter_fourcc(*'XVID'), fps, size)
              
        index = 1
        while(cap.isOpened()):
            ret,frame = cap.read()
            if ret == True:
                index += 1
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                newframe = cv2.add(gray,mask)            
                #cv2.putText(gray, 'fps: ' + str(fps), (0, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 2)
                #cv2.putText(gray, 'count: ' + str(frameCount), (0, 10), cv2.FONT_HERSHEY_SIMPLEX,0.4, 0, 2)
                cv2.putText(newframe, 'frame: ' + str(index), (0, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 2)
                cv2.putText(newframe,'size: '+str(size),(0,25),cv2.FONT_HERSHEY_SIMPLEX,0.4,0,2)
                #cv2.putText(gray, 'time: ' + str(round(index / 24.0, 2)) + "s", (0,50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 2)
                newvideo.write(newframe)
                cv2.imshow("new video", newframe)
                print(f'frame {index} saved successfully ')
                print(ret)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                        break                
            else:
                print('finish transfer!')
                break
        newvideo.release()
        cap.release()
        cv2.destroyAllWindows()
            
       
    
        
    def video_to_csv (self,Interval_number=1,diff_gray_value=30,mask = 0):
        
        ts = pd.read_csv(self.videots_path, sep=" ",encoding = "utf-16",header='infer',names=['ts(s)'])
        frame_index = pd.DataFrame({'Frame_No':list(range(1,len(ts)+1))})
        ts.insert(0,'Frame_No',frame_index.pop('Frame_No'))
        print('\n'+self.videots_path+'Frame Number & timestamps are loaded sucessfully \nvideo is processing frame by frame...')


        cap = cv2.VideoCapture(self.video_path)
        frames = []
        frame_No = []
        frame_count = 1
        

        while(1):
            ret,frame = cap.read()
            if ret == True:
                if (frame_count-1)%Interval_number == 0:
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame_gray = cv2.add(mask,frame_gray)
                    if frame_count ==1:                    
                        cv2.imwrite(self.masked_path,frame_gray)
                    if frame_count <=100:
                        cv2.imshow(self.masked_path,frame_gray)
                        cv2.waitKey(10)
                    frame_No.append(frame_count)
                    frames.append(frame_gray)
                    #print(f'the {frame_count}th frame is picked out')
                frame_count = frame_count +1
            else :
                break
        cap.release()
        cv2.destroyAllWindows()

        
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
    
        dataframe.to_csv(self.videofreezing_path,index = False,sep = ',')

        print(self.video_path+r' finish processing \nand saving of Frame_number, timestamps, chaged pixel number and percentage(%).')
        return 0

    def _video_to_csv2 (self,Interval_number=1,mask = 0,show = True):
        cap = cv2.VideoCapture(self.video_path)              
        frame_count = 1        

        while(1):
            ret,frame = cap.read()
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
        
    def video_to_cvs2(self,Interval_number=1,mask = 0,show =True,diff_gray_value=30):
        if os.path.exists(self.videots_path):
            ts = pd.read_csv(self.videots_path, sep=" ",encoding = "utf-16",header =None,names=['ts(s)'])
            ts['Frame_No'] = list(range(1,len(ts)+1))
        else:
            print ('there is no timestamp file')

        print(self.video_name+' Frame Number & timestamps are loaded sucessfully \nvideo is processing frame by frame...')

        frame_grays = self._video_to_csv2(Interval_number = Interval_number,mask = mask,show = False)       

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




if __name__ == '__main__':
    video = Video(r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\2019031100002.AVI')
    video.video_to_cvs2()
