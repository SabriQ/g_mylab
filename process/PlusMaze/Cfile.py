
from mylab.Cfile import File
import glob,os,sys,re
import pandas as pd
import numpy as np


class PlusMazeLogFile(File):
    def __init__(self,file_path):
        super().__init__(file_path)

        self.date = re.findall(r"(\d{8})-\d{6}",self.file_path)[0]
        self.mouse_id = re.findall(r"(\d+)-\d{8}-\d{6}",self.file_path)[0]
        self.aim = re.findall(r"CrossMaze-(.*)-%s"%self.mouse_id,self.file_path)[0]
        self.data = pd.read_csv(self.file_path ,skiprows=3)


    def cal_seq_length(self):
        choice_class = self.data["Choice_class"].tolist()
        seq_length = []
        for i in range(len(choice_class)):
            if  i == 0:
                seq_length.append(1)
            elif choice_class[i] == 1:
                seq_length.append(seq_length[i-1]+1)
            elif choice_class[i] == 0:
                seq_length.append(0)
        seq_length
        return seq_length

    def cal_total_accuracy(self):
        all_count = self.data.shape[0]
        hit_count = self.data["Choice_class"].sum()
        return hit_count/all_count, all_count


    def cal_context_in_accuracy(self,rule=[2,3,4,1],context_map=["A","B","C","D"]):
        data = self.data
        locations = set(self.data["Choice"]) # [1,2,3,4]
        result = dict()
        for location in locations:
            context  = context_map[location-1]
            # all trial in location 
            selected_data = data[data["Choice"]==location]
            # all_count in location
            all_count = selected_data.shape[0]
            # hit_count in location
            hit_count = selected_data["Choice_class"].sum()
            result[context]=[hit_count/all_count,all_count]

        return result



    def cal_context_info(self):
        data = self.data
        length = data.shape[0]
        locations = set(self.data["Choice"])
        counts = np.full((len(locations),len(locations)),0)
        for i in range(length-1):
            for current_locaion in locations:
                if data.loc[i]["Choice"]==current_locaion:
                    for next_location in locations:
                        if data.loc[i+1]["Choice"] == next_location:
                            counts[current_locaion-1,next_location-1]=counts[current_locaion-1,next_location-1]+1

        return counts

    def plot_start2stop(self):
        matrix = self.cal_context_info()
        new_matrix = np.column_stack((matrix[:,1:],matrix[:,0]))

        sns.heatmap(new_matrix,annot=True,linewidths=1,cbar=False)
        plt.xticks(np.arange(0,4)+0.5,["B","C","D","A"])
        plt.yticks(np.arange(0,4)+0.5,["A","B","C","D"],rotation=0)
        plt.ylabel("start-arm")
        plt.xlabel("stop-arm")
        plt.title("start-->stop %s,%s"%(self.mouse_id,self.date))
        plt.savefig(self.file_path.replace(".csv",".png"),format="png")
        plt.show()