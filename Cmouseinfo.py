import pickle
import json
import os,sys
class MouseInfo():
    def __init__(self,mouse_info_path):
        self.mouse_info_path = mouse_info_path

        if os.path.exists(self.mouse_info_path):
            self._load_mouseinfo()
            print("loaded info: %s"% self.mouse_info_path)
        else:
            self._info = {"mouse_info_path":self.mouse_info_path}
            print("create info %s"%self.mouse_info_path)

    @property
    def keys(self):
        return self._info.keys()
        
    @property
    def info(self):
        return self._info
    
    @property
    def save(self):
        return self._save_mouseinfo()
    
    @property
    def lick_water(self):
        if not "lick_water" in self.keys:
            print ("'lick_water' inexistent")
        else:
            return self._info["lick_water"]
    @property
    def CDC(self):
        if not "CDC" in self.keys:
            print("CDC" inexistent)
        else:
            return self._info["CDC"]
    
    def add_exp(self,exp):
        if exp in self.keys:
            print("already have %s"%exp)
        else:
            self._info[exp]={}

    def add_key(self,key,value,exp=None,update=False):
        if exp == None:
            if exp in self.keys:
                if update:
                    self._info[key]=value
                    print("update %s"%key)
                else:
                    print("please use 'update_key' or set 'update = True'")
            else:   
                self._info[key]=value
                print("add %s"%key)
        else:
            if exp in self.keys:
                self._info[exp][key]=value
                print("add %s"%key)
            else:
                self.add_exp(exp)
                self.add_key(key,value,exp=exp)

    def update_key(self,key,value,exp=None):
        if exp == None:
            self._info[key]=value
        else:
            self._info[exp][key]=value
        print("update %s"%key)
    
    def __del__(self):
        pass

    def _load_mouseinfo(self):
        with open(self.mouse_info_path,'r',encoding="utf-8") as f:
            js = f.read()
            self._info =  json.loads(js)

    def _save_mouseinfo(self):      
        with open(self.mouse_info_path,'w',encoding="utf-8") as f:
            f.write(json.dumps(self._info,indent=4))
        print("save info: %s" %self.mouse_info_path)




if __name__ == "__main__":
    MouseInfo(mouse_info_path=r"Z:\QiuShou\mouse_info\191173_info.txt")
