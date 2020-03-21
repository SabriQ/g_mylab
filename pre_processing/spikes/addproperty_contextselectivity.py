from Cunit import Unit
import os
import numpy as np



unitDir=r"C:\Users\Sabri\Desktop\program\spike\units"
unitPathes = [os.path.join(unitDir,i) for i in os.listdir(unitDir) if i.endswith(".pkl")]


##Context_selectivity_indexes = []

##neuron = Unit(unitPathes[10])
for unitPath in unitPathes:
    if "#M028_11122018001-008_" in unitPath:
        neuron = Unit(unitPath)
        # 求 trial A,trial B or trial all 中median的平均发放率
        A_median_avefr= sum([i['median'] for i in neuron.unit['SpikeCount'] if i['context_name']=="A"])/\
        sum([i['median'] for i in neuron.unit['Duration'] if i['context_name']=="A"])
        B_median_avefr= sum([i['median'] for i in neuron.unit['SpikeCount'] if i['context_name']=="B"])/\
        sum([i['median'] for i in neuron.unit['Duration'] if i['context_name']=="B"])
        median_avefr = sum([i['median'] for i in neuron.unit['SpikeCount']])/\
        sum([i['median'] for i in neuron.unit['Duration']])
            
        #求 trial A,trial B or trial all 中median的平均发放率
        A_doorOpen_avefr= sum([i['doorOpen'] for i in neuron.unit['SpikeCount'] if i['context_name']=="A"])/\
        sum([i['median'] for i in neuron.unit['Duration'] if i['context_name']=="A"])
        B_doorOpen_avefr= sum([i['doorOpen'] for i in neuron.unit['SpikeCount'] if i['context_name']=="B"])/\
        sum([i['median'] for i in neuron.unit['Duration'] if i['context_name']=="B"])
        doorOpen_avefr = sum([i['doorOpen'] for i in neuron.unit['SpikeCount']])/\
        sum([i['median'] for i in neuron.unit['Duration']])  
            
        # trial A,trial B or trial all 中Context的平均发放率
        A_context_avefr= sum([i['context'] for i in neuron.unit['SpikeCount'] if i['context_name']=="A"])/\
        sum([i['median'] for i in neuron.unit['Duration'] if i['context_name']=="A"])
        B_context_avefr= sum([i['context'] for i in neuron.unit['SpikeCount'] if i['context_name']=="B"])/\
        sum([i['median'] for i in neuron.unit['Duration'] if i['context_name']=="B"])
        context_avefr = sum([i['context'] for i in neuron.unit['SpikeCount']])/\
        sum([i['median'] for i in neuron.unit['Duration']])

        ##print("median average firingrate",A_median_avefr,B_median_avefr,median_avefr)
        ##print("dooropen average firingrate",A_doorOpen_avefr,B_doorOpen_avefr,doorOpen_avefr)
        ##print("context averrage firiingrate",A_context_avefr,B_context_avefr,context_avefr)

        sti_firingrate = dict([("A_median_avefr",A_median_avefr),
                              ("B_median_avefr",B_median_avefr),
                              ("median_avefr",median_avefr),
                               ("A_doorOpen_avefr",A_doorOpen_avefr),
                              ("doorOpen_avefr",doorOpen_avefr),
                              ("doorOpen_avefr",doorOpen_avefr),
                              ("A_context_avefr",A_context_avefr),
                              ("B_context_avefr",B_context_avefr),
                              ("context_avefr",context_avefr)])
        
        neuron.AddProperty("sti_firingrate",sti_firingrate)
        
        Context_selectivity_index = (B_context_avefr-A_context_avefr)/(A_context_avefr+B_context_avefr)
        neuron.AddProperty("Context_selectivity_index",Context_selectivity_index)
        
##        Context_selectivity_indexes.append(Context_selectivity_index)


