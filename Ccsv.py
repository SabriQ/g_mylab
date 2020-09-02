import matplotlib.pyplot as plt
import os,sys
import pandas as pd
import numpy as np
import warnings
import csv
import seaborn as sns
from scipy import stats
class Csv():
    def __init__(self,csvPath):
        self.csvPath = csvPath        
        self.freezingEpochPath = os.path.join(os.path.dirname(csvPath),'behave_video_'+os.path.splitext(os.path.basename(csvPath))[0]+'epoch.csv')
        print(self.freezingEpochPath)
    def _rlc(self,x):
        name=[]
        length=[]
        for i,c in enumerate(x,0):
            if i ==0:
                name.append(x[0])
                count=1
            elif i>0 and x[i] == name[-1]:
                count += 1
            elif i>0 and x[i] != name[-1]:
                name.append(x[i])
                length.append(count)
                count = 1
        length.append(count)
        return name,length

        
    def Cpa_figure(self):        
        df = pd.read_csv(self.csvPath)
        data = df.loc[:,['day','mouse_id','score','state','group']]
        fig = plt.figure("",(15,5))
        # P = T(black) / (T(black)+T(white))
        plt.subplot2grid((1,3),(0,0),colspan=2)
        x = pd.unique(data['day'])
        for mouse in pd.unique(data['mouse_id']):            
            y=data['score'].loc[data['mouse_id']==mouse ].values
            if pd.unique(data['group'].loc[data['mouse_id']==mouse])=='mCherry':
                plt.plot(x,y,color='red')
            if pd.unique(data['group'].loc[data['mouse_id']==mouse])=='NpHR':
                plt.plot(x,y,color='green')
        plt.ylabel("P=T(black)/(T(black)+T(white))")
        plt.title("")
        
        #CPA-score with errorbar
        plt.subplot2grid((1,3),(0,2),colspan=1)
        
        pre = data.loc[data['state']=="pre"]
        post = data.loc[data['state']=="post"]
        temp = pre['score'].values - post['score'].values
        CPA_index = pre.loc[:,['mouse_id','group']]
        CPA_index['index'] = temp
        y = CPA_index.groupby(['group','mouse_id']).mean().reset_index()
        x = y['group'].values
        print(x)
        y_points = y['index'].values
        print(y)
    
        
##        plt.bar(pd.unique(x),y_mean,color=['green','red'])
        for xi,yi in zip(x,y_points):
            if xi=='NpHR':
                plt.plot(xi,yi,'g.')
            else:
                plt.plot(xi,yi,'r.')
        plt.axhline(0,color='gray',alpha=0.2,linestyle='--')

        index_mean_NpHR = np.mean(y['index'].loc[y['group']=='NpHR'])
        index_std_NpHR = np.std(y['index'].loc[y['group']=='NpHR'])
        plt.errorbar(['NpHR'],index_mean_NpHR,yerr=index_std_NpHR,color='black',elinewidth=1,capsize=2)
        index_mean_mCherry = np.mean(y['index'].loc[y['group']=='mCherry'])
        index_std_mCherry = np.std(y['index'].loc[y['group']=='mCherry'])
        plt.errorbar(['mCherry'],index_mean_mCherry,yerr=index_std_mCherry,color='black',elinewidth=1,capsize=2)
        
        plt.xlim(-0.5,1.5)
        plt.ylim(-0.2,1)
        plt.ylabel("CPA-score")
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=0.5, hspace=None)
        
        a = y['index'].loc[y['group']=="NpHR"]
        b = y['index'].loc[y['group']=="mCherry"]
        
        print("方差齐次性检验：",stats.levene(a,b))
        print("t.test: ",stats.ttest_ind(a,b))
        print("wilcox: ",stats.ranksums(a,b))
        print("NpHR: ",len(a),"; mCherry: ",len(b))
        plt.show()
              

    def Novel_context(self):
        df = pd.read_csv(self.csvPath)
        data = df.loc[:,['location','batch','mouse_id','day','group','distance_in_pixel']]
        data_aca3 = data.loc[data['location']=='aCA3'] # 7 batches 
        data_ica3 = data.loc[data['location']=='iCA3'] # 6 batches

        # for aca3 --> dpca1 projections
        mCherry_day1_means=[]
        samples = data_aca3.groupby(['batch','day','group'],as_index=False).mean()        
           
        fig = plt.figure()
        
        batches_aca3 = pd.unique(data_aca3['batch'])
        ## for each batch
        for i in range(len(batches_aca3)):
            plt.subplot(2,4,i+1)
        ###for average bar
            sample = samples.loc[samples['batch'] == batches_aca3[i]]            
