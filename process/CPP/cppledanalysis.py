import glob,os,sys
from mylab.process.CPP.Ccppvideo import CPP_Video
from mylab.process.CPP.Ccppfile import CPPLedPixelValue

from multiprocessing import Pool


def cpp_led_value_of_lickwater_c(video,thresh=900,show=False):
    """
    video: video path
    thresh: define led off when pixel value is lesh than thresh
    show: boolen. show trace of leds pixel values when True
    """
    v = CPP_Video(video)
    # generate ***_led_value_ts.csv
    if not os.path.exists(v.led_value_ts):
        v.leds_pixel_value(half_diameter=8,according="each_frame",binarize=True)
        # add led1,led2 off/offset in csv
        f = CPPLedPixelValue(v.led_value_ts)    
        f.lick_water(thresh=thresh,led1_trace=f.df["1"],led2_trace=f.df["2"],show=show)
        print("***_ledvalue_ts.csv file is generated")
    else:
        print("***_ledvalue_ts.csv file has been generated")

def add_led_value(video):
    """
    video: video path
    thresh: define led off when pixel value is lesh than thresh
    show: boolen. show trace of leds pixel values when True
    """
    v = CPP_Video(video)

    v.leds_pixel_value(half_diameter=8,according="median",binarize=True)
    # add led1,led2 off/offset in csv
    print("***_ledvalue_ts.csv file is generated")

def add_led_offset(video):
    """
    """
    v = CPP_Video(video)
    if os.path.exists(v.led_value_ts):
        f = CPPLedPixelValue(v.led_value_ts)
        f.lick_water(baseline=(30,5),threshold=None,led1_trace=None,led2_trace=None,save=True,show=False)
    else:
        cpp_led_value(video)
        add_led_offset(video)

def add_both(video):
    print("=======%s========"%os.path.basename(video))
    # add led_value
    v = CPP_Video(video)
    v.leds_pixel_value(half_diameter=8,according="median",binarize=True)
    # add led off/offset
    f = CPPLedPixelValue(v.led_value_ts)
    f.lick_water(baseline=(30,5),threshold=None,led1_trace=None,led2_trace=None,save=True,show=False)

if __name__ == "__main__":
    videos = glob.glob(r"/run/user/1000/gvfs/smb-share:server=10.10.46.135,share=lab_members/XuChun/Lab Projects/03_IBIST/chenhaoshan/IBIST_behavior/*/CPP/*/*/*.AVI")
    [print(i) for i in videos]
    pool = Pool(processes=8)

    pool.map(add_both,videos)
    # for video in videos:
    #     pool.apply_async(add_led_offset,args=(video,)) # 非阻塞 apply
    #     # pool.apply(cpp_led_value,args=(video,)) # 阻塞
    # pool.close()
    # pool.join()
