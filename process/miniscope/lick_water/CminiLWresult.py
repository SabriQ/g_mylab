
from mylab.process.miniscope.lick_water.Cminiresult import MiniResult as MR
from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
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

        if not self.exp_name in self.mouse_info.keys:
            self.mouse_info.add_exp(exp=self.exp_name)
            print("add json %s"%self.exp_name)

        self.behave_dir = behave_dir
        print(self.behave_dir)
        self.mouse_info.save
        # here are all the possible format of self.genesulted by CNMF
        self.ms_ts_Path=glob.glob(os.path.join(self.cnmf_result_dir,'ms_ts.pkl'))


        self.check_behave_info()


    def __add_behave_info(self):
        def sort_key(s):     
            if s:            
                try:         
                    date = re.findall('-(\d{8})-', s)[0]
                except:      
                    date = -1            
                try:         
                    HMS = re.findall('-\d{8}-(\d{6})',s)[0]
                except:      
                    HMS = -1          
                return [int(date),int(HMS)]

        behave_trackfiledir = os.path.join(self.behave_dir,"*.h5")
        behave_trackfiles= [i for i in glob.glob(behave_trackfiledir) if '2019111' not in i]
        if len(behave_trackfiles)==0:
            print("%s is wrong,nothing is found"% self.behave_dir)
            sys.exit()
        sorted(behave_trackfiles,key=sort_key)
        self.mouse_info.add_key(key="behave_trackfiles",value=behave_trackfiles,exp=self.exp_name)       
        print(behave_trackfiles)
        print("add info behave_trackfiles")

        behave_timestampdir = os.path.join(self.behave_dir,"*_ts.txt")
        print(behave_timestampdir)
        behave_timestamps = [i for i in glob.glob(behave_timestampdir) if '2019111' not in i]
        sorted(behave_timestamps,key=sort_key)
        self.mouse_info.add_key(key="behave_timestamps",value=behave_timestamps,exp = self.exp_name)
        print(behave_timestamps)
        print("add info behave_timestamps")

        behave_logffiledir = os.path.join(self.behave_dir,"*log.csv")
        behave_logfiles = [i for i in glob.glob(behave_logffiledir) if '2019111' not in i]
        sorted(behave_logfiles,key=sort_key)
        self.mouse_info.add_key(key="behave_logfiles",value=behave_logfiles,exp = self.exp_name)
        print(behave_logfiles)
        print("add info behave_logfiles")

        behave_videodir = os.path.join(self.behave_dir,"*_labeled.mp4")
        behave_videos = [i for i in glob.glob(behave_videodir) if '2019111' not in i]
        sorted(behave_videos,key=sort_key)
        self.mouse_info.add_key(key="behave_videos",value=behave_videos,exp = self.exp_name)
        print(behave_videos)
        print("add info behave_videos")

        behave_sessionnames = [os.path.basename(i).split('_ts.txt')[0] for i in behave_timestamps]
        self.mouse_info.add_key(key="behave_sessionnames",value=behave_sessionnames,exp=self.exp_name)
        print(behave_sessionnames)
        print("add info behave_sessionnames")
        self.mouse_info.save


    def __add_videoscale(self,distance=40):
        s = Video(self.mouse_info.info[self.exp_name]["behave_videos"][0]).scale(distance)
        self.mouse_info.add_key(key="video_scale",value= [s,'cm/pixel'],exp =self.exp_name)
        self.mouse_info.save
        if not "video_scale" in self.mouse_info.info[self.exp_name].keys():
            return self.__add_videoscale(distance)

    def check_behave_info(self):
        #check for ["context_orders","context_angles","ms_starts"]
        j1 = [i for i in ["context_orders","context_angles","ms_starts"] if i not in self.mouse_info.info[self.exp_name].keys() ]
        if j1:
            print("%s is not defined"% j1)
            sys.exit()
        else:
            print("%s is okay"% ["context_orders","context_angles","ms_starts"])
            

        # check for ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"] 
        j2 = [i for i in ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"] if not i in self.mouse_info.info[self.exp_name].keys()]        
        if j2:
            self.__add_behave_info()
            j3 = [i for i in ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"] if not i in self.mouse_info.info[self.exp_name].keys()]  
            if j3:
                print("behave info is not complete")
                sys.exit()
        else:
            print("%s is okay"% ["behave_trackfiles","behave_timestamps","behave_logfiles","behave_videos"])
            

        #check for ["video_scale"]
        if not "video_scale" in self.mouse_info.info[self.exp_name].keys():
            scale(self.mouse_info.info[self.exp_name]["behave_videos"][0],distance=40)
        else:
            print("%s is okay"% ["video_scale"])

    def sigraw2mssessions(self,ms_ts,sigraw,acceptedPool):
        '''
        according to ms_ts, we divided sigraw, a [(531,79031),(cell_number,frames)] numpy.ndarray into mssessions, a list of dataframe
        '''
        if sigraw.shape[1]==2: #专门为CaTraces 设置，其与sigraw的格式不同，需要np.array和np.transpose
            sigraw = np.transpose(np.array([i.tolist() for i in sigraw[:,0]]))
        print(sigraw.shape)
        sigraw = sigraw[:,acceptedPool]
        start = 0
        end=0
        len_ms_ts=[]
        mssessions=[]
        for i, ts in enumerate(ms_ts,1):
            len_ms_ts.append(len(ts))        
            start = end
            end = end+len(ts)        
            session=pd.DataFrame(sigraw[start:end,:],columns=acceptedPool)
            session['ms_ts']=ts
            print('trace and ms_ts[',start,end,']constructed as DataFrame')
            mssessions.append(session)
        print("sigraw have been constructed as a list of DataFrame as ms_ts. ")
        self.ana_result["mssessions"] =  mssessions
        
    def dlctrack2behavesessions(self,behave_trackfiles,behave_timestamps,behave_sessionnames,block_nums):
        
        behavesessions=[]
        i=1 
        for behave_trackfile,behave_timestamp,behave_sessionname,block_num in zip(behave_trackfiles,behave_timestamps,behave_sessionnames,block_nums):    
            print(f'{i}/{len(behave_trackfiles)} sessions:')
            #读取behave_trackfile
            if behave_sessionname in behave_trackfile:
                track = pd.read_hdf(behave_trackfile) #这一步比其他步骤耗时
                behavesession=pd.DataFrame(track[track.columns[0:9]].values,
                 columns=['Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh','Tail_x','Tail_y','Tail_lh'])
            #读取behave_timestamp
                
            if behave_sessionname in behave_timestamp:
                ts = pd.read_table(behave_timestamp,sep='\n',header=None)
                # if txt is encoded with utf-16
                #ts = pd.read_table(behave_timestamp,sep='\n',header=None,encoding='utf-16-le')
                behavesession['be_ts']=ts[0]
                #增加block_num
            behavesession["block_num"]=block_num

            behavesessions.append(behavesession)
            print("generate 'behavesessions'")
            print(f"behave data of {behave_sessionname} has been constructed as DataFrame")
            i= i+1
        print("All the behave info has been constructed as a list of DataFrame. ")

        self.ana_result["behavesessions"] =  behavesessions


    def align_behavesessions2mssessions(self,ms_starts,mssessions,behavesessions,alpha=0.1):
        '''
        alpha means the time miniscope need to start,we need to minus it
        '''
        for i,start in enumerate(ms_starts,0):
            delta_t = behavesessions[i]['be_ts'][start-1]-alpha 
            #这个-0.1s即100ms指的大概是 miniscope启动大概需要100ms的时间，即miniscope的0时刻大约比led_on要晚大约100ms,
            #这是通过对比ms_ts(原始)的最大值，和视频的结束时间的出来的，如果不-0.1,差值的平均在113ms左右
            behavesessions[i]['correct_ts']=behavesessions[i]['be_ts']-delta_t
        print("be_ts has been corrected as correct_ts")
        aligned2ms_behavesessions=[]
        i = 1
        for mssession,behavesession in zip(mssessions,behavesessions):
            aligned2ms_behavesession = pd.DataFrame()
            #以miniscope时间轴"ms_ts"作为reference
            aligned2ms_behavesession['ms_ts'] = mssession['ms_ts']     
            print(f"{i}/{len(mssessions)} session is aligning behave DataFrame according to ms_ts...",end=' ')
            #找到 行为学矫正时间"correct_ts"和miniscope时间"ms_ts"最相近的行为帧的索引 变为"be_frame"
            aligned2ms_behavesession['be_frame']=[find_close_fast(arr=(behavesession['correct_ts']*1000),e=k) for k in mssession['ms_ts']]
            print('-->aligned.',end=' ')
            # aligned2ms_behavesession = aligned2ms_behavesession.join(behavesession.iloc[aligned2ms_behavesession['be_frame'].tolist(),].reset_index())
            #aligned2ms_behavesession的"be_frame"作为behavesession的行索引
            aligned2ms_behavesession = aligned2ms_behavesession.join(behavesession,on="be_frame")

            aligned2ms_behavesession['Headspeeds'],aligned2ms_behavesession['Headspeed_angles'] = speed(aligned2ms_behavesession['Head_x'],aligned2ms_behavesession['Head_y'],aligned2ms_behavesession['be_ts'],0.16)
            aligned2ms_behavesession['Bodyspeeds'],aligned2ms_behavesession['Bodyspeed_angles'] = speed(aligned2ms_behavesession['Body_x'],aligned2ms_behavesession['Body_y'],aligned2ms_behavesession['be_ts'],0.16)
            aligned2ms_behavesession['Tailspeeds'],aligned2ms_behavesession['Tailspeed_angles'] = speed(aligned2ms_behavesession['Tail_x'],aligned2ms_behavesession['Tail_y'],aligned2ms_behavesession['be_ts'],0.16)
            aligned2ms_behavesession['headdirections'],aligned2ms_behavesession['taildirections'], aligned2ms_behavesession['arch_angles'] = direction(aligned2ms_behavesession['Head_x'].tolist(),aligned2ms_behavesession['Head_y'].tolist(),aligned2ms_behavesession['Body_x'].tolist(),aligned2ms_behavesession['Body_y'].tolist(),aligned2ms_behavesession['Tail_x'].tolist(),aligned2ms_behavesession['Tail_y'].tolist())
            aligned2ms_behavesessions.append(aligned2ms_behavesession)    
            print(f"Caculated speeds")
            i=i+1
        self.ana_result["aligned2ms_behavesessions"] =  aligned2ms_behavesessions

    def run(self):
        try:
            self.load_msts(l_dff = self.cnmf_result['CaTraces'][0][0].shape[0])
        except:
            print("extraction of length of Traces is wrong")
        # try:
        #     self.load_msts(self.cnmf_result['ms']["dff"])
        # except:
        #     print("ms_ts and frames are not equalong ")
        #     sys.exit()

        if "mssessions" not in self.keys:
            # self.sigraw2mssessions(self.ana_result["ms_ts"],self.cnmf_result['ms']["sigraw"],self.cnmf_result["acceptedPool"]-1)
            self.sigraw2mssessions(self.ana_result["ms_ts"],self.cnmf_result['CaTraces'],self.cnmf_result["acceptedPool"]-1)

        if "behavesessions" not in self.keys:
            self.dlctrack2behavesessions(self.mouse_info.info[self.exp_name]["behave_trackfiles"],self.mouse_info.info[self.exp_name]["behave_timestamps"],self.mouse_info.info[self.exp_name]["behave_sessionnames"],self.mouse_info.info[self.exp_name]["block_nums"])

        if "aligned2ms_behavesessions" not in self.keys:
            self.align_behavesessions2mssessions(self.mouse_info.info[self.exp_name]["ms_starts"],self.ana_result["mssessions"],self.ana_result["behavesessions"])



if __name__ == "__main__":
    lw_result = MiniLWResult(mouse_info_path=r"Z:\QiuShou\mouse_info\191086_info.txt"
        ,cnmf_result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191086\20191016_102454_all"
        ,behave_dir= r"X:\miniscope\2019*\191086")
    lw_result.run()
    # lw_result.save
