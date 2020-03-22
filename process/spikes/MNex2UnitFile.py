'''
'Nex2Unit' reads a complete .nex file containing several units and
    save as .nex/.npy/.pkl./mat/.json (default to be .mat) files each of which containing only one-unit infomation
        information incuding(plan to add properties):
            neuron
            events(start, stop)
            waveform
            markers(Evt01,Evt02...KBD01,KBD02...)
            
'Read_Unit' automatically read .npy/.pkl./mat/ (.nex/.json not finished yet) file and return a dict of unit
By qiushou @ 2019.2.28

'''
from mylab.spikes import nexfile as nex
import numpy as np
import json
import pickle
import os
import glob
import scipy.io as scio


def Nex2singleunitNex(inFilePath,outFileDir):
    
##        if  extension == '.nex':
##            nexout = nex.NexWriter(40000,useNumpy = True)
####          each unit's structure
####          nexout.fileData['FileHeader']['Comment'] = 'this is a test'
##            nexout.AddNeuron(neuron['Header']['Name'],neuron['Timestamps'])
##            for waveform in waveforms:
##                if neuron['Header']['Name'] in waveform['Header']['Name']:
##                    nexout.AddWave(waveform['Header']['Name'],waveform['Timestamps'],waveform['Header']['SamplingRate'],waveform['WaveformValues'])
##
##            for event in events:            
##                nexout.AddEvent(event['Header']['Name'],event['Timestamps'])
##            for marker in markers:
##                nexout.AddMarker(marker['Header']['Name'],marker['Timestamps'],marker['MarkerFieldNames'],marker['Markers'])
##            nexout.WriteNexFile(outFilePath)
                
##        else:  
    '''
    for writing to a nex(5) file, we can not add any extra information besides 'Comment'
    还有一个潜在的功能就是将多个unit合成一个nex文件可以写
    '''
    outFilePathPrefix = outFileDir + '\\'+inFilePath.split('\\')[-2]+'_'+inFilePath.split('\\')[-1].split('.')[-2]+'-'
    nexin = nex.Reader(useNumpy = True).ReadNexFile(inFilePath)
##    print(nexin['FileHeader'])
    neurons = []
    waveforms = []
    events = []
    markers = []
    
    for var in nexin['Variables']:
        if var['Header']['Type'] == 0:
            neurons.append(var)
            print('neuron',len(neurons))
            
        if var['Header']['Type'] == 1:
            events.append(var)
            print('events',len(events))

        if var['Header']['Type'] == 3:
            waveforms.append(var)
            print('waveforms',len(waveforms))

        if var['Header']['Type'] == 5:
            pass

        if var['Header']['Type'] == 6 and len(var['Timestamps']) != 0:
            markers.append(var)
            print('markers',len(markers))           

    for neuron in neurons:
        outFilePath = outFilePathPrefix+neuron['Header']['Name']+'.nex'
        print(outFilePath)
        nexout = nex.NexWriter(40000,useNumpy = True)
##      each unit's structure
##        nexout.fileData['FileHeader']['Comment'] = 'this is a test'
        nexout.AddNeuron(neuron['Header']['Name'],neuron['Timestamps'])
        for waveform in waveforms:
            if neuron['Header']['Name'] in waveform['Header']['Name']:
                nexout.AddWave(waveform['Header']['Name'],waveform['Timestamps'],waveform['Header']['SamplingRate'],waveform['WaveformValues'])
        for event in events:            
            nexout.AddEvent(event['Header']['Name'],event['Timestamps'])
        for marker in markers:
            nexout.AddMarker(marker['Header']['Name'],marker['Timestamps'],marker['MarkerFieldNames'],marker['Markers'])
        nexout.WriteNexFile(outFilePath)
      
class MyEncoder(json.JSONEncoder): # special for json
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)

def Nex2Unit(inFilePath):
    print(f'reading {inFilePath} ...')
    nexin = nex.Reader(useNumpy = True).ReadNexFile(inFilePath)
    print('>>>data loaded')
    spiketrains = []
    waveforms = []
    events = []
    markers = []
    
    for var in nexin['Variables']:
        if var['Header']['Type'] == 0:
            spiketrains.append(var)
##            print('spiketrain',spiketrains[-1]['Header']['Name'])
            
        if var['Header']['Type'] == 1:
            events.append(var)
##            print('events',events[-1]["Header"]["Name"])
    
        if var['Header']['Type'] == 3:
            waveforms.append(var)
##            print('waveform',waveforms[-1]["Header"]["Name"])

        if var['Header']['Type'] == 5:
            pass

        if var['Header']['Type'] == 6 and len(var['Timestamps']) != 0:
            markers.append(var)
##            print('markers',markers[-1]["Header"]["Name"])   


     
    units=[]

    for spiketrain, waveform in zip(spiketrains,waveforms):
        unit = {}
        unit["name"]=inFilePath.split('\\')[-2]+'_'+inFilePath.split('\\')[-1].split('.')[-2]+'_'+spiketrain['Header']['Name']
        unit["spiketrain"] = spiketrain["Timestamps"]
        print(waveform["WaveformValues"].shape)
        if spiketrain['Header']['Name'] in waveform['Header']['Name']:
            unit["waveforms"] = waveform["WaveformValues"]
            print(unit["waveforms"].shape)
        else:
            print("spiketrain has different name with waveform")


        for event in events:
            unit[event["Header"]["Name"]]=event["Timestamps"]
##            print(event["Header"]["Name"])
        for marker in markers:
            unit[marker["Header"]["Name"]]=marker["Timestamps"]
##            print(marker["Header"]["Name"])
        units.append(unit)
    return units
            

def WriteUnit(units,outFileDir,extension='.pkl'):
    if isinstance(units,dict):
        units = list([units])

    for unit in units:
        outFilePath = os.path.join(outFileDir,unit['name'])+extension
        print(outFilePath)
        
        if extension == '.pkl':
##      save as .pkl
            with open(outFilePath, 'wb') as fp:
                pickle.dump(unit,fp)
            print('saved as pklfile')

            
        elif extension == '.npy':
            np.save(outFilePath,unit)
        elif extension == '.json':
##      save as .json
            with open(outFilePath, 'w', encoding='utf-8') as fp:
                json.dump(unit,fp,cls=MyEncoder)
        elif extension == '.mat':
##      save as .mat
            scio.savemat(outFilePath,unit)
            print('save as matfile')
    


def Read_Unit(unitPath):
    extension = os.path.splitext(unitPath)[-1]
    if extension == '.npy':
        unit = np.load(unitPath).item()
        return unit

    
    elif extension  == '.pkl':     
        with open(unitPath,'rb') as f:
            unit= pickle.load(f)
            return unit
 

    elif extension == '.mat':
        unit = scio.loadmat(unitPath)
        return unit
    elif extension == '.nex':
        print('not finish coding yet')
        pass
    elif extension == '.json':
##        print('json.loads() get problems')
        pass
    else:
        print('wrong file extension!')
    
    
    

if __name__ == "__main__" :

    nexfiles = glob.glob(r'Y:\Qiushou\5 Multi-channel data\sorting\#M028\11302018001-12042018005.nex')
    outFileDir = r'C:\Users\Sabri\Desktop\program\spike\units'
    for nexfile in nexfiles:
        units = Nex2Unit(nexfile)
        WriteUnit(units,outFileDir)
    
