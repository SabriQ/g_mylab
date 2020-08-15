import cv2
import numpy as np
import os
import sys
import pandas as pd
import re
import platform,subprocess
import time
import glob
import math
import csv 
import json
from mylab.Functions import *

class Video():
    """
    """
    def __init__(self,video_path):
        self.video_path = video_path
        self.video_name = os.path.basename(self.video_path)
        self.extension = os.path.splitext(self.video_path)[-1]
        self.abs_prefix = os.path.splitext(self.video_path)[-2]
        self.xy = os.path.dirname(self.video_path)+'\\'+'xy.txt'
        self.videots_path = self.abs_prefix + '_ts.txt'
        self.video_track_path = glob.glob(self.abs_prefix+".h5")


    def play(self):
        """
        instructions:
            'q' for quit
            'f' for fast farward
            'b' for fast backward
        Args:

        """
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
            if cv2.waitKey(wait) & 0xFF == ord('b'):
                wait = wait + step
        cap.release()
        cv2.destroyAllWindows()

    def crop_video(self,x,y,w,h):
        '''
        ffmpeg -i $1 -vf crop=$2:$3:$4:$5 -loglevel quiet $6

        可以使用
        ret,frame = cv2.VideoCapture(videopath)
        cv2.selectRoi(frame)
        来返回 x,y,w,h
        '''

        croped_video_name
        command = [
        "ffmpeg",
        "-i",self.video_path,"-vf",
        "crop=%d:%d:%d:%d" % (x,y,w,h),
        "-loglevel","quiet",croped_video_name]

    @staticmethod
    def contrastbrightness(videolists):
        for video in videolists:
            print(video)
            command=[
                "ffmpeg",
                "-i",video,
                "-vf","eq=contrast=2:brightness=0.5",
                video.replace(".AVI",".mp4")
            ]

            child = subprocess.Popen(command,stdout = subprocess.PIPE,stderr=subprocess.PIPE)
            out = child.communicate()[1].decode('utf-8')
        #     print(out)
            child.wait()
            print("%s done"%video)
    
    def _HMS2seconds(self,time_point):
        sum = int(time_point.split(":")[0])*3600+int(time_point.split(":")[1])*60+int(time_point.split(":")[2])*1
        return sum

    def _seconds2HMS(self,seconds):
        return time.strftime('%H:%M:%S',time.gmtime(seconds))

    def cut_video_seconds(self,start,end):
        '''
        this is for video cut in seconds
        ffmpeg -ss 00:00:00 -i video.mp4 -vcodec copy -acodec copy -t 00:00:31 output1.mp4
        starts and ends are in format 00:00:00
        '''
        i=1
        print(start,end)

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

    def scale(self,distance):    
        """
        Args:
            distance: the length in cm of a line that you draw
        """
        while True:
            _,coords_in_pixel = self.draw_rois(aim='scale')
            if len(coords_in_pixel[0]) ==2:
                break
            else:
                print("you should draw a line but not a polygon")

        print(coords_in_pixel[0][1],coords_in_pixel[0][0])
        distance_in_pixel = np.sqrt(np.sum(np.square(np.array(coords_in_pixel[0][1])-np.array(coords_in_pixel[0][0]))))
        distance_in_cm = int(distance) #int(input("直线长(in cm)： "))
        s = distance_in_cm/distance_in_pixel
        print(f"scale: {s} cm/pixel")
        return s

    @staticmethod
    def _angle(dx1,dy1,dx2,dy2):
        """
        dx1 = v1[2]-v1[0]
        dy1 = v1[3]-v1[1]
        dx2 = v2[2]-v2[0]
        dy2 = v2[3]-v2[1]
        """
        angle1 = math.atan2(dy1, dx1) * 180/math.pi
        if angle1 <0:
            angle1 = 360+angle1
        # print(angle1)
        angle2 = math.atan2(dy2, dx2) * 180/math.pi
        if angle2<0:
            angle2 = 360+angle2
        # print(angle2)
        return abs(angle1-angle2)

    @classmethod
    def speed(cls,X,Y,T,s,sigma=3):
        speeds=[0]
        speed_angles=[0]
        for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
            distance = np.sqrt(delta_x**2+delta_y**2)
            speeds.append(distance*s/delta_t)
            speed_angles.append(cls._angle(1,0,delta_x,delta_y))
        return pd.Series(speeds),pd.Series(speed_angles) # in cm/s

    def play_with_track(self,show = "Head"):
        """
        instructions:
            'q' for quit
            'f' for fast farward
            'b' for fast backward
        Args:
            show. "Head",Body" or "Tail". default to be "Body"
        """
        if not os.path.exists(self.videots_path):
            try:
                print("generating timestamps by ffmpeg")
                self.generate_ts_txt()
            except:
                print("fail to generate timestamps by ffprobe")
                sys.exit()
        else:
            ts = pd.read_table(self.videots_path,sep='\n',header=None,encoding="utf-16")

        if not os.path.exists(self.video_track_path):
            print("you haven't done deeplabcut tracking")
            sys.exit()
        else:
            track = pd.read_hdf(self.video_track_path)


        s = self.scale(70)
        try:
            behaveblock=pd.DataFrame(track[track.columns[0:9]].values,columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
            print("get track of head, body and tail")
        except:
            behaveblock=pd.DataFrame(track[track.columns[0:6]].values,columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh'])
            print("get track of head and body")
        behaveblock['be_ts'] = ts[0]
        behaveblock['Headspeeds'],behaveblock['Headspeed_angles'] = self.speed(behaveblock['Head_x'],behaveblock['Head_y'],behaveblock['be_ts'],s)
        behaveblock['Bodyspeeds'],behaveblock['Bodyspeed_angles'] = self.speed(behaveblock['Body_x'],behaveblock['Body_y'],behaveblock['be_ts'],s)
        # behaveblock['Tailspeeds'],behaveblock['Tailspeed_angles'] = self.speed(behaveblock['Tail_x'],behaveblock['Tail_y'],behaveblock['be_ts'],s)
        if show ==  "Body":
            x = [int(i) for i in behaveblock["Body_x"]]
            y = [int(i) for i in behaveblock["Body_y"]]
            speed = behaveblock["Bodyspeeds"]
        elif show == "Head":
            x = [int(i) for i in behaveblock["Head_x"]]
            y = [int(i) for i in behaveblock["Head_y"]]
            speed = behaveblock["Headspeeds"]
        else:
            print("pleas choose from 'Body' and 'Head'")
        t = [i for i in behaveblock["be_ts"]]

        font = cv2.FONT_ITALIC
        cap = cv2.VideoCapture(self.video_path)
        wait=30
        step = 1
        frame_No = 0
        while True:
            ret,frame = cap.read()
            if ret:
                # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,0,255),-1)
                cv2.putText(frame,f'{round(speed[frame_No],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
                for i in range(frame_No,0,-1):
                    if (t[frame_No]-t[i])<10:
                        pts1=(x[i],y[i]);pts2=(x[i-1],y[i-1])
                        thickness=1
                        if (t[frame_No]-t[i])<5:
                            thickness=2
                        cv2.line(frame, pts1, pts2, (0, 0, 255), thickness)
                cv2.imshow(self.video_name,frame)
                frame_No = frame_No + 1
                if cv2.waitKey(wait) & 0xFF == ord('q'):
                    break
                if cv2.waitKey(wait) & 0xFF == ord('f'):
                    if wait > 1:
                        wait = wait -step
                    else:
                        print("it has played at the fast speed without dropping any frame")
                    print("fps: %d"%round(1000/wait,1))
                if cv2.waitKey(wait) & 0xFF == ord('b'):
                    wait = wait + step
                    print("fps: %d"%round(1000/wait,1))
            else:
                break
        cap.release()
        cv2.destroyAllWindows()


    def generate_ts_txt(self):
        if not os.path.exists(self.videots_path):
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
        else:
            print("%s is aready there."%self.videots_path)

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

    def draw_rois(self,aim,count = 1):
        '''
        count means how many arenas to draw, for each arena:
            double clicks of left mouse button to make sure
            click of right mouse button to move
            click of left mouse button to choose point
        '''
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES,1000)
        ret,frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        origin = []
        coord = []
        coord_current = [] # used when move
        masks = []
        coords = []
        font = cv2.FONT_HERSHEY_COMPLEX
        state = "go"
        if os.path.exists(self.xy):
            existed_coords = self._extract_coord(self.xy,aim)
            for existed_coord in existed_coords:
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
                print("you have drawn rois of %s"%aim)
                return masks,coords
            if len(existed_coords) < count:
                print("please draw left rois of %s"%aim)
        else:
            print("please draw rois of %s"%aim)

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
                        cv2.fillPoly(black_bg,[existed_coord],(127,255,100))
                        cv2.putText(black_bg,f'{i}',tuple(np.trunc(existed_coord.mean(axis=0)).astype(np.int32)), font, 1, (0,0,255))
            if state == "go" and event == cv2.EVENT_LBUTTONDOWN:
                coord.append([x,y])
            if event == cv2.EVENT_MOUSEMOVE:
                if state == "go":
                    if len(coord) ==1:
                        cv2.line(black_bg,tuple(coord[0]),(x,y),(127,255,100),2)
                    if len(coord) >1:
                        pts = np.append(coord,[[x,y]],axis = 0)
                        cv2.fillPoly(black_bg,[pts],(127,255,100))
                    frame = cv2.addWeighted(param['img'],1,black_bg,0.3,0)
                    cv2.imshow("draw_roi",frame)
                if state == "stop":
                    pts = np.array(coord,np.int32)
                    cv2.fillPoly(black_bg,[pts],(127,255,100))
                    frame = cv2.addWeighted(param['img'],1,black_bg,0.3,0)
                    cv2.imshow("draw_roi",frame)
                if state == "move":
                    coord_current = np.array(coord,np.int32) +(np.array([x,y])-np.array(origin) )
                    pts = np.array(coord_current,np.int32)
                    cv2.fillPoly(black_bg,[pts],(127,255,100))
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
                return self.draw_rois(aim,count = count)
            if key==27:
                print("exit")
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
        
        return masks,coords

    def check_frames(self,location = "rightup",*args):
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
            
        cv2.namedWindow("check_frames")
        total_frame = int(cap.get(7))
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
                if key == ord('c'):
                    frame_No=frame_No +10
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
                if key == ord('z'):
                    frame_No=frame_No -10
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

class LT_Videos(Video):
    def __init__(self,video_path):
        super().__init__(video_path)
        self.led_xy = self.abs_prefix + '_led_xy.txt'
        self.led_value_ts = self.abs_prefix+'_ledvalue_ts.csv'
        self.in_context.xy = self.abs_prefix + '_in_context_xy.txt'



    def _led_brightness(self):

        if not os.path.exists(self.led_xy):
            self.draw_led_location()
        # read led locations
        f = open(self.led_xy)
        led_coords = f.read()
        f.close
        led_coords = eval(led_coords)

        cap = cv2.VideoCapture(self.video_path)
        total_frame = cap.get(7)
        frame_No = 1
        while True:
            # key = cv2.waitKey(10) & 0xFF
            ret,frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                
                # if key == ord('q'):
                #     break
                led_pixel_values = []
                for x,y in led_coords:
                    cv2.rectangle(frame,(x-5,y-5),(x+5,y+5),(255,255,255),2)
                    #注意cv2中的image 中的x，y是反的
                    led_location = gray[(y-5):(y+5),(x-5):(x+5)]
                    led_pixel_values.append(sum(sum(led_location)))
                # print("\r %s/%s"%(frame_No,int(total_frame)))
                frame_No = frame_No +1
                yield led_pixel_values
                # cv2.imshow("crop_frame",led_location)
            else:
                break

        cap.release()
        cv2.destroyAllWindows()
    def led_pixel_value(self):
        if not os.path.exists(self.videots_path):
            self.generate_ts_txt()
        # read timestamps
        if os.path.exists(self.led_value_ts):
            print("%s is already there"%self.led_value_ts)
        else:
            ts= pd.read_table(self.videots_path,sep='\n',header=None,encoding='utf-16-le')
            ts = list(ts[0])
            miniscope=[]
            event=[]
            lick=[]
            for m,e,l in self._led_brightness():
                miniscope.append(m)
                event.append(e)
                lick.append(l)

            df= pd.DataFrame({'ts':ts,'miniscope':miniscope,'event':event,'lick':lick})
            df.to_csv(self.led_value_ts,index = False,sep = ',')
            print("%s is saved"%self.led_value_ts)
    def draw_leds_location(self,count=3,frame_No=10000):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
        ret,frame = cap.read()
        # total_frame = cap.get(7)

        led_coords = []
        ix = []
        iy = []

        def draw_rectangle(event,x,y,flags,param):
            nonlocal ix,iy
            frame = param["img"]
            rows,cols,channels= frame.shape
            black_bg = np.zeros((rows,cols,channels),np.uint8)
            if event == cv2.EVENT_LBUTTONDOWN: 
                ix.append(x)
                iy.append(y)

            if event == cv2.EVENT_MOUSEMOVE:
                for (x,y) in zip(ix,iy):
                    cv2.rectangle(black_bg,(x-5,y-5),(x+5,y+5),(255,255,255),2)
                show_frame = cv2.addWeighted(frame,1,black_bg,0.9,0)
                cv2.imshow('draw_led_location',show_frame)

            if event == cv2.EVENT_RBUTTONDOWN:
                if len(ix)>0:
                    ix.pop()
                    iy.pop()
                    print("delete latest point")
                else:
                    print("no points to delete")



        if os.path.exists(self.led_xy):
            print("you have drawn the location of leds")
            f = open(self.led_xy)
            led_coords = f.read()
            f.close
            return eval(led_coords)
        else:
            print("Mark the led location")
            cv2.namedWindow('draw_led_location')
            cv2.setMouseCallback('draw_led_location',draw_rectangle,{"img":frame})

            while True:
                key = cv2.waitKey(10) & 0xFF
                
                if key == ord('s'):
                    #cv2.imwrite(self.mask_path,black_bg_inv)
                    if len(ix)==count:
                        cv2.destroyWindow('draw_led_location')
                        led_coords = [[x,y] for x,y in zip(ix,iy)]
                        f = open(self.led_xy,'w+')
                        f.write(str(led_coords))
                        f.close
                        print('led location is saved in file')
                        cap.release()
                        cv2.destroyWindow('draw_led_location')
                        return led_coords
                    else:
                        print("number of leds is not as many as expected")
                elif key == ord('q'):
                    cv2.destroyWindow('draw_led_location')
                    print("give up drawing led location")
                    return 0
                elif key == ord('d'):
                    if len(ix)>0:
                        ix.pop()
                        iy.pop()
                    for (x,y) in zip(ix,iy):
                        print(x,y)
                # elif key == ord('f'):
                #     frame_No=frame_No +100
                #     if frame_No >= total_frame:
                #         frame_No = total_frame
                #         print(f"you have reached the final frame {total_frame}")
                #     cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                #     ret,frame = cap.read()
                # elif key == ord('b'):
                #     frame_No=frame_No -10
                #     if frame_No < 1:
                #         frame_No = 1
                #         print(f"you have reached the first frame")
                #     cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No-1)
                #     ret,frame = cap.read()
                else:
                    pass



class Videos():
    """
    """
    def __init__(self,videolists,concat_txt=None,concat_video=None):
        self.videolists = videolists
        if len(videolists)==0:
            print("there is no video in videolists")
            sys.exit()
        if not concat_txt is None:
            self.concat_txt = concat_txt
        else:
            self.concat_txt = os.path.join(os.path.dirname(videolists[0]),"concat.txt")
        if not concat_video is None:
            self.concat_video = concat_video
        else:
            self.concat_video = os.path.join(os.path.dirname(videolists[0]),"concat_video"+os.path.splitext(videolists[0])[-1])

    def _generate_concat_list_txt(self):

        with open(self.concat_txt,'w') as f:
            for video in self.videolists:
                info ="file "+f"'{video}'\n"
                print(info)
                f.write(info)
        print(f"{self.concat_txt} is generated")


    def concat(self):
        """
        在不同的系统中，路径中的斜杠会很影响结果
        """
        if not os.path.exists(self.concat_txt):
            self._generate_concat_list_txt()
        if os.path.exists(self.concat_video):
            print(f"{self.concat_video} is already there")
            sys.exit()

        command=["ffmpeg"
                ,"-f","concat"
                ,"-safe","0"
                ,"-i",self.concat_txt
                ,"-c","copy"
                # ,"-vsync","vfr"
                # ,"-pix_fmt","yuv420p"
                ,self.concat_video]
        child = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
        out = child.communicate()[1]
        print(f"\r{out}",end=" ")
        child.wait()
        print("concatenation finished!")

if __name__ == "__main__":
    # Video(r"C:\Users\admin\Desktop\test\test\200309094857Cam-1.asf").play_with_track()

    videolists = glob.glob(r"C:\Users\Sabri\Desktop\*.asf")
    print(videolists)
    Videos(videolists).concat()
