import cv2
import numpy as np
import os
import sys
import pandas as pd
import re
import platform,subprocess
class Video():
    def __init__(self,video_path):
        self.video_path = video_path		 
        self.video_name = os.path.basename(self.video_path)
        
        extension = os.path.splitext(self.video_path)[-1]
        abs_prefix = os.path.splitext(self.video_path)[-2]
        
        self.xy = os.path.dirname(self.video_path)+'\\'+'xy.txt'
        self.led_xy = os.path.dirname(self.video_path)+'\\'+'led_xy.txt'
        
##        if os.path.splitext(self.video_path)[-1] == '.asf':
        self.videots_path = abs_prefix + '_ts.txt'
        self.videofreezing_path = abs_prefix + '_freezing.csv'
        
    def generate_ts_txt(self):
        if (platform.system()=="Linux"):
            command = r'ffprobe -i %s -show_frames -select_streams v  -loglevel quiet| grep pkt_pts_time= | cut -c 14-24 > %s' % (self.video_path,self.videots_path)
            child = subprocess.Popen(command,shell=True)
        if (platform.system()=="Windows"):
            try:
                powershell=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            except:
                print("your windows system doesn't have powershell")
                sys.exit()
            # command below relys on powershell so we open powershell with a process named child and input command through stdin way.
            child = subprocess.Popen(powershell,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            command = r'ffprobe.exe -i %s -show_frames -loglevel quiet |Select-String media_type=video -context 0,4 |foreach{$_.context.PostContext[3] -replace {.*=}} |Out-File %s' % (self.video_path,self.videots_path)
            child.stdin.write(command.encode('utf-8'))
            out = child.communicate()[1].decode('gbk') # has to be 'gbk'
        
    def _extract_coord (self,file,aim):
        f = open (file)
        temp = f.readlines()
        coords = []
        for eachline in temp:
            eachline = str(eachline)
            if aim in str(eachline):
                coord = []
                pattern_x = re.compile('\[(\d+),')
                coord_x = pattern_x.findall(str(eachline))
                pattern_y = re.compile('(\d+)\]')
                coord_y = pattern_y.findall(str(eachline))
                for x,y in zip(coord_x,coord_y):
                    coord.append([int(x),int(y)])
                coords.append(coord)
        f.close()
        return coords

    
    def draw_rois(self,aim="freezing",count = 1):
        if os.path.exists(self.xy):
            existed_coords = self._extract_coord(self.xy,aim)
            print("you have drawn before")
        cap = cv2.VideoCapture(self.video_path)
        ret,frame = cap.read()
        origin = []
        coord = []
        coord_current = [] # used when move 
        masks = []
        coords = []
        font = cv2.FONT_HERSHEY_COMPLEX
        state = "go"
        if os.path.exists(self.xy):
            for existed_coord in existed_coords:
##                print(len(coords),count)
                if len(existed_coord) >0:
                    existed_coord = np.array(existed_coord,np.int32)
                    coords.append(existed_coord)
                    mask = 255*np.ones_like(frame)
                    cv2.fillPoly(mask,[existed_coord],0)
                    masks.append(mask)
                    mask = 255*np.ones_like(frame)
                    if len(coords) >= count:
                        return masks,coords
        def draw_polygon(event,x,y,flags,param):
            nonlocal state, origin,coord,coord_current,mask,frame
            try:
                rows,cols,channels= param['img'].shape
            except:
                print("Your video is broken,please check that if it could be opened with potplayer?")
                sys.exit()
            black_bg = np.zeros((rows,cols,channels),np.uint8)
            if os.path.exists(self.xy):
                for i,existed_coord in enumerate(existed_coords,1):
                    if len(existed_coord)>0:
                        existed_coord = np.array(existed_coord,np.int32)                 
                        cv2.fillPoly(black_bg,[existed_coord],(127,255,10))                    
                        cv2.putText(black_bg,f'{i}',tuple(np.trunc(existed_coord.mean(axis=0)).astype(np.int32)), font, 1, (0,0,255))
            if state == "go" and event == cv2.EVENT_LBUTTONDOWN:
                coord.append([x,y])                
            if event == cv2.EVENT_MOUSEMOVE:
                if state == "go":
                    if len(coord) ==1:
                        cv2.line(black_bg,tuple(coord[0]),(x,y),(127,255,10),2)
                    if len(coord) >1:
                        pts = np.append(coord,[[x,y]],axis = 0)
##                        print(pts)
                        cv2.fillPoly(black_bg,[pts],(127,255,10))
                    frame = cv2.addWeighted(param['img'],1,black_bg,0.3,0)                
                    cv2.imshow("draw_roi",frame)
                if state == "stop":
                    pts = np.array(coord,np.int32)
                    cv2.fillPoly(black_bg,[pts],(127,255,10))
                    frame = cv2.addWeighted(param['img'],1,black_bg,0.3,0)                
                    cv2.imshow("draw_roi",frame)
                if state == "move":                    
                    coord_current = np.array(coord,np.int32) +(np.array([x,y])-np.array(origin) )
                    pts = np.array(coord_current,np.int32)
                    cv2.fillPoly(black_bg,[pts],(127,255,10))
                    cv2.fillPoly(mask,[pts],0)
                    frame = cv2.addWeighted(param['img'],1,black_bg,0.3,0)                
                    cv2.imshow("draw_roi",frame)                
            if event == cv2.EVENT_RBUTTONDOWN:
                origin =  [x,y]
                state = "move"
            if event == cv2.EVENT_LBUTTONDBLCLK:              
                if state == "move":
                    coord = coord_current.tolist()
                state = "stop"
                mask = 255*np.ones_like(frame)
                pts = np.array(coord,np.int32)
                cv2.fillPoly(mask,[pts],0)
                
        cv2.namedWindow("draw_roi")
        cv2.setMouseCallback("draw_roi",draw_polygon,{"img":frame})
        while(1):
            key = cv2.waitKey(10) & 0xFF 
            if key == ord('s'):
                if len(coord) >0:
                    masks.append(mask)
                    coords.append(coord)
                    f = open(self.xy,'a+')
                    f.write(f'{aim} {coord}\n')
                    f.close()                    
                print(f'{self.xy} is saved')
                cv2.destroyAllWindows()
                break
            if key == ord('q'):
                print("selected points are aborted")
                cv2.destroyAllWindows()
                return self.draw_rois()
            if key == ord('a'):
                f = open(self.xy,'a+')
                f.write(f'{aim} {coord}\n')
                f.close()       
                print('please draw another aread')
                cv2.destroyAllWindows()
                return self.draw_rois(aim=aim,count = count)
        cap.release()
        cv2.destroyAllWindows()
        return masks,coords

    
    def draw_roi(self,points = 4):
        cap = cv2.VideoCapture(self.video_path)
        ret,frame = cap.read()
        coord = []
        pts=[]
        mask = 255*np.ones_like(frame)
        
        def draw_polygon(event,x,y,flags,param):
            try:
                rows,cols,channels= param['img'].shape
            except:
                print("Your video is broken,please check that if it could be opened with potplayer?")
                sys.exit()
            black_bg = np.zeros((rows,cols,channels),np.uint8)
            
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(coord) < points:
                    coord.append([x,y])
                else:
                    print(f"you already have choosed {points} points")                                
                
            if event == cv2.EVENT_MOUSEMOVE:
                if len(coord) ==1:
                    cv2.line(black_bg,tuple(coord[0]),(x,y),(127,255,10),2)
                if len(coord) >1 and len(coord) <points:
                    pts = np.append(coord,[[x,y]],axis = 0)
                    cv2.fillPoly(black_bg,[pts],(127,255,10))
                if len(coord) == points:
                    pts = np.array(coord,np.int32)
                    cv2.fillPoly(black_bg,[pts],(127,255,10))
                    cv2.fillPoly(mask,[pts],0)

                frame = cv2.addWeighted(param['img'],1,black_bg,0.3,0)                
                cv2.imshow("draw_roi",frame)
                
        cv2.namedWindow("draw_roi")
        cv2.setMouseCallback("draw_roi",draw_polygon,{"img":frame})
        while(1):
            key = cv2.waitKey(10) & 0xFF 
            if len(coord)==4:
                cv2.imshow("mask",mask)
            if key == ord('s'):                    
                f = open(self.xy,'w+')
                f.write(f'x:{[i[0] for i in coord]}\ny:{[i[1] for i in coord]}')
                f.close()                    
                print(f'{self.xy} is saved')
                cv2.destroyAllWindows()
                break
            if key == ord('q'):
                print("selected points are aborted")
                cv2.destroyAllWindows()
                return self.draw_roi()
        cap.release()
        cv2.destroyAllWindows()
        return mask,pts
    
    # mask_generate mask same as draw_roi, besides it could generate mask when xy.txt exist
    def mask_generate(self):
        cap = cv2.VideoCapture(self.video_path)
        ret,frame = cap.read()
        coord = []
        pts=[]
        mask = 255*np.ones_like(frame)
        
        if os.path.exists(self.xy):
            print(f'{self.xy} existed')
            f = open(self.xy)
            temp = f.read()
            f.close()
            coord_x = temp.split('\n')[0]
            coord_y = temp.split('\n')[1]
            coord.append([int(coord_x.split(',')[0][3:6]),int(coord_y.split(',')[0][3:6])])
            coord.append([int(coord_x.split(',')[1]),int(coord_y.split(',')[1])])
            coord.append([int(coord_x.split(',')[2]),int(coord_y.split(',')[2])])
            coord.append([int(coord_x.split(',')[3].replace(']','')),int(coord_y.split(',')[3].replace(']',''))])
            pts = np.array(coord,np.int32)
##            print(pts)
            cv2.fillPoly(mask,[pts],0)        
        else:
            mask,_ = self.draw_roi()      
        cap.release()        
        return mask
    
    def _draw_led_location(self,img):
        ix = []
        iy = []
        rows,cols,channels= img.shape
        black_bg= np.zeros((rows,cols,channels),np.uint8)
        
        def draw_rectangle(event,x,y,flags,param):
##            print(x,y)
            if event == cv2.EVENT_LBUTTONDOWN:
                ix.append(x)
                iy.append(y)            
                cv2.rectangle(black_bg,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,255,255),2)
        if os.path.exists(self.led_xy):
            print('led_xy existed')
            f = open(self.led_xy)
            coord = f.read()
            f.close
            coord_x = re.split('[\n:\[\]xy]',coord)[3]
            coord_y = re.split('[\n:\[\]xy]',coord)[8]
            
            ix.append(int(coord_x))
            iy.append(int(coord_y))
            cv2.rectangle(black_bg,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,255,255),2)
            return ix,iy,black_bg
        else:
            print('Mark the led location please')
            cv2.namedWindow('draw_led_location')
            cv2.setMouseCallback('draw_led_location',draw_rectangle)
            
            while(1):
                img_show = cv2.add(img,black_bg)
                cv2.imshow('draw_led_location',img_show)
                key = cv2.waitKey(10) & 0xFF
                if key == ord('s'):
                    #cv2.imwrite(self.mask_path,black_bg_inv)
                    cv2.destroyWindow('draw_led_location')

                    f = open(self.led_xy,'w+')
                    f.write(f'x:{ix}\ny:{iy}')
                    f.close

                    print('led_xy.txt is created')
                    cv2.destroyWindow('draw_led_location')
                    return ix,iy,black_bg               
                    
                elif key == ord(' '):
                    ix = []
                    iy = []
                    cv2.destroyWindow('draw_led_location')
                    self.draw_led_location(img)
                elif key == ord ('q'):
                    cv2.destroyWindow('draw_led_location')
                    print("give up drawing led location")
                    sys.exit()
                    

        
    def led_on_frames (self,*args,threshold1 = 220,threshold2 = 50):
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
        if ret:
            #frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            ix,iy,mask = self._draw_led_location(frame)
        else:
            print("video can not be read")
            sys.exit()
        
        print('Got the led location')  
