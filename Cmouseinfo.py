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
    

    def __getitem__(self,key):
        if key in self.keys:
            return self._mouse_info[key]
        else:
            return "no %s"%(key)

    def __setitem__(self,key,value):
        if not key in self.keys: 
            self._mouse_info[key] = value
            print("%s is added"%key)
        else:
            print("reset or update is not allowed.")
    
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
