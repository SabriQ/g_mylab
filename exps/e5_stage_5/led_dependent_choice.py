import sys,os
import time
import csv
class Led_dependent_choice(Exp):
    def __init__(self,port,mode="Train",data_dir=""):
        super().__init__(port,data_dir)
        self.video_dir = video_dir
        self.mode=mode

    def __call__(self,mouse_id):
        self.mouse_id = mouse_id
        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        video_name = self.__name__+self.mouse_id+'-'+current_time+'.mp4'
        log_name = self.__name__+self.mouse_id+'-'+current_time+'_log.csv'
        self.video_path = os.path.join(self.video_dir,video_name)
        self.log_path = os.path.join(self.video_dir,log_name)


        input("请按Enter开始实验（倒计时3s之后开启，摄像头会率先启动：")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage",self.__name__])
            writer.writerow(["exp_time",current_time])

        if self.mode == "Train":
            p = self.record_camera(self.video_path)
            self.run()
            self.stop_camera(p)
        else:
            self.run()

    def run():
        trial = self.led_dependent_choice()
        while True:
            try:
                Trial_Num,left_choice,right_choice,Choice_Class,A_NosePoke,A_Choice,P_NosePoke,P_Choice = next(trial)
                self.graph_by_trial()
            except Exception as ret:
                print(ret.value)
                break


    def graph_by_trial(self,Trial_Num,left_choice,right_choice,Choice_Class,A_NosePoke,A_Choice,P_NosePoke,P_Choice):
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

    def led_dependent_choice(self):
        '''
        一个led, flash 或者Continuous_on随机切换，做左右抉择
        '''
        with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Trial_Num","led_stat","left_choice","right_choice","Choice_Class","A_NosePoke","A_Choice","P_NosePoke","P_Choice"])
        
        start_time = time.time()
        Trial_Num=[];
        led_stat=[];
        left_choice=[];right_choice=[]
        Choice_Class=[];A_NosePoke=[];A_Choice=[];P_NosePoke=[];P_Choice=[];
        show_info = "Ready "
    
        while True:
            info = self.ser.readline().decode("utf-8").strip().split(" ")
            time_elapse = time.time()-start_time
            if len(info)>1:
                show_info = ''.join([i for i in info])
                if "Stat1:" in info:
                    P_NosePoke.append(time_elapse);            
                if "Stat2:" in info:                
                    P_Choice.append(time_elapse)
    ##                print(info)                
                    if "choice_l" in info:
                        if "correct" in info:
                            led_stat.append("flash")
                        else:
                            led_stat.append("Continuous_on")
                    elif "choice_r" in info:
                        if "correct" in info:
                            led_stat.append("Continuous_on")
                        else:
                            led_stat.append("flash")
                    else:
                        led_stat.append("terminated")
                if "Sum:" in info and info[1] !=0:

                    Trial_Num.append(info[1])
                    left_choice.append(info[2])
                    right_choice.append(info[3])
                    Choice_Class.append(info[4])
                    A_NosePoke.append(info[5])
                    A_Choice.append(info[6])
                    
                    row=[Trial_Num[-1],led_stat[-1],left_choice[-1],right_choice[-1],Choice_Class[-1],A_NosePoke[-1],A_Choice[-1],P_NosePoke[-1],P_Choice[-1]]
                    with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(row)
                    print(row[0:5])
            #时间进度输出
                if "Sum" in show_info:
                    show_info = "Ready "
                yield (Trial_Num,left_choice,right_choice,Choice_Class,A_NosePoke,A_Choice,P_NosePoke,P_Choice)
            print(f"\r{show_info}".ljust(24),f"{round(time_elapse,1)}s".ljust(8),end="")

if __name__ =="__main__":
    ldc = Led_dependent_choice("com12","C:\Users\Sabri\Desktop\test")
    ldc(191174)
