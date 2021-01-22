import sys,os
import time
import csv
from mylab.exps.Cexps import *
import numpy as np
from mylab.sys_camera import *

class LickWater(Exp):
    def __init__(self,port,data_dir=r"D:\cross_maze",mode="test",video_record=True):
        super().__init__(port,data_dir)
        self.data_dir = os.path.join(data_dir,time.strftime("%Y%m%d", time.localtime()))
        self.video_record = video_record
        self.mode = mode
        modes =["local-global","blank","context-switch","train","test"]
        if not self.mode in modes:
            print("please choose mode from %s"% modes)
            sys.exit()



    def start(self,mouse_id,context_setup):
        self.mouse_id =str(mouse_id)
        self.context_setup = str(context_setup).upper()

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = "CrossMaze-"+self.mode+"-"+self.mouse_id+'-'+current_time+'_log.csv'

        self.log_path = os.path.join(self.data_dir,log_name)
        
       
       
        input("请按Enter开始实验:")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",self.mouse_id])
            writer.writerow(["stage","TemporalContext-Dependent-Choice",self.mode])
            writer.writerow(["exp_time",current_time, "port(1,2,3,4)-context-alignment", self.context_setup])
            
        if not self.video_record:
            p = video_online_play()
            self.run()
            os.kill(p.pid,signal.SIGKILL)
        else:
            video_name = "CDC-"+self.mode+"-"+self.mouse_id+'-'+current_time+'.mp4'
            self.video_path = os.path.join(self.data_dir,video_name)
            p = video_recording(self.video_path)
            self.run()
            p.communicate("q")
            print("video is saved") 
    def graph(self,Trial_Num,Port,Context,Choice_class):
        pass
    def run(self):
        '''
        学习按序列舔水
        序列为:
            suppose start_choice is 1(A)
            2(B)
            3(C)
            4(D)
        '''
        with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Trial_Num", "Port", "Context", "Choice_class", "A_nose_poke","P_nose_poke"])
        
        start_time = time.time()
        Trial_Num=[];Port=[];Context=[];Choice_class=[];A_nose_poke=[];P_nose_poke=[];
        print("Trial_Num","Port","Context","Choice_class")
        
        show_info = "Ready "
        Accuracy = []
        while True:
            info = self.ser.readline().decode("utf-8").strip().split(" ")
            time_elapse = time.time()-start_time
            print(f"\r{show_info}".ljust(55),f"{round(time_elapse,1)}s".ljust(8),end="")
            if "Stat2:" in info:
                print("\r")
                break
            if len(info)>3:
                show_info = ' '.join([i for i in info])
                
                if "Stat0:" in info :
                    Choice_class.append(0)
                if "Stat1:" in info:
                    Choice_class.append(1)
    
                Trial_Num.append(info[0])
                port_num = int(list(info[2])[5])
                Port.append(port_num)
                Context.append(self.context_setup[port_num-1])
                A_nose_poke.append(info[3])
                P_nose_poke.append(time_elapse)
                        
                row = [Trial_Num[-1],Port[-1],Context[-1],Choice_class[-1],A_nose_poke[-1],P_nose_poke[-1]]
                print("\r", row)
                # graph(Trial_Num,Port,Context,Choice_class)
                with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(row)                        
             

                
if __name__ =="__main__":
    cdc = LickWater("COM5")
    cdc.start(sys.argv[2], sys.argv[1])