##            x = pd.unique(sample['day'].values)
            x=np.array([1,2])
            
            mCherry_day1_mean = sample['distance_in_pixel'].loc[sample['day']=='day1'].loc[sample['group']=='mCherry'].values

            y_NpHR = sample['distance_in_pixel'].loc[sample['group']=='NpHR'].values
            y_mCherry = sample['distance_in_pixel'].loc[sample['group']=='mCherry'].values
            plt.ylim(0,2)
            plt.axhline(1,linestyle='--',color='gray',alpha=0.3)
            plt.yticks([0,0.5,1,1.5])
            plt.xticks([1,2],["day1","day2"])
            plt.bar(x-0.15,y_NpHR/mCherry_day1_mean,width=0.3,color='green',alpha=0.5)
            plt.bar(x+0.15,y_mCherry/mCherry_day1_mean,width=0.3,color='red',alpha=0.5)

        ###for scatter
            points = data_aca3.loc[data_aca3['batch'] == batches_aca3[i]]
            points_NpHR_x = pd.factorize(points['day'].loc[points['group']=='NpHR'].values)[0]+1            
            points_NpHR_y = points['distance_in_pixel'].loc[points['group']=='NpHR'].values/mCherry_day1_mean
            
            mCherry_day1_means.append((batches_aca3[i],mCherry_day1_mean))
            
            points_mCherry_x = pd.factorize(points['day'].loc[points['group']=='mCherry'].values)[0]+1
            points_mCherry_y = points['distance_in_pixel'].loc[points['group']=='mCherry'].values/mCherry_day1_mean
            
            plt.plot(points_NpHR_x-0.15,points_NpHR_y,'.',color='green')
            plt.plot(points_mCherry_x+0.15,points_mCherry_y,'.',color='red')


        ##for all batches
        ###normalize distance_in_pixel
        distance_norm=[]
        for batch,distance in zip(data_aca3['batch'],data_aca3['distance_in_pixel']):
            index = np.where(np.array([i[0] for i in mCherry_day1_means])==batch)[0][0]
            distance_norm.append(distance/[i[1] for i in mCherry_day1_means][index][0])
        data_aca3['distance_norm']=distance_norm
        ###for bar plot
        all_samples = data_aca3.groupby(['day','group'],as_index=False).mean()

        plt.subplot(2,4,8)
        x = np.array([1,2])
        y_NpHR_all = all_samples['distance_norm'].loc[all_samples['group']=='NpHR'].values
        y_mCherry_all = all_samples['distance_norm'].loc[all_samples['group']=='mCherry'].values
        plt.bar(x-0.15,y_NpHR_all,width=0.3,color='green',alpha=0.5)
        plt.bar(x+0.15,y_mCherry_all,width=0.3,color='red',alpha=0.5)

        plt.ylim(0,2)
        plt.yticks([0,0.5,1,1.5])
        plt.xticks([1,2],["day1","day2"])

        
        ###for errorbar
        sd_samples = data_aca3['distance_norm'].groupby([data_aca3['day'],data_aca3['group']]).std().reset_index()
 
        plt.errorbar(1-0.15,y_NpHR_all[0],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='NpHR'].loc[sd_samples['day']=='day1'],color='black',elinewidth=1,capsize=2)
        plt.errorbar(2-0.15,y_NpHR_all[1],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='NpHR'].loc[sd_samples['day']=='day2'],color='black',elinewidth=1,capsize=2)

        plt.errorbar(1+0.15,y_mCherry_all[0],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='mCherry'].loc[sd_samples['day']=='day1'],color='black',elinewidth=1,capsize=2)
        plt.errorbar(2+0.15,y_mCherry_all[1],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='mCherry'].loc[sd_samples['day']=='day2'],color='black',elinewidth=1,capsize=2)

        ###for scatter
        
        all_NpHR_x = pd.factorize(data_aca3['day'].loc[data_aca3['group']=='NpHR'].values)[0]+1
        all_NpHR_y = data_aca3['distance_norm'].loc[data_aca3['group']=='NpHR'].values
        all_mCherry_x = pd.factorize(data_aca3['day'].loc[data_aca3['group']=='mCherry'].values)[0]+1
        all_mCherry_y = data_aca3['distance_norm'].loc[data_aca3['group']=='mCherry'].values

        plt.plot(all_NpHR_x-0.15,all_NpHR_y,'.',color='green',alpha=0.3,zorder=1)
        plt.plot(all_mCherry_x+0.15,all_mCherry_y,'.',color='red',alpha=0.3,y=1)

        #for statistic
        out_stat_aca3 = pd.DataFrame({
            "NpHR_day1":data_aca3['distance_norm'].loc[data_aca3['group']=='NpHR'].loc[data_aca3['day']=="day1"].values,
            "NpHR_day2":data_aca3['distance_norm'].loc[data_aca3['group']=='NpHR'].loc[data_aca3['day']=="day2"].values,
            "mCherry_day1":data_aca3['distance_norm'].loc[data_aca3['group']=='NpHR'].loc[data_aca3['day']=="day1"].values,
            "mCherry_day2":data_aca3['distance_norm'].loc[data_aca3['group']=='NpHR'].loc[data_aca3['day']=="day2"].values})
        out_stat_aca3.to_csv(r'C:\Users\Sabri\Desktop\out_stat_aca3.csv',sep=",",index=False)

        
        
        
       
   
