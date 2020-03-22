import os

zdat_path = r'Y:\zhangna\vgat-gain_function_acquisition\20190718'
video_path = r'Y:\zhangna\vgat-gain_function_acquisition\20190718\Video'

def f(zdat_path,extension):
    for i in os.listdir(zdat_path):
        i = os.path.join(zdat_path,i)
        if os.path.isfile(i):
            if os.path.splitext(i)[1] == extension:
##                print(i)
                name.append(i)
        else:
            f(i,extension)    
    return name 
        
name = []
zdatnames = f(zdat_path,'.zdat')
name = []
videonames = f(video_path,'.asf')



for zdatname in zdatnames:
##    print(zdatname)
    for videoname in videonames:
        #print('>>>',videoname)
        judge = videoname.split('\\')[-1].replace('Cam-1.asf','')
##        print(judge)
        if judge[0:-3] in zdatname:
            prefix = zdatname.split('\\')[-2]
            #print(prefix)
            newvideoname = videoname.replace(judge,prefix+'_'+judge)
            #print(newvideoname)
            os.rename(videoname,newvideoname)
