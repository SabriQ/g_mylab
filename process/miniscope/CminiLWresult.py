from mylab.process.miniscope.Cminiresult import MiniResult as MR
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as pyplot
from mylab.Cvideo import Video
from mylab.Cmouseinfo import MouseInfo
import glob,os,sys
import math
class MiniLWResult(MR):
    def __init__(self,mouse_info_path,cnmf_result_dir,behave_dir):
        super().__init__(mouse_info_path,cnmf_result_dir)
        self.exp_name = "lick_water"

        if not self.exp_name in self._info.keys:
            self._info[self.exp_name]={}
            print("add json %s"%self.exp_name)

        self.behave_dir = behave_dir
        self._info[self.exp_name]["behave_dir"] = self.behave_dir
        print(self.behave_dir)
        self._info.save
        # here are all the possible format of self.genesulted by CNMF
        self.ms_ts_Path=glob.glob(os.path.join(self.cnmf_result_dir,'ms_ts.pkl'))


        self.neccessary_info = ["video_scale","context_orders","context_angles","ms_starts","behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"]
        self.__check_behave_info()

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

        behave_trackfiledir = os.path.join(self.behave_dir,"*.h5")
        self._info[self.exp_name]["behave_trackfiles"] = [i for i in glob.glob(behave_trackfiledir) if '2019111' not in i]
        if len(self._info[self.exp_name]["behave_trackfiles"])==0:
            print("%s is wrong,nothing is found"% self.behave_dir)
            sys.exit()
        self._info[self.exp_name]["behave_trackfiles"].sort(key=sort_key)
        print("add info behave_trackfiles")

        behave_timestampdir = os.path.join(self.behave_dir,"*_ts.txt")
        self._info[self.exp_name]["behave_timestamps"] = [i for i in glob.glob(behave_timestampdir) if '2019111' not in i]
        self._info[self.exp_name]["behave_timestamps"].sort(key=sort_key)
        print("add info behave_timestamps")

        behave_logffiledir = os.path.join(self.behave_dir,"*log.csv")
        self._info[self.exp_name]["behave_logfiles"] = [i for i in glob.glob(behave_logffiledir) if '2019111' not in i]
        self._info[self.exp_name]["behave_logfiles"].sort(key=sort_key)
        print("add info behave_logfiles")

        behave_videodir = os.path.join(self.behave_dir,"*_labeled.mp4")
        self._info[self.exp_name]["behave_videos"] = [i for i in glob.glob(behave_videodir) if '2019111' not in i]
        self._info[self.exp_name]["behave_videos"].sort(key=sort_key)
        print("add info behave_videos")

        self._info[self.exp_name]["behave_blocknames"] = [os.path.basename(i).split('_ts.txt')[0] for i in self._info[self.exp_name]["behave_timestamps"]]
        print("add info behave_blocknames")
        self._info.save


    def __add_videoscale(self,distance=40):
        s = Video(self._info[self.exp_name]["behave_videos"][0]).scale(distance)
        self._info[self.exp_name]["video_scale"] = [s,'cm/pixel']
        self._info.save
        if not "video_scale" in self._info[self.exp_name].keys():
            return self.__add_videoscale(distance)

    def __check_behave_info(self):
        j1 = [i for i in ["context_orders","context_angles","ms_starts"] if i not in self._info[self.exp_name].keys() ]
        if j1:
            print("%s is not defined"% j1)
        else:
            print("%s is okay"% ["context_orders","context_angles","ms_starts"])

        j2 = [i for i in ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"] if not i in self._info[self.exp_name].keys()]        
        if j2:
            self.__add_behave_info()
        else:
            print("%s is okay"% ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"])

        if not "video_scale" in self._info[self.exp_name].keys():
            self.__add_videoscale()
        else:
            print("%s is okay"% ["video_scale"])

    def _equal_frames(self,dff,ms_ts):
        l_dff = dff.shape[0]# or sigraw.shape[0] or sigdeconvolved.shape[0] or CaTraces.shape[0]
        l_ms_ts = sum([len(i) for i in ms_ts])
        print(">>>>>",[l_dff,l_ms_ts])
        if l_dff != l_ms_ts:
            return 0
        else:
            return 1

    def load_msts(self,dff):
        # attention to check whether frames of ms_ts are equal to that of traces
        dff = np.transpose(dff)
        with open(self.ms_ts_Path[0],'rb') as f:
            ms_ts = pickle.load(f)

        if self._equal_frames(dff,ms_ts):
            print("frames of timestaps and traces are equal!")
            self.ana_result["ms_ts"] = ms_ts
        else:
            print("please regenerate ms_ts")
            print("ms_ts: %s;frames: %s"%(dff.shape[0],sum([len(i) for i in ms_ts])))


    def sigraw2msblocks(self,ms_ts,sigraw,acceptedPool):
        '''
        according to ms_ts, we divided sigraw, a [(531,79031),(cell_number,frames)] numpy.ndarray into msblocks, a list of dataframe
        '''
        sigraw = sigraw[:,acceptedPool-1]
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
        self.ana_result["msblocks"] =  msblocks
        
    def dlctrack2behaveblocks(self,behave_trackfiles,behave_timestamps,behave_blocknames):
        behaveblocks=[]
        i=1 
        for behave_trackfile,behave_timestamp,behave_blockname in zip(behave_trackfiles,behave_timestamps,behave_blocknames):    
            print(f'{i}/{len(behave_trackfiles)} blocks:')
            if behave_blockname in behave_trackfile:
                track = pd.read_hdf(behave_trackfile) #这一步比其他步骤耗时
                behaveblock=pd.DataFrame(track[track.columns[0:9]].values,
                 columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])

            if behave_blockname in behave_timestamp:
                ts = pd.read_table(behave_timestamp,sep='\n',header=None)
                behaveblock['be_ts']=ts[0]
            behaveblocks.append(behaveblock)
            print("generate 'behaveblocks'")
            print(f"behave data of {behave_blockname} has been constructed as DataFrame")
            i= i+1
        print("All the behave info has been constructed as a list of DataFrame. ")
        self.ana_result["behaveblocks"] =  behaveblocks

    @staticmethod
    def direction(Head_X,Head_Y,Body_X,Body_Y,Tail_X,Tail_Y):
        headdirections=[] # head_c - body_c
        taildirections=[]
        arch_angles=[]
        for x1,y1,x2,y2,x3,y3 in zip(Head_X,Head_Y,Body_X,Body_Y,Tail_X,Tail_Y):
            hb_delta_x = x1-x2 # hb means head to body
            hb_delta_y = y1-y2
            headdirection = _angle(1,0,hb_delta_x,hb_delta_y)
            headdirections.append(headdirection)
            tb_delta_x = x3-x2
            tb_delta_y = y3-y2
            taildirection = _angle(1,0,tb_delta_x,tb_delta_y)
            taildirections.append(taildirection)
            arch_angle = abs(headdirection - taildirection)
            if arch_angle>180:
                arch_angle = 360-arch_angle
            arch_angles.append(arch_angle)
        return pd.Series(headdirections), pd.Series(taildirections), pd.Series(arch_angles)
    

    @staticmethod
    def _angle(dx1,dy1,dx2,dy2):
        """
    #def _angle(v1,v2)    #v1 = [0,1,1,1] v2 = [x1,y1,x2,y2]
    #    dx1 = v1[2]-v1[0]
    #    dy1 = v1[3]-v1[1]
    #    dx2 = v2[2]-v2[0]
    #    dy2 = v2[3]-v2[1]
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
    # dx1 = 1,dy1 = 0,this is sure ,because we always want to know between the varial vector with vector[0,1,1,1]
    
    @staticmethod
    def _speed(X,Y,T,s):
        speeds=[0]
        speed_angles=[0]
        for delta_x,delta_y,delta_t in zip(np.diff(X),np.diff(Y),np.diff(T)):
            distance = np.sqrt(delta_x**2+delta_y**2)
            speeds.append(distance*s/delta_t)
            speed_angles.append(self._angle(1,0,delta_x,delta_y))
        return pd.Series(speeds),pd.Series(speed_angles) # in cm/s

    @staticmethod
    def find_close_fast(arr,e):    
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
        return idx

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
            aligned_msblocks_behaveblock['be_frame']=[self.find_close_fast(arr=(behaveblock['correct_ts']*1000),e=k) for k in msblock['ms_ts']]
            print('-->aligned.',end=' ')
            aligned_msblocks_behaveblock = aligned_msblocks_behaveblock.join(behaveblock.iloc[aligned_msblocks_behaveblock['be_frame'].tolist(),].reset_index())
            aligned_msblocks_behaveblock['Headspeeds'],aligned_msblocks_behaveblock['Headspeed_angles'] = self._speed(aligned_msblocks_behaveblock['Head_x'],aligned_msblocks_behaveblock['Head_y'],aligned_msblocks_behaveblock['be_ts'],0.16)
            aligned_msblocks_behaveblock['Bodyspeeds'],aligned_msblocks_behaveblock['Bodyspeed_angles'] = self._speed(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y'],aligned_msblocks_behaveblock['be_ts'],0.16)
            aligned_msblocks_behaveblock['Tailspeeds'],aligned_msblocks_behaveblock['Tailspeed_angles'] = self._speed(aligned_msblocks_behaveblock['Tail_x'],aligned_msblocks_behaveblock['Tail_y'],aligned_msblocks_behaveblock['be_ts'],0.16)
            aligned_msblocks_behaveblock['headdirections'],aligned_msblocks_behaveblock['taildirections'], aligned_msblocks_behaveblock['arch_angles'] = self.direction(aligned_msblocks_behaveblock['Head_x'].tolist(),aligned_msblocks_behaveblock['Head_y'].tolist(),aligned_msblocks_behaveblock['Body_x'].tolist(),aligned_msblocks_behaveblock['Body_y'].tolist(),aligned_msblocks_behaveblock['Tail_x'].tolist(),aligned_msblocks_behaveblock['Tail_y'].tolist())
            aligned_msblocks_behaveblocks.append(aligned_msblocks_behaveblock)    
            print(f"Caculated speeds")
            i=i+1
        self.ana_result["aligned_msblocks_behaveblocks"] =  aligned_msblocks_behaveblocks

    def select_in_context(self,behave_videos,align_msblocks_behaveblocks):
        contextcoords=[]
        for video in behave_videos:
            print(os.path.basename(video),end=': ')
            masks,coords = Video(video).draw_rois(aim="in_context",count=1)
            contextcoords.append((masks,coords))
        self._info[self.exp_name]["in_context_contextcoords"]=contextcoords
        self._info.save
        for aligned_msblocks_behaveblock, contextcoord in zip(aligned_msblocks_behaveblocks,contextcoords):
            masks = contextcoord[0][0]
            in_context = []
            for x,y in zip(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y']):
                if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                    in_context.append(0)
                else:
                    in_context.append(1)
            self.ana_result["aligned_msblocks_behaveblocks"]['in_context'] = in_context
        print("add condition 'in_context'")

    def extract_trials_in_context(self):
        pass

    def TrackinZoneView(self,contextcoords,align_msblocks_behaveblocks,blocknames):
        pass

    def select_in_track(self,behave_videos,align_msblocks_behaveblocks):
        contextcoords=[]
        for video in behave_videos:
            print(os.path.basename(video),end=': ')
            masks,coords = Video(video).draw_rois(aim="in_track",count=1)
            contextcoords.append((masks,coords))
        self._info[self.exp_name]["in_track_contextcoords"]=contextcoords
        self._info.save

        for aligned_msblocks_behaveblock, contextcoord in zip(aligned_msblocks_behaveblocks,contextcoords):
            masks = contextcoord[0][0]
            in_track = []
            for x,y in zip(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y']):
                if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                    in_track.append(0)
                else:
                    in_track.append(1)
            self.ana_result["aligned_msblocks_behaveblocks"]['in_track'] = in_track
        print("add condition 'in_track'")


    def run(self):
        self.load_msts(self.cnmf_result['ms']["dff"])
        # try:
        #     self.load_msts(self.cnmf_result['ms']["dff"])
        # except:
        #     print("ms_ts and frames are not equalong ")
        #     sys.exit()

        if "msblocks" not in self.keys:
            self.sigraw2msblocks(self.ana_result["ms_ts"],self.cnmf_result['ms']["sigraw"],self.cnmf_result["acceptedPool"]-1)

        if "behaveblocks" not in self.keys:
            self.dlctrack2behaveblocks(self._info[self.exp_name]["behave_trackfiles"],self._info[self.exp_name]["behave_timestamps"],self._info[self.exp_name]["behave_blocknames"])

        if "aligned_msblocks_behaveblocks" not in self.keys:
            self.align_msblocks_behaveblocks(self._info[self.exp_name]["ms_starts"],self.ana_result["msblocks"],self.ana_result["behaveblocks"])

        if "in_context" not in self.ana_result["aligned_msblocks_behaveblocks"].keys():
            self.select_in_context(self._info[self.exp_name]["behave_videos"],self.ana_result["aligned_msblocks_behaveblocks"])

        if "in_track" not in self.ana_result["aligned_msblocks_behaveblocks"].keys():
            self.select_in_track(self._info[self.exp_name]["behave_videos"],self.ana_result["aligned_msblocks_behaveblocks"])

if __name__ == "__main__":
    lw = MiniLWResult(mouse_info_path=r"X:\QiuShou\mouse_info\191173_info.txt"
        ,cnmf_result_dir = r"X:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all"
        ,behave_dir= r"W:\qiushou\miniscope\2019*\191173")
    lw.run()
