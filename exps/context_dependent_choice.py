import sys,os
import time
import csv
from mylab.exps.Cexps import *
class Context-Dependent-Choice(Exp):
    def __init__(self,port,data_dir=r"/home/qiushou/Documents/data/linear_track"):
        super().__init__(port)
        self.data_dir = os.path.join(data_dir,time.strftime("%Y%m%d", time.localtime()))

        plt.ion()
        self.fig = plt.figure()
        plt.title("Context-Dependent-Choice")

    def __call__(self,mouse_id):
        self.mouse_id =str(mouse_id)

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = "CDC-"+self.mouse_id+'-'+current_time+'_log.csv'

        self.log_path = os.path.join(self.data_dir,log_name)
        fig_name = "CDC"+self.mouse_id+'-'+current_time+'.png'
        self.log_path = os.path.join(self.data_dir,log_name)
        self.fig_path = os.path.join(self.data_dir,fig_name)

        input("请按Enter开始实验:")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage","Context-Dependent-Choice"])
            writer.writerow(["exp_time",current_time])

        self.lick_water()
#        self.test()
    def graph_by_trial(self,P_nose_poke,P_choice):
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
        
        pass

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
            writer.writerow(["Trial_Num","Enter_ctx","Exit_ctx","Choice_class","Left_choice","Right_choice",
                "A_nose_poke","A_enter","A_exit","A_choice","A_r_enter","A_r_exit"
                ,"P_nose_poke","P_enter","P_exit","P_choice","P_r_enter","P_r_exit"])
        
        start_time = time.time()
        Trial_Num=[];Enter_ctx=[];Exit_ctx=[];Choice_class=[];Left_choice=[];Right_choice=[];
        A_nose_poke=[];A_enter=[];A_exit=[];A_choice=[];A_r_enter=[];A_r_exit=[];
        P_nose_poke=[];P_enter=[];P_exit=[];P_choice=[];P_r_enter=[];P_r_exit=[];
        print("Trial_Num","Enter_ctx","Exit_ctx","Left_choice","Right_choice","Choice_class")
        
        show_info = "Ready "
    
        while True:
            info = self.ser.readline().decode("utf-8").strip().split(" ")
            time_elapse = time.time()-start_time
            if time_elapse > 1200:
                send_wechat("%s: already 1200s"%self.mouse_id,"Trial number: %s"%Trial_Num[-1])
            print(f"\r{show_info}".ljust(24),f"{round(time_elapse,1)}s".ljust(8),end="")
            if len(info)>1:
                show_info = ''.join([i for i in info])
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

                        print("\r",row[0:6])
                        show_info = "Ready "
                    else:
                        row=["Terminated"]
                        print("\r",row[0])

                    with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(row)

                    self.graph_by_trial(Trial_Num,P_nose_poke,P_choice)

                if "Stat7:" in info:
                    print("\r","All Done!")

if __name__ =="__main__":
    cdc = CDC("/dev/ttyUSB0")
    cdc(sys.argv[1])
