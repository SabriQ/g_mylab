import pickle
import os,sys
import glob
from scipy.io import savemat
import scipy.io as spio
import numpy as np
# from caiman.source_extraction.cnmf.cnmf import load_CNMF

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
    """
    将ms_ts.pkl写入到ms.mat中
    考虑仅有一个ms_ts.pkl的情况
    """
    result = load_mat(ms_mat_path)

    hdf = os.path.join(os.path.dirname(ms_mat_path),"result.hdf5")
    pkl_path = os.path.join(os.path.dirname(ms_mat_path),"ms_ts.pkl")
    ms_mat_path = os.path.join(os.path.dirname(ms_mat_path),"ms_ts.mat")
    # cnm = load_CNMF(hdf)
    # SFP = cnm.estimates.A
    # SFP_dims = list(cnm.dims).append(len(cnm.estimates.idx_components_bad)+len(cnm.estimates.idx_components))
    # SFP = np.reshape(SFP.toarray(), SFP_dims, order='F')

    mat_path = os.path.join(os.path.dirname(ms_mat_path),"ms2.mat")
    try:
        with open(pkl_path,"rb") as f:
            ms_ts = pickle.load(f)
    except:
        ms_ts = load_mat(ms_mat_path)["ms_ts"]

    result["ms"]["ms_ts"]=ms_ts
    # result["ms"]["SFP"]=SFP
    savemat(mat_path,result)

def pkl2mat2(ms_mat_path):
    """
    将多个ms_ts.pkl写入到一个ms.mat中
    考虑多天合并跑的情况
    """

    result = load_mat(ms_mat_path)

    # hdf = os.path.join(os.path.dirname(ms_mat_path),"result.hdf5")
    pkl_pathes = glob.glob(os.path.join(os.path.dirname(ms_mat_path),"*\ms_ts.pkl"))
    # print(pkl_pathes)
    # cnm = load_CNMF(hdf)
    # SFP = cnm.estimates.A
    # SFP_dims = list(cnm.dims).append(len(cnm.estimates.idx_components_bad)+len(cnm.estimates.idx_components))
    # SFP = np.reshape(SFP.toarray(), SFP_dims, order='F')

    mat_path = os.path.join(os.path.dirname(ms_mat_path),"ms2.mat")
    ms_ts_all=[]
    for pkl_path in pkl_pathes:
        with open(pkl_path,"rb") as f:
            ms_ts = pickle.load(f)
        for temp in ms_ts:
            ms_ts_all.append(np.array(temp))
    result["ms"]["ms_ts"]=np.array(ms_ts_all)
    savemat(mat_path,result)
    print("save mat %s"%mat_path)
    
def ms_tses2ms_ts(dirpath):
    """
    将每天的ms_ts.pkl合并成一个ms_ts.mat/ms_ts.pkl
    """
    ms_tses = glob.glob(os.path.join(dirpath,"*[0-9]/ms_ts.pkl"))
    [print(i) for i in ms_tses]
    mss = []
    for ms_ts in ms_tses:
        with open(ms_ts,"rb") as f:
            ms = pickle.load(f)
        print(len(ms))
        [mss.append(i) for i in ms]
    print(len(mss))
    pklpath=os.path.join(dirpath,"ms_ts.pkl")
    matpath=os.path.join(dirpath,"ms_ts.mat")

    savemat(matpath,{'ms_ts':np.array(mss)})

    with open(pklpath,"wb") as output:
        pickle.dump(mss,output)

    print("concate all the ms_ts and saved")

if __name__ == "__main__":
    # ms_tses2ms_ts(dirpath=r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_201033")
    # ms_tses2ms_ts(dirpath=r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_201034")
    ms_tses2ms_ts(dirpath=r"\\10.10.46.135\share\zhangna\miniscope_result\Results_201037")
    ms_tses2ms_ts(dirpath=r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_202061")
    # pathes = [r"\\10.10.47.163\Data_archive\chenhaoshan\miniscope_results\Results_201033\ms.mat"]
    # for path in pathes:
    #     pkl2mat2(path)
    
    # pathes = glob.glob(r"\\10.10.46.135\share\zhangna\4_Miniscope\miniscope_result\*\ms.mat")
    # for path in pathes:
    #     pkl2mat2(path)
