import sys,os
import time
import csv
from mylab.exps.Cexps import *
from matplotlib.pyplot import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
class LearnLickWater(Exp):
    def __init__(self,port,data_dir=r"/home/qiushou/Documents/data/linear_track"):
        super().__init__(port,data_dir)

        plt.ion()
        self.fig = plt.figure()
        plt.title("LearnLickWater_ITI-Trial_Num")
    def __call__(self,mouse_id):
        self.mouse_id =str(mouse_id)

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = "LearnLickWater-"+self.mouse_id+'-'+current_time+'_log.csv'
        fig_name = "LearnLickWater_ITI-Trial_Num-"+self.mouse_id+'-'+current_time+'.png'
        self.log_path = os.path.join(self.data_dir,log_name)
        self.fig_path = os.path.join(self.data_dir,fig_name)

        input("请按Enter开始实验:")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage","LearnLickWater"])
            writer.writerow(["exp_time",current_time])

        self.run()
#        self.test()
    def graph_by_trial(self,Trial_Num,P_left):
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
        plt.cla()
        plt.title(self.mouse_id+" LearnLickWater_ITI-Trial_Num")
        plt.xlabel("Trial_Num")
        plt.ylabel("ITI(s)")
        x_major_locator=MultipleLocator(4)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        if not "0" in Trial_Num:            
            ITI = np.insert(np.diff(P_left),0,0)
            if len(Trial_Num)>=60:
                xright = len(Trial_Num)
            else:
                xright=60
            if max(ITI)>=20:
                yup = max(ITI)
            else:
                yup=20
            plt.xlim(1,xright)
            plt.ylim(1,yup)
            plt.plot(Trial_Num,ITI,'r-')
            plt.scatter(Trial_Num,ITI,s=2,c='green')
            self.fig.canvas.draw()
            plt.pause(0.5)
        else:
            ITI = np.insert(np.diff(P_left),0,0)
            if len(Trial_Num)>=60:
                xright = len(Trial_Num)-1
            else:
                xright=60
            if max(ITI)>=20:
                yup = max(ITI)
            else:
                yup=20
            plt.xlim(1,xright)
            plt.ylim(1,yup)
            plt.plot(Trial_Num,ITI,'r-')
            plt.scatter(Trial_Num[0:-1],ITI[0:-1],s=2,c='green')
            plt.savefig(self.fig_path) 
            plt.close()
            print("result fig is saved!")
            sys.exit()
        
    def test(self):
        while True:
            print(f"\r{time.time()}".ljust(24),end="")
    def run(self):
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


                    if not Trial_Num[-1]=="0":
                        row = [Trial_Num[-1],A_left[-1],A_enter[-1],A_exit[-1],A_right[-1],A_r_enter[-1],A_r_exit[-1],P_left[-1],P_enter[-1],P_exit[-1],P_right[-1],P_r_enter[-1],P_r_exit[-1]]

                        print("\r",row[0].ljust(8),str(round(row[7],1)).ljust(8),str(round(row[10],1)).ljust(8),"          ")
                        show_info = "Ready "
                        

                    else:
                        row = ["Terminated"]
                        print("\r",row[0])
                        
                    with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(row)
                    # if int(Trial_Num[-1])%20 == 0:
                    #     send_wechat("Trial number: %s"%Trial_Num[-1],"Null ")
                    self.graph_by_trial(Trial_Num,P_left)

                if "Stat7:" in info:
                    print("\r","All Done!")
if __name__ =="__main__":
    lw = LearnLickWater("/dev/ttyUSB0")
    lw(sys.argv[1])
    # 画图测试
