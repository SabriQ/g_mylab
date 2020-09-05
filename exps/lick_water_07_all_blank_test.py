import sys,os
import time
import csv
from mylab.exps.Cexps import *
from matplotlib.pyplot import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
class LickWater(Exp):
    def __init__(self,port,data_dir=r"E:\linear_track",mode="all_blank",video_record=True):
        super().__init__(port,data_dir)
        self.data_dir = os.path.join(data_dir,time.strftime("%Y%m%d", time.localtime()))
        self.video_record = video_record
        self.mode = mode
        modes = ["adaptation_40cm","adaptation_60cm","adaptation_80cm","adaptation_80cm_CCC","local-global","elements-omission","train","test","all_blank"]
        if not self.mode in modes:
            print("please choose mode from %s"% modes)
            sys.exit()

        
        #plt.axes(rect, projection=None, polar=False, **kwargs)
        #rect [left, bottom, width, height]
        plt.ion()
        self.fig = plt.figure(figsize=[6,9])

##        self.fig.canvas.manager.window.move(0,0) 

        self.ax1 = plt.axes([0.15,0.55,0.75,0.4]) # ax_ITI
        self.ax1.set_title("ITI-Trial_Num")
        self.ax1.set_ylabel("ITI(s)")

        self.ax2 = plt.axes([0.15,0.05,0.75,0.4]) # ax_accuracy
        self.ax2.set_title("Accuracy(%)-Trial_Num")
        self.ax2.set_xlabel("Trial")
        self.ax2.set_ylabel("Accuracy(%)")


    def __call__(self,mouse_id):
        self.mouse_id =str(mouse_id)

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = "LickWater-"+self.mode+"-"+self.mouse_id+'-'+current_time+'_log.csv'

        self.log_path = os.path.join(self.data_dir,log_name)
        fig_name = "LickWater-"+self.mode+"-"+self.mouse_id+'-'+current_time+'.png'
        self.log_path = os.path.join(self.data_dir,log_name)
        self.fig_path = os.path.join(self.data_dir,fig_name)

        input("请按Enter开始实验:")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage","Context-Dependent-Choice",self.mode])
            writer.writerow(["exp_time",current_time])
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

            
    def graph_by_trial(self,Trial_Num,Accuracy,Choice_class,P_nose_poke,P_r_exit):
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
        plt.title(self.mouse_id+" LickWater real-time monitoring")
        self.ax1.set_title("ITI-Trial_Num")
        self.ax1.set_ylabel("ITI(s)")
        self.ax2.set_title("Accuracy(%)-Trial_Num")
        self.ax2.set_xlabel("Trial")
        self.ax2.set_ylabel("Accuracy(%)")
        x_major_locator=MultipleLocator(4)
        self.ax1.xaxis.set_major_locator(x_major_locator)
        self.ax2.xaxis.set_major_locator(x_major_locator)
        if not "0" in Trial_Num:
            ITI = np.array(P_r_exit)-np.array(P_nose_poke)

            if len(Trial_Num)>=60:
                xright=len(Trial_Num)
            else:
                xright=60
            if max(ITI)>=20:
                yup = max(ITI)
            else:
                yup=20

            colors = ["green" if i =="1" else "red" for i in Choice_class]

            self.ax1.set_ylim(1,yup)
            self.ax1.plot(Trial_Num,ITI,color='black',linestyle='-')
            self.ax1.scatter(Trial_Num,ITI,s=6,c=colors)
            #self.ax1.legend(())

            self.ax2.set_ylim(-1,105)
            self.ax2.plot(Trial_Num,Accuracy,'black')
            self.ax2.scatter(Trial_Num,Accuracy,s=6,c=colors)

            self.fig.canvas.draw()
            plt.pause(0.5)

    def save_graph(self):
            plt.savefig(self.fig_path)
            plt.ioff()
            plt.close()
            print("result fig is saved!")


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
            writer.writerow(["Trial_Num","Enter_ctx","Exit_ctx","Choice_class","Left_choice","Right_choice",
                "A_nose_poke","A_enter","A_exit","A_choice","A_r_enter","A_r_exit"
                ,"P_nose_poke","P_enter","P_exit","P_choice","P_r_enter","P_r_exit"])
        
        start_time = time.time()
        Trial_Num=[];Enter_ctx=[];Exit_ctx=[];Choice_class=[];Left_choice=[];Right_choice=[];
        A_nose_poke=[];A_enter=[];A_exit=[];A_choice=[];A_r_enter=[];A_r_exit=[];
        P_nose_poke=[];P_enter=[];P_exit=[];P_choice=[];P_r_enter=[];P_r_exit=[];
        print("Trial_Num","Enter_ctx","Exit_ctx","Choice_class","Left_choice","Right_choice")
        
        show_info = "Ready "
        Accuracy = []
        while True:
            info = self.ser.readline().decode("utf-8").strip().split(" ")
            time_elapse = time.time()-start_time
            #if time_elapse > 1200:
            #    send_wechat("%s: already 1200s"%self.mouse_id,"Trial number: %s"%Trial_Num[-1])
            print(f"\r{show_info}".ljust(55),f"{round(time_elapse,1)}s".ljust(8),end="")
            if len(info)>1:
                show_info = ' '.join([i for i in info])
                if "Stat1:" in info:
                    P_nose_poke.append(time_elapse)
                if "Stat2:" in info:
                    P_enter.append(time_elapse);            
                if "Stat3:" in info:
                    P_exit.append(time_elapse);            
                if "Stat4:" in info:
                    P_choice.append(time_elapse);            
                if "Stat5:" in info:
                    P_r_enter.append(time_elapse);            
                if "Stat6:" in info:
                    P_r_exit.append(time_elapse);            
                if "Sum:" in info and info[1] !=0:
                    Trial_Num.append(info[1])
                    Enter_ctx.append(info[2])
                    Exit_ctx.append(info[3])
                    Choice_class.append(info[4])
                    Left_choice.append(info[5])
                    Right_choice.append(info[6])

                    A_nose_poke.append(info[7])
                    A_enter.append(info[8])
                    A_exit.append(info[9])
                    A_choice.append(info[10])
                    A_r_enter.append(info[11])
                    A_r_exit.append(info[12])
                    
                    if not Trial_Num[-1]=="0":
                        row = [Trial_Num[-1],Enter_ctx[-1],Exit_ctx[-1],Choice_class[-1],Left_choice[-1],Right_choice[-1]
                        ,A_nose_poke[-1],A_enter[-1],A_exit[-1],A_choice[-1],A_r_enter[-1],A_r_exit[-1]
                        ,P_nose_poke[-1],P_enter[-1],P_exit[-1],P_choice[-1],P_r_enter[-1],P_r_exit[-1]]

                        print("\r",row[0].center(9)
                                    ,row[1].center(9)
                                    ,row[2].center(8)
                                    ,row[3].center(7)
                                    ,row[4].center(15)
                                    ,row[5].center(14))
                        show_info = "Ready "
                        
                        with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(row)

                        Accuracy.append(sum([int(i) for i in Choice_class])/len(Choice_class)*100)
                        self.graph_by_trial(Trial_Num,Accuracy,Choice_class,P_nose_poke,P_r_exit)
                    else:
                        print("\r","Terminated")
                        self.save_graph()
                        break

                if "Stat7:" in info:
                    print("\r","All Done!")

if __name__ =="__main__":
    cdc = LickWater("COM22")
    cdc(sys.argv[1])