##        plt.show()
#####################################################################################################
        # for ica3 --> vpca1 projections
        mCherry_day1_means=[]
        samples = data_ica3.groupby(['batch','day','group'],as_index=False).mean()        
           
        fig = plt.figure()
        
        batches_ica3 = pd.unique(data_ica3['batch'])
        ## for each batch
        for i in range(len(batches_ica3)):
            plt.subplot(2,4,i+1)
        ###for average bar
            sample = samples.loc[samples['batch'] == batches_ica3[i]]            
##            x = pd.unique(sample['day'].values)
            x=np.array([1,2])
            
            mCherry_day1_mean = sample['distance_in_pixel'].loc[sample['day']=='day1'].loc[sample['group']=='mCherry'].values

            y_NpHR = sample['distance_in_pixel'].loc[sample['group']=='NpHR'].values
            y_mCherry = sample['distance_in_pixel'].loc[sample['group']=='mCherry'].values
            plt.ylim(0,2)
            plt.axhline(1,linestyle='--',color='gray',alpha=0.3)
            plt.yticks([0,0.5,1,1.5])
            plt.xticks([1,2],["day1","day2"])
            plt.bar(x-0.15,y_NpHR/mCherry_day1_mean,width=0.3,color='green',alpha=0.5)
            plt.bar(x+0.15,y_mCherry/mCherry_day1_mean,width=0.3,color='red',alpha=0.5)

        ###for scatter
            points = data_ica3.loc[data_ica3['batch'] == batches_ica3[i]]
            points_NpHR_x = pd.factorize(points['day'].loc[points['group']=='NpHR'].values)[0]+1            
            points_NpHR_y = points['distance_in_pixel'].loc[points['group']=='NpHR'].values/mCherry_day1_mean
            
            mCherry_day1_means.append((batches_ica3[i],mCherry_day1_mean))
            
            points_mCherry_x = pd.factorize(points['day'].loc[points['group']=='mCherry'].values)[0]+1
            points_mCherry_y = points['distance_in_pixel'].loc[points['group']=='mCherry'].values/mCherry_day1_mean
            
            plt.plot(points_NpHR_x-0.15,points_NpHR_y,'.',color='green')
            plt.plot(points_mCherry_x+0.15,points_mCherry_y,'.',color='red')

 
        ##for all batches
        ###normalize distance_in_pixel
        distance_norm=[]
        for batch,distance in zip(data_ica3['batch'],data_ica3['distance_in_pixel']):
            index = np.where(np.array([i[0] for i in mCherry_day1_means])==batch)[0][0]
            distance_norm.append(distance/[i[1] for i in mCherry_day1_means][index][0])
        data_ica3['distance_norm']=distance_norm
        ###for bar plot
        all_samples = data_ica3.groupby(['day','group'],as_index=False).mean()

        plt.subplot(2,4,8)
        x = np.array([1,2])
        y_NpHR_all = all_samples['distance_norm'].loc[all_samples['group']=='NpHR'].values
        y_mCherry_all = all_samples['distance_norm'].loc[all_samples['group']=='mCherry'].values
        plt.bar(x-0.15,y_NpHR_all,width=0.3,color='green',alpha=0.5)
        plt.bar(x+0.15,y_mCherry_all,width=0.3,color='red',alpha=0.5)

        plt.ylim(0,2)
        plt.yticks([0,0.5,1,1.5])
        plt.xticks([1,2],["day1","day2"])

        
        ###for errorbar
        sd_samples = data_ica3['distance_norm'].groupby([data_ica3['day'],data_ica3['group']]).std().reset_index()
 
        plt.errorbar(1-0.15,y_NpHR_all[0],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='NpHR'].loc[sd_samples['day']=='day1'],color='black',elinewidth=1,capsize=2)
        plt.errorbar(2-0.15,y_NpHR_all[1],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='NpHR'].loc[sd_samples['day']=='day2'],color='black',elinewidth=1,capsize=2)

        plt.errorbar(1+0.15,y_mCherry_all[0],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='mCherry'].loc[sd_samples['day']=='day1'],color='black',elinewidth=1,capsize=2)
        plt.errorbar(2+0.15,y_mCherry_all[1],yerr=sd_samples['distance_norm'].loc[sd_samples['group']=='mCherry'].loc[sd_samples['day']=='day2'],color='black',elinewidth=1,capsize=2)

        ###for scatter
        
        all_NpHR_x = pd.factorize(data_ica3['day'].loc[data_ica3['group']=='NpHR'].values)[0]+1
        all_NpHR_y = data_ica3['distance_norm'].loc[data_ica3['group']=='NpHR'].values
        all_mCherry_x = pd.factorize(data_ica3['day'].loc[data_ica3['group']=='mCherry'].values)[0]+1
        all_mCherry_y = data_ica3['distance_norm'].loc[data_ica3['group']=='mCherry'].values

        plt.plot(all_NpHR_x-0.15,all_NpHR_y,'.',color='green',alpha=0.3,zorder=1)
        plt.plot(all_mCherry_x+0.15,all_mCherry_y,'.',color='red',alpha=0.3,zorder=1)#
        
        out_stat_ica3 = pd.DataFrame({
            "NpHR_day1":data_ica3['distance_norm'].loc[data_ica3['group']=='NpHR'].loc[data_ica3['day']=="day1"].values,
            "NpHR_day2":data_ica3['distance_norm'].loc[data_ica3['group']=='NpHR'].loc[data_ica3['day']=="day2"].values,
            "mCherry_day1":data_ica3['distance_norm'].loc[data_ica3['group']=='NpHR'].loc[data_ica3['day']=="day1"].values,
            "mCherry_day2":data_ica3['distance_norm'].loc[data_ica3['group']=='NpHR'].loc[data_ica3['day']=="day2"].values})
        out_stat_ica3.to_csv(r'C:\Users\Sabri\Desktop\out_stat_ica3.csv',sep=",",index=False)
        plt.show()
        
    def Novel_context2(self):
        df = pd.read_csv(self.csvPath)
        data = df.loc[:,['location','batch','mouse_id','day','group','distance_in_pixel']]
##        data_aca3 = data.loc[data['location']=='aCA3'] # 7 batches 
##        data_ica3 = data.loc[data['location']=='iCA3'] # 6 batches
        distance_ratio = []
##        for mouse,day,distance in zip(data['mouse_id'],data['day'],data['distance_in_pixel']):
        data_day1 = data.loc[data['day']=="day1"]
        data_day2 = data.loc[data['day']=="day2"]
        distance_ratio = np.array(data_day2['distance_in_pixel'])/np.array(data_day1['distance_in_pixel'])
        new_data = data_day1.loc[:,['location','batch','mouse_id','day','group']]
        new_data["distance_ratio"] = distance_ratio
        
        #for aCA3
        aCA3_count=1
        iCA3_count=9
        for batch in pd.unique(new_data['batch']):
            df = new_data.loc[new_data['batch']==batch].sort_values(by='group')
            
            
            if 'aCA3' in pd.unique(df['location']):            
                plt.subplot(4,4,aCA3_count)
                aCA3_count+=1
                for x,y in zip(df['group'],df['distance_ratio']):
                    if x == 'NpHR':
                        plt.plot(x,y,'.',color="green")
                    else:
                        plt.plot(x,y,'.',color='red')
                plt.title('each-aca3')
                plt.xlim([-0.5,1.5])               
                plt.ylim(0,2)
                
            if 'iCA3' in pd.unique(df['location']):            
                plt.subplot(4,4,iCA3_count)
                iCA3_count+=1
                for x,y in zip(df['group'],df['distance_ratio']):
                    if x == 'NpHR':
                        plt.plot(x,y,'.',color="green")
                    else:
                        plt.plot(x,y,'.',color='red')
                plt.title('each-ica3')
                plt.xlim([-0.5,1.5]) 
                plt.ylim(0,1.5)
                
        df2 = new_data.loc[new_data['location']=='aCA3'].sort_values(by='group')
        plt.subplot(4,4,8)
        for x,y in zip(df2['group'],df2['distance_ratio']):
            if x == 'NpHR':
                plt.plot(x,y,'.',color="green",zorder=1,alpha=0.2)
            else:
                plt.plot(x,y,'.',color='red',zorder=1,alpha=0.2)
                
        sd_NpHR = np.std(df2['distance_ratio'].loc[df2['group']=='NpHR'])
        mean_NpHR = np.mean(df2['distance_ratio'].loc[df2['group']=='NpHR'])
        plt.errorbar(['NpHR'],mean_NpHR,yerr=sd_NpHR,color='black',elinewidth=1,capsize=2)
        
        sd_mCherry = np.std(df2['distance_ratio'].loc[df2['group']=='mCherry'])
        mean_mCherry = np.mean(df2['distance_ratio'].loc[df2['group']=='mCherry'])    
        plt.errorbar(['mCherry'],mean_mCherry,yerr=sd_mCherry,color='black',elinewidth=1,capsize=2)
        
        plt.title('sum-aca3')
        plt.ylim(0,2)
        plt.xlim([-0.5,1.5])

        #样本正态性检验 p-value=0.02<0.05
        print(stats.levene(df2['distance_ratio'].loc[df2['group']=='NpHR'], df2['distance_ratio'].loc[df2['group']=='mCherry']))
        #所以采用符号检验
        print(stats.ranksums(df2['distance_ratio'].loc[df2['group']=='NpHR'], df2['distance_ratio'].loc[df2['group']=='mCherry']))
        print("NpHR:",len(df2['distance_ratio'].loc[df2['group']=='NpHR']),"; mCherry:",len(df2['distance_ratio'].loc[df2['group']=='mCherry']))       
        
        

        
        df3 = new_data.loc[new_data['location']=='iCA3'].sort_values(by='group')
        plt.subplot(4,4,16)
        for x,y in zip(df3['group'],df3['distance_ratio']):
            if x == 'NpHR':
                plt.plot(x,y,'.',color="green",zorder=1,alpha=0.2)
            else:
                plt.plot(x,y,'.',color='red',zorder=1,alpha=0.2)
                
        sd_NpHR = np.std(df3['distance_ratio'].loc[df3['group']=='NpHR'])
        mean_NpHR = np.mean(df3['distance_ratio'].loc[df3['group']=='NpHR'])
        plt.errorbar(['NpHR'],mean_NpHR,yerr=sd_NpHR,color='black',elinewidth=1,capsize=2)
        
        sd_mCherry = np.std(df3['distance_ratio'].loc[df3['group']=='mCherry'])
        mean_mCherry = np.mean(df3['distance_ratio'].loc[df3['group']=='mCherry'])
        plt.errorbar(['mCherry'],mean_mCherry,yerr=sd_mCherry,color='black',elinewidth=1,capsize=2)
        
        plt.title('sum-ica3')
        plt.ylim(0,1.5)
        plt.xlim([-0.5,1.5])
        
        #样本正态性检验 p-value=0.02<0.05
        print(stats.levene(df3['distance_ratio'].loc[df3['group']=='NpHR'], df3['distance_ratio'].loc[df3['group']=='mCherry']))
        #所以采用t.test
        print(stats.ttest_ind(df3['distance_ratio'].loc[df3['group']=='NpHR'], df3['distance_ratio'].loc[df3['group']=='mCherry']))
        print("NpHR:",len(df3['distance_ratio'].loc[df3['group']=='NpHR']),"; mCherry:",len(df3['distance_ratio'].loc[df3['group']=='mCherry']))

        plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=0.5, hspace=1)
        plt.show()
        
        
            
            
            
            

if __name__ == "__main__":
##    novel_context_csv_path=r'Y:\Qiushou\2_Novel-context recognition\output-screened_by_histology.csv'
##    Csv(novel_context_csv_path).Novel_context2()

    cpa_csv_path=r'Y:\Qiushou\1 acquisition\4 contextual-fear-conditioning_backup20190724\coulbourn-1trial-20190418_#192045-#192056_aCa3-dpCA1_QS\Video\20190418\#192045_190418144350Cam-1_freezing.csv'
    Csv(cpa_csv_path).freezing_percentage()
    
    
