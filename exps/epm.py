import sys,os
import time
class EPM(Exp):
    def __init__(self,port,data_dir):
        super().__init__(port,data_dir)

    def __call__(self,mouse_id,data_dir="",):
        self.mouse_id = mouse_id
        video_name = "EPM_"+self.mouse_id+'-'+time.strftime("%Y%m%d-%H%M%S", time.localtime())+'.mp4'
        self.video_path = os.path.join(video_dir,video_name)

        self.run(app=app)

    def run(self,app):
        p = self.record_camera(self.video_path)
        app()
        self.stop_camera(p)

    def Epm_opto(self):     
        '''
        1 start the video recording
        2 3min for arms exploration without laser
        3 3min for arms exploration with laser, led on when laser on or off
        4 3min for arms exploration without laser
        5 3min for arms exploration with laser
        ''' 
        print(">>>without laser for 3 mins: ")
        self.ser.write("2".encode())
        self.countdown(180)
        print(">>>with laser(20HZ,5ms on and 45ms off) for 3mins: ")
        self.ser.write('1'.encode())
        self.countdown(180) 
        print(">>>without laser for 3mins: ")
        self.ser.write('2'.encode())
        self.countdown(180)
        
    

if __name__ =="__main__":
    epm = EPM()
    epm()