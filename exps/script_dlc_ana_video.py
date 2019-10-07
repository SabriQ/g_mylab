import deeplabcut
import glob
import sys
print(">>>>>>>")
print("1-2 attention to the 'config_path' please ")
print("2-2 attention to the 'glob.glob()' please ")
print("<<<<<<<")

videolists = sys.argv[1]

config_path = sys.argv[2]


deeplabcut.analyze_videos(config_path,videolists,shuffle=1,save_as_csv=True,videotype=sys.argv[3])
deeplabcut.plot_trajectories(config_path,videolists)
deeplabcut.create_labeled_video(config_path,videolists)