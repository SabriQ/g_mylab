import pickle
import os,sys
import glob
from scipy.io import savemat
import scipy.io as spio
import numpy as np
from caiman.source_extraction.cnmf.cnmf import load_CNMF

def Concatenate_ms_ts(fnames=['data_endscope.tif'],newpath=None):
    ms_ts=[]
    ms_ts_path = os.path.join(newpath,"ms_ts.pkl")
    ms_ts_mat_name = os.path.join(newpath,'ms_ts.mat')
    for fname in fnames:
        single_ms_ts = os.path.join(os.path.basename(fname),"ms_ts.pkl")
        with open(single_ms_ts,'rb') as f:
            ts = pickle.load(f)
        ms_ts.append(ts)
    with open(ms_ts_name,'wb') as output:
        pickle.dump(ms_ts,output,pickle.HIGHEST_PROTOCOL)
    savemat(ms_ts_mat_name,{'ms_ts':ms_ts})

def load_mat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict


def pkl2mat(ms_mat_path):
    result = load_mat(ms_mat_path)

    hdf = os.path.join(os.path.dirname(ms_mat_path),"result.hdf5")
    pkl_path = os.path.join(os.path.dirname(ms_mat_path),"ms_ts.pkl")
    # cnm = load_CNMF(hdf)
    # SFP = cnm.estimates.A
    # SFP_dims = list(cnm.dims).append(len(cnm.estimates.idx_components_bad)+len(cnm.estimates.idx_components))
    # SFP = np.reshape(SFP.toarray(), SFP_dims, order='F')

    mat_path = os.path.join(os.path.dirname(ms_mat_path),"ms2.mat")

    with open(pkl_path,"rb") as f:
        ms_ts = pickle.load(f)

    result["ms"]["ms_ts"]=ms_ts
    # result["ms"]["SFP"]=SFP
    savemat(mat_path,result)

if __name__ == "__main__":
    pathes = [r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_201017\20200422_144525_10fps\ms.mat",
    r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_201018\20200422_155451_10fps\ms.mat",
    r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_201019\20200422_155524_10fps\ms.mat"]
    for path in pathes:
        pkl2mat(path)
