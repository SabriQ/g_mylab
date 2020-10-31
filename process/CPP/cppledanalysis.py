import glob,os,sys
from mylab.process.CPP.Ccppvideo import CPP_Video
from mylab.process.CPP.Ccppfile import CPPLedPixelValue




def cpp_led_value_of_lickwater(video,thresh=900,show=False):
    """
    video: video path
    thresh: define led off when pixel value is lesh than thresh
    show: boolen. show trace of leds pixel values when True
    """
    v = CPP_Video(video)
    # generate ***_led_value_ts.csv
    if not os.path.exists(v.led_value_ts):
        v.leds_pixel_value(v.tracked_coords)
    else:
        print("***_ledvalue_ts.csv file has been generated")
    # add led1,led2 off/offset in csv
    f = CPPLedPixelValue(v.led_value_ts)    
    f.lick_water(thresh=thresh,led1_trace=f.df["1"],led2_trace=f.df["2"],show=show)



if __name__ == "__main__":
    videos = glob.glob(r"C:\Users\Sabri\Desktop\LED_CPP_demo\*.AVI")

    for video in videos:    
        cpp_led_value_of_lickwater(video)