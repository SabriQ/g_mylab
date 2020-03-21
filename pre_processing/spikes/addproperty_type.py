from Cunit import Unit
import os
import numpy as np


unitDir=r"C:\Users\Sabri\Desktop\program\spike\units"
unitPathes = [os.path.join(unitDir,i) for i in os.listdir(unitDir) if i.endswith(".pkl")]

for unitPath in unitPathes:
    if "#M028_11122018001-008_" in unitPath:
        neuron = Unit(unitPath)        
        neuron.AddProperty('type',"Context_Selection")
        # if type == "Context_Selection"
##        neuron.AddProperty("sti_firingrate",sti_firingrate)
##        neuron.AddProperty("Context_selectivity_index",Context_selectivity_index)
        neuron.AddProperty('ContextOrder',"A|B|A|B|A|B|B|A")
        neuron.SaveTrial_CountandFiringRateandDuration()
        
        
##    if "#M028_11182018002-020_TETSPK" not in unitPath:
##        neuron = Unit(unitPath)
##        neuron.AddProperty('type',"Context_Selection")
##    else:
##        neuron = Unit(unitPath)
##        neuron.AddProperty('type',"CS_beforeORafter_shock")

