import sys,os
import time
import csv
class Lick_water(Exp):
    def __init__(self,port,data_dir=r"/home/qiushou/Documents/data/linear_track"):
        super().__init__(port)
        self.data_dir = data_dir

    def __call__(self,mouse_id):
        self.mouse_id = mouse_id

        current_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        log_name = self.__name__+self.mouse_id+'-'+current_time+'_log.csv'
        self.log_path = os.path.join(self.data_dir,log_name)


        input("请按Enter开始实验（倒计时3s之后开启，摄像头会率先启动：")

        with open(self.log_path, 'w',newline="",encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["mouse_id",mouse_id])
            writer.writerow(["stage",self.__name__])
            writer.writerow(["exp_time",current_time])

        self.run()

    def run():
        trial = self.lick_water()
        while True:
            try:
                Trial_Num,P_left,P_right = next(lick_water)
                self.graph_by_trial(P_left,P_right)
            except Exception as ret:
                print(ret.value)
                break


    def graph_by_trial(self,P_left,P,right):
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
            writer.writerow(["Trial_Num","A_left","A_enter","A_exit","A_right","A_r_enter","A_r_exit","P_left","P_enter","P_exit","P_right","P_r_enter","P_r_exit"])
        
        start_time = time.time()
        Trial_Num=[];
        A_left=[];A_enter=[];A_exit=[];A_right=[];A_r_enter=[];A_r_exit=[];
        P_left=[];P_enter=[];P_exit=[];P_right=[];P_r_enter=[];P_r_exit=[];
        
        
        show_info = "Ready "
    
        while True:
            info = self.ser.readline().decode("utf-8").strip().split(" ")
            time_elapse = time.time()-start_time
            if len(info)>1:
                show_info = ''.join([i for i in info])
                if "Stat1:" in info:
                    P_left.append(time_elapse);            
                if "Stat2:" in info:
                    P_enter.append(time_elapse);            
                if "Stat3:" in info:
                    P_exit.append(time_elapse);            
                if "Stat4:" in info:
                    P_right.append(time_elapse);            
                if "Stat5:" in info:
                    P_r_enter.append(time_elapse);            
                if "Stat:" in info:
                    P_r_exit.append(time_elapse);            
                if "Sum:" in info and info[1] !=0:

                    Trial_Num.append(info[1])
                    A_left.append(info[2])
                    A_enter.append(info[3])
                    A_exit.append(info[4])
                    A_right.append(info[5])
                    A_r_enter(info[6])
                    A_r_exit(info[7])
                    
                    row=[Trial_Num[-1],
                        A_left[-1],A_enter[-1],A_exit[-1],A_right[-1],A_r_enter[-1],A_r_exit[-1],
                        P_left[-1],P_enter[-1],P_exit[-1],P_right[-1],P_r_enter[-1],P_r_exit[-1]]

                    with open(self.log_path,"a",newline="\n",encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(row)
                    print(row[0],row[7],row[10])
            #时间进度输出
                if "Sum" in show_info:
                    show_info = "Ready "
                yield (Trial_Num,P_left,P_right)
            print(f"\r{show_info}".ljust(24),f"{round(time_elapse,1)}s".ljust(8),end="")

if __name__ =="__main__":
    ldc = Led_dependent_choice("/dev/tteUSB0","")
    ldc(191174)
