import sys,os
import time
import csv
from Cexps import *
import numpy as np

class LickWater(Exp):
    def __init__(self,port,data_dir=r"D:\cross_maze",mode="train",video_record=False):
        super().__init__(port,data_dir)
        self.data_dir = os.path.join(data_dir,time.strftime("%Y%m%d", time.localtime()))
        self.video_record = video_record
        self.mode = mode
        modes =["local-global","blank","context-switch","train","test"]
        if not self.mode in modes:
            print("please choose mode from %s"% modes)
            sys.exit()



    def __call__(self,mouse_id):
        self.mouse_id =str(mouse_id)

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = "CrossMaze-"+self.mode+"-"+self.mouse_id+'-'+current_time+'_log.csv'

        self.log_path = os.path.join(self.data_dir,log_name)
        
       
       
        input("请按Enter开始实验:")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage","TemporalContext-Dependent-Choice",self.mode])
            writer.writerow(["exp_time",current_time])
            
            
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
            writer.writerow(["Trial_Num","Choice","Choice_class","A_choice","B_choice","C_choice","D_choice",
                "A_nose_poke","P_nose_poke","seq_length"])
        
        start_time = time.time()
        Trial_Num=[];Choice=[];Choice_class=[];A_choice=[];B_choice=[];
        A_nose_poke=[];P_nose_poke=[];C_choice=[];D_choice=[];seq_length=[]
        print("Trial_Num","Choice","Choice_class")
        
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
                Choice.append(int(list(info[2])[5]))
                A_nose_poke.append(info[3])
                P_nose_poke.append(time_elapse)
                
                if "port_1" in info:
                    A_choice.append(1);
                    B_choice.append(0);
                    C_choice.append(0);
                    D_choice.append(0);
                elif "port_2" in info:
                    A_choice.append(0);
                    B_choice.append(1);
                    C_choice.append(0);
                    D_choice.append(0);           
                elif "port_3" in info:
                    A_choice.append(0);
                    B_choice.append(0);
                    C_choice.append(1);
                    D_choice.append(0);       
                elif "port_4" in info:
                    A_choice.append(0);
                    B_choice.append(0);
                    C_choice.append(0);
                    D_choice.append(1);
                else:
                    print(info)
                    break
                    A_choice.append(0);
                    B_choice.append(0);
                    C_choice.append(0);
                    D_choice.append(0);
                        
                row = [Trial_Num[-1],Choice[-1],Choice_class[-1],A_choice[-1],B_choice[-1],
        C_choice[-1],D_choice[-1],A_nose_poke[-1],P_nose_poke[-1]]
                print("\r")
                with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(row)                        
             

                
if __name__ =="__main__":
    cdc = LickWater("COM5")
    cdc.__call__(sys.argv[1])
    cdc.run()
