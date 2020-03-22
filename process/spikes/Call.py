from Cunit import Unit
import os
import numpy as np
import matplotlib.pyplot as plt
class Statistic():
    def __init__(self,):
        
        self.unitDir=r"C:\Users\Sabri\Desktop\program\spike\units"
        self.unitPathes = [os.path.join(self.unitDir,i) for i in os.listdir(self.unitDir) if i.endswith(".pkl")]

        saveDir=r"C:\Users\Sabri\Desktop\program\spike\results"

        pass
    def Context_selectivity(self):
        '''
        mean firing rate of various period:
            median, door open and context is needed
        in eight trial 
        '''
        Context_selectivity_indexes = []
        for unitPath in self.unitPathes:
            neuron = Unit(unitPath)
            if neuron.unit['type'] == "Context_Selection":
                Context_selectivity_indexes.append(neuron.unit["Context_selectivity_index"])
                
        x = np.linspace(1,len(Context_selectivity_indexes),len(Context_selectivity_indexes))
        y = sorted(Context_selectivity_indexes)
        plt.figure('Context_selectivity')
   
        plt.plot(y,x,'o',markersize=2,color = "blue")
        plt.axvline(0,0,1,linestyle='--',color ="black")
        plt.xlim(-1,1)
        plt.yticks([])
        plt.xticks(np.linspace(-1,1,7),("A","-0.75","-0.25","0","0.25","0.75","B"))
        plt.title('Context Selectivity')
        plt.ylabel('Counts')
        plt.show()

                
if __name__ == '__main__':
    stat = Statistic()
    stat.Context_selectivity()
    
