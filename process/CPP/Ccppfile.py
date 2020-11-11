
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

        self.df = pd.read_csv(self.file_path)
    
    def show_change_along_thresholds(self,v1=800,v2=980):
        """
        v1: specified the minimum threshold
        v2: specified the maxmum threshold
        """
        threshods = np.arange(v1,v2)
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

    def _led_off_epoch_detection(self,trace,thresh):
        """
        trace: any timeseries data. 
        thresh: the minimum absolute deviation from baseline, which could be negtive.
        """
        trace = np.array(trace)
        points = np.reshape(np.argwhere(trace<thresh),-1)
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
                    last_epoch_index=[]
                    last_epoch_index.append(points[i])        
        return epoch_indexes

    def lick_water(self,thresh=(900,900),led1_trace=None,led2_trace=None,save=True,show=False):
        """
        Arguments:
            thresh: (led1_thresh,led2_thresh)
            led1_trace
            led2_trace
        """
        
        led1_trace = self.df["1"] if led1_trace == None else led1_trace
        led2_trace = self.df["2"] if led2_trace == None else led2_trace

        led1_indexes = self._led_off_epoch_detection(led1_trace,thresh[0])
        led2_indexes= self._led_off_epoch_detection(led2_trace,thresh[1])

        led1_off = []
        led1_offset = []
        for i in led1_indexes:
            led1_offset.append(i[0])
            for j in i:
                led1_off.append(j)

        self.df["led1_off"]=[1 if i in led1_off else 0 for i in range(len(self.df))]
        self.df["led1_offset"] = [1 if i in led1_offset else 0 for i in range(len(self.df))]

        led2_off = []
        led2_offset = []
        for i in led2_indexes:
            led2_offset.append(i[0])
            for j in i:
                led2_off.append(j)

        self.df["led2_off"]=[1 if i in led2_off else 0 for i in range(len(self.df))]
        self.df["led2_offset"] = [1 if i in led2_offset else 0 for i in range(len(self.df))]

        if show:
            plt.figure(figsize=(600,1))
            plt.plot(self.df["ts"],led1_trace,color="orange")
            for epochs_index in led1_indexes:
                if len(epochs_index)==1:
                    plt.scatter(self.df["ts"][epochs_index[0]],led1_trace[epochs_index[0]],s=20,marker="x",c="green")
                else:
                    plt.plot(self.df["ts"][epochs_index[0]:(epochs_index[-1]+1)],led1_trace[epochs_index[0]:(epochs_index[-1]+1)],color="red")

            plt.plot(self.df["ts"],led2_trace+1000,color="blue")
            for epochs_index in led2_indexes:
                if len(epochs_index)==1:
                    plt.scatter(self.df["ts"][epochs_index[0]],led2_trace[epochs_index[0]]+1000,s=20,marker="x",c="green")
                else:
                    plt.plot(self.df["ts"][epochs_index[0]:(epochs_index[-1]+1)],led2_trace[epochs_index[0]:(epochs_index[-1]+1)]+1000,color="red")
        if save:
            self.df.to_csv(self.file_path,index = False,sep = ',')
            print("lick_water information has been added and saved.")
        else:
            return self.df