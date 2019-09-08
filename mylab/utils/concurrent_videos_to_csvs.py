from mylab.exps.cfc import video_to_csv as v2c
import os,sys
import concurrent.futures
import glob
if __name__ == '__main__':
    if len(sys.argv)==3:
        dir_path_pattern = sys.argv[1] # "~/video/*/*.asf"
        numberCores = sys.argv[2]
    elif len(sys.argv)==2:
        dir_path_pattern = sys.argv[1]
        numberCores = 2
    else:
        print("dir_path_pattern and numberCores are lacking",end=' ')
        print("Input like this:\n'python concurrent_freezing_analysis_for_videos_in_one_folder.py ~/*/*asf 2'" )
        sys.exit()

    videolists = glob.glob(dir_path_pattern)
    if len(videolists)==0:
        print("there are no video choosed")
    else:
        print(videolists)
        with concurrent.futures.ProcessPoolExecutor(max_workers=int(numberCores)) as executor:
            for i,_ in enumerate(executor.map(v2c,videolists),1):
                print (f'{i}/{len(videolists)} is done')


    
