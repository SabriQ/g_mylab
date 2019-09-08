def _nothing (self,x):
    pass
def correct (self):
    print('''
        请注意调整成 英文输入法
        "a": backward 100 frames
        "s": forward 100 frames
        "f": player slower
        "g": play faster
        "q": quit
        ''')
    track_csv = os.path.dirname(self.video_path)+'\\'+'tracking.csv'
    track = pd.read_csv(self.videotrack_path)
##        Frame_No=track['Frame']
    X = list(track['X'])
    Y = list(track['Y'])
##        print(x,y)
    cv2.namedWindow('correct_coordination',0)
##        cv2.resizeWindow("correct_coordination", 800, 600)
    cap = cv2.VideoCapture(self.video_path)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
              
    cv2.createTrackbar('frames', 'correct_coordination', 0, frames, self._nothing)
    bar_pos = 0
    step = 1
    wait = 11

##        
    while 1:
        ret,frame = cap.read()            
        bar_pos = cv2.getTrackbarPos('frames','correct_coordination')            
        cap.set(cv2.CAP_PROP_POS_FRAMES, bar_pos)

        x_pos = int(round(X[bar_pos-1]/0.11))
        y_pos = int(round(Y[bar_pos-1]/0.11))
    
        def draw_circle(event,x,y,flags,param):
            if event == cv2.EVENT_MOUSEMOVE:
                cv2.circle(frame,(x,y),5,(255,0,0),2)##                    
            if event == cv2.EVENT_LBUTTONDOWN:                
                X[bar_pos] = x * 0.11
                Y[bar_pos] = y * 0.11
                print(f'Frame{bar_pos} is corrected @ {x*0.11} and {y*0.11}')
       
        if ret:
            cv2.circle(frame,(x_pos,y_pos),5,(0,0,255),2)
            cv2.setMouseCallback('correct_coordination',draw_circle)
            cv2.imshow('correct_coordination',frame)
        else:
            temp  = input('save(yes) or not: ')
            if temp == 'yes':
                track['X']=X
                track['Y']=Y
                print('correct successfully!')
                break
            else:
                print('give up correction')
                break
        
        bar_pos += step
        cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
        
        key = cv2.waitKey(wait) & 0xFF
        
        if key == 32:                
            cv2.waitKey(0)
                
        if key == ord('a'):
            bar_pos = bar_pos -100
            cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
        if key == ord('s'):
            bar_pos = bar_pos +100
            cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
        if key == ord('f'):
            wait += 10
        if key == ord('g'):
            if wait <= 2:
                wait = wait
                print("it has played at the fastest speed")
            else:
                wait = wait - 10
                
        if key == ord('q'):
            break

        
    
    cap.release()
    cv2.destroyAllWindows()
    
def correct2 (self):
    print('''
        请注意调整成 英文输入法
        "a": backward 100 frames
        "s": backward 10 frames
        "d": backward 1 frame
        "f": forward 1 frames
        "g": froward 10 frames
        "q": quit
        ''')
    track_csv = os.path.dirname(self.video_path)+'\\'+'tracking.csv'
    track = pd.read_csv(self.videotrack_path)
##        Frame_No=track['Frame']
    X = list(track['X'])
    Y = list(track['Y'])
    
    def correct3():
    # distance vector in cm
        distances = (np.diff(X)**2 + np.diff(Y) ** 2)**0.5
        mean = np.mean(distances)
        std = np.std(distances,ddof = 1)
        wrong_frames = []
        
        
        for index, distance in enumerate(distances,2):
            z_score = (distance-mean)/std
##            print(z_score)
            if abs(z_score) >2.33:
                wrong_frames.append(index)           
           
    
##        print(x,y)
        cv2.namedWindow('correct_coordination',0)
