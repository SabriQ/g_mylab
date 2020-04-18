from mylab.process.miniscope.Cminiresult import MiniResult as MR
import pickle
import pandas as pd
import numpy as numpy
import matplotlib.pyplot as pyplot
from mylab.Cvideo import Video
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


        self.neccessary_info = ["video_scale","context_orders","context_angles","ms_starts","behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"]
        if not self.__check_behave_info(self.neccessary_info):
            print("please check info %s"%self.neccessary_info)


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

    def __add_behave_info(self,):
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
        if len(self._mouse_info[self.exp_name]["behave_trackfiles"])==0:
            print("%s is wrong",nothing is found%self.behave_dir)
                sys.exit()
        self._mouse_info[self.exp_name]["behave_trackfiles"].sort(key=sort_key)
        print("add info behave_trackfiles")
        behave_timestampdir = os.path.join(behave_dir,"*_ts.txt")
        self._mouse_info[self.exp_name]["behave_timestamps"] = [i for i in glob.glob(behave_timestampdir) if '2019111' not in i]
        self._mouse_info[self.exp_name]["behave_timestamps"].sort(key=sort_key)
        print("add info behave_timestamps")
        behave_logffiledir = os.path.join(behave_dir,"*log.csv")
        self._mouse_info[self.exp_name]["behave_logfiles"] = [i for i in glob.glob(behave_logffiledir) if '2019111' not in i]
        self._mouse_info[self.exp_name]["behave_logfiles"].sort(key=sort_key)
        print("add info behave_logfiles")
        behave_videodir = os.path.join(behave_dir,"*_labeled.mp4")
        self._mouse_info[self.exp_name]["behave_videos"] = [i for i in glob.glob(behave_videodir) if '2019111' not in i]
        self._mouse_info[self.exp_name]["behave_videos"].sort(key=sort_key)
        print("add info behave_videos")
        self._mouse_info[self.exp_name]["behave_blocknames"] = [os.path.basename(i).split('_ts.txt')[0] for i in self._mouse_info[self.exp_name]["behave_timestamps"]]
        print("add info behave_blocknames")

    def __add_videoscale(self,distance=40):
        self._mouse_info[self.exp_name]["video_scale"] = Video(self._mouse_info[self.exp_name]["behave_videos"][0]).scale(distance)

    def __check_behave_info(self):
        j1 = [i for i in ["context_orders","context_angles","ms_starts"] if i not in self.keys ]
        if j1:
            print("%s is not defined")
        j2 = [i for i in ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"] if not i in self.keys]        
        if j2:
            self.__add_behave_info()
        if not "video_scale" in self.keys:
            self.__add_videoscale()






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
        result["msblocks"] =  msblocks
        
    def dlctrack2behaveblocks(self,behave_trackfiles,behave_timestamps,behave_blocknames):
        behaveblocks=[]
        i=1 
        for behave_trackfile,behave_timestamp,behave_blockname in zip(behave_trackfiles,behave_timestamps,behave_blocknames):    
            print(f'{i}/{len(behave_trackfiles])} blocks:')
            if blockname in behave_trackfile:
                track = pd.read_hdf(behave_trackfile) #这一步比其他步骤耗时
                behaveblock=pd.DataFrame(track[track.columns[0:9]].values,
                 columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])

            if blockname in behave_timestamp:
                ts = pd.read_table(behave_timestamp,sep='\n',header=None)
                behaveblock['be_ts']=ts[0]
            behaveblocks.append(behaveblock)
            print("generate 'behaveblocks'")
            print(f"behave data of {blockname} has been constructed as DataFrame")
            i= i+1
        print("All the behave info has been constructed as a list of DataFrame. ")
        result["behaveblocks"] =  behaveblocks

    def _speed(cls,X,Y,T,s):
        speeds=[0]
        speed_angles=[0]
        for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
            distance = np.sqrt(delta_x**2+delta_y**2)
            speeds.append(distance*s/delta_t)
            speed_angles.append(cls._angle(1,0,delta_x,delta_y))
        return pd.Series(speeds),pd.Series(speed_angles) # in cm/s

    def align_msblocks_behaveblocks(self,ms_starts,msblocks,behaveblocks,alpha=0.1):
        '''
        alpha means the time miniscope need to start,we need to minus it
        '''
        for i,start in enumerate(ms_starts,0):
            delta_t = behaveblocks[i]['be_ts'][start-1]-alpha 
            #这个-0.1s即100ms指的大概是 miniscope启动大概需要100ms的时间，即miniscope的0时刻大约比led_on要晚大约100ms,
            #这是通过对比ms_ts(原始)的最大值，和视频的结束时间的出来的，如果不-0.1,差值的平均在113ms左右
            behaveblocks[i]['correct_ts']=behaveblocks[i]['be_ts']-delta_t
        print("be_ts has been corrected as correct_ts")
        aligned_msblocks_behaveblocks=[]
        i = 1
        for msblock,behaveblock in zip(msblocks,behaveblocks):
            aligned_msblocks_behaveblock = pd.DataFrame()
            aligned_msblocks_behaveblock['ms_ts'] = msblock['ms_ts']     
            print(f"{i}/{len(msblocks)} block is aligning behave DataFrame according to ms_ts...",end=' ')
            aligned_msblocks_behaveblock['be_frame']=[find_close_fast((behaveblock['correct_ts']*1000),i) for i in msblock['ms_ts']]
            print('-->aligned.',end=' ')
            aligned_msblocks_behaveblock = aligned_msblocks_behaveblock.join(behaveblock.iloc[aligned_msblocks_behaveblock['be_frame'].tolist(),].reset_index())
            aligned_msblocks_behaveblock['Headspeeds'],aligned_msblocks_behaveblock['Headspeed_angles'] = self._speed(aligned_msblocks_behaveblock['Head_x'],aligned_msblocks_behaveblock['Head_y'],aligned_msblocks_behaveblock['be_ts'],self._mouse_info[self.exp_name]["video_scale"])
            aligned_msblocks_behaveblock['Bodyspeeds'],aligned_msblocks_behaveblock['Bodyspeed_angles'] = self._(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y'],aligned_msblocks_behaveblock['be_ts'],self._mouse_info[self.exp_name]["video_scale"])
            aligned_msblocks_behaveblock['Tailspeeds'],aligned_msblocks_behaveblock['Tailspeed_angles'] = self._speed(aligned_msblocks_behaveblock['Tail_x'],aligned_msblocks_behaveblock['Tail_y'],aligned_msblocks_behaveblock['be_ts'],self._mouse_info[self.exp_name]["video_scale"])
            aligned_msblocks_behaveblock['headdirections'],aligned_msblocks_behaveblock['taildirections'], aligned_msblocks_behaveblock['arch_angles'] = direction(aligned_msblocks_behaveblock['Head_x'].tolist(),aligned_msblocks_behaveblock['Head_y'].tolist(),aligned_msblocks_behaveblock['Body_x'].tolist(),aligned_msblocks_behaveblock['Body_y'].tolist(),aligned_msblocks_behaveblock['Tail_x'].tolist(),aligned_msblocks_behaveblock['Tail_y'].tolist())
            aligned_msblocks_behaveblocks.append(aligned_msblocks_behaveblock)    
            print(f"Caculated speeds")
        result["aligned_msblocks_behaveblocks"] =  aligned_msblocks_behaveblocks

    def select_in_context(self,behave_videos,align_msblocks_behaveblocks):
        contextcoords=[]
        for video in behave_videos:
            print(os.path.basename(video),end=': ')
            masks,coords = Video(video).draw_rois(aim="in_context",count=1)
            contextcoords.append((masks,coords))
        self._mouse_info[self.exp_name]["in_context_contextcoords"]=contextcoords

        for aligned_msblocks_behaveblock, contextcoord in zip(aligned_msblocks_behaveblocks,contextcoords):
            masks = contextcoord[0][0]
            in_context = []
            for x,y in zip(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y']):
                if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                    in_context.append(0)
                else:
                    in_context.append(1)
            aligned_msblocks_behaveblock['in_context'] = in_context
        print("add condition 'in_context'")

    def TrackinZoneView(self,contextcoords,align_msblocks_behaveblocks,blocknames):
        pass

    def select_in_track(self,behave_videos,align_msblocks_behaveblocks):
        contextcoords=[]
        for video in behave_videos:
            print(os.path.basename(video),end=': ')
            masks,coords = Video(video).draw_rois(aim="in_track",count=1)
            contextcoords.append((masks,coords))
        self._mouse_info[self.exp_name]["in_track_contextcoords"]=contextcoords

        for aligned_msblocks_behaveblock, contextcoord in zip(aligned_msblocks_behaveblocks,contextcoords):
            masks = contextcoord[0][0]
            in_track = []
            for x,y in zip(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y']):
                if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                    in_track.append(0)
                else:
                    in_track.append(1)
            aligned_msblocks_behaveblock['in_track'] = in_track
        print("add condition 'in_track'")


    def run(self):
        result = self.load_result()
        try:
            result["ms_ts"] = self.load_msts(result["dff"])
        except:
            print("ms_ts and frames are not equalong ")
            sys.exit()
        if "msblocks" not in result.keys():
            self.sigraw2msblocks(result["ms_ts"],result["sigraw"],result["acceptedPool"]-1)
        if "behaveblocks" not in result.keys():
            self.dlctrack2behaveblocks(self._mouse_info[self.exp_name]["behave_trackfiles"],self._mouse_info[self.exp_name]["behave_timestamps"],self._mouse_info[self.exp_name]["behave_blocknames"])
        if "aligned_msblocks_behaveblocks" not in result.keys():
            self.aligned_msblocks_behaveblocks(self._mouse_info[self.exp_name]["ms_starts"],result["msblocks"],result["behaveblocks"])
        if "in_context" not in result["aligned_msblocks_behaveblocks"].keys():
            self.select_in_context(self._mouse_info[self.exp_name]["behave_videos"],result["aligned_msblocks_behaveblocks"])
        if "in_track" not in result["aligned_msblocks_behaveblocks"].keys():
            self.select_in_track(self._mouse_info[self.exp_name]["behave_videos"],result["aligned_msblocks_behaveblocks"])

if __name__ == "__main__":
    pass