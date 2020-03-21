from mylab.spikes.MNex2UnitFile import Nex2Unit, WriteUnit
from mylab.spikes.Cunit import Unit
from mylab.spikes.Ccontext_discrimination import Context_discrimination
from mylab.spikes.Cmulti_elements import Multi_elements
from mylab.spikes.Cshock import Shock
import glob





unitPathes = glob.glob(r'C:\Users\Sabri\Desktop\program\spike\units\*pkl')

context_discriminations = [("M028","20181102","A|A|B|A|B|B|B|A"),
                           ("M028","20181112","A|B|A|B|A|B|B|A"),
                           ("19043","20190311","B|A|B|A|B|A|A|B"),
                           ("19043","20190318","B|A|B|A|B|A|A|B"),
                           ("192076","20190423","B|A|B|A|B|A|A|B"),]

multi_elements =[("M028","20181130","B|B1|B2|B3|A|A|A1|A2|A3|B|"),
                 ("192076","20190424","A|A1|A2|B|A|A1|A2|B"),
                 ("192076","20190429","A|A1|A2|B|A|A1|A2|B|A|A1|A2|B")]

shocks = [("M028","20181118","b|b|b|b|b|b|b|b|d|d|a|a|a|a|a|a|a|a")]

# experiments contains "Context_discrimination","","Shock"
for each in context_discriminations:
    pathes = [i for i in unitPathes if each[0] in i and each[1] in i]
    for path in pathes:
        Unit(path).AddExperiment("Context_discrimination")
        Context_discrimination(path).AddProperty("context_order",each[2])



for each in multi_elements:
    pathes = [i for i in unitPathes if each[0] in i and each[1] in i]
    for path in pathes:
        Unit(path).AddExperiment("Multi_elements")
        Multi_elements(path).AddProperty("context_order",each[2])

for each in shocks:
    pathes = [i for i in unitPathes if each[0] in i and each[1] in i]
    for path in pathes:    
        Unit(path).AddExperiment("Shock")
        Shock(path).AddProperty("shock_order",each[2])

    