##        cv2.resizeWindow("correct_coordination", 800, 600)
        cap = cv2.VideoCapture(self.video_path)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                  
        cv2.createTrackbar('frames', 'correct_coordination', 0, frames, self._nothing)
        frame_pos = 1
        
        for wrong_frame in wrong_frames:
            if frame_pos > wrong_frame:
                continue
            else:
                frame_pos = wrong_frame
                bar_pos = frame_pos
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                cv2.setTrackbarPos('frames','correct_coordination', bar_pos)                           					   															
                
                   
                ret = True
                temp_Frame_No = []
                temp_X = []
                temp_Y = []                    
                
                while ret:
                    ret,frame = cap.read()                        
                    def draw_circle(event,x,y,flags,param):                         
                        
                        if event == cv2.EVENT_LBUTTONDOWN:
                            temp_Frame_No.append(frame_pos)
                            temp_X.append(x*0.11)
                            temp_Y.append(y*0.11)
                            
                            cv2.circle(frame,(x,y),5,(255,0,0),2) 
                            print(len(temp_Frame_No))
                        
                            if len(temp_Frame_No) == 0:
                                print("there is no point selected")
                            if len(temp_Frame_No) == 1:
                                print(f"the 1st point,length {len(temp_X)}")                                
                            if len(temp_Frame_No) == 2:
                                print(f"the 2nd point,length {len(temp_X)}")
                                print(temp_X)
                                print(temp_Y)
                                print(temp_Frame_No)
                                if temp_Frame_No[1] < temp_Frame_No[0]:
                                    temp_Frame_No[0], temp_Frame_No[1] = temp_Frame_No[1],temp_Frame_No[0]
                                
                                insert_x = np.linspace(temp_X[0],temp_X[1],temp_Frame_No[1]-temp_Frame_No[0],endpoint = False)[1:]
                                print(insert_x)
                                insert_y = np.linspace(temp_Y[0],temp_Y[1],temp_Frame_No[1]-temp_Frame_No[0],endpoint = False)[1:]
                                print("---debug")
                                X[temp_Frame_No[0]+1:temp_Frame_No[1]] = insert_x
                                Y[temp_Frame_No[0]+1:temp_Frame_No[1]] = insert_y
                         
                                    
                                print(f'Frame{frame_pos} is corrected ')
                    cv2.setMouseCallback('correct_coordination',draw_circle)
                    
                    frame_pos = cv2.getTrackbarPos('frames','correct_coordination')
                    x_pos = int(round(X[frame_pos-1]/0.11))
                    y_pos = int(round(Y[frame_pos-1]/0.11))
                    cv2.circle(frame,(x_pos,y_pos),5,(0,0,255),2)                    
                    cv2.imshow('correct_coordination',frame)
                    
                    # cv2.setTrackbarPos('frames','correct_coordination',bar_pos)	
                    
                    key = cv2.waitKey(0) & 0xFF
                    
                    
                    # if key == 32:
                        # cv2.waitKey(0)                                   
                    if key == ord('a'):
                        frame_pos = frame_pos -100						
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                        bar_pos = frame_pos
                        cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
                    if key == ord('s'):
                        frame_pos = frame_pos -10						
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                        bar_pos = frame_pos
                        cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
                    if key == ord('d'):
                        frame_pos = frame_pos -1					
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                        bar_pos = frame_pos
                        cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
                            
                    if key == ord('f'):
                        frame_pos = frame_pos +1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                        bar_pos = frame_pos
                        cv2.setTrackbarPos('frames','correct_coordination',bar_pos)
                            
                    if key == ord('g'):
                        frame_pos = frame_pos +10
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                        bar_pos = frame_pos
                        cv2.setTrackbarPos('frames','correct_coordination',bar_pos)							
                    if key == ord('n'):
                        break
                                      
    
        temp  = input('iter(yes) or not: ')
        if temp == 'y':                               
            print('correct again!')
            correct3()
        else:
            track['X']=X
            track['Y']=Y
            #track.tocsv...
            print('save your correction!')				 		

        cap.release()
        cv2.destroyAllWindows()
    correct3()








        
    
