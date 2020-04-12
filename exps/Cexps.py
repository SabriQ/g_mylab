import serial
import serial.tools.list_ports
import subprocess
import time
import os
import sys
from mylab.sys_camera import video_online_play
from mylab.sys_camera import video_recording

class Exp():
    def __init__(self,port):
        self.port = port

        try:
          self.ser = serial.Serial(self.port,baudrate=9600,timeout=0.1)   
          self.countdown(3) 
        except Exception as e:
          print(e)
          ports = [i.device for i in serial.tools.list_ports.comports()]
          print("choose port from %s"% ports)
          sys.exit()


    @staticmethod
    def countdown(seconds):
        i=0
        while True:
            sys.stdout.write("%.1is in total %ss"%(i,seconds))
            sys.stdout.write("\r")
            time.sleep(1)
            i += 1
            if i >= seconds:
                #sys.stdout.write("%s countdown finished"%seconds)
                break

    def record_camera(self,video_path):
        print("----start camera recording----")
        p = video_recording(video_path)
        time.sleep(3)
        return p
    def play_camera(self):
        print("----start camera playing----")
        p = video_online_play()
        return p
    def stop_record_camera(self,p):
        print("----stop camera----")
        time.sleep(1)
        try:
            p.kill()                  
        except Exception as e:
            print(e)

    def __del__(self):
        self.close()

    def close(self):
        self.ser.close()
        print('PORT:%s get closed'%self.port)
if __name__ == "__main__":
    exp = Exp("test")
    p = exp.play_camera()
    exp.countdown(4)
    exp.stop_record_camera(p)
