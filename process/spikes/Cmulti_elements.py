from mylab.spikes.Ccontext_discrimination import Context_discrimination
import numpy as np
import matplotlib.pyplot as plt

class Multi_elements(Context_discrimination):
    def __init__(self,unitPath):
        super().__init__(unitPath)

    


    def AddProperty(self,name,value):
        if name not in self.unit['Multi_elements'].keys():
            print(f'{name} gets added')
        else:
            print(f'{name} gets updated')
        self.unit['Multi_elements'][name]=value
        self._Savepkl()
        
