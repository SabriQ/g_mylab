import sys,os
import time
import csv
from mylab.exps.Cexps import *
import matplotlib.pyplot as plt
import numpy as np

class EPM(Exp):
    def __init__(self,port,data_dir=r"D:\EPM"):
        super().__init__(port,data_dir)

    def __call__(self,):
        self.run()

    def optogenetics(self):
        mouse_id = input("请输入mouse_id,并按Enter开始实验:")
        self.mouse_id = str(mouse_id)

        ## experimental process

        self.opencv_is_record()# start video record
        print(">>>without laser for 3 mins: ")
        self.ser.write("2".encode())
        self.countdown(180)
        print(">>>with laser(20HZ,5ms on and 45ms off) for 3mins: ")
        self.ser.write('1'.encode())
        self.countdown(180) 
        print(">>>without laser for 3mins: ")
        self.ser.write('2'.encode())
        self.countdown(180)


        self.opencv_is_record()# stop video record
        if EPM.is_stop == 1:
            return 0
        else:
            return self.retrieval_test()
        
    def run(self):
        '''
        '''
        behave_fourcc = cv2.VideoWriter_fourcc(*'mpeg')
        camera_behave = threading.Thread(target=self.play_video,args=(0,))
        camera_behave_save = threading.Thread(target=self.save_video,args=(0,behave_fourcc,11,(640,480),))

        exp = threading.Thread(target=self.optogenetics)
        
        camera_behave.start()
        camera_behave_save.start()
        exp.start()

        camera_behave.join()
        camera_behave_save.join()
        exp.join()
        print("main process is done!")

if __name__ =="__main__":
    lw = EPM(port=None,data_dir=r"C:\Users\qiushou\Desktop\test")
    lw()
    # 画图测试
