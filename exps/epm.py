from mylab.video.Cvideo import Video
import pandas as pd
import numpy as np
import sys,os
import glob
import csv
import matplotlib.pyplot as plt
import cv2
#######
videolists = glob.glob(r"C:\Users\Sabri\Desktop\test\*mp4")
##print(videolists)
h5lists = glob.glob(r"C:\Users\Sabri\Desktop\test\*h5")
##print(h5lists)
ts_lists = glob.glob(r"C:\Users\Sabri\Desktop\test\*txt")
##print(ts_lists)

def Count(masks,X,Y,T):
    time = {}
    distance = {} # in pixel
    for i in range(len(masks)):
        time[i+1]=0
        distance[i+1]=0
    time["others"]=0
    distance["others"]=0
    count = 0

    for x,y in zip(X,Y):
        if count >0:
            delt_t = T[count]-T[count-1]
            delt_d = np.sqrt((X[count]-X[count-1])**2+(Y[count]-Y[count-1])**2)
            target_masks = np.add(np.where(np.array([sum(masks[j][int(round(y)),int(round(x))]) for j in range(len(masks))])==0)[0],1)
            if len(target_masks):
                for target_mask in target_masks:
                    time[target_mask] = delt_t + time[target_mask]
                    distance[target_mask] =delt_d +distance[target_mask]
            else:
                time['others']=delt_t+time['others']
                distance['others'] = delt_d + distance['others']            
              
        count = count +1
    return time,distance
                    
        
        
for h5list in h5lists:
    f = pd.read_hdf(h5list)
##    print(f.DeepCut_resnet50_ephy_si_mp4Jun9shuffle1_500000.)
    X =np.array(f.DeepCut_resnet50_ephy_si_mp4Jun9shuffle1_500000.Body['x'])
    Y =np.array(f.DeepCut_resnet50_ephy_si_mp4Jun9shuffle1_500000.Body['y'])
    L = np.array(f.DeepCut_resnet50_ephy_si_mp4Jun9shuffle1_500000.Body['likelihood'])
    ts_list = [i for i in ts_lists if os.path.basename(h5list)[0:12] in i]

    T = np.array(pd.read_csv(ts_list[0],sep='\n',encoding='utf-16',header=None)[0])
    Frame_No = np.linspace(1,len(T),len(T),dtype=np.int16)

    videolist = [i for i in videolists if os.path.basename(h5list)[0:14] in i]
##    plt.scatter(X,Y)
##    plt.show()
    if videolist:
        masks,coords = Video(videolist[0]).draw_rois(aim="epm")
##        for i,mask in enumerate(masks,1):
##            cv2.imshow(f"test{i}",mask)
    else:
        print(f'{videolist[0]} does exist!')
        sys.exit()

    time,distance = Count(masks,X,Y,T)
    print(f'{os.path.basename(videolist[0])} process done.')
    output_head = ["head"]+[str(key)+"_time" for key,value in time.items()]+[str(key)+"_distance" for key,value in distance.items()]
    output_count= [os.path.basename(videolist[0])]+[value for key,value in time.items()]+[value for key,value in distance.items()]
    with open(os.path.join(os.path.dirname(videolist[0]),"output.csv"),'a+') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(output_head)
        f_csv.writerow(output_count)



    
