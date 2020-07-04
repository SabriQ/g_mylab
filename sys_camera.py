import subprocess,os,re,time,platform
def get_cameraName():
    if (platform.system()=='Windows'):
        command = [
            "ffmpeg.exe",
            '-list_devices','true',
            '-f','dshow',
            '-i','dummy']
        child = subprocess.Popen(command,stderr=subprocess.PIPE,bufsize=10**8)
    if (platform.system()=='Linux'):
        return r'/dev/video0'
    out = child.communicate()[1].decode("utf-8")
##    print(out)
    pattern = re.compile('"(.*)"')    
    return pattern.findall(out)[1]    ##改这里

def get_cameraParam():
    cameraName = get_cameraName()
    if (platform.system()=="Windows"):
        command=[ 
            "ffmpeg.exe",
            '-list_options','true',
            '-f','dshow',
            '-i','video='+cameraName]
        child = subprocess.Popen(command,stderr=subprocess.PIPE,bufsize=10**8)
        out = child.communicate()[1].decode("utf-8")
##    print(out)
        pattern = re.compile(r'(fps=\d+|s=\d+x\d+)')
    
    if (platform.system()=='Linux'):
        command = [
            "ffmpeg",
            '-f','v4l2',
            '-list_formats','all',
            '-i',cameraName]
        child = subprocess.Popen(command,stdout = subprocess.PIPE,stderr=subprocess.PIPE,bufsize=10**8)
        out = child.communicate()[1].decode('utf-8')
        print(out)
        pattern = re.compile(r'( \d{3}x\d{3})')
    
    return pattern.findall(out)
    
def video_online_play():
    cameraName = get_cameraName()
    if (platform.system()=="Windows"):
        command = [
        "ffplay.exe",
        '-f','dshow',
        '-video_size','640x480',
        '-i','video='+cameraName,
        '-vf',r"drawtext=fontsize=12:text='%{localtime\:%Y\-%m\-%d %H\\\:%M\\\:%S}':fontcolor=green'",
        '-loglevel','quiet']
        child = subprocess.Popen(command,stdin=subprocess.PIPE,encoding='utf-8')
    if (platform.system()=="Linux"):
        command = [
            "ffplay",
            '-f','v4l2',
            '-video_size','640x480',
            '-i',cameraName,
            '-vf',r"drawtext=fontsize=16:text='%{localtime\:%Y\-%m\-%d %H\\\:%M\\\:%S}':fontcolor=green'",
            '-loglevel','quiet']
        child = subprocess.Popen(command,stdin=subprocess.PIPE,encoding='utf-8')
    return child
def video_recording(video_name):
    cameraName = get_cameraName()
    if (platform.system()=="Windows"):
        command = [
        "ffmpeg.exe",
        '-f','dshow',
        '-rtbufsize','2G',
        '-video_size','640x480',
        '-i','video='+cameraName,
        '-vcodec','rawvideo',
        '-pix_fmt','yuv420p',    
        '-vf',r"drawtext=fontsize=12:text='%{localtime\:%Y\-%m\-%d %H\\\:%M\\\:%S}':fontcolor=green'",
        '-f','sdl','Recording',
        '-vf',r"drawtext=fontsize=12:text='%{localtime\:%Y\-%m\-%d %H\\\:%M\\\:%S}':fontcolor=white'",
        '-loglevel','quiet',
        video_name ]
        child = subprocess.Popen(command,stdin=subprocess.PIPE,encoding='utf-8')
    if (platform.system()=="Linux"):
        command = [
        'ffmpeg',
        '-f','v4l2',
        '-rtbufsize', '2G',
        '-video_size', '640x480',
        '-i',cameraName,
        '-vcodec','rawvideo',
        '-pix_fmt','yuv420p',
        '-vf',"drawtext=fontsize=18:text='%{localtime\:%Y\-%m\-%d %H\\\\\:%M\\\\\:%S}':fontcolor=green",
        '-f', 'sdl', "/dev/video0-Recording",
        '-vf',"drawtext=fontsize=18:text='%{localtime\:%Y\-%m\-%d %H\\\\\:%M\\\\\:%S}':fontcolor=blue",
        '-loglevel','quiet',video_name] 
        child = subprocess.Popen(command,stdin=subprocess.PIPE,encoding='utf-8')
    return child
if __name__ == "__main__":
    video_online_play()
