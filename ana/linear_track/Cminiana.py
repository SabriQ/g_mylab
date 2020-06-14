from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
from mylab.Cmouseinfo import MouseInfo

class MiniAna():
    def __init__(self,mouse_info_path,cnmf_result_dir):

        self.mouse_info = MouseInfo(mouse_info_path)
        self.cnmf_result_dir= cnmf_result_dir
        self.ana_result_path = os.path.join(self.cnmf_result_dir,"ana_result.pkl")
        self.ana_result = load_pkl(self.ana_result_path)


    @property
    def keys(self):
        return self.ana_result.keys()

    @property
    def save(self):
        return save_pkl(self.ana_result,self.ana_result_path)

    @property
    def neuron_ids(self):
        return self.ana_result["mssessions"][0].columns.drop("ms_ts")
    
    def update(self,key,value):
        if key in self.keys:
            self.ana_result[key] = value
            print("update %s."% key)
        else:
            print("please add %s first"% key)
            
    def add(self,key,value):
        if not key in self.keys:
            self.ana_result[key] = value
            print("add %s."% key)
        else:
            print("%s is already there, please use 'update'")
    
    
    def si(self):
        """spatial information 


        """
        pass

    def csi(self):
        """context selectivity index"""
        pass

    def hdsi(self):
        """head direction selectivity index"""
        pass

        
if __name__ == "__main__":
    pass