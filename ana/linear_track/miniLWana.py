from mylab.Cmouseinfo import MouseInfo
class MiniLWAna():
    def __init__(self,mouse_info_path,cnmf_result_dir):
        self._info = MouseInfo(mouse_info_path)
        self.ana_result_path = os.path.join(self.cnmf_result_dir,"ana_result.pkl")
        self._info = MouseInfo(mouse_info_path)
        self.ana_result = self.load_ana_result()

    def load_ana_result(self):
        if os.path.exists(self.ana_result_path):
            with open(self.ana_result_path,'r') as f:
                return pickle.load(f)
        else:
            return {}
    def __del__(self):
        self.save_ana_result_pkl()

    def save_ana_result_pkl(self):
        with open(self.ana_result_path,'wb') as f:
            pickle.dump(self.ana_result_path,f)
        print("ana_result is saved as %s."%self.ana_result_path)


    def si(self):
        """spatial information """
        pass

    def csi(self):
        """context selectivity index"""
        pass

    def hdsi(self):
        """head direction selectivity index"""
        pass

if __name__ == "__main__":
    pass