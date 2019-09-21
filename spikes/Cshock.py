from mylab.spikes.Ccontext_discrimination import Context_discrimination
import numpy as np
import matplotlib.pyplot as plt

class Shock(Context_discrimination):
    def __init__(self,unitPath):
        super().__init__(unitPath)

    
    def AddProperty(self,name,value):
        if name not in self.unit["Shock"].keys():
            print(f'{name} gets added')
        else:
            print(f'{name} gets updated')
        self.unit["Shock"][name]=value
        self._Savepkl()
        
