from mylab.ana.miniscope.context_exposure.Cminiana import *
from mylab.developing.single_cell_analysis.Mfunctions import *
from mylab.Functions import *

import glob,sys,os,re
from multiprocessing import Pool



def savecelltypes2(session):
    mouse_id = re.findall("Results_(\d+)",session)[0]
    part = re.findall("part(\d+)",session)[0]
    session_num = re.findall("session(\d+).pkl",session)[0]
    filename = "cell_type_%s_part%s_session%s.pkl"%(mouse_id,part,session_num)

    savepath = os.path.join(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\results\celltypes",filename)
    print(filename)
    try:
        contextcells,rdcells,pccells = cellids(session)
        if type(contextcells) == int:
            savepath = savepath.replace(".pkl","_hc.pkl")
        save_pkl(result={
            "mouse_id":mouse_id,
            "part":part,
            "session":session_num,
            "contextcells":contextcells,
            "rdcells":rdcells,
            "pccells":rdcells},result_path=savepath)
    except:
        savepath = savepath.replace(".pkl","_bug.pkl")
        save_pkl(result={
            "mouse_id":mouse_id,
            "part":part,
            "session":session},result_path=savepath)

    print("========================================")
    
def savecelltypes(mouse_id,part,day):
    session = build_session(mouse_id,part,day)
    filename = "cell_type_%s_part%s_day%s.pkl"%(mouse_id,part,day)
    savepath = os.path.join(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\results\celltypes",filename)
    try:
        contextcells,rdcells,pccells = cellids(session)
        if type(contextcells) == int:
            savepath = savepath.replace(".pkl","_hc.pkl")
        save_pkl(result={
            "mouse_id":mouse_id,
            "part":part,
            "day":day,

            "contextcells":contextcells,
            "rdcells":rdcells,
            "pccells":rdcells},result_path=savepath)
    except:
        savepath = savepath.replace(".pkl","_bug.pkl")
        save_pkl(result={
            "mouse_id":mouse_id,
            "part":part,
            "session":session},result_path=savepath)
    print("=====%s-%s-%s======"%(mouse_id,part,day))

if __name__ == "__main__":

    # file_pathes1 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_201033-finish\part*")
    # file_pathes2 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_201034-finish\part*")
    # file_pathes3 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_206551-finish\part*")
    # file_pathes4 = glob.glob(r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_206552-finish\part*")

    # file_pathes = file_pathes1+file_pathes2+file_pathes3+file_pathes4

    
    # for file_path in file_pathes:
    #     sessions = glob.glob(os.path.join(file_path,"session*.pkl"))
    #     # for session in sessions:
    #     #     func(session)
    #     [print(i) for i in sessions]
    #     pool = Pool(processes=8)

    #     pool.map(func,sessions)

    mouse_id="201033"
    part = "1"
    days = ["20200721","20200722","20200723","20200724"]
    for day in days:
        if day == "20200722":
            savecelltypes(mouse_id,part,day)
