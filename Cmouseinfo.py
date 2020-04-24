import pickle
import json
import os,sys
class MouseInfo():
    def __init__(self,mouse_info_path):
        self._mouse_info_path = mouse_info_path

        if os.path.exists(self._mouse_info_path):
            self._load_mouseinfo()
            print("loaded info: %s"% self._mouse_info_path)
        else:
            self._mouse_info = {"mouse_info_path":self._mouse_info_path}
            print("create info %s"%self._mouse_info_path)

    @property
    def keys(self):
        return self._mouse_info.keys()

    @property
    def save(self):
        return self._save_mouseinfo()
    
    @property
    def lick_water(self):
        if not "lick_water" in self.keys:
            print ("'lick_water' inexistent")
        else:
            print (self._mouse_info["lick_water"].keys())
    
    def add_exp(self,exp):
        if exp in self.keys:
            print("already have %s"%exp)
        else:
            self._mouse_info[exp]={}

    def add_key(self,key,value,exp=None,update=False):
        if exp == None:
            if exp in self.keys:
                if update:
                    self._mouse_info[key]=value
                    print("update %s"%key)
                else:
                    print("please use 'update_key' or set 'update = True'")
            else:   
                self._mouse_info[key]=value
                print("add %s"%key)
        else:
            if exp in self.keys():
                self._mouse_info[exp][key]=value
                print("add %s"%key)
            else:
                self.add_exp(exp)
                self.add_key(key,value,exp=exp)

    def update_key(self,key,value,exp=None):
        if exp == None:
            self._mouse_info[key]=value
        else:
            self._mouse_info[exp][key]=value
        print("update %s"%key)
    
    def __del__(self):
        pass

    def _load_mouseinfo(self):
        with open(self._mouse_info_path,'r') as f:
            js = f.read()
            self._mouse_info =  json.loads(js)

    def _save_mouseinfo(self):      
        with open(self._mouse_info_path,'w') as f:
            f.write(json.dumps(self._mouse_info,indent=4))
        print("save info: %s" %self._mouse_info_path)




if __name__ == "__main__":
    MouseInfo(mouse_info_path=r"X:\QiuShou\mouse_info\191173_info.txt")
