import sys,os
import time
import csv
from mylab.exps.Cexps import *
from matplotlib.pyplot import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np


class CFC(Exp):

    def __init__(self,port,data_dir=r"D:\CFC"):
        super().__init__(port,data_dir)
        print("------------------jichen------------")
    def __call__(self,):
        self.run()


    def event_test(self):
        print("1HZ 1000-HZ tone for 5s")
        for i in range(5):
            self.do_tone()
            time.sleep(1)

    def event1(self):
        """
        laser and shock for 5s
        laser 1-5s
        shock 3-4
        """
        print("laser and shock for 5s")
        self.do_yellowlaser()
        self.countdown(2)
        self.do_shock()
        self.countdown(58)

    def conditioning(self):
        mouse_id = input("请输入mouse_id,并按Enter开始实验:")
        while not self.is_stop:
            self.mouse_id = str(mouse_id)
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)            

            self.opencv_is_record()# start video record
            print("start recording")
            print("preexposure for 178s")
            self.countdown(2)

            for i in range(3):
                self.event_test()

            self.countdown(2)        
            
            self.opencv_is_record()# stop video record

            if CFC.is_stop == 1:
                return 0
            else:
                return self.conditioning()


    def retrieval_test(self,duration):
        mouse_id = input("请输入mouse_id,并按Enter开始实验:")
        while not self.is_stop:
            self.mouse_id = str(mouse_id)
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                
            self.opencv_is_record()# start video record

            print("start recording for %s s"%duration)
            self.countdown(duration)

            self.opencv_is_record()# stop video record

            if CFC.is_stop == 1:
                return 0
            else:
                return self.retrieval_test()
        
    def run(self):

        behave_fourcc = cv2.VideoWriter_fourcc(*'mpeg')
        # threads 1
        camera_behave = threading.Thread(target=self.play_video,args=(0,))
        # threads 2
        camera_behave_save = threading.Thread(target=self.save_video,args=(0,behave_fourcc,30,(640,480),))
        # threads 3
        exp = threading.Thread(target=self.conditioning)
        # threads 4
        T_tone = threading.Thread(target=self.tone1,args=(1000,500,500,))
        # threads 5
        # T_shock = threading.Thread(target=self.shock,args=(2,))

        
        camera_behave.start()
        camera_behave_save.start()
        exp.start()
        T_tone.start()
        # T_shock.start()
        
        print("main process is done!")

if __name__ =="__main__":
    lw = CFC(port=None,data_dir=r"C:\Users\qiushou\Desktop\test")
    lw()
    # 画图测试
