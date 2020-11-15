
import matplotlib.pyplot as plt
import glob
import numpy as np
import pandas as pd
import os,re,sys
from mylab.Cfile import File

class CPPLedPixelValue(File):
    def __init__(self,file_path):
        super().__init__(file_path)

        if not self.file_path.endswith("_ledvalue_ts.csv"):
            pirnt("wrong file input")
            sys.exit()

        self.df = pd.read_csv(self.file_path)
    
    def show_ledoff_point_num_along_thresholds(self,start=800,stop=980):
        """
        start: specified the minimum threshold
        stop: specified the maxmum threshold
        """
        threshods = np.arange(start,stop)
        points1=[]
        points2=[]

        for thre in threshods:
            points1.append(sum([ 1 if i< thre  else 0 for i in self.df["1"]]))
            points2.append(sum([ 1 if i< thre  else 0 for i in self.df["2"]]))

        plt.plot(threshods,points1)
        plt.plot(threshods,points2)
        plt.xlabel("Threshod of ROI pixel value")
        plt.ylabel("Numbers of led-off frames")
        plt.title("For choosing threshold")
        plt.legend(["led1","led2"])
        # plt.axvline(x=930,color="green",linestyle="--")
        plt.show()

    def _led_off_epoch_detection(self,trace,baseline,threshold=None):
        """
        Argument:
            trace: any timeseries data. 
            baseline: the maximum led value which could be defined as led off
            threshold: the minimus led value which should larger than the threshold.
            Given baseline and threshold, the part less than baseline part and  the minimum value of which is less than threshold 
        will be selected as the led_off epoch
        Returns
            epoch_indexes: return a list of epoches in which led value is less than baseline
        """
        trace = np.array(trace)
        points = np.reshape(np.argwhere(trace<baseline),-1)
        epoch_indexes = []
        last_epoch_index=[]
        for i in range(len(points)):
            if i == 0:
                last_epoch_index.append(points[i])
            else:
                if points[i]-points[i-1]==1:
                    last_epoch_index.append(points[i])
                else:
                    epoch_indexes.append(last_epoch_index)
                    last_epoch_index = []
                    last_epoch_index.append(points[i])
                    # if not threshold is None:
                    #     print(last_epoch_index)
                    #     if np.min(trace[last_epoch_index])<=threshold:
                    #         epoch_indexes.append(last_epoch_index)
                    #         last_epoch_index.append(points[i])
                    #     else:
                    #         last_epoch_index=[]
        if len(last_epoch_index) > 0:
            epoch_indexes.append(last_epoch_index)

        if not threshold  is None:
            accepted_epoch_index=[]
            for epoch_index in epoch_indexes:
                if len(epoch_index)>0:
                    if np.min(trace[epoch_index]<=threshold):
                        accepted_epoch_index.append(epoch_index)

            return accepted_epoch_index 
        else:
            return epoch_indexes

    def lick_water(self,baseline=(900,900),threshold=None,led1_trace=None,led2_trace=None,save=False,show=False):
        """
        Arguments:
            baseline: (led1_thresh,led2_thresh)
            led1_trace
            led2_trace
        """
        
        led1_trace = np.array(self.df["1"]) if led1_trace == None else led1_trace
        led2_trace = np.array(self.df["2"]) if led2_trace == None else led2_trace

        threshold = baseline if threshold == None else threshold
        led1_indexes = self._led_off_epoch_detection(led1_trace,baseline[0],threshold[0])
        led2_indexes= self._led_off_epoch_detection(led2_trace,baseline[1],threshold[1])

        print("led off epoch length:",len(led1_indexes),len(led2_indexes))
        # sys.exit()

        length = len(self.df)

        led1_off = []
        led1_offset = []
        for i in led1_indexes:
            led1_offset.append(i[0])
            for j in i:
                led1_off.append(j)

        print("led1 off length",len(led1_off),len(led1_offset))

        self.df["led1_off"]=[1 if i in led1_off else 0 for i in range(length)]
        self.df["led1_offset"] = [1 if i in led1_offset else 0 for i in range(length)]

        led2_off = []
        led2_offset = []
        for i in led2_indexes:
            led2_offset.append(i[0])
            for j in i:
                led2_off.append(j)

        print("led2 off length",len(led2_off),len(led2_offset))

        self.df["led2_off"]=[1 if i in led2_off else 0 for i in range(length)]
        self.df["led2_offset"] = [1 if i in led2_offset else 0 for i in range(length)]

        if show:
            plt.figure(figsize=(600,1))
            plt.plot(self.df["ts"],led1_trace,color="blue")
            for epochs_index in led1_indexes:
                if len(epochs_index)==1:
                    plt.scatter(self.df["ts"][epochs_index[0]],led1_trace[epochs_index[0]],s=20,marker="x",c="green")
                else:
                    plt.scatter(self.df["ts"][epochs_index[0]:(epochs_index[-1]+1)],led1_trace[epochs_index[0]:(epochs_index[-1]+1)],c="red",s=10)

            plt.plot(self.df["ts"],led2_trace+100,color="orange")
            for epochs_index in led2_indexes:
                if len(epochs_index)==1:
                    plt.scatter(self.df["ts"][epochs_index[0]],led2_trace[epochs_index[0]]+100,s=20,marker="x",c="green")
                else:
                    plt.scatter(self.df["ts"][epochs_index[0]:(epochs_index[-1]+1)],led2_trace[epochs_index[0]:(epochs_index[-1]+1)]+100,c="red",s=10)
        if save:
            self.df.to_csv(self.file_path,index = False,sep = ',')
            print("lick_water information has been added and saved.")
        else:
            return self.df