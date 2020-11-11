from mylab.Cvideo import Video
import os,sys,glob
import cv2
from mylab.Cfile import TimestampsFile,TrackFile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CPP_Video(Video):
    def __init__(self,video_path):
        super().__init__(video_path)
        self.led_xy = self.abs_prefix + '_led_xy.txt' # 这个数据结构和self.xy不一样，这个
        self.led_value_ts = self.abs_prefix+'_ledvalue_ts.csv'
        self.ts = TimestampsFile(self.videots_path,method="ffmpeg").ts

        self.track = TrackFile(self.video_track_path,parts=["Head","Body","Tail","led1","led2"]).behave_track

    @property
    def tracked_coords(self):
        tracked_coords=[]

        for led_x1,led_y1,led2_x1,led2_y1 in zip(self.track["led1_x"],self.track["led1_y"],self.track["led2_x"],self.track["led2_y"]):
            tracked_coords.append([(led_x1,led_y1),(led2_x1,led2_y1)])
        return tracked_coords
    

    def show_behaveframe_anotations(self,coords=None,half_diameter=13,frame_No=10000,color=(255,255,255)):
        """
        Arguments:
            coords: [(x1,y1),(x2,y2)]
        """

        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
        ret,frame = cap.read()

        if not coords is None:
            for coord in coords:
                x= int(coord[0])
                y=int(coord[1])

                cv2.rectangle(frame, (x-half_diameter, y-half_diameter), (x+half_diameter, y+half_diameter), color, 2)

        while True:
            cv2.imshow("led_location",frame)
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        
    

    def _led_brightness(self,half_diamter=15,according="each_frame"):
        """
        output the mean pixel value of specified coords of led
        tracked_coords: [[(led1_x1,led1_y1),(led2_x1,led2_y1),...],[],...,[(led1_xn,led1_yn),(led2_xn,led2_yn),...]]
        half_diameter: led gray value in roi defined by (x-half_diamter,x+half_diameter,y-half_diamter,y+half_diameter) was summarzied. 
        according, chose from ["each frame","median"]. led locations were tracked in each frames. 
                    "each _frame" suggest led_location of each frame was used
                    "median" suggest the median of all tracked led location was used.

        """
        cap = cv2.VideoCapture(self.video_path)
        total_frame = cap.get(7)
        frame_No = 0
        median_coords = np.median(self.tracked_coords,axis=0)
        while True:
            # key = cv2.waitKey(10) & 0xFF
            ret,frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                
                # if key == ord('q'):
                #     break
                if according == "each_frame":
                    coords=self.tracked_coords[frame_No] # [(led1_xn,led1_yn),(led2_xn,led2_yn)]
                    frame_No = frame_No +1
                elif according == "median":
                    coords = median_coords
                else:
                    print("according could only be chosed from ['each_frame','median']")
                    sys.exit()

                led_pixel_values = []
                for coord in coords: 
                    #注意cv2中的image 中的x，y是反的
                    x,y=coord
                    x= int(x)
                    y= int(y)
                    try:
                        led_zone = gray[(y-half_diamter):(y+half_diamter),(x-half_diamter):(x+half_diamter)]
                        led_pixel_values.append(sum(sum(led_zone))/(4*(half_diamter**2)))
                    except:
                        try:
                            led_pixel_values.append(led_pixel_values[-1])
                        except:
                            led_pixel_values.append(np.nan)
                            print("%sth frame: wrong track of  (%s,%s), which is recognized at the border of videw"%(frame_No,x,y))
                    # print("\r %s/%s"%(frame_No,int(total_frame)))
                    
                yield led_pixel_values # [led1_value,led2_value]
                # cv2.imshow("crop_frame",led_zone)

            else:
                break

        cap.release()


    def leds_pixel_value(self,half_diamter=15,according="each_frame"):
        """
        generate *_ledvalue_ts.csv
        tracked_coords: [[(led1_x1,led1_y1),(led2_x1,led2_y1),...],[],...,[(led1_xn,led1_yn),(led2_xn,led2_yn),...]]

        returns
            gray value of led1,led2,... was added as one column of the csv file to be saved.
        """
        leds_pixel=[]
        print("calculating frame by frame...")
        i = 1
        for led_pixel_value in self._led_brightness(half_diamter=half_diamter,according=according):
            leds_pixel.append(led_pixel_value)
            # print(i)
            i = i+1


        df= pd.DataFrame(np.array(leds_pixel),columns=np.arange(len(led_pixel_value))+1)
        df["ts"]=self.ts
        df.to_csv(self.led_value_ts,index = False,sep = ',')  
        print("%s is saved"%self.led_value_ts)
        # return df
        
    def check_frames(self,args,location_coords=None):
        '''
        'a':后退一帧
        'd':前进一帧
        'w':前进一百帧
        's':后退一百帧
        'n':下一个指定帧
        args: [(frame_No,led_1_value,led_2_value),...]
        '''
        #(10,15):left up, (400,15), right up
        location_coords = (10,15) if location_coords ==None else location_coords

        font = cv2.FONT_ITALIC
        cap = cv2.VideoCapture(self.video_path)
        
        def nothing(x):  
            pass
            
        # cv2.namedWindow("check_frames")
        total_frame = int(cap.get(7))
        # cv2.createTrackbar('frame_No','check_frames',1,int(total_frame),nothing)
        print(f"there are {int(total_frame)} frames in total")
        
        frame_No=1
        
        specific_frames = args

        if len(specific_frames)==0:
            specific_frames=[0,-1,-1]
        else:
            print(specific_frames,"frames to check")
        marked_frames=[]
        
        for info in specific_frames:
            i,led_1_value,led_2_value = info
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
                
            cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No)
            cv2.setTrackbarPos("frame_No","check_frames",frame_No)
            
            ret,frame = cap.read()
            cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
            cv2.imshow('check_frames',frame)
            while 1:                
                key = cv2.waitKey(1) & 0xFF
                frame_No = cv2.getTrackbarPos('frame_No','check_frames')                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                ret,frame = cap.read()
                cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
                cv2.imshow('check_frames',frame)
                
                if key == ord('m'):
                    marked_frames.append(frame_No)
                    print(f"the {frame_No} frame is marked")
                if key == ord('d'):
                    frame_No = frame_No +1
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('a'):
                    frame_No = frame_No - 1
                    if frame_No <=1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES,frame_No)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('w'):
                    frame_No=frame_No +100
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('c'):
                    frame_No=frame_No +10
                    if frame_No >= total_frame:
                        frame_No = total_frame
                        print(f"you have reached the final frame {total_frame}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('s'):
                    frame_No=frame_No -100
                    if frame_No <= 1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
                    cv2.imshow('check_frames',frame)
                if key == ord('z'):
                    frame_No=frame_No -10
                    if frame_No <= 1:
                        frame_No = 1
                        print(f"you have reached the first frame")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
                    cv2.setTrackbarPos("frame_No","check_frames",frame_No)
                    ret,frame = cap.read()
                    cv2.putText(frame,"frame_No %s %s %s"%(frame_No,led_1_value,led_2_value),location_coords, font, 0.5, (255,255,255))
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
    def draw_leds_location(self,count=2,frame_No=10000):

        # get the frame_No(default 10000 here) frame
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
        ret,frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        led_coords = []
        ix = []
        iy = []

        if os.path.exists(self.led_xy):
            print("you have drawn the location of leds")
            f = open(self.led_xy)
            led_coords = f.read()
            f.close
            if len(led_coords)==count:
                return eval(led_coords)
            else:
                print("you have drawn %s/%s led location,please draw the left"%(len(led_coords),count))
        else:
            print("Mark the led location")
            

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
                    cv2.destroyWindow('draw_led_location')
                    break
                else:
                    print("%s/%s led location is finished"%(len(ix),count))
            elif key == ord('q'):
                cv2.destroyWindow('draw_led_location')
                print("give up drawing led location")
                return self.draw_led_location(count=count,frame_No = frame_No)
            elif key == ord('d'):
                if len(ix)>0:
                    print("delete the points(%s,%s)"%(ix.pop(),iy.pop()))
                for (x,y) in zip(ix,iy):
                    print(x,y)

            # elif key == ord('f'):
            #     frame_No=frame_No +100
            #     if frame_No >= total_frame:
            #         frame_No = total_frame
            #         print(f"you have reached the final frame {total_frame}")
            #     cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
            #     ret,frame = cap.read()
            # elif key == ord('b'):
            #     frame_No=frame_No -10
            #     if frame_No < 1:
            #         frame_No = 1
            #         print(f"you have reached the first frame")
            #     cap.set(cv2.CAP_PROP_POS_FRAMES, frame_No)
            #     ret,frame = cap.read()
            else:
                pass
        return led_coords
