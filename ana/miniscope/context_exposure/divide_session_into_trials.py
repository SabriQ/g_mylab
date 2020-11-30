import glob,cv2,os,re
from mylab.ana.miniscope.context_exposure.Cminiana import divide_sessions_into_trials
from multiprocessing import Pool

if __name__ == '__main__':
    raw_data_dir = r"\\10.10.46.135\Lab_Members\_Lab Data Analysis\02_Linear_Track\Miniscope_Linear_Track\batch3\Results_*\part*"
    sessions = glob.glob(os.path.join(raw_data_dir,"session*.pkl"))
    

    pool = Pool(processes=8)
    pool.map(divide_sessions_into_trials,sessions)