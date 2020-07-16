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

    def __call__(self,):
        self.run()

    def retrieval_test(self):
        mouse_id = input("请输入mouse_id,并按Enter开始实验:")
        self.mouse_id = str(mouse_id)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.opencv_is_record()# start video record
        print("start recording for 300s")
        self.countdown(10)
        self.opencv_is_record()# stop video record
        if CFC.is_stop == 1:
            return 0
        else:
            return self.retrieval_test()
        
    def run(self):
        '''
        '''
        behave_fourcc = cv2.VideoWriter_fourcc(*'mpeg')
        camera_behave = threading.Thread(target=self.play_video,args=(0,))
        camera_behave_save = threading.Thread(target=self.save_video,args=(0,behave_fourcc,11,(640,480),))
        exp = threading.Thread(target=self.retrieval_test)
        
        camera_behave.start()
        camera_behave_save.start()
        exp.start()
        print("main process is done!")

if __name__ =="__main__":
    lw = CFC(port=None)
    lw()
    # 画图测试
