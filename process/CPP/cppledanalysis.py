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

def cpp_led_value(video):
    """
    video: video path
    thresh: define led off when pixel value is lesh than thresh
    show: boolen. show trace of leds pixel values when True
    """
    v = CPP_Video(video)

    v.leds_pixel_value(half_diameter=8,according="median",binarize=True)
    # add led1,led2 off/offset in csv
    print("***_ledvalue_ts.csv file is generated")


if __name__ == "__main__":
    videos = glob.glob(r"/run/user/1000/gvfs/smb-share:server=10.10.46.135,share=share/ChenHaoshan/cpp_led/*/*/*.AVI")
    [print(i) for i in videos]
    pool = Pool(processes=8)


    for video in videos:
        pool.apply_async(cpp_led_value,args=(video,))

    pool.close()
    pool.join()
