import pickle

class MouseInfo():
    def __init__(self,mouse_info_path):
        self._mouse_info_path = mouse_info_path

        if os.path.exits(self._mouse_info_path):
            self._mouse_info = self._load_mouseinfo()
        else:
            self._mouse_info = {}
            print("create info %s"%self._mouse_info_path)

    @property
    def keys(self):
        return self._mouse_info.keys()

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
        self._save_mouseinfo()

    def _load_mouseinfo(self):
        with open(self._mouse_info_path,'r') as f:
            return json.load(f)
        print("load info %s"% self._mouse_info_path)

    def _save_mouseinfo(self):      
        with open(self._mouse_info_path,'w') as f:
            f.write(json.dumps(self._mouse_info,indent=4))
        print("update %s" %os.path.basename(self._mouse_info_path))




if __name__ == "__main__":
    pass
