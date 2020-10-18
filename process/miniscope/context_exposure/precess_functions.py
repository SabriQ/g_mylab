

def divide_matrix_into_session_pkl(
    ms_mat_path
    ,ms_ts_path
    ,Result_dir
    ,orders=None):
    """
    ms_mat_path: the path of "ms.mat" 
    ms_ts_path: the path of "ms_ts.pkl"
    Result_dir: the path of CNMFe result directory
    orders, lists of the session or in CNMFe analyzing
    """
    if os.path.exists(ms_mat_path):        
        print("loading %s"%ms_mat_path)
        ms = load_mat(ms_mat_path)
        print("loaded %s"%ms_mat_path)
    else:
        print("loading %s"%ms_mat_path2)
        ms = load_pkl(ms_mat_path2)
        print("loaded %s"%ms_mat_path2)

    try:
        sigraw = ms['ms']['sigraw'] #默认为sigraw
        S_dff = ms['ms']['S_dff']
    except:            
        print("saving sigraw or S_dff problem")
        sys.exit(0)


    idx_accepted = ms['ms']['idx_accepted']
    idx_deleeted = ms['ms']['idx_deleted']

    with open(ms_ts_path,'rb') as f:
        timestamps = pickle.load(f)
    [print(len(i)) for i in timestamps]
    print("session lenth:%s, timestamps length:%s, dff shape:%s"%(len(timestamps),sum([len(i) for i in timestamps]),dff.shape))

    # 对不同session的分析先后顺序排序
    if not orders == None:
        timestamps_order = np.array([timestamps[i] for i in np.array(orders)-1])
        [print(len(i)) for i in timestamps_order]
        print("timestamps are sorted by %s"%orders)


    #根据timestamps将dff切成对应的session
    slice = []
    for i,timestamp in enumerate(timestamps_order):
        if i == 0:
            start = 0
            stop = len(timestamp)
            slice.append((start,stop))
        else:
            start = slice[i-1][1]
            stop = start+len(timestamp)
    #         if i == len(timestamps)-1:
    #             stop = -1
            slice.append((start,stop))
    # print(slice)

    for s,i in zip(slice,orders):
        name = "session"+str(i)+".pkl"
        result = {
            "ms_ts":timestamps[i-1],
            "dff":np.transpose(dff)[s[0]:s[1]],
            "S_dff":np.transpose(S_dff)[s[0]:s[1]],
            "sigraw":sigraw[s[0]:s[1]],
            "idx_accepted":idx_accepted
        }

        with open(os.path.join(Result_dir,name),'wb') as f:
            pickle.dump(result,f)
        print("%s is saved"%name)


def concatenate_sessions(session1,session2):
    """
    仅限于记录时有多个sessions但是只有一个behavioral video的情况
    """
    with open(session1,"rb") as f:
        s1 = pickle.load(f)
    with open(session2,"rb") as f:
        s2 = pickle.load(f)

    if (s1["idx_accepted"]==s2["idx_accepted"]).all():
        s1["ms_ts"] = np.concatenate((s1["ms_ts"],s2["ms_ts"]+s1["ms_ts"].max()+33),axis=0)
        s1["dff"] = np.vstack((s1.get("dff"),s2.get("dff")))
        s1["S_dff"] = np.vstack((s1.get("S_dff"),s2.get("S_dff")))
        s1["sigraw"] = np.vstack((s1.get("sigraw"),s2.get("sigraw")))
        s1["idx_accepted"] = s1["idx_accepted"]

        with open(session1,"wb") as f:
            pickle.dump(s1,f)
        print("%s has been merged in %s"%(session2,session1))
        print("you should remove %s"%session2)
    else:
        print("%s is not connected to %s"%(session2,session1))

