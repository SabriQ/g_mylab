import cv2,imageio
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
from mylab.Cfile import *

class Video():
    """
    """
    def __init__(self,video_path):
        self.video_path = video_path
        self.video_name = os.path.basename(self.video_path)
        self.extension = os.path.splitext(self.video_path)[-1]
        self.abs_prefix = os.path.splitext(self.video_path)[-2]
        self.xy = os.path.join(os.path.dirname(self.video_path),'xy.txt')
        self.videots_path = self.abs_prefix + '_ts.txt'
        try:
            self.video_track_path = glob.glob(self.abs_prefix+"*.h5")[0]
        except:
            self.video_track_path = 0
            print("video haven't been tracked")

        self.videosize = os.path.getsize(self.video_path)/1073741824 # video size is quantified by GB


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


    def save_gif(self,interval=900,duration=0.1,gif_path=None):
        cap = cv2.VideoCapture(self.video_path)
        total_frame = cap.get(7)
        buff=[]
        for i in np.arange(0,total_frame,interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES,i)
            ret,frame = cap.read()
            buff.append(frame)
        gif_path = self.abs_prefix+".gif" if gif_path == None else gif_path
        imageio.mimsave(gif_path,buff,"GIF",duration=duration)
        cap.release()
        print("%s is saved"%(self.abs_prefix+'.gif'))
    def show_masks(self,aim="in_context"):
        masks = self.draw_rois(aim=aim)[0]
        for mask in masks:
            plt.imshow(mask)
            plt.show()

    def transcode(self,show_details=True):
        """
        for save larger size video  as very smaller one
        """
        if self.videosize>1:
            print("%s is as large as %.2fGB"%(self.video_path,self.videosize))
            if self.video_path.endswith(".avi"):
                newvideo=self.video_path.replace(".avi",".mp4")
                command = ["ffmpeg","-i",self.video_path,newvideo]

                child = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
                out = child.communicate()[1]
                if show_details:
                    print(out)
                child.wait()
                print("%s has been transcoded")

    def crop_video(self,show_details=False,multiprocess=False):
        '''
        ffmpeg -i $1 -vf crop=$2:$3:$4:$5 -loglevel quiet $6

        可以使用
        ret,frame = cv2.VideoCapture(videopath)
        cv2.selectRoi(frame)
        来返回 x,y,w,h
        '''

        croped_video = self.abs_prefix+"_crop.avi"
        crop_video_file = self.abs_prefix+"_crop.txt"

        if not os.path.exists(croped_video):
            if not os.path.exists(crop_video_file):
                cap = cv2.VideoCapture(self.video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES,1000)
                ret,frame = cap.read()
                x,y,w,h = cv2.selectROI("%s"%os.path.basename(self.video_path),frame)
                cv2.destroyAllWindows()
                coords = pd.DataFrame(data={"x":[x],"y":[y],"w":[w],"h":[h]})
                print(coords)
                coords.to_csv(crop_video_file,index=False)
            else:
                print("coords exists")
                coords = pd.read_table(crop_video_file,sep=",")

            command = [
            "ffmpeg",
            "-i",self.video_path,"-vf",
            "crop=%d:%d:%d:%d" % (coords["w"],coords["h"],coords["x"],coords["y"]),
            "-loglevel","quiet",croped_video]

            child = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
            out = child.communicate()[1]
            if show_details:
                print(out)
            if not multiprocess:
                child.wait()
            print("%s has been cropped"%video)
        else:
            print("%s was cropped."%video)


    def contrastbrightness(self,):
        print(self.video_path)
        command=[
            "ffmpeg",
            "-i",self.video_path,
            "-vf","eq=contrast=2:brightness=0.5",
            self.video_path.replace(".mp4",".avi")
        ]
        print("%s is adjusting contrast and brightness" % self.video_path)
        child = subprocess.Popen(command,stdout = subprocess.PIPE,stderr=subprocess.PIPE)
        out = child.communicate()[1].decode('utf-8')
        #print(out)
        child.wait()
        print("%s done"%self.video_path)
    
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

    def play_with_track(self,show = "Body",scale=40,latest=300):
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


        s = self.scale(40)
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
            print("please choose from 'Body' and 'Head'")
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
                cv2.circle(frame,(x[frame_No],y[frame_No]),3,(0,255,0),-1)
                cv2.putText(frame,f'{round(speed[frame_No],2)}cm/s',(x[frame_No]+5,y[frame_No]), font, 0.5, (100,100,255))
                for i in range(frame_No,0,-1):
                    if (t[frame_No]-t[i])<latest:
                        pts1=(x[i],y[i]);pts2=(x[i-1],y[i-1])
                        thickness=1
                        color = (0,0,255)
                        if (t[frame_No]-t[i])<5:
                            thickness=2
                            color = (0,255,0)
                        cv2.line(frame, pts1, pts2, color, thickness)
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
            print("generating timestamps...")
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
                print("you have drawn rois of '%s'"%aim)
                return masks,coords
            if len(existed_coords) < count:
                print("please draw left rois of '%s'"%aim)
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

    def check_frames(self,*args,location = "rightup",time_point=False):
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
            
        # cv2.namedWindow("check_frames")
        total_frame = int(cap.get(7))
        # cv2.createTrackbar('frame_No','check_frames',1,int(total_frame),nothing)
        print(f"there are {int(total_frame)} frames in total")
        
        frame_No=1
        
        if time_point:
            #转换成帧数，start from 1,因为在后面播放的时候，有-1的操作。
            args=[find_close_fast[self.timestamps.to_numpy(),i]+1 for i in args]

        specific_frames = args
        if len(specific_frames)==0:
            specific_frames=[0]
        else:
            print(specific_frames,"frames to check")
        marked_frames=[]
        
        for i in specific_frames:
            cv2.namedWindow("check_frames")
            cv2.createTrackbar('frame_No','check_frames',1,int(total_frame),nothing)
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
                    print('end of this round checking')
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
        self.place_xy = os.path.join(os.path.dirname(self.video_path),'place_xy.txt')


    def draw_midline_of_whole_track_for_each_day(self,aim="midline_of_track",count=7):
        """
        return coords containing 7 points 
            0:nosepoke for initial a trial,
            1:curve near the nosepoke,
            2:start of context,
            3:end of context,
            4:curve near the choise,
            5:nosepoke for left choice,
            6:nosepoke for right choice
        """
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES,1000)
        ret,frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        coords = []

        def draw_lines(event,x,y,flags,param):
            nonlocal coords
            rows,cols,channels= frame.shape
            black_bg = np.zeros((rows,cols,channels),np.uint8)

            if event == cv2.EVENT_LBUTTONDOWN: 
                coords.append([x,y])
                f = open(self.place_xy,"w+")
                f.write(str(coords))
                f.close
                print("you have drawn %s/%s coords"%(len(coords),count))

            if event == cv2.EVENT_MOUSEMOVE:
                if len(coords) == 0:
                    pass
                elif len(coords)==1:
                    cv2.line(black_bg,tuple(coords[0]),(x,y),(0,255,0),2)
                elif len(coords)>=2 and len(coords)<=7:
                    for i in range(len(coords)-1):
                        cv2.line(black_bg,tuple(coords[i]),tuple(coords[i+1]),(0,255,0),2)
                    if len(coords)<6:
                        cv2.line(black_bg,tuple(coords[-1]),(x,y),(0,255,0),2)
                    if len(coords)==6:
                        cv2.line(black_bg,tuple(coords[-2]),(x,y),(0,255,0),2)
                    if len(coords)==7:
                        cv2.line(black_bg,tuple(coords[-3]),tuple(coords[-1]),(0,255,0),2)
                else:
                    pass
                
                show_frame = cv2.addWeighted(frame,1,black_bg,0.9,0)
                cv2.imshow('draw_midline_of_whole_track_for_each_day',show_frame)

            if event == cv2.EVENT_RBUTTONDOWN:
                if len(coords)>0:
                    coords.pop()
                    print("delete the latest point")
                else:
                    print("no points to delete")

        if os.path.exists(self.place_xy):
            print("you have drawn the location of points")
            f = open(self.place_xy)
            coords = f.read()
            coords = eval(coords)
            f.close
            if len(coords) == count:
                # print(coords)
                return coords
            else:
                print("you have drawn %s/%s coords"%(len(coords),count))
        
        print("Mark the point")
        cv2.namedWindow("draw_midline_of_whole_track_for_each_day")
        cv2.setMouseCallback("draw_midline_of_whole_track_for_each_day",draw_lines,{"img":frame})

        while True:
            key = cv2.waitKey(10) & 0xFF

            if key == ord("q"):
                cv2.destroyWindow("draw_midline_of_whole_track_for_each_day")
                print("give up drawing coords")
                break
            else:
                pass
        # print(coords)
        return coords

    def show_midline_of_whole_track(self):
        """
        show the frame with midline of the track
        """
        if os.path.exists(self.place_xy):
            print("you have drawn the location of points")
            f = open(self.place_xy)
            coords = f.read()
            coords = eval(coords)
            f.close
        else:
            return self.draw_midline_of_whole_track_for_each_day(aim="midline_of_track",count=7)
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES,1000)
        ret,frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        rows,cols,channels= frame.shape
        black_bg = np.zeros((rows,cols,channels),np.uint8)

        for i in range(len(coords)-2):
            cv2.line(black_bg,tuple(coords[i]),tuple(coords[i+1]),(0,255,0),2)
        cv2.line(black_bg,tuple(coords[-3]),tuple(coords[-1]),(0,255,0),2)

        show_frame = cv2.addWeighted(frame,1,black_bg,0.9,0)
        while True:
            key = cv2.waitKey(10) & 0xFF
            cv2.imshow('midline_of_whole_track',show_frame)
            if key == ord("q"):
                cv2.destroyWindow("draw_midline_of_whole_track_for_each_day")
                print("give up drawing coords")
                break
            else:
                pass        
        cv2.destroyAllWindows()

    def generate_placebin_according_to_midline(self,place_bin_nums=[3,3,20,3,3,3]):
        """
        generating a list of placebins of the same size as the behavioral video
        """
        # generate the midline_of_track_coords: in our track,
        # there are 7 points in the midline, returned by 'self.draw_midline_of_whole_track_for_each_day'
        coords = self.draw_midline_of_whole_track_for_each_day(aim="midline_of_track",count=7)
        # generate the line segments of each neighbor points 
        # ((0,1),(1,2),(2,3),(3,4),(4,5)) of the first 6 points
        # and (4,6) 
        
        lines = [(coords[i],coords[i+1]) for i in range(len(coords)-2)] # [(0,1),(1,2),(2,3),(3,4),(4,5)]
        
        lines.append((coords[-3],coords[-1])) # (4,6)
        
        place_bin_mids=[] # 每个placebin 的中点坐标
        for line, place_bin_num in zip(lines,place_bin_nums):
            #计算每个placebin中点的坐标。
            #首先 计算每个placebin边界点的坐标
            xs = np.linspace(line[0][0],line[1][0],place_bin_num+1)
            ys = np.linspace(line[0][1],line[1][1],place_bin_num+1)
            #然后计算 每个placebin的中点坐标
            xs_mid = [np.mean([xs[i],xs[i+1]]) for i in range(len(xs)-1)]
            ys_mid = [np.mean([ys[i],ys[i+1]]) for i in range(len(ys)-1)]
            place_bin_mids.extend([(x,y) for x,y in zip(xs_mid,ys_mid)])

        X = TrackFile(self.video_track_path).behave_track["Head_x"]
        Y = TrackFile(self.video_track_path).behave_track["Head_y"]

        place_bin_No=[]
        for x,y in zip(X,Y):
            distances=[]
            for place_bin_mid in place_bin_mids:
                distance = np.sqrt((x-place_bin_mid[0])**2+(y-place_bin_mid[1])**2)
                distances.append(distance)
            # print(distances)
            # sys.exit()  
            place_bin_No.append(np.argmin(distances))
        print(np.unique(place_bin_No))
        return place_bin_No



if __name__ == "__main__":

    video = r"C:\Users\qiushou\Desktop\Results_test\test\CDC-test-201033-20200901-194548.mp4"
    LT_Videos(video).generate_placebin_according_to_midline(place_bin_nums=[3,3,20,3,3,3])
    # CPP_Video(video).draw_leds_location()
    # LT_Videos(video).show_midline_of_whole_track()