##        pixel_sum_base = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)]))
##        def show_frame (frame_No,frame):
##            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
##            frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
##            cv2.imshow('led location',frame_gray)
        # for check
        led_on_frame = []
        if len(led_ons):
            print("please press 'a' or 'f' to confirm the first led_on frame, and 's' to save the frame_No!")
            for i in np.arange(1,len(led_ons)+1):
                frame_No = led_ons[i-1]
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)  
                ret,frame = cap.read()
                frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))
                frame_show = cv2.add(frame,mask)
                #cv2.rectangle(frame_show,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                cv2.putText(frame_show,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
                cv2.imshow('led location',frame_show)
                while 1:
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('f'):                        
                        frame_No +=1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                        ret,frame = cap.read()
                        if ret:
                            frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                            judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))                     
                            frame_show = cv2.add(frame,mask)
                            #cv2.rectangle(frame_show,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                            cv2.putText(frame_show,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
                            cv2.imshow('led location',frame_show)
                            #print(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)])
                        else:
                            frame_No = frame_No-1
                            print(f'frame_No {frame_No} is the last frame')
                        
                    if key == ord('a'):
                        frame_No = frame_No - 1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-2)
                        ret,frame = cap.read()
                        frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                        judge = sum(sum(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)] > threshold1))
                        frame_show = cv2.add(frame,mask)
                        #cv2.rectangle(frame_show,(ix[-1]-10,iy[-1]-10),(ix[-1]+10,iy[-1]+10),(255,0,0),2)
                        cv2.putText(frame_show,f'frame_No:{frame_No} have {judge} pixels hugely changed',(10,15), font, 0.5, (255,255,255))
                        cv2.imshow('led location',frame_show)
                        #print(frame_gray[(iy[-1]-10):(iy[-1]+10),(ix[-1]-10):(ix[-1]+10)])
                        
                    if key == ord('s'):
                        led_on_frame.append(frame_No)
                        print(f'{frame_No} frame is saved')              
                        break
                    if key == ord('n'):
                        #led_ons.pop(i-1)
                        print('end of checking')
                        cv2.destroyAllWindows()
                        break
                    if key == ord('q'):
                        print('give up checking')
                        cv2.destroyAllWindows()
                        sys.exit()
            return led_ons
        else:
            print('finding the first frame where led on...')
            while(1):
                ret,frame = cap.read()
                if ret:
                    #frame_show = cv2.add(frame,mask)
                    #cv2.imshow('searching...',frame_show)
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

    def extract_timestamps(self):
        print("not yet code")
        pass
            
            
if __name__ == '__main__':

    video = Video (r'Y:\Qiushou\12 Miniscope\20190928\191126\191126B-20190928-221031.mp4')
    frames = video.led_on_frames()
    print(frames)
#    masks,ptss = video.draw_rois(aim="epm")
#    print(len(masks),len(ptss))
##    for mask, pts in zip(masks,ptss):
##        cv2.imshow("mask",mask)
##        print(pts)

