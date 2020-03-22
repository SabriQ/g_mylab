from Cunit import Unit
import numpy as np
import matplotlib.pyplot as plt

class Bt2AC(Unit):
    def __init__(self,unitPath):
##        super(Context_Discrimination,self).__init__(unitPath)
        super().__init__(unitPath)

    def Rasters_PSTH(self,align="KBD3",pre=10,post=10):
        
        y=[]
        for origin in self.unit[align]:
            y.append(np.array([i for i in self.unit['spiketrain'] if i> origin-pre and i < origin+post])-origin)
            
##        for i in range(len(y)-1,-1,-1):
        for i in range(len(y)):
            plt.eventplot(y[i],lineoffsets=i+1,color = 'black')
##        plt.yticks([i+1 for i in range(len(y))],self.orders)
##        plt.gca().invert_yaxis()
        plt.axvline(0,linestyle='--',color = 'red')
##        plt.axvline(2,linestyle='--',color = 'green')
##        plt.ylabel('Trials\n<---')
##        plt.xlabel('Time(s)')
##        plt.title(f"{self.unit['name']}")
        plt.show()
if __name__ == '__main__':
    unitPath=r"Y:\BaiTao\ephy\191516\20190509\20190509_05092019003_TETWB01a.pkl"
    a = Bt2AC(unitPath)
    a.Rasters_PSTH(align="EVT07")
        
