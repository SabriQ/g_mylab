from Cunit import Unit
import os
import numpy as np

unitDir=r"C:\Users\Sabri\Desktop\program\spike\units"
unitPathes = [os.path.join(unitDir,i) for i in os.listdir(unitDir) if i.endswith(".pkl")]
for unitPath in unitPathes:
    con = Unit(unitPath)
##    if "#M028_11022018002-010_TETSPK" in unitPath:        
##        con.AddProperty("KBD3",(92.123875,666.09405,1252.181325,1827.937975,2392.8576,3030.25825,3588.842925,4186.041975))
##        con.AddProperty("ContextOrder","A|A|B|A|B|B|A")
##    elif "#M028_11182018002-020-TETSPK" in unitPath:
##        con.AddProperty("ContextOrder","B|A|B|A|B|A|A|B|B|A|B|A|B|A|A|B")
##    else:
##        con.AddProperty("ContextOrder","B|A|B|A|B|A|A|B")
    con.SaveTrial_CountandFiringRateandDuration()
   
    