def save_behave_pkl(
    behavevideo
    ,logfilepath = r"C:\Users\qiushou\OneDrive\miniscope_2\202016\starts_firstnp_stops.csv"
    ,Result_dir
    ):
    """
    behavebideo
    logfilepath
    Result_dir: the path of CNMFe result directory
    """
    key = str(re.findall('\d{8}-\d{6}',behavevideo)[0])
    mark = starts_firstnp_stops(logfilepath)

    _,start,first_np,mark_point,stop = mark(behavevideo)
    
    # index log file
    behave_log =[i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*log*")) if key in i][0]
    log = pd.read_csv(behave_log,skiprows=3)
    behavelog_time = log.iloc[:,12:]-min(log["P_nose_poke"])
    behavelog_info = log.iloc[:,:6]
    print("correct 'behavelog_time' when the first_np as 0")

    # index track file
    behave_track = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*DLC*h5")) if key in i][0]    
    track = pd.read_hdf(behave_track)
    behave_track=pd.DataFrame(track[track.columns[0:9]].values,
                 columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
    
    
    # index timestamps file
    behave_ts = [i for i in glob.glob(os.path.join(os.path.dirname(behavevideo),"*_ts.txt*")) if key in i][0]
    ts = pd.read_table(behave_ts,sep='\n',header=None,encoding='utf-16-le')
    
    # aligned log_time and behave video_time
    if mark_point  == 1:
        delta_t = ts[0][first_np-1]-behavelog_time["P_nose_poke"][0]
    
    ## 这里有时候因为first-np的灯刚好被手遮住，所以用第二个点的信号代替，即第一次enter_ctx的时间
    if mark_point == 2:
        delta_t = ts[0][first_np-1]-behavelog_time["P_enter"][0]

    behave_track['be_ts']=ts[0]-delta_t

    print("correct 'be_ts' when the first_np as 0")
    # index in_context
    print(behavevideo)
    in_context_mask,in_context_coords=Video(behavevideo).draw_rois(aim="in_context",count = 1)

    # index in_lineartrack
    in_lineartrack_mask,in_lineartrack_coords=Video(behavevideo).draw_rois(aim="in_lineartrack",count = 1)

    result = {"behavevideo":[behavevideo,key,start,first_np,mark_point,stop]
              ,"behavelog_time":behavelog_time
              ,"behavelog_info":behavelog_info
              ,"behave_track":behave_track
              ,"in_context_mask":in_context_mask[0]
              ,"in_context_coords":in_context_coords[0]
             ,"in_lineartrack_mask":in_lineartrack_mask[0]
             ,"in_lineartrack_coords":in_lineartrack_coords[0]}

    savename = os.path.join(Result_dir,"behave_"+str(key)+".pkl")
    with open(savename,'wb') as f:
        pickle.dump(result,f)
    print("%s get saved"%savename)


class behave_session(self):
    def __init__(behave_session_path):
        self.behave_session_path = behave_session_path

    def _load_session(self):
        with open(self.behave_session_path,'rb') as f:
            self.behave_result = pickle.load(f)

    @property
    def save(self):
        return self._save_session
    
    def _save_session(self):
        pass

    def mark_start_np_stop(self):
        pass


    # add in_context, speed, in_context_running_direction, placebin_num, 
    def add_info2aligned_behave2ms(self,scale=0.2339021309714166,placebin_number=10):
        #     scale = 0.2339021309714166 #cm/pixel 40cm的台子，202016，202017.202019适用
        logger.info("FUN:: add_info2aligned_behave2ms scale: %scm/pixel ; placebin_number: %s"%(scale,placebin_number))
        update = 0
            
        if "aligned_behave2ms" in self.result.keys():
            #1 添加 "in_context" in behave_track
            mask = self.result["in_context_mask"]
            if not "in_context" in self.result.keys():
                in_context=[]
                for x,y in zip(self.result["aligned_behave2ms"]["Body_x"],self.result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        in_context.append(0)
                    else:
                        in_context.append(1)
                self.result["in_context"]=pd.Series(in_context)
                logger.info("'in_context' has been added")
                update = 1
            else:
                print("'in_context' has been there")

            #2 添加“Body_speed" "Body_speed_angle"
            if not "Body_speed" in self.result.keys():
                Body_speed,Body_speed_angle = Video.speed(X=self.result["aligned_behave2ms"]["Body_x"]
                                                        ,Y=self.result["aligned_behave2ms"]["Body_y"]
                                                        ,T=self.result["aligned_behave2ms"]["be_ts"]
                                                        ,s=scale)
                logger.info("Body_speed is trimed by FUN: speed_optimize with 'gaussian_filter1d' with sigma=3")
                self.result["Body_speed"]=speed_optimize(Body_speed,method="gaussian_filter1d",sigma=3)
                self.result["Body_speed_angle"]=Body_speed_angle
                logger.info("Body_speed and Body_speed_angle have been added")
                update = 1
            else:
                print("'Body_speed'and'Body_speed_angle' has been there")
            
            #3 添加"in_context_running_direction"
            if not "in_context_running_direction" in self.result.keys():
                in_context_running_direction=[]

                for Trial, in_context,Body_speed,Body_speed_angle in zip(self.result["Trial_Num"],self.result["in_context"],self.result["Body_speed"],self.result["Body_speed_angle"]):
                    if Trial == -1:
                        in_context_running_direction.append(-1)
                    else:
                        if in_context == 0:
                            in_context_running_direction.append(-1)
                        else:
                            if Body_speed_angle > 90 and Body_speed_angle < 280 :
                                in_context_running_direction.append(0)
                            else:
                                in_context_running_direction.append(1)
                self.result["in_context_running_direction"]=pd.Series(in_context_running_direction)
                logger.info("in_context_running_direction has been added")
                update = 1
            else:
                print("in_context_running_direction has been there")

            #4 添加 in_context_placebin_num"
            if not "in_context_placebin_num" in self.result.keys():
                # print(self.result["in_context_coords"])
                Cx_min = np.min(np.array(self.result["in_context_coords"])[:,0])
                Cx_max = np.max(np.array(self.result["in_context_coords"])[:,0])
    
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                print(placebins)
                for in_context,x in zip(self.result['in_context'],self.result["aligned_behave2ms"]['Body_x']):
                    # x = int(x)
                    if not in_context:
                        in_context_placebin_num.append(0)
                    else:   
                        if x == placebins[0][0]:
                            in_context_placebin_num.append(1)
                        else:
                            for i,placebin in enumerate(placebins,0):
                                # print(x,placebin[0],placebin[1],end="|")
                                if x>placebin[0] and x <= placebin[1]:
                                    temp=i+1
                                    break                                    
                                else:
                                    pass
                            try:
                                in_context_placebin_num.append(temp)
                            except:
                                logger.warning("%s is in context but not in any place bin"%x)

                logger.info("in_context_placebin_num should start from 1, 0 means out of context")
                        
                print(len(in_context_placebin_num),self.result["aligned_behave2ms"].shape)
                self.result["in_context_placebin_num"] = pd.Series(in_context_placebin_num)
                update = 1
            else:
                print("'in_context_placebin_num' has been there")
            
        else:
            print("you haven't align behave to ms or it's homecage session")

        if update:
            with open(self.session_path,'wb') as f:
                pickle.dump(self.result,f)
            print("aligned_behave2ms is updated and saved %s" %self.session_path)



