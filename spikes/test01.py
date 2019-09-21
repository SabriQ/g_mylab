from Ccontext_discrimination import Context_discrimination as cd
import os
import numpy as np
import matplotlib.pyplot as plt


unitDir=r"C:\Users\Sabri\Desktop\program\spike\units"
unitPathes = [os.path.join(unitDir,i) for i in os.listdir(unitDir) if i.endswith(".pkl")]

for unitPath in unitPathes:
    neuron = cd(unitPath)
    neuron.CountFiringrateDuration()
  

    
##    if "#M028_11182018002-020_TETSPK" not in unitPath:
##        neuron = Unit(unitPath)
##        neuron.AddProperty('type',"Context_Selection")
##    else:
##        neuron = Unit(unitPath)
##        neuron.AddProperty('type',"CS_beforeORafter_shock")
##
##
##x = np.linspace(1,len(Context_selectivity_indexes),len(Context_selectivity_indexes))
##y = sorted(Context_selectivity_indexes)
##plt.figure('Context_selectivity')
##plt.plot(y,x,'o')
##plt.show()
