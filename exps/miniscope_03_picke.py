# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:36:20 2019

@author: Sabri
"""

from Cfile import TrackFile
from Cvideo import Video

# for each video
# track file
# read log file; read track file
# 计算速度
##去除roi外的点，用前后的平均值作为补充
##对log file 的每一个点：
    1 其前的一个时间点（@ crossline）作为context exit
    2 其后的一个时间点（@ crossline）作为context enter
    3 其后的一个时间点（@ speed=0 , which last >2s）作为lick start
    4 any time when speed = 0 & last >1s defined as 停顿
        停顿 include 抓挠，啃食，阻挠
    5 any time there is a rotate about 180 degree defined as 转身
    6 any time there is a decrease between head and tail, defined as 攀爬
