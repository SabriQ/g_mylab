from mylab.process.miniscope.Mfunctions import *
from mylab.process.miniscope.Mplot import *
from mylab.Cmouseinfo import MouseInfo
from mylab.ana.linear_track.Cminiana import MiniAna as MA
import os,sys
#%%
class MiniLWAna(MA):
    def __init__(self,mouse_info_path,cnmf_result_dir):
        super().__init__(mouse_info_path,cnmf_result_dir)
        # self.mouse_info = self.mouse_info.lick_water

    def select_in_context(self,):
        #in_context_contextcoords
        if not "in_context_contextcoords" in self.mouse_info.keys:
            contextcoords=[]
            for video in self.mouse_info.lick_water["behave_videos"]:
                if os.path.exists(video):
                    # print(os.path.basename(video),end=': ')
                    masks,coords = Video(video).draw_rois(aim="in_context",count=1)
                    contextcoords.append((masks,coords))
                else:
                    print("%s 盘符不对"%video)
                    sys.exit()
            self.mouse_info.add_key("in_context_contextcoords",[i[1][0].tolist() for i in contextcoords],exp="lick_water")
            self.mouse_info.save
        else:
            contextcoords = self.mouse_info.lick_water["in_context_contextcoords"]

        #aligned_msblocks_behaveblocks增加“in_context”
        if not "in_context" in self.ana_result["aligned_msblocks_behaveblocks"][0].columns:
            aligned_msblocks_behaveblocks = self.ana_result["aligned_msblocks_behaveblocks"]
            for aligned_msblocks_behaveblock, contextcoord in zip(aligned_msblocks_behaveblocks,contextcoords):
                masks = contextcoord[0][0]
                in_context = []
                for x,y in zip(aligned_msblocks_behaveblock['Body_x'],aligned_msblocks_behaveblock['Body_y']):
                    if 255 in masks[int(y),int(x)]: # according the mask presenting the context area we have drawn, pick out any frame when mouse is in context area 
                        in_context.append(0)
                    else:
                        in_context.append(1)
                aligned_msblocks_behaveblock['in_context'] = in_context
                
            self.update("aligned_msblocks_behaveblocks", aligned_msblocks_behaveblocks)
            print("add condition 'in_context' in aligned_msblocks_behaveblocks")
        else:
            print("'in_context' is already in aligned_msblocks_behaveblocks")

        #产生in_context_msblocks,in_context_behaveblocks
        if not "in_context_msblocks" in self.keys:
            in_context_msblocks=[]
            in_context_behaveblocks=[]
            for msblock, aligned_msblocks_behaveblock in zip(self.ana_result["msblocks"],self.ana_result["aligned_msblocks_behaveblocks"]):
                in_context = aligned_msblocks_behaveblock['in_context']
                in_context_msblock = msblock.iloc[(in_context==1).values]
                in_context_behaveblock=aligned_msblocks_behaveblock.iloc[(in_context==1).values]

                in_context_msblocks.append(in_context_msblock)
                in_context_behaveblocks.append(in_context_behaveblock)
            self.add("in_context_msblocks", in_context_msblocks)
            self.add("in_context_behaveblocks",in_context_behaveblocks)
        else:
            print("'in_context_msblocks' and 'in_context_behaveblocks' are already in ana_result")

        #产生in_context_MeanFr_msblocks
        if not "in_context_MeanFr_msblocks" in self.keys:
            temp = [i.drop(columns=["ms_ts"]).mean().values for i in in_context_msblocks]
            in_context_MeanFr_msblocks = pd.DataFrame(temp,index=self.mouse_info.lick_water["behave_blocknames"],columns=in_context_msblocks[0].columns.drop("ms_ts"))
            self.add("in_context_MeanFr_msblocks", in_context_MeanFr_msblocks)
        else:
            print("'in_context_MeanFr_msblocks' are already in ana_result")


        #产生in_context_msblocks_trials,in_context_behaveblocks
        

        #产生in_context_MeanFr_msblocks_trials

        # 产生





if __name__ == "__main__":
    mouse_info_path = r"Z:\QiuShou\mouse_info\191173_info.txt"
    cnmf_result_dir = r"Z:\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track\Results_191173\20191110_160946_20191028-1102all"
    lw_ana = MiniLWAna(mouse_info_path,cnmf_result_dir)
    lw_ana.select_in_context()