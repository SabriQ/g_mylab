# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 12:59:28 2020

@author: qiushou
"""

import glob
import re
import pandas as pd
import numpy as np
import csv
import os
#%%

def rlc(x):
    name=[]
    length=[]
    for i,c in enumerate(x,0):
        if i ==0:
            name.append(x[0])
            count=1
        elif i >0 and x[i] == name[-1]:
            count += 1
        elif i>0 and x[i] != name[-1]:
            name.append(x[i])
            length.append(count)
            count = 1
    length.append(count)
    return name,length

def sort_key(s):
    if s:
        date = re.findall('(\d{8})-\d{6}', s)[0]
        time = re.findall('\d{8}-(\d{6})', s)[0]
        try:
            condidates = re.findall('(\d{6})[-|_]',s)
            mouse_id = [i for i in condidates if i != time and i not in date][0]
        except:
            mouse_id = -1
    return [int(mouse_id),int(date),int(time)]

def save_behavior_readout(result_file):
    if not os.path.exists(result_file):
        f= open(result_file,'w',newline="")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["filename","mouse_id","date","time","total_trial_number","total_accuracy","right_accuracy","left_accuracy","bias","left_times","right_times"])
        f.close()
        print(f"{result_file} has been build")

    def behavior_readout(filename = r"/home/qiushou/Documents/QS_data/stage_1_training/20191231/192227-20191231-115040_log.csv",save = True):
        mouse_id,date,time = sort_key(filename)
        f = open(result_file,'a+',newline="")
        csv_writer=csv.writer(f)
        try:
            data = pd.read_csv(filename)
        except:
            print(f"{filename} is empty")
            return 0
        #print(data)
        correct_l=0
        correct_r=0
        wrong_l=0
        wrong_r=0
        for row in data.iterrows():
            row = row[1]
            if row["Choice"]=="l":
                if row["Choice_Class"]=="correct":
                    correct_l = correct_l +1
                if row["Choice_Class"]=="wrong":
                    wrong_l = wrong_l +1
            if row["Choice"]=="r":
                if row["Choice_Class"]=="correct":
                    correct_r = correct_r +1
                if row["Choice_Class"]=="wrong":
                    wrong_r = wrong_r +1                    
            
        #left_times,right_times
        total_trial_number = correct_l +correct_r +wrong_l + wrong_r
        if total_trial_number != 0:
            total_accuracy = (correct_l+correct_r)/total_trial_number
            left_times = correct_l + wrong_l
            right_times = correct_r + wrong_r
            if right_times !=0:
                right_accuracy = correct_r/right_times
            else:
                right_accuracy =0
            if left_times !=0:
                left_accuracy = correct_l/left_times
            else:
                left_accuracy = 0
            bias = (left_times-right_times)/(left_times+right_times)
            if save:
                csv_writer.writerow([filename,mouse_id,date,time,total_trial_number,total_accuracy,right_accuracy,left_accuracy,bias,left_times,right_times])
        f.close()
    return behavior_readout





