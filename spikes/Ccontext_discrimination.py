from mylab.spikes.Cunit import Unit
import numpy as np
import matplotlib.pyplot as plt
import glob

class Context_discrimination(Unit):
    def __init__(self,unitPath):
##        super(Context_Discrimination,self).__init__(unitPath)
        super().__init__(unitPath)
        
        
    def ShowInfo(self):
        for key,value in self.unit.items():
            if not key == 'Context_discrimination':
                print(key,":", str(value)[0:50],'...')
            else:
                print(key,":")
                for key2,value2 in self.unit['Context_discrimination'].items():
                    print('+--',key2,':',str(value2)[0:50])
    def AddProperty(self,name,value):
        if name not in self.unit['Context_discrimination'].keys():
            print(f'{name} gets added')
        else:
            print(f'{name} gets updated')
        self.unit['Context_discrimination'][name]=value
        self._Savepkl()
        
    def temp(self):
        del self.unit['Context_discrimination']['type']                    
      
    def _calFiringCountandFRandDuration(self,start,end):
        count = len([i for i in self.unit['spiketrain'] if i>= start and i<= end])
        firingrate = count / (end-start)
        return count,firingrate,end-start

    def CountFiringrateDuration(self):
        door_open = self.unit['KBD1']
        door_close = self.unit['KBD3']
        
        
        SpikeCount=[]
        FiringRate = []
        Duration = []
        keys = ['Trial_No','context_name','median','doorOpen','context']

##        from collections import namedtuple
##        SpikeCount_tuple = namedtuple('SpikeCount',['No','context_name','median','doorOpen','context'])
##        Duration_tuple = namedtuple('Duration',['No','context_name','median','doorOpen','context'])
##        FiringRate_tuple = namedtuple('FiringRate',['No','context_name','median','doorOpen','context'])
##        
##        #for each trial, we get a Count namedtuple, a FiringRate namedtuple and a Duration namedtuple
##        #So three lists are created to contain all the each-trial Count namedtuples, FiringRate namedtuples and Duration namedtuples seperately
##        unluckily, pickle doesn't support namedtuple daaaaaaaaaaaaaaamn it!!!!!!!!!!!!!!
        
        for i,order in enumerate(self.orders,0):
####            print(f'{i},{order}>>>')
            
            spikecount_median,firintrate_median,duration_median = self._calFiringCountandFRandDuration(self.unit['Start'][i],door_open[i])
            spikecount_doorOpen,firingrate_doorOpen,duration_doorOpen = self._calFiringCountandFRandDuration(door_open[i],door_close[i])
            spikecount_context,firingrate_context,duration_context = self._calFiringCountandFRandDuration(door_close[i],self.unit['Stop'][i])
##          
            SpikeCount.append(dict(zip(keys,[i+1,order,spikecount_median,spikecount_doorOpen,spikecount_context])))
            FiringRate.append(dict(zip(keys,[i+1,order,firintrate_median,firingrate_doorOpen,firingrate_context])))
            Duration.append(dict(zip(keys,[i+1,order,duration_median,duration_doorOpen,duration_context])))          

        self.AddProperty("SpikeCount",SpikeCount)
        self.AddProperty("FiringRate",FiringRate)
        self.AddProperty("Duration",Duration)     
    def PlotHist(self,binwidth=5,savePath=None):
        
        door_open = self.unit['KBD1']
        door_close = self.unit['KBD3']
        orders = self.unit['Context_discrimination']['context_oders'].split("|")
  
            
        plt.figure('Histogram',(20,10))
      
        for i in range(len(self.unit['Start'])):
            plt.subplot(1,len(self.unit['Start']),i+1)
            hist,bin_edges = np.histogram(self.unit['spiketrain'],bins=np.arange(self.unit['Start'][i],self.unit['Stop'][i]+binwidth,binwidth))            
            y = hist/binwidth
            plt.bar(bin_edges[0:-1],y,width = binwidth)
            print(door_open[i],door_close[i])
            plt.axvspan(door_open[i],door_close[i],0,1,facecolor='red',edgecolor = 'None',alpha = 0.4)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            if i == 0:
                 plt.ylabel('Freqency(Hz)')
            plt.xlabel(f'{orders[i]}')
            if not i == 0:
                plt.gca().spines['left'].set_visible(False)
                plt.yticks([])
##            plt.ylim(0,15)
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
    def ChangePoint(self,binwidth=0.5,align='KBD1',pre=2,post=20):
            
        y = []
        for origin in self.unit[align]:
            hist,bin_edges = np.histogram(self.unit['spiketrain'],bins=np.arange(origin-pre,origin+post,binwidth))
            y.append(hist/binwidth)        
##        x = np.linspace(1,len(y[0]),len(y[0]))
        x = np.arange(-1*pre,post-binwidth,binwidth)
        plt.plot(x,y[0],"--")
        plt.plot(x,y[2],"--")
        plt.plot(x,y[4],"--")
        plt.plot(x,y[7],"--")
        plt.plot(x,np.mean(y,axis=0),'b-')
        plt.axvline(0,linestyle='--',color = 'red') 
        plt.ylabel("Firing Rate(Hz)")
        plt.xlabel("Time(s)")
        plt.title(f"{self.unit['name']}")

        plt.show()
        
    def Rasters_PSTH(self,align="KBD3",pre=10,post=20):
        
        if "ContextOrder" not in self.unit['Context_discrimination'].keys():
           print("pleas update common units value of ContextOrder")
           return None
        
        y=[]
        for origin in self.unit[align]:
            y.append(np.array([i for i in self.unit['spiketrain'] if i> origin-pre and i < origin+post])-origin)
            
##        for i in range(len(y)-1,-1,-1):
        for i in range(len(y)):
            plt.eventplot(y[i],lineoffsets=i+1,color = 'black')
        plt.yticks([i+1 for i in range(len(y))],self.orders)
        plt.gca().invert_yaxis()
        plt.axvline(0,linestyle='--',color = 'red')        
        plt.ylabel('Trials\n<---')
        plt.xlabel('Time(s)')
        plt.title(f"{self.unit['name']}")
        plt.show()
    def Hotplot(self,):
        pass

class Context_Discrimination_all():
    def __init__(self,unitDir):
        self.unitDir = r"C:\Users\Sabri\Desktop\program\spike\units"
    
        
        
        
##
if __name__ == '__main__':
##    unitPathes=glob.glob(r"C:\Users\Sabri\Desktop\program\spike\units\*113020*.pkl")
##    for unitPath in unitPathes:
##        a = Context_discrimination(unitPath)
####        a.unit['KBD3'] = np.insert(a.unit['KBD3'],9,3600.831)
##        a.unit['KBD1'] = np.delete(a.unit['KBD1'],9)
##        a.AddProperty('Context_Oders',a.unit['Context_discrimination']['context_oders'])

    
##    unitPath=r"C:\Users\Sabri\Desktop\program\spike\units\#M028_11302018001-12042018005_TETSPK01a.pkl"    
##    a=Context_discrimination(unitPath)
##    a.ShowInfo()
##    print(len(a.unit['KBD1']),len(a.unit['KBD3']))
##    a.PlotHist()
##

    unitPathes=glob.glob(r"C:\Users\Sabri\Desktop\program\spike\units\*113020*.pkl")
    for unitPath in unitPathes:
        a=Context_discrimination(unitPath)
        a.ShowInfo()
        print(len(a.unit['KBD1']),len(a.unit['KBD3']))
        a.PlotWaveform()
##    

    
