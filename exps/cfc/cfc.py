import sys,os
import time
import csv
from mylab.exps.Cexps import Exp
from matplotlib.pyplot import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
from multiprocessing import Process,Queue
import cv2

class CFC(Exp):
    def __init__(self,port,data_dir=r"D:\CFC"):
        super(CFC,self).__init__(port,data_dir)

    def __call__(self,):
        self.run()


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
        self.countdown(3)

    def event2(self):
        """
        bluelaser and shock for 2s
        laser and shock start at the same time, and persistant for 2s.
        """
        self.do_bluelaser()
        self.do_shock()
        self.countdown(2)


    def experiment(self):
        mouse_id = input("请输入mouse_id,并按Enter开始实验:")
        if not self.is_stop:
            print("")
            self.mouse_id = str(mouse_id)
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)            

            self.opencv_is_record()# start video record
            
            print("preexposure for 178s")
            self.countdown(2)

            self.event2()
            

            self.countdown(2)        
            
            self.opencv_is_stop()# stop video record

            if CFC.is_stop == 1:
                return 0
            else:
                return self.conditioning()


    def run(self,):
        """
        this is just a demo
        """
        camera_behave = Thread(target=self.play_video,args=(0,))
        behave_fourcc = cv2.VideoWriter_fourcc(*'XVID') # (*'mpeg')
        camera_behave_save = Thread(target=self.save_video,args=(0,behave_fourcc,10,(640,480),))
        exp = Thread(target=self.experiment)
        shock = Thread(target=self.shock,args=(2,))
        bluelaser= Thread(target=self.bluelaser,args=(2,))

        camera_behave.start()
        camera_behave_save.start()
        shock.start()
        bluelaser.start()
        exp.start()


        camera_behave.join()
        camera_behave_save.join()
        shock.oin()
        bluelaser.join()
        exp.join()

        print("main process is done!")

if __name__ =="__main__":
    lw = CFC(port="COM27",data_dir=r"C:\Users\dell\Desktop\test")
    lw()
    # 画图测试
