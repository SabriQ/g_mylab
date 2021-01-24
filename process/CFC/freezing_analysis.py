from mylab.process.CFC.Ccfcvideo import CFCvideo
import glob,sys

# 使用前请在powershell 执行 “ conda activate mylab”
# 然后在执行本脚本 python freezing_analysis.py即可

timestamp_method="ffmpeg" # timestamps 的文件，注意在ffmpeg,datetime,miniscope中进行选择
Interval_number=2 # 选第1+7n帧用于计算。产生_freezing_csv文件时，参考coulbourn system每秒有4个数据，所以建议调整产生数据的帧间隔（frame_interval）至每秒4-8个数据左右
diff_gray_value=30 #前后两帧同样像素点位置是否变化的阈值，一般不变，但是当曝光很暗，比如低于10lux时可以适当降低这个值
show = True #显示前100帧视频
threshold = 0.04#当总共至少有多少比例的像素点变化了时，我们认为小鼠时运动着的，这里表示0.52%
start = 0 #分析行为学起始时间, in seconds
stop = 300#分析行为学结束时间 in seconds
show_detail=True#将结果,比如freezing的epoch 输出到屏幕上
percent =True#freezing 时间比列 用省略百分号的百分比表示
save_epoch=True# 将freezing的epoch也存储下来

videolists=glob.glob(r"\\10.10.46.135\share\Qiushou\3_1_coulbourn_system_threshold_test\*.asf")
if not len(videolists)==0:
    [print(i) for i in videolists]
else:
    print("videolists 路径不对")
CFCvideo(videolists[0]).freezing_percentage(
    timestamp_method=timestamp_method
    ,Interval_number=Interval_number
    ,diff_gray_value=diff_gray_value
    ,show = show
    ,threshold = threshold
    ,start = start
    ,stop = stop
    ,show_detail=show_detail
    ,percent =percent
    ,save_epoch=save_epoch)

Batch = True

if Batch: #如果调仓完毕，将Batch=False 改为Batch=
    CFCvideo.freezing_percentages(
        timestamp_method=timestamp_method
        ,videolists=videolists
        ,Interval_number=Interval_number
        ,diff_gray_value=diff_gray_value
        ,show = show
        ,threshold = threshold
        ,start = start
        ,stop = stop
        ,show_detail=show_detail
        ,percent =percent
        ,save_epoch=save_epoch)
else:
    print("you didn't set batch mode, default to analysis the first video in the videolists")