import sys,os
import time
import csv
from mylab.exps.Cexps import *
import matplotlib.pyploy as plt
import numpy as np
class Lick_water(Exp):
    def __init__(self,port,data_dir=r"/home/qiushou/Documents/data/linear_track"):
        super().__init__(port)
        self.data_dir = os.path.join(data_dir,time.strftime("%Y%m%d", time.localtime()))
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print("%s is created"%self.data_dir)

        

    def __call__(self,mouse_id):
        self.mouse_id =str(mouse_id)

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = "Lick_water-"+self.mouse_id+'-'+current_time+'_log.csv'
        self.log_path = os.path.join(self.data_dir,log_name)


        input("请按Enter开始实验:")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage","Lick_water"])
            writer.writerow(["exp_time",current_time])

        self.graph_by_trial()
#        self.test()
    def graph_by_trial(self):
        """
        正确率， Accuracy
        left_choice_accuracy
        right_choice_accuracy
        bias
        ITI_1
        ITI_2
        c_history
        w_history
        """
        plt.ion()
        self.fig = plt.figure()
        trial = self.lick_water()
        while True:
            try:
                Trial_Num,P_left,P_right = next()
                interval = np.array(P_right)-np.array(P_left)
            except Exception as e:
                plt.ioff()
                plt.show()
                break
            else:
                plt.cla()        
                self.line = plt.plot(Trial_Num,interval,'--')[0]
                self.fig.canvas.draw()
                plt.pause(0.5)
        
    def test(self):
        while True:
            print(f"\r{time.time()}".ljust(24),end="")
    def left_water(self):
        self.ser.writer("0".encode())
    def right_water(self):
        self.ser.writer("1".encode())
    def lick_water(self):
        '''
        学习往返舔水
        时间结构包括:
            left
            enter
            exit
            right
            r_enter
            r_exit
        '''
        with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Trial_Num","A_left","A_enter","A_exit","A_right","A_r_enter","A_r_exit","P_left","P_enter","P_exit","P_right","P_r_enter","P_r_exit"])
        
        start_time = time.time()
        Trial_Num=[];
        A_left=[];A_enter=[];A_exit=[];A_right=[];A_r_enter=[];A_r_exit=[];
        P_left=[];P_enter=[];P_exit=[];P_right=[];P_r_enter=[];P_r_exit=[];
        print("Trial_Num","left","    right")
        
        show_info = "Ready "
    
        while True:
            info = self.ser.readline().decode("utf-8").strip().split(" ")
            time_elapse = time.time()-start_time
            print(f"\r{show_info}".ljust(24),f"{round(time_elapse,1)}s".ljust(8),end="")
            if len(info)>1:
                show_info = ''.join([i for i in info])
                if "Stat1:" in info:
                    P_left.append(time_elapse)
                if "Stat2:" in info:
                    P_enter.append(time_elapse);            
                if "Stat3:" in info:
                    P_exit.append(time_elapse);            
                if "Stat4:" in info:
                    P_right.append(time_elapse);            
                if "Stat5:" in info:
                    P_r_enter.append(time_elapse);            
                if "Stat6:" in info:
                    P_r_exit.append(time_elapse);            
                if "Sum:" in info and info[1] !=0:
                    Trial_Num.append(info[1])
                    A_left.append(info[2])
                    A_enter.append(info[3])
                    A_exit.append(info[4])
                    A_right.append(info[5])
                    A_r_enter.append(info[6])
                    A_r_exit.append(info[7])
                    
                    row = [Trial_Num[-1],A_left[-1],A_enter[-1],A_exit[-1],A_right[-1],A_r_enter[-1],A_r_exit[-1],P_left[-1],P_enter[-1],P_exit[-1],P_right[-1],P_r_enter[-1],P_r_exit[-1]]

                    with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(row)
                    print("\r",row[0].ljust(8),str(round(row[7],1)).ljust(8),str(round(row[10],1)).ljust(8),"          ")
                    show_info = "Ready "
                    yield (Trial_Num,P_left,P_right)
                if "Stat7:" in info:
                    send_wechat(self.mouse_id,"finish lick_water")
if __name__ =="__main__":
    lw = Lick_water("/dev/ttyUSB0")
    lw(sys.argv[1])
