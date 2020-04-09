# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:10:53 2020

@author: Sabri
"""

import pandas as pd
import matplotlib.pyplot as plt
data  =  pd.read_csv(r"C:\Users\Sabri\Desktop\program\data\linear_track_training\stat.csv")
print(data)
plt.figure(figsize=(8,6))
plt.plot(pd.Series([1,2,3,4,5]),data.mean(axis=1),color='black',markersize=20)
plt.errorbar(pd.Series([1,2,3,4,5]),data.mean(axis=1),color='black',yerr=data.std(axis=1))
plt.plot(pd.Series([1,2,3,4,5]),data['192227'],'--',alpha=0.5)
plt.plot(pd.Series([1,2,3,4,5]),data['192228'],'--',alpha=0.5)
plt.plot(pd.Series([1,2,3,4,5]),data['192229'],'--',alpha=0.5)
plt.plot(pd.Series([1,2,3,4,5]),data['192230'],'--',alpha=0.5)
plt.plot(pd.Series([1,2,3,4,5]),data['192231'],'--',alpha=0.5)
plt.plot(pd.Series([1,2,3,4,5]),data['192232'],'--',alpha=0.5)
plt.scatter(pd.Series([1,2,3,4,5]),data.mean(axis=1),color='black',s=20)
plt.xticks([1,2,3,4,5])
plt.legend(["Average",'192227',"192228","192229","192230","192231","192232"])
#plt.axhline(y=0.7,color="gray")
plt.yticks(ticks = [0.5,0.6,0.7,0.8,0.9,1.0],labels=[50,60,70,80,90,100])
plt.xlabel("days")
plt.ylabel("Accuracy(%)")
plt.savefig(r"C:\Users\Sabri\Desktop\program\data\linear_track_training\stat.png",dpi=180)