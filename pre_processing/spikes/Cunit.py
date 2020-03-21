from mylab.spikes import MNex2UnitFile as n2u
import numpy as np
import matplotlib.pyplot as plt
import os 
import pickle


class Unit (object):
    
    def __init__(self,unitPath):
        self.unitPath = unitPath
        self.unitDir = os.path.dirname(unitPath)        
        self.unit = n2u.Read_Unit(unitPath)
        
    def ShowInfo(self):        
            
        for key,value in self.unit.items():
            if len(str(value))<=50:
                print(key,":", value)
            else:
                print(key,":", str(value)[0:50],'...')       
                

    def AddExperiment(self,Experiment):
        if Experiment not in self.unit.keys():
            print(f'Nex experiment {Experiment} is added')
        else:
            print(f'Experiment {Experiment} is existed')
            
        self.unit[Experiment]={}
        print(f'{Experiment} is constructed!')
        self._Savepkl()
    
    def temp (self):
        del self.unit['ContextOrder']
        del self.unit['SpikeCount']
        del self.unit['FiringRate']
        del self.unit['Duration']
        del self.unit['sti_firingrate']
        del self.unit['Context_selectivity_index']
        del self.unit['type']
        self._Savepkl()
                
    def AddProperty(self,name,value):
        #if error messaging about "self.unit.keys()",it might the the mistake of "pickle.load"， 
        if name not in self.unit.keys():
            print(f'{name} gets added')
        else:
            print(f'{name} gets updated')
        self.unit[name]=value
        self._Savepkl()


    def _Savepkl(self):
##        n2u.WriteUnit(self.unit,self.unitDir)
        with open(self.unitPath,'wb') as f:
            pickle.dump(self.unit,f)
        print(f"{self.unit['name']} gets saved")
                
    
    def PlotWaveform(self,savePath=None):  
##        print(len(waveforms))
        ave_waveform = np.mean(self.unit['waveforms'],axis = 0)
        sd_waveform = np.std(self.unit['waveforms'],axis = 0,ddof = 1)
        
        # ddof means delta degrees of freedom,
        # ddof = 0  means the population, divided by sqrt(n) 
        # ddof = 1 means the sample, divided by sqrt(n-1)
        # np.std([1,2,3],ddof = 0) = 0.8164965;
        # np.std([1,2,3],ddof = 1) = 1            
       
        x = np.linspace(1,len(ave_waveform),len(ave_waveform))
        y = ave_waveform       
        
        wf_fig = plt.figure('wf_fig',(20,5))

        plt.plot(x,y,color ='dodgerblue')
        plt.fill_between(x,y+sd_waveform,y-sd_waveform,color ='dodgerblue',alpha = 0.3)
        #the interval space among waveforms
        plt.axvline(max(x)/4,linewidth = 3,color = 'white')
        plt.axvline(max(x)/2,linewidth = 3,color = 'white')
        plt.axvline(max(x)/4*3,linewidth = 3,color = 'white')

        plt.axis('off')

        #scalebar ax2
        plt.vlines(max(x)-20,min(y),min(y)+0.1) # 0.1mv
        plt.text(max(x)-23.5,min(y)+0.06,'100uv',rotation = 90)
        
        plt.hlines(min(y),max(x)-20,max(x))    # 20*25us = 0.5ms
        plt.text(max(x)-14,min(y)-0.015,'500us')        

        plt.title(self.unit["name"],y=1.08)
        
        if savePath:
            if not os.path.exists(savePath):
                print("the directory you specified is not exist!")
            else:
                savePath = os.path.join(savePath,self.unit["name"])
                plt.savefig(savePath)
                plt.close()
        else:            
            print(self.unit['name'])
            plt.show() 

              
        
    def PlotIsi(self,savePath=None):
        spikeisi = np.diff(self.unit["spiketrain"])
        isi_fig = plt.figure("ISI",(10,4))

        hist, bin_edges = np.histogram(spikeisi,bins = 20000)
        x = bin_edges * 1000
        y = hist/sum(hist) *100
        print(sum(hist))
        
        
        plt.fill_between(x[0:-1][x[0:-1]<=1],y[x[0:-1]<=1],linestyle = 'None',color = 'red')
        plt.fill_between(x[0:-1][x[0:-1]>1],y[x[0:-1]>1],linestyle = 'None',color = 'pink')
           
        plt.xlim(0,1000)
        
        noise_prob = sum(hist[x[0:-1]<=1])/sum(hist)*100
        if noise_prob >= 0.005:
            note = str('Prob of isi less 1ms is '+str(noise_prob)+'%')
            plt.text(100,max(y)*0.95,note,color = 'red')
        
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)

        plt.xlabel('Time(ms)')
        plt.ylabel('Prob(%)')
        plt.title(self.unit['name'],y=1.08)

        if savePath:
            if not os.path.exists(savePath):
                print("the directory you specified is not exist!")
            else:
                savePath = os.path.join(savePath,self.unit["name"])
                plt.savefig(savePath)
                plt.close()
        else:            
            print(self.unit['name'])
            plt.show() 
        

        
    def PlotHist(self,binwidth=5,savePath=None):

        door_open = self.unit['KBD1']
        door_close = self.unit['KBD3']
      
        
        if "ContextOrder" not in self.unit.keys():
           print("pleas update common units value of ContextOrder")
           return None
        orders = self.unit["ContextOrder"].split("|")
            
        plt.figure('Histogram',(20,8))
      
        for i in range(len(self.unit['Start'])):
            plt.subplot(1,len(self.unit['Start']),i+1)
            hist,bin_edges = np.histogram(self.unit['spiketrain'],bins=np.arange(self.unit['Start'][i],self.unit['Stop'][i]+binwidth,binwidth))            
            y = hist/binwidth
            plt.bar(bin_edges[0:-1],y,width = binwidth)
            plt.axvspan(door_open[i],door_close[i],0,1,facecolor='red',edgecolor = 'None',alpha = 0.4,)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            if i == 0:
                 plt.ylabel('Freqency(Hz)')
            plt.xlabel(f'{orders[i]}')
            if not i == 0:
                plt.gca().spines['left'].set_visible(False)
                plt.yticks([])
            plt.ylim(0,15)
        plt.title(self.unit['name'],x=-3,y=1.08)
        
        if savePath:
            if not os.path.exists(savePath):
                print("the directory you specified is not exist!")
            else:
                savePath = os.path.join(savePath,self.unit["name"])
                plt.savefig(savePath)
                plt.close()
        else:            
            print(self.unit['name'])
            plt.show()       
        
        


    def PlotRaster(self,savePath=None):
        door_open = self.unit['KBD1']
        door_close = self.unit['KBD3']

        Raster_fig = plt.figure('Raster_fig',(20,1))      
        #plot raster
##        plt.plot(spiketrain,np.ones_like(spiketrain),color = 'gray',linestyle = 'None',marker = '|',markersize = 30,zorder = 0)

        plt.vlines(self.unit['spiketrain'],0.8*np.ones_like(self.unit['spiketrain']),1.2*np.ones_like(self.unit['spiketrain']),
                   color = 'gray',linestyle = 'solid',alpha = 0.5,zorder=0)

        #plot trail interval vetical line
##        plt.plot(stop,stop/stop,color = 'black',linestyle = 'None',marker = '|',markersize = 35)
##        plt.vlines(stop,0.8*np.ones_like(spiketrain),1.2*np.ones_like(spiketrain),color = 'black',linestyle = '--',linewidth = 2)
        for t in self.unit['Start']:
            plt.axvline(t,0,1,color = 'black',linestyle = '--')
        #plot shading area from door open to door close
        for (t1,t2) in zip(door_open,door_close):
##            print (t1,t2,'||')
            plt.axvspan(t1,t2,0,1,color = 'red',alpha = 0.4)

        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().get_yaxis().set_visible(False)

        plt.title(self.unit['name'],y=1.08)
        if savePath:
            if not os.path.exists(savePath):
                print("the directory you specified is not exist!")
            else:
                savePath = os.path.join(savePath,self.unit["name"])
                plt.savefig(savePath)
                plt.close()
        else:            
            print(self.unit['name'])
            plt.show()         
##        plt.show()      

        
if __name__ == "__main__":
    
    unitPath=r"Y:\BaiTao\ephy\191516\20190509\20190509_05092019003_TETWB01a.pkl"
    a = Unit(unitPath)
    a.ShowInfo()

##    a.PlotRaster()
##    a.PlotHist2()
##    a.PlotIsi()
##    a.AddProperty("KBD3",(92.123875,666.09405,1252.181325,1827.937975,2392.8576,3030.25825,3588.842925,4186.041975))
##    a.AddProperty("ContextOrder","B|A|B|A|B|A|A|B")
##    a.SaveTrial_CountandFiringRateandDuration()
