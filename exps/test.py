
import matplotlib.pyplot as plt
import numpy as np
import time 
class StreamGraph():
    def __init__(self):
        pass




    
    def run(self):
        
            plt.ion()
            self.fig = plt.figure()
            trial = self.gen_data()
            while True:
                
                try:
                    data = next(trial)
                except Exception as e:
                    print(">>>>>")
                    plt.ioff()
                    plt.show()
                    break
                else:
                    plt.cla()
                    print("data:",data)
                    self.line = plt.plot(data,[i**3 for i in data],'--')[0]
                    self.fig.canvas.draw()
                    plt.pause(0.5)
                    



            # for data in self.gen_data():
            #     plt.cla()
            #     # plt.xlim((1,10))
            #     # plt.ylim((1,10))
            #     self.line = plt.plot(data,[i**3 for i in data],'--')[0]

            #     self.fig.canvas.draw()
            #     plt.pause(0.5)



            # plt.close()
            # plt.show()
        # data = [1,2,3]

        # while True:
        #     print("----1-----")
        #     # a = next(self.gen_data())
        #     data.append(4)
        #     self.set_graph(data)
        #     time.sleep(5)
        #     print("----4-----")


    def gen_data(self):
        print("----2-----")
        for i in range(100):
            print("---%s-----"%i)
            # time.sleep(2)
            yield [j for j in range(i)]
            

    def set_graph(self,data):
        plt.clf()
        self.line.set_xdata(data)
        self.line.set_ydata(data)
        self.line.figure.canvas.draw()

    def AcuracyTrial_Num(self, datalist,showLen = 10):

        plt.clf()
        xdata = np.linspace(1,len(datalist),len(datalist))[-1*showLen:]
        ydata = datalist[-1*showLen:]
        # plt.cla()
        self.ax1.set_xlim([0, showLen])
        self.ax1.set_ylim([min(ydata), max(ydata)])
        self.ax1.plot(xdata, ydata, '-o',linewidth=2, color='coral', label="Line1")
        
        plt.xlabel('Acuracy (%)')
        plt.ylabel('Trial_Num')
        plt.title('Acuracy-Trial_Num')
        print("------")

        # self.ax1.figure.canvas.draw()
        plt.show()
        # plt.pause(0)

if __name__ == "__main__":
    graph = StreamGraph()
    graph.run()
    # graph.AcuracyTrial_Num(showLen=10,datalist=[i for i in range(70)])
