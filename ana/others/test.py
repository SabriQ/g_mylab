import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


videotrack_path = r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\2019031100002_tracking.csv'
video_path = r'C:\Users\Sabri\Desktop\program\video\video_analyze\correct_coord\2019031100002.AVI'

track = pd.read_csv(videotrack_path)
Frame_No = track['Frame']

X = list(track['X'])
Y = list(track['Y'])

