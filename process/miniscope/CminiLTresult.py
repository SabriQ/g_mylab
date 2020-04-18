from mylab.process.miniscope.Cminiresult import MiniResult as MR
import pickle
class MiniLWResult(MR):
    def __init__(self,result_dir,mouse_info_path,behave_dir):
        super().__init__(result_dir,mouse_info_path)
        self.exp_name = "lick_water"
        self.behave_dir = behave_dir
        # here are all the possible format of result generesulted by CNMF
        self.hdf5_Path=glob.glob(os.path.join(self.result_dir),'*/hdf5')[0]
        self.ms_ts_Path=glob.glob(os.path.join(self.result_dir),'ms_ts.pkl')[0]
        self.msmat_Path=glob.glob(os.path.join(self.result_dir),'ms.mat')[0]
        self.mspkl_Path=glob.glob(os.path.join(self.result_dir),'ms.pkl')[0]

        self.__check_behave_info(["context_orders","context_angles","ms_starts",
            "behave_trackfiles","behave_timestamps","behave_logfiles",
            "behave_videos"])

    @property
    def keys(self):
        self._mouse_info[self.exp_name].keys()

    @property
    def allkeys(self):
        self._mouse_info.keys()
    
    def __getitem__(self,key):
        return self._mouse_info[self.exp_name][key]

    def __setitem__(self,key,value):
        if not key in self.keys: 
            self._mouse_info[self.exp_name][key] = value
            print("%s is added"%key)
        else:
            print("reset or update is not allowed")

    def __check_behave_info(self,behaveinfo_lists):
        if [False for e in behaveinfo_lists if e not in self.keys]:
            '''
            [False] 说明 behaveinfo_lists 中有信息在self.keys中没有
            [] 说明...都有 
            '''
            def sort_key(s):     
                if s:            
                    try:         
                        date = re.findall('-(\d{8})-', s)[0]
                    except:      
                        date = -1            
                    try:         
                        HMS = re.findall('-(\d{6})[_|D]',s)[0]
                    except:      
                        HMS = -1          
                    return [int(date),int(HMS)]
            behave_trackfiledir = os.path.join(behave_dir,"*.h5")
            self._mouse_info[self.exp_name]["behave_trackfiles"] = [i for i in glob.glob(behave_trackfiledir) if '2019111' not in i]
            self._mouse_info[self.exp_name]["behave_trackfiles"].sort(key=sort_key)

            behave_timestampdir = os.path.join(behave_dir,"*_ts.txt")
            self._mouse_info[self.exp_name]["behave_timestamps"] = [i for i in glob.glob(behave_timestampdir) if '2019111' not in i]
            self._mouse_info[self.exp_name]["behave_timestamps"].sort(key=sort_key)

            behave_logffiledir = os.path.join(behave_dir,"*log.csv")
            self._mouse_info[self.exp_name]["behave_logfiles"] = [i for i in glob.glob(behave_logffiledir) if '2019111' not in i]
            self._mouse_info[self.exp_name]["behave_logfiles"].sort(key=sort_key)

            behave_videodir = os.path.join(behave_dir,"*_labeled.mp4")
            self._mouse_info[self.exp_name]["behave_videos"] = [i for i in glob.glob(behave_videodir) if '2019111' not in i]
            self._mouse_info[self.exp_name]["behave_videos"].sort(key=sort_key)


            self._mouse_info[self.exp_name]["blocknames"] = [os.path.basename(i).split('_ts.txt')[0] for i in self._mouse_info[self.exp_name]["behave_timestamps"]]

            return  __check_behave_info(self,behaveinfo_lists)
        else:
            if len((len(i) for i in behaveinfo_lists)) > 1:
                return "behaveinfo is not complete"
            else:
                return "behaveinfo is complete"



    def _equal_frames(self,dff,ms_ts):
        l_dff = dff.shape[0]# or sigraw.shape[0] or sigdeconvolved.shape[0] or CaTraces.shape[0]
        l_ms_ts = sum([len(i) for i in ms_ts])
        if l_dff != l_ms_ts:
            return 0
        else:
            return 1
    def load_msts(self,dff):
        # attention to check whether frames of ms_ts are equal to that of traces
        with open(self.mspkl_Path,'rb') as f:
            ms_ts_pkl = pickle.load(f)
        if self._equal_frames(dff,ms_ts_pkl):
            print("frames of timestaps and traces are equal!")
            return ms_ts_pkl
        else:
            print("please regenerate ms_ts")
            print("ms_ts_pkl: %s;frames: %s"%(dff.shape[0],sum([len(i) for i in ms_ts_pkl])))

    def sigraw2msblocks(self,ms_ts,sigraw,acceptedPool):
    '''
    according to ms_ts, we divided sigraw, a [(531,79031),(cell_number,frames)] numpy.ndarray into msblocks, a list of dataframe
    '''
    start = 0
    end=0
    len_ms_ts=[]
    msblocks=[]
    for i, ts in enumerate(ms_ts,1):
        len_ms_ts.append(len(ts))        
        start = end
        end = end+len(ts)        
        block=pd.DataFrame(sigraw[start:end,:],columns=acceptedPool)
        block['ms_ts']=ts
        print('trace and ms_ts[',start,end,']constructed as DataFrame')
        msblocks.append(block)
    print("sigraw have been constructed as a list of DataFrame as ms_ts. ")
    return msblocks
        

    def msblocks(self):
        pass
    def crop_video(self):
        pass
    def scale_video(self):
        pass

    def msblocks(self):
        pass
    def behaveblocks(self):
        pass
    def aligned_behaveblocks(self):
        pass
    def saveresult_pkl(self):
        pass
    def saveresult_mat(self):
        pass
    def main(self):
        result = self.load_result()
        try:
            ms_ts = self.load_msts(result["dff"])
        except:
            print("ms_ts and frames are not equalong ")
            sys.exit()

        self.sigraw2msblocks()