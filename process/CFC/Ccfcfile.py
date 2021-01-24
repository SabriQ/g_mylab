import numpy as np
import pandas as pd
import os,sys,csv
from mylab.Cfile import File
import warnings
class FreezingFile(File):
    def __init__(self,file_path):
        super().__init__(file_path)
        self.freezingEpochPath = os.path.join(self.dirname,'behave_video_'+self.file_name_noextension+'_epoch.csv')
        
    def _rlc(self,x):
        name=[]
        length=[]
        for i,c in enumerate(x,0):
            if i ==0:
                name.append(x[0])
                count=1
            elif i>0 and x[i] == name[-1]:
                count += 1
            elif i>0 and x[i] != name[-1]:
                name.append(x[i])
                length.append(count)
                count = 1
        length.append(count)
        return name,length

    def freezing_percentage(self,threshold = 0.005, start = 0, stop = 300,show_detail=False,percent =True,save_epoch=True): 
        data = pd.read_csv(self.file_path)
        print(data)
        print(len(data['ts']),"time points ;",len(data['Frame_No']),"frames")

        data = data.dropna(axis=0)             
        #print(f"{self.file_path}")
        data = data.reset_index()
        # slice (start->stop)
        
        #start_index
        if start>stop:
            start,stop = stop,start
            warning.warn("start time is later than stop time")
        if start >=max(data['ts']):
            warnings.warn("the selected period start is later than the end of experiment")
            sys.exit()
        elif start <=min(data['ts']):            
            start_index = 0
        else:
            start_index = [i for i in range(len(data['ts'])) if data['ts'][i]<=start and  data['ts'][i+1]>start][0]+1

        #stop_index
        if stop >= max(data['ts']):
            stop_index = len(data['ts'])-1
            warnings.warn("the selected period exceed the record time, automatically change to the end time.")
        elif stop <=min(data['ts']):
            warnings.warn("the selected period stop is earlier than the start of experiment")
            sys.exit()
        else:            
            stop_index = [i for i in range(len(data['ts'])) if data['ts'][i]<=stop and  data['ts'][i+1]>stop][0]

        selected_data = data.iloc[start_index:stop_index+1]

        values,lengthes = self._rlc(np.int64(np.array(selected_data['percentage'].tolist())<=threshold))


        
        sum_freezing_time = 0
        if save_epoch:
            with open(self.freezingEpochPath,'w+',newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["start","stop"])
        for i,value in enumerate(values,0):
            if value ==1:              
                begin = sum(lengthes[0:i])
                end = sum(lengthes[0:i+1])
                if end > len(selected_data['ts'])-1:
                    end = len(selected_data['ts'])-1
                condition = selected_data['ts'].iat[end]-selected_data['ts'].iat[begin]
                if condition >=1:
                    if show_detail:
                        print(f"{round(selected_data['ts'].iat[begin],1)}s--{round(selected_data['ts'].iat[end],1)}s,duration is {round(condition,1)}s".rjust(35,'-'))
                    if save_epoch:
                        with open(self.freezingEpochPath,'a+',newline="") as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow([selected_data['ts'].iat[begin],selected_data['ts'].iat[end]])
                    sum_freezing_time = sum_freezing_time + condition
                else:
                    sum_freezing_time = sum_freezing_time
        print(f'the freezing percentage during [{start}s --> {stop}s] is {round(sum_freezing_time*100/(stop-start),2)}% ')
        if save_epoch:
            with open(self.freezingEpochPath,'a+',newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["","",f"{round(sum_freezing_time*100/(stop-start),2)}%"])
        if  percent:
            return sum_freezing_time*100/(stop-start)
        else:
            return sum_freezing_time/(stop-start)