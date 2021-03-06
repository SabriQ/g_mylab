import cv2
import numpy as np
import os
import sys
import pandas as pd
import re
import platform,subprocess
import time
import glob

def find_close_fast(arr, e):    
    '''
    返回arr列表中与e最相近的值的idx
    '''
    start_time = datetime.datetime.now()            
    low = 0    
    high = len(arr) - 1    
    idx = -1     
    while low <= high:        
        mid = int((low + high) / 2)        
        if e == arr[mid] or mid == low:            
            idx = mid            
            break        
        elif e > arr[mid]:            
            low = mid        
        elif e < arr[mid]:            
            high = mid     
    if idx + 1 < len(arr) and abs(e - arr[idx]) > abs(e - arr[idx + 1]):        
        idx += 1            
    use_time = datetime.datetime.now() - start_time    
    return idx

class Video():
    def __init__(self,video_path):
        self.video_path = video_path
        self.video_name = os.path.basename(self.video_path)

        self.extension = os.path.splitext(self.video_path)[-1]
        self.abs_prefix = os.path.splitext(self.video_path)[-2]

        self.xy = os.path.dirname(self.video_path)+'\\'+'xy.txt'
        self.led_xy = os.path.dirname(self.video_path)+'\\'+'led_xy.txt'

##        if os.path.splitext(self.video_path)[-1] == '.asf':
        self.videots_path = self.abs_prefix + '_ts.txt'
        self.videofreezing_path = self.abs_prefix + '_freezing.csv'
        
    def crop_video():
        '''
        ffmpeg -i $1 -vf crop=$2:$3:$4:$5 -loglevel quiet $6

        '''
        croped_video_name
        command = [
        "ffmpeg",
        "-i",self.video_path,"-vf",
        "crop=%d:%d:%d:%d" % (x,y,w,h),
        "-loglevel","quiet",croped_video_name]


    def _HMS2seconds(self,time_point):
        sum = int(time_point.split(":")[0])*3600+int(time_point.split(":")[1])*60+int(time_point.split(":")[2])*1
        return sum
    def _seconds2HMS(self,seconds):
        return time.strftime('%H:%M:%S',time.gmtime(seconds))
    def cut_video_seconds(self,*args):
        '''
        this is for video cut in seconds
        ffmpeg -ss 00:00:00 -i video.mp4 -vcodec copy -acodec copy -t 00:00:31 output1.mp4

        '''

        starts = args[:-1]
        ends = args[1:]
        i=1
        print(starts,ends)
        for start,end in zip(starts,ends):
            duration = self._seconds2HMS(self._HMS2seconds(end)-self._HMS2seconds(start))
            output_video_name = os.path.splitext(self.video_path)[0]+f"_cut_{i}"+os.path.splitext(self.video_path)[1]
            command = [
            "ffmpeg.exe",
            "-ss",start,
            "-i",self.video_path,
            "-vcodec","copy",
            "-acodec","copy",
            "-t",duration,
            output_video_name]
            print(f"{i}/{len(starts)} {self.video_path} is being cut")
            i = i+1
            child = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
            out = child.communicate()[1]
            #print(out)
            child.wait()


    def cut_video_frames(*args):
        '''
        this is for video cut in specific frames
        '''
        pass
    def generate_ts_txt(self):
        if (platform.system()=="Linux"):
            command = r'ffprobe -i %s -show_frames -select_streams v -loglevel quiet| grep pkt_pts_time= | cut -c 14-24 > %s' % (self.video_path,self.videots_path)
            child = subprocess.Popen(command,shell=True)
        if (platform.system()=="Windows"):
            try:
                powershell=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            except:
                print("your windows system doesn't have powershell")
                sys.exit()
            # command below relys on powershell so we open powershell with a process named child and input command through stdin way.
            child = subprocess.Popen(powershell,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            command = r'ffprobe.exe -i "%s" -show_frames -loglevel quiet |Select-String media_type=video -context 0,4 |foreach{$_.context.PostContext[3] -replace {.*=}} |Out-File "%s"' % (self.video_path,self.videots_path)
            child.stdin.write(command.encode('utf-8'))
            out = child.communicate()[1].decode('gbk') # has to be 'gbk'
            #print(out)
            child.wait()
            print(f"{self.video_path} has generated _ts files")
    def _extract_coord (self,file,aim):
        '''
        for reading txt file generated by draw_rois
        '''
        f = open (file)
        temp = f.readlines()
        coords = []
        for eachline in temp:
            eachline = str(eachline)
            if aim+' ' in str(eachline):
                #print (eachline)
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
        '''
        count means how many arenas to draw, for each arena:
            double clicks of left mouse button to make sure
            click of right mouse button to move
            click of left mouse button to choose point
        '''
#        if os.path.exists(self.xy):
#            existed_coords = self._extract_coord(self.xy,aim)
#            if len(existed_coords):
#                print("you have drawn before")
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
            existed_coords = self._extract_coord(self.xy,aim)
#            print("you have drawn before")
            for existed_coord in existed_coords:
##                print(len(coords),count)
                if len(existed_coord) >0:
                    existed_coord = np.array(existed_coord,np.int32)
                    coords.append(existed_coord)
                    mask = 255*np.ones_like(frame)
                    cv2.fillPoly(mask,[existed_coord],0)
                    masks.append(mask)
                    mask = 255*np.ones_like(frame)
                else:
                    print("there is blank coord record ")
                    continue
            if len(existed_coords) > count:
                print(f"there are more coords than you want, take the first {count}: ")
                print(coords[0:count])
                return masks[0:count],coords[0:count]
            if len(existed_coords) == count:
                print(f"you have drawn {aim}")
#                print(f"the coords is: ")
#                print(coords)
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
                state = "end of this arena"
                print("stop")
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
            if key==27:
                print("exit")
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
        cap.release()
        cv2.destroyAllWindows()
        return masks,coords


    def draw_roi(self,points = 4):
        '''
        for only freezing analysis
        '''
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
        '''
        only for led_on_frames()
        '''
        ix = []
        iy = []
        rows,cols,channels= img.shape
        black_bg= np.zeros((rows,cols,channels),np.uint8)

        def draw_rectangle(event,x,y,flags,param):
##            print(x,y)
            if event == cv2.EVENT_LBUTTONDOWN:
                ix.append(x)
                iy.append(y)
                cv2.rectangle(black_bg,(ix[-1]-5,iy[-1]-5),(ix[-1]+5,iy[-1]+5),(255,255,255),2)
        if os.path.exists(self.led_xy):
            print('led_xy existed')
            f = open(self.led_xy)
            coord = f.read()
            f.close
            coord_x = re.split('[\n:\[\]xy]',coord)[3]
            coord_y = re.split('[\n:\[\]xy]',coord)[8]

            ix.append(int(coord_x))
            iy.append(int(coord_y))
            cv2.rectangle(black_bg,(ix[-1]-5,iy[-1]-5),(ix[-1]+5,iy[-1]+5),(255,255,255),2)
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
    
    
    def check_frames_info(self,*args,speed,be_frame,x,y):
        '''
        'a':后退一帧
        'd':前进一帧
        'w':前进一百帧
        's':后退一百帧
        'n':下一个指定帧
        '''
        font = cv2.FONT_ITALIC
        cap = cv2.VideoCapture(self.video_path)
        total_frame = cap.get(7)
        print(f"there are {total_frame} frames in total")
        frame_No=1
        led_ons = args
        for i in led_ons:
            if i < 1:
                frame_No = 1
                print(f"there is before the first frame")
            elif i > total_frame:
                frame_No = total_frame
                print(f"{i} is after the last frame")
            else:
                frame_No = i

            cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No-1)
            ret,frame = cap.read()
            cv2.putText(frame,f'frame_No:{frame_No} ',(10,15), font, 0.5, (255,255,255))
            cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,0,255),-1)
            speed_frame = find_close_fast(be_frame,frame_No)
            cv2.putText(frame,f'{round(speed[speed_frame],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
            cv2.imshow('check_frames',frame)
            while 1:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('d'):
                    frame_No = frame_No +1
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',(10,15), font, 0.5, (255,255,255))
                    cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,0,255),-1)
                    speed_frame = find_close_fast(be_frame,frame_No)
                    cv2.putText(frame,f'{round(speed[speed_frame],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('a'):
                    frame_No = frame_No - 1
                    if frame_No <=1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',(10,15), font, 0.5, (255,255,255))
                    cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,0,255),-1)
                    speed_frame = find_close_fast(be_frame,frame_No)
                    cv2.putText(frame,f'{round(speed[speed_frame],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('w'):
                    frame_No=frame_No +100
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',(10,15), font, 0.5, (255,255,255))
                    cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,0,255),-1)
                    speed_frame = find_close_fast(be_frame,frame_No)
                    cv2.putText(frame,f'{round(speed[speed_frame],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('s'):
                    frame_No=frame_No -100
                    if frame_No <= 1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',(10,15), font, 0.5, (255,255,255))
                    cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,0,255),-1)
                    speed_frame = find_close_fast(be_frame,frame_No)
                    cv2.putText(frame,f'{round(speed[speed_frame],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('n'):
                    #led_ons.pop(i-1)
                    print('end of checking')
                    cv2.destroyAllWindows()
                    break
                if key == ord('q'):
                    print('give up checking')
                    cv2.destroyAllWindows()
                    sys.exit()
        print("finish checking")
        
    def check_frames(self,*args,location = "rightup"):
        '''
        'a':后退一帧
        'd':前进一帧
        'w':前进一百帧
        's':后退一百帧
        'n':下一个指定帧
        '''
        if location == "leftup":
            location_coords = (10,15)
        if location == "rightup":
            location_coords = (400,15)
        font = cv2.FONT_ITALIC
        cap = cv2.VideoCapture(self.video_path)
        
        total_frame = cap.get(7)
        print(f"there are {total_frame} frames in total")
        frame_No=1
        specific_frames = args
        if len(specific_frames)==0:
            specific_frames=[0]
        marked_frames=[]
        for i in specific_frames:
            if i < 1:
                frame_No = 1
                print(f"the minimum frame_No is 1")
            elif i > total_frame:
                frame_No = total_frame
                print(f"{i} is after the last frame")
            else:
                frame_No = i

            cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No-1)
            ret,frame = cap.read()
            cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
            cv2.imshow('check_frames',frame)
            while 1:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('m'):
                    marked_frames.append(frame_No)
                    print(f"the {frame_No} frame is marked")
                if key == ord('d'):
                    frame_No = frame_No +1
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('a'):
                    frame_No = frame_No - 1
                    if frame_No <=1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('w'):
                    frame_No=frame_No +100
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('s'):
                    frame_No=frame_No -100
                    if frame_No <= 1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('n'):
                    #led_ons.pop(i-1)
                    print('end of checking')
                    cv2.destroyAllWindows()
                    break
                if key == ord('q'):
                    print('break out checking of this round')
                    cv2.destroyAllWindows()
                    break
                if key == 27:
                    print("quit checking")
                    cv2.destroyAllWindows()
                    sys.exit()                    
        print("finish checking")
        if len(marked_frames) !=0:
            return marked_frames

    def check_frames_trackbar(self,*args,location = "rightup"):
        '''
        'a':后退一帧
        'd':前进一帧
        'w':前进一百帧
        's':后退一百帧
        'n':下一个指定帧
        '''
        if location == "leftup":
            location_coords = (10,15)
        if location == "rightup":
            location_coords = (400,15)
        font = cv2.FONT_ITALIC
        cap = cv2.VideoCapture(self.video_path)
        
        def nothing(x):  
            pass
#            cap.set(cv2.CAP_PROP_POS_FRAMES,x-1)
            
        cv2.namedWindow("check_frames")
        total_frame = cap.get(7)
        cv2.createTrackbar('frame_No','check_frames',1,int(total_frame),nothing)
        print(f"there are {int(total_frame)} frames in total")
        
        frame_No=1
        specific_frames = args
        if len(specific_frames)==0:
            specific_frames=[0]
        marked_frames=[]
        
        for i in specific_frames:
            if i < 1:
                frame_No = 1
                print(f"there is before the first frame")
            elif i > total_frame:
                frame_No = total_frame
                print(f"{i} is after the last frame")
            else:
                frame_No = i
                
            cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No-1)
            cv2.setTrackbarPos("frame_No","check_frames",frame_No)
            
            ret,frame = cap.read()
            cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
            cv2.imshow('check_frames',frame)
            while 1:                
                key = cv2.waitKey(1) & 0xFF
                frame_No = cv2.getTrackbarPos('frame_No','check_frames')                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                ret,frame = cap.read()
                cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                cv2.imshow('check_frames',frame)
                
                if key == ord('m'):
                    marked_frames.append(frame_No)
                    print(f"the {frame_No} frame is marked")
                if key == ord('d'):
                    frame_No = frame_No +1
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('a'):
                    frame_No = frame_No - 1
                    if frame_No <=1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No-1)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('w'):
                    frame_No=frame_No +100
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('s'):
                    frame_No=frame_No -100
                    if frame_No <= 1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,f'frame_No:{frame_No} ',location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('n'):
                    #led_ons.pop(i-1)
                    print('end of checking')
                    cv2.destroyAllWindows()
                    break
                if key == ord('q'):
                    print('break out checking of this round')
                    cv2.destroyAllWindows()
                    break
                if key == 27:
                    print("quit checking")
                    cv2.destroyAllWindows()
                    sys.exit()                    
        print("finish checking")
        if len(marked_frames) !=0:
            print(marked_frames)
            return marked_frames
        
    def led_on_frames (self,*args,threshold1 = 240,threshold2 = 2):
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
                    judge = sum(sum(frame_gray[(iy[-1]-5):(iy[-1]+5),(ix[-1]-5):(ix[-1]+5)] > threshold1))
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



if __name__ == '__main__':
    #%% led on frames
    Video(result["behave_videos"][0]).check_frames_info(2000,
          speed=result["aligned_behaveblocks"][0]["Bodyspeeds"].tolist(),
          be_frame = result["aligned_behaveblocks"][0]["be_frame"],
          x=np.array(result["behaveblocks"][0]["Body_x"].tolist()).astype(np.int),
          y=np.array(result["behaveblocks"][0]["Body_y"].tolist()).astype(np.int))  
    #%% check frames
    
    #%%
    
#    video_pathes =glob.glob (r'Y:\zhangna\3. EPM and open field\open_field\*.mp4')
#    #video_pathes = [i for i in video_pathes if "cut" not in i]
#    print(video_pathes)
#    for video in video_pathes:
#        video = Video(video)
#        video.generate_ts_txt()
        #video.cut_video_seconds("00:00:03","00:03:02","00:06:03","00:09:03")
#    masks,coords = video.draw_rois(aim="freezing",count = 3)
##    print(frames)
#    masks,ptss = video.draw_rois(aim="epm")
#    print(len(masks),len(ptss))
##    for mask, pts in zip(masks,ptss):
##        cv2.imshow("mask",mask)
##        print(pts)